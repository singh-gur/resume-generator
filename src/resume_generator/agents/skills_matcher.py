import json
from typing import List
from resume_generator.agents.base import BaseAgent
from resume_generator.models.schemas import SkillMatch, UserProfile, JobDescription
from resume_generator.workflows.state import WorkflowState


class SkillsMatcherAgent(BaseAgent):
    def match_skills(self, state: WorkflowState) -> WorkflowState:
        try:
            user_profile = state.get("user_profile")
            job_description = state.get("job_description")

            if not user_profile or not job_description:
                state["errors"] = state.get("errors", []) + [
                    "Missing user profile or job description for skills matching"
                ]
                return state

            skill_matches = self._analyze_skill_matches(user_profile, job_description)

            state["skill_matches"] = skill_matches
            state["step_completed"] = state.get("step_completed", []) + [
                "skills_matching"
            ]

        except Exception as e:
            state["errors"] = state.get("errors", []) + [
                f"Skills matching error: {str(e)}"
            ]

        return state

    def _analyze_skill_matches(
        self, user_profile: UserProfile, job_description: JobDescription
    ) -> List[SkillMatch]:
        system_message = """
        You are an expert at matching candidate skills with job requirements.
        Your task is to analyze the user's profile against the job requirements and determine skill matches.
        
        For each requirement in the job description, determine:
        1. Whether the user has this skill (based on their profile)
        2. The proficiency level (beginner, intermediate, advanced) if they have it
        3. A match score from 0.0 to 1.0
        4. Evidence from their profile that demonstrates this skill
        
        Consider:
        - Direct skill mentions
        - Technology experience from work/projects
        - Education background
        - Certifications
        - Project descriptions that imply skill usage
        
        Return a JSON array of skill matches, one for each job requirement.
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
            "certifications": [
                {"name": cert.name, "issuer": cert.issuer}
                for cert in user_profile.certifications
            ],
        }

        job_requirements = [
            {
                "category": req.category,
                "skill_or_requirement": req.skill_or_requirement,
                "importance_weight": req.importance_weight,
            }
            for req in job_description.requirements
        ]

        user_message = f"""
        User Profile Data:
        {json.dumps(user_data, indent=2)}
        
        Job Requirements:
        {json.dumps(job_requirements, indent=2)}
        
        Analyze and return skill matches.
        """

        messages = self.create_prompt(system_message, user_message)
        response = self.llm.invoke(messages)

        # Parse the JSON response
        matches_data = json.loads(response.content)

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
