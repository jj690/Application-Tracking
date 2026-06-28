import psycopg
from mail_model import Updates


class SQLHandler:
    def __init__(self, db_connection: psycopg.Connection):
        self.db_connection = db_connection

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id SERIAL PRIMARY KEY,
                company_name TEXT NOT NULL,
                job_title TEXT,
                reference_number TEXT,
                update_type TEXT NOT NULL,
                contact_person TEXT,
                contact_email TEXT,
                short_summary TEXT,
                confidence REAL,
                date TEXT
            )
            """)
        self.db_connection.commit()

    def insert_email(self, email: Updates):
        self.create_table()  # Ensure the table exists before inserting
        cursor = self.db_connection.cursor()
        cursor.execute(
            "INSERT INTO emails (company_name, job_title, reference_number, update_type, contact_person, contact_email, short_summary, confidence, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                email.company_name,
                email.job_title,
                email.reference_number,
                email.update_type,
                email.contact_person,
                email.contact_email,
                email.short_summary,
                email.confidence,
                email.email_sent_date,
            ),
        )
        self.db_connection.commit()

    def get_all_emails(self):
        self.create_table()  # Ensure the table exists before querying
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM emails")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        entries_dicts = [dict(zip(column_names, row)) for row in rows]
        return entries_dicts

    def save_changes(self, df: list[dict]):
        self.create_table()  # Ensure the table exists before saving changes
        cursor = self.db_connection.cursor()

        incoming_ids = []
        for row in df:
            row_id = row.get("id")
            if row_id is None:
                continue

            incoming_ids.append(row_id)
            cursor.execute(
                "UPDATE emails SET company_name=%s, job_title=%s, reference_number=%s, update_type=%s, contact_person=%s, contact_email=%s, short_summary=%s, confidence=%s, date=%s WHERE id=%s",
                (
                    row["company_name"],
                    row["job_title"],
                    row["reference_number"],
                    row["update_type"],
                    row["contact_person"],
                    row["contact_email"],
                    row["short_summary"],
                    row["confidence"],
                    row["date"],
                    row_id,
                ),
            )

        if incoming_ids:
            placeholders = ", ".join(["%s"] * len(incoming_ids))
            cursor.execute(f"DELETE FROM emails WHERE id NOT IN ({placeholders})", incoming_ids)
        else:
            cursor.execute("DELETE FROM emails")

        self.db_connection.commit()
