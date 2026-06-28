from typing import Type, TypeVar, Literal
from pydantic import BaseModel
from openai import OpenAI
from datetime import datetime

T = TypeVar("T", bound=BaseModel)


class Updates(BaseModel):
    company_name: str
    job_title: str | None
    reference_number: str | None
    update_type: Literal[
        "application_received",
        "in_review",
        "missing_documents",
        "online_interview",
        "on_site_interview",
        "offer",
        "rejection",
        "withdrawn",
        "on_hold",
        "no_update",
        "other",
    ]
    contact_person: str | None
    contact_email: str | None
    short_summary: str | None
    confidence: float | None
    email_sent_date: datetime | None


def run_structured_prompt(model_cls: Type[T], *, prompt: str, instructions: str) -> T:
    client = OpenAI()
    response = client.responses.parse(
        model="gpt-4o-mini",
        instructions=instructions,
        input=prompt,
        text_format=model_cls,
        max_output_tokens=500,
    )
    return response.output_parsed


class E_Mail(BaseModel):
    subject: str
    body: str
    sender: str
    date: datetime

    def is_possibly_relevant(self) -> bool:
        """
        Determine if the email is relevant to job applications or hiring processes.
        """

        instructions = """
Return true only if this email clearly refers to a specific job application the user has already submitted.

Return false for job suggestions, job alerts, recommendations, newsletters, generic job ads, networking, recruiter marketing, and career tips.

A suggested job is never an existing application.
If uncertain, return false.
"""

        class App_Relevant(BaseModel):
            is_relevant: bool

        response = run_structured_prompt(App_Relevant, prompt=f"Subject: {self.subject}, Body: {self.body}, Sender: {self.sender}, Date: {self.date}", instructions=instructions)

        return response.is_relevant

    def classify(self):
        instructions = (
            "Extract the most relevant and recent information from this email regarding the job application."
        )

        print(f"Classifying email")
        response = run_structured_prompt(Updates, prompt=f"Subject: {self.subject}\n\nBody: {self.body}\n\nSender: {self.sender}\n\nDate: {self.date}", instructions=instructions)

        return response
