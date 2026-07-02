import requests
import plotly.express as px
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
API_URL = os.getenv("API_URL")


class DataHandler:
    @staticmethod
    def fetch_database(search_company=None, update_type=None, max_age=None):
        response = requests.get(API_URL + "/api/database")
        df = pd.DataFrame(*response.json())
        df["date"] = pd.to_datetime(df["date"], errors="coerce")  # Convert date column to datetime

        if search_company:
            df = df[df["company_name"].str.contains(search_company, case=False)]
        if update_type:
            df = df[df["update_type"].str.contains(update_type, case=False)]
        if max_age is not None:
            df = df[df["date"] >= pd.Timestamp.now(tz="UTC") - pd.to_timedelta(max_age, unit="d")]
        df = df.sort_values(by="date", ascending=False).reset_index(drop=True)
        return df

    @staticmethod
    def create_scatter_plot(df):
        fig = px.scatter(
            df,
            x="date",
            y="company_name",
            color="update_type",
            hover_data=["job_title", "reference_number", "contact_person", "contact_email", "short_summary", "confidence"],
            title="Application Timeline",
        )

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Company",
            height=500,
        )
        fig.update_yaxes(
        categoryorder="array",
        categoryarray=sorted(df["company_name"].dropna().unique(), reverse=True)
        )
        return fig
    
    @staticmethod
    def save_changes(df: pd.DataFrame):
        df = df.copy()

        if "date" in df.columns:
            df["date"] = (
                pd.to_datetime(df["date"], errors="coerce", utc=True)
                .dt.strftime("%Y-%m-%d %H:%M:%S+00")
            )
        df = df.astype(object)  
        df = df.fillna(None)

        response = requests.post(
            API_URL + "/api/save_changes",
            json=df.to_dict(orient="records"),
            timeout=10
        )
        response.raise_for_status()
        return response.json()

