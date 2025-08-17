import json
from typing import Any

from langchain.schema import BaseMessage

from resume_generator.agents.base import BaseAgent
from resume_generator.models.schemas import JobListing, SkillMatch, UserProfile
from resume_generator.workflows.state import WorkflowState


class SkillsMatcherAgent(BaseAgent):
    def match_skills(self, state: WorkflowState) -> WorkflowState:
        try:
            user_profile = state.get("user_profile")
            job_matches = state.get("job_matches")

            if not user_profile or not job_matches:
                state["errors"] = state.get("errors", []) + ["Missing user profile or job matches for skills matching"]
                return state

            # Generate skill matches for each job listing
            job_skill_matches = []
            for job_listing in job_matches.jobs:
                skill_matches = self._analyze_skill_matches_for_job(user_profile, job_listing)
                job_skill_matches.append({"job_listing": job_listing, "skill_matches": skill_matches})

            state["job_skill_matches"] = job_skill_matches
            state["step_completed"] = state.get("step_completed", []) + ["skills_matching"]

        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Skills matching error: {str(e)}"]

        return state

    def _analyze_skill_matches_for_job(self, user_profile: UserProfile, job_listing: JobListing) -> list[SkillMatch]:
        system_message = """
        You are an expert at matching candidate skills with job listings.
        Your task is to analyze the user's profile against a job listing and determine skill matches.
        
        Based on the job title, company, and description, infer the key skills and requirements needed.
        For each inferred skill/requirement, determine:
        1. Whether the user has this skill (based on their profile)
        2. The proficiency level (beginner, intermediate, advanced) if they have it
        3. A match score from 0.0 to 1.0
        4. Evidence from their profile that demonstrates this skill
        
        Consider:
        - Direct skill mentions in user profile
        - Technology experience from work/projects
        - Education background
        - Certifications
        - Project descriptions that imply skill usage
        - Job title and description keywords
        
        Focus on the most important 8-10 skills/requirements for this specific job.
        Return a JSON array of skill matches.
        """

        user_data = {
            "skills": user_profile.skills,
            "experience": [
                {
                    "company": exp.company,
                    "position": exp.position,
                    "description": exp.description,
                    "technologies_used": exp.technologies_used,
                    "key_achievements": exp.key_achievements,
                }
                for exp in user_profile.experience
            ],
            "projects": [
                {
                    "name": proj.name,
                    "description": proj.description,
                    "technologies_used": proj.technologies_used,
                }
                for proj in user_profile.projects
            ],
            "education": [
                {
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                    "relevant_coursework": edu.relevant_coursework,
                }
                for edu in user_profile.education
            ],
            "certifications": [{"name": cert.name, "issuer": cert.issuer} for cert in user_profile.certifications],
        }

        job_data = {
            "title": job_listing.title,
            "company": job_listing.company,
            "location": job_listing.location,
            "description": job_listing.description,
            "job_type": job_listing.job_type,
            "is_remote": job_listing.is_remote,
        }

        user_message = f"""
        User Profile Data:
        {json.dumps(user_data, indent=2)}
        
        Job Listing:
        {json.dumps(job_data, indent=2)}
        
        Analyze the job listing and determine the key skills/requirements needed, then match against the user profile.
        """

        messages = self.create_prompt(system_message, user_message)
        response = self.llm.invoke(messages)

        # Parse the JSON response
        response_content = response.content if isinstance(response, BaseMessage) else str(response)
        matches_data = json.loads(response_content)  # type: ignore

        # Convert to SkillMatch objects
        skill_matches = []
        for match_data in matches_data:
            skill_match = SkillMatch(
                skill=match_data.get("skill", ""),
                user_has_skill=match_data.get("user_has_skill", False),
                proficiency_level=match_data.get("proficiency_level"),
                match_score=match_data.get("match_score", 0.0),
                evidence=match_data.get("evidence", []),
            )
            skill_matches.append(skill_match)

        return skill_matches

    def process(self, state: dict[str, Any]) -> dict[str, Any]:
        # Convert dict to WorkflowState for the typed method
        workflow_state: WorkflowState = state  # type: ignore
        result = self.match_skills(workflow_state)
        return dict(result)
