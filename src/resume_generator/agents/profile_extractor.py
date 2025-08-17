import json
from datetime import datetime
from typing import Any

from resume_generator.agents.base import BaseAgent
from resume_generator.models.schemas import (
    Certification,
    ContactInfo,
    Education,
    Experience,
    Project,
    UserProfile,
)
from resume_generator.workflows.state import WorkflowState


class ProfileExtractorAgent(BaseAgent):
    def extract_profile(self, state: WorkflowState) -> WorkflowState:
        try:
            user_profile_raw = state.get("user_profile_raw", "")
            if not user_profile_raw:
                state["errors"] = state.get("errors", []) + ["No user profile data provided"]
                return state

            system_message = """
            You are an expert at extracting structured information from resumes and user profiles.
            Your task is to parse the provided user profile text and extract relevant information into a structured format.
            
            Extract the following information:
            - Full name
            - Contact information (email, phone, linkedin, github, portfolio, location)
            - Professional summary
            - Skills (technical and soft skills)
            - Education (institution, degree, field of study, graduation date, GPA if mentioned, relevant coursework)
            - Work experience (company, position, start/end dates, description, key achievements, technologies used)
            - Projects (name, description, technologies used, URL if available, achievements)
            - Certifications (name, issuer, dates, credential URL if available)
            - Languages
            
            Return ONLY a valid JSON object that matches the UserProfile schema structure.
            For dates, use YYYY-MM-DD format. If only year is available, use YYYY-01-01.
            If information is not available, omit the field or use empty arrays/null as appropriate.
            """

            user_message = f"Extract structured information from this user profile:\n\n{user_profile_raw}"

            messages = self.create_prompt(system_message, user_message)
            response = self.llm.invoke(messages)

            # Parse the JSON response
            profile_data = json.loads(response.content)

            # Convert to Pydantic model
            user_profile = self._parse_profile_data(profile_data)

            state["user_profile"] = user_profile
            state["step_completed"] = state.get("step_completed", []) + ["profile_extraction"]

        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Profile extraction error: {str(e)}"]

        return state

    def _parse_profile_data(self, data: dict[str, Any]) -> UserProfile:
        # Parse contact info
        contact_data = data.get("contact_info", {})
        contact_info = ContactInfo(
            email=contact_data.get("email", ""),
            phone=contact_data.get("phone"),
            linkedin=contact_data.get("linkedin"),
            github=contact_data.get("github"),
            portfolio=contact_data.get("portfolio"),
            location=contact_data.get("location"),
        )

        # Parse education
        education_list = []
        for edu_data in data.get("education", []):
            education = Education(
                institution=edu_data.get("institution", ""),
                degree=edu_data.get("degree", ""),
                field_of_study=edu_data.get("field_of_study"),
                graduation_date=self._parse_date(edu_data.get("graduation_date")),
                gpa=edu_data.get("gpa"),
                relevant_coursework=edu_data.get("relevant_coursework", []),
            )
            education_list.append(education)

        # Parse experience
        experience_list = []
        for exp_data in data.get("experience", []):
            experience = Experience(
                company=exp_data.get("company", ""),
                position=exp_data.get("position", ""),
                start_date=self._parse_date(exp_data.get("start_date")),
                end_date=self._parse_date(exp_data.get("end_date")),
                description=exp_data.get("description", ""),
                key_achievements=exp_data.get("key_achievements", []),
                technologies_used=exp_data.get("technologies_used", []),
            )
            experience_list.append(experience)

        # Parse projects
        projects_list = []
        for proj_data in data.get("projects", []):
            project = Project(
                name=proj_data.get("name", ""),
                description=proj_data.get("description", ""),
                technologies_used=proj_data.get("technologies_used", []),
                url=proj_data.get("url"),
                achievements=proj_data.get("achievements", []),
            )
            projects_list.append(project)

        # Parse certifications
        certifications_list = []
        for cert_data in data.get("certifications", []):
            certification = Certification(
                name=cert_data.get("name", ""),
                issuer=cert_data.get("issuer", ""),
                issue_date=self._parse_date(cert_data.get("issue_date")),
                expiry_date=self._parse_date(cert_data.get("expiry_date")),
                credential_url=cert_data.get("credential_url"),
            )
            certifications_list.append(certification)

        return UserProfile(
            full_name=data.get("full_name", ""),
            contact_info=contact_info,
            professional_summary=data.get("professional_summary"),
            skills=data.get("skills", []),
            education=education_list,
            experience=experience_list,
            projects=projects_list,
            certifications=certifications_list,
            languages=data.get("languages", []),
        )

    def _parse_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            try:
                return datetime.strptime(f"{date_str}-01-01", "%Y-%m-%d").date()
            except Exception:
                return None

    def process(self, state: dict[str, Any]) -> dict[str, Any]:
        return self.extract_profile(state)  # type: ignore
