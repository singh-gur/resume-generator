import json
from typing import Any

from resume_generator.agents.base import BaseAgent
from resume_generator.models.schemas import JobDescription, JobRequirement
from resume_generator.workflows.state import WorkflowState


class JobAnalyzerAgent(BaseAgent):
    def analyze_job(self, state: WorkflowState) -> WorkflowState:
        try:
            job_description_raw = state.get("job_description_raw", "")
            if not job_description_raw:
                state["errors"] = state.get("errors", []) + ["No job description data provided"]
                return state

            system_message = """
            You are an expert at analyzing job descriptions and extracting structured information.
            Your task is to parse the provided job description and extract relevant information into a structured format.
            
            Extract the following information:
            - Job title
            - Company name
            - Location (if mentioned)
            - Job type (full-time, part-time, contract, remote, hybrid, etc.)
            - Salary range (if mentioned)
            - Job description/overview
            - Key responsibilities (as a list)
            - Requirements (categorize as required, preferred, or nice-to-have with importance weights)
            - Preferred qualifications
            - Company culture information
            - Benefits (if mentioned)
            
            For requirements, assign importance weights:
            - Required skills: 1.0
            - Preferred skills: 0.7
            - Nice-to-have skills: 0.3
            
            Return ONLY a valid JSON object that matches the JobDescription schema structure.
            """

            user_message = f"Analyze this job description and extract structured information:\n\n{job_description_raw}"

            messages = self.create_prompt(system_message, user_message)
            response = self.llm.invoke(messages)

            # Parse the JSON response
            job_data = json.loads(response.content)

            # Convert to Pydantic model
            job_description = self._parse_job_data(job_data)

            state["job_description"] = job_description
            state["step_completed"] = state.get("step_completed", []) + ["job_analysis"]

        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Job analysis error: {str(e)}"]

        return state

    def _parse_job_data(self, data: dict[str, Any]) -> JobDescription:
        # Parse requirements
        requirements_list = []
        for req_data in data.get("requirements", []):
            requirement = JobRequirement(
                category=req_data.get("category", "required"),
                skill_or_requirement=req_data.get("skill_or_requirement", ""),
                importance_weight=req_data.get("importance_weight", 1.0),
            )
            requirements_list.append(requirement)

        return JobDescription(
            title=data.get("title", ""),
            company=data.get("company", ""),
            location=data.get("location"),
            job_type=data.get("job_type"),
            salary_range=data.get("salary_range"),
            description=data.get("description", ""),
            responsibilities=data.get("responsibilities", []),
            requirements=requirements_list,
            preferred_qualifications=data.get("preferred_qualifications", []),
            company_culture=data.get("company_culture"),
            benefits=data.get("benefits", []),
        )

    def process(self, state: dict[str, Any]) -> dict[str, Any]:
        return self.analyze_job(state)  # type: ignore
