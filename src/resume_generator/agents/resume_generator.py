from typing import Any

from resume_generator.agents.base import BaseAgent
from resume_generator.models.schemas import (
    GeneratedResume,
    JobDescription,
    ResumeSection,
    SkillMatch,
    UserProfile,
)
from resume_generator.workflows.state import WorkflowState


class ResumeGeneratorAgent(BaseAgent):
    def generate_resume(self, state: WorkflowState) -> WorkflowState:
        try:
            user_profile = state.get("user_profile")
            job_description = state.get("job_description")
            skill_matches = state.get("skill_matches")

            if not all([user_profile, job_description, skill_matches]):
                state["errors"] = state.get("errors", []) + ["Missing required data for resume generation"]
                return state

            generated_resume = self._create_tailored_resume(
                user_profile,  # type: ignore
                job_description,  # type: ignore
                skill_matches,  # type: ignore
            )

            state["generated_resume"] = generated_resume
            state["step_completed"] = state.get("step_completed", []) + ["resume_generation"]

        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Resume generation error: {str(e)}"]

        return state

    def _create_tailored_resume(
        self,
        user_profile: UserProfile,
        job_description: JobDescription,
        skill_matches: list[SkillMatch],
    ) -> GeneratedResume:
        # Generate customized professional summary
        customized_summary = self._generate_custom_summary(user_profile, job_description, skill_matches)

        # Generate resume sections
        sections = self._generate_resume_sections(user_profile, job_description, skill_matches)

        # Calculate match percentage
        match_percentage = self._calculate_match_percentage(skill_matches)

        # Generate tailoring notes
        tailoring_notes = self._generate_tailoring_notes(skill_matches, job_description)

        return GeneratedResume(
            user_profile=user_profile,
            job_description=job_description,
            skill_matches=skill_matches,
            customized_summary=customized_summary,
            sections=sections,
            tailoring_notes=tailoring_notes,
            match_percentage=match_percentage,
        )

    def _generate_custom_summary(
        self,
        user_profile: UserProfile,
        job_description: JobDescription,
        skill_matches: list[SkillMatch],
    ) -> str:
        system_message = """
        You are an expert resume writer. Create a compelling, tailored professional summary that:
        1. Highlights the candidate's most relevant skills and experience for this specific job
        2. Uses keywords from the job description naturally
        3. Emphasizes achievements and value proposition
        4. Is concise (3-4 sentences)
        5. Matches the tone and industry expectations
        
        Focus on the skills and experiences that best match the job requirements.
        """

        # Get top matching skills
        top_skills = [match.skill for match in skill_matches if match.user_has_skill and match.match_score > 0.7][:5]

        user_message = f"""
        Job Title: {job_description.title}
        Company: {job_description.company}
        
        User's Background:
        - Current Summary: {user_profile.professional_summary or "No existing summary"}
        - Top Relevant Skills: {", ".join(top_skills)}
        - Years of Experience: {len(user_profile.experience)} positions
        - Education: {user_profile.education[0].degree if user_profile.education else "Not specified"}
        
        Job Requirements Summary:
        {job_description.description[:500]}...
        
        Create a tailored professional summary.
        """

        messages = self.create_prompt(system_message, user_message)
        response = self.llm.invoke(messages)

        return response.content.strip()

    def _generate_resume_sections(
        self,
        user_profile: UserProfile,
        job_description: JobDescription,
        skill_matches: list[SkillMatch],
    ) -> list[ResumeSection]:
        sections = []

        # Contact Information
        contact_section = self._create_contact_section(user_profile)
        sections.append(contact_section)

        # Professional Summary (already generated)

        # Skills Section (tailored)
        skills_section = self._create_skills_section(user_profile, skill_matches)
        sections.append(skills_section)

        # Experience Section (prioritized and tailored)
        experience_section = self._create_experience_section(user_profile, job_description, skill_matches)
        sections.append(experience_section)

        # Education Section
        education_section = self._create_education_section(user_profile)
        sections.append(education_section)

        # Projects Section (if relevant)
        if user_profile.projects:
            projects_section = self._create_projects_section(user_profile, skill_matches)
            sections.append(projects_section)

        # Certifications Section (if any)
        if user_profile.certifications:
            certifications_section = self._create_certifications_section(user_profile)
            sections.append(certifications_section)

        return sections

    def _create_contact_section(self, user_profile: UserProfile) -> ResumeSection:
        contact_info = []
        contact_info.append(user_profile.full_name)
        contact_info.append(user_profile.contact_info.email)

        if user_profile.contact_info.phone:
            contact_info.append(user_profile.contact_info.phone)
        if user_profile.contact_info.linkedin:
            contact_info.append(f"LinkedIn: {user_profile.contact_info.linkedin}")
        if user_profile.contact_info.github:
            contact_info.append(f"GitHub: {user_profile.contact_info.github}")
        if user_profile.contact_info.location:
            contact_info.append(user_profile.contact_info.location)

        return ResumeSection(
            section_name="Contact Information",
            content="\n".join(contact_info),
            priority=1,
        )

    def _create_skills_section(self, user_profile: UserProfile, skill_matches: list[SkillMatch]) -> ResumeSection:
        # Prioritize skills based on job relevance
        matched_skills = [match.skill for match in skill_matches if match.user_has_skill and match.match_score > 0.5]
        user_skills = user_profile.skills

        # Combine and prioritize
        prioritized_skills = []
        for skill in matched_skills:
            if any(skill.lower() in user_skill.lower() or user_skill.lower() in skill.lower() for user_skill in user_skills):
                prioritized_skills.append(skill)

        # Add remaining user skills
        for skill in user_skills:
            if not any(skill.lower() in ps.lower() for ps in prioritized_skills):
                prioritized_skills.append(skill)

        return ResumeSection(
            section_name="Technical Skills",
            content=", ".join(prioritized_skills[:15]),  # Limit to top 15 skills
            priority=2,
        )

    def _create_experience_section(
        self,
        user_profile: UserProfile,
        job_description: JobDescription,
        skill_matches: list[SkillMatch],
    ) -> ResumeSection:
        experience_content = []

        for exp in user_profile.experience:
            exp_content = []
            exp_content.append(f"{exp.position} | {exp.company}")

            # Add dates
            start_date = exp.start_date.strftime("%Y-%m") if exp.start_date else "Unknown"
            end_date = exp.end_date.strftime("%Y-%m") if exp.end_date else "Present"
            exp_content.append(f"{start_date} - {end_date}")

            # Add description
            exp_content.append(f"• {exp.description}")

            # Add key achievements
            for achievement in exp.key_achievements:
                exp_content.append(f"• {achievement}")

            # Add technologies if relevant
            if exp.technologies_used:
                relevant_techs = [
                    tech
                    for tech in exp.technologies_used
                    if any(match.skill.lower() in tech.lower() for match in skill_matches if match.user_has_skill)
                ]
                if relevant_techs:
                    exp_content.append(f"Technologies: {', '.join(relevant_techs)}")

            experience_content.append("\n".join(exp_content))

        return ResumeSection(
            section_name="Professional Experience",
            content="\n\n".join(experience_content),
            priority=3,
        )

    def _create_education_section(self, user_profile: UserProfile) -> ResumeSection:
        education_content = []

        for edu in user_profile.education:
            edu_content = []
            edu_content.append(f"{edu.degree}")
            if edu.field_of_study:
                edu_content.append(f"in {edu.field_of_study}")
            edu_content.append(f"| {edu.institution}")

            if edu.graduation_date:
                edu_content.append(f"| {edu.graduation_date.year}")

            if edu.gpa and edu.gpa >= 3.5:
                edu_content.append(f"| GPA: {edu.gpa}")

            education_content.append(" ".join(edu_content))

            if edu.relevant_coursework:
                education_content.append(f"Relevant Coursework: {', '.join(edu.relevant_coursework[:5])}")

        return ResumeSection(section_name="Education", content="\n\n".join(education_content), priority=4)

    def _create_projects_section(self, user_profile: UserProfile, skill_matches: list[SkillMatch]) -> ResumeSection:
        # Select most relevant projects
        relevant_projects = []
        matched_skills = [match.skill.lower() for match in skill_matches if match.user_has_skill]

        for project in user_profile.projects:
            relevance_score = sum(1 for tech in project.technologies_used if any(skill in tech.lower() for skill in matched_skills))
            relevant_projects.append((project, relevance_score))

        # Sort by relevance and take top 3
        relevant_projects.sort(key=lambda x: x[1], reverse=True)
        top_projects = [proj[0] for proj in relevant_projects[:3]]

        projects_content = []
        for project in top_projects:
            proj_content = []
            proj_content.append(f"{project.name}")
            if project.url:
                proj_content.append(f"({project.url})")
            proj_content.append(f"• {project.description}")

            if project.technologies_used:
                proj_content.append(f"Technologies: {', '.join(project.technologies_used)}")

            for achievement in project.achievements:
                proj_content.append(f"• {achievement}")

            projects_content.append("\n".join(proj_content))

        return ResumeSection(
            section_name="Key Projects",
            content="\n\n".join(projects_content),
            priority=5,
        )

    def _create_certifications_section(self, user_profile: UserProfile) -> ResumeSection:
        certifications_content = []

        for cert in user_profile.certifications:
            cert_content = f"{cert.name} | {cert.issuer}"
            if cert.issue_date:
                cert_content += f" | {cert.issue_date.year}"
            certifications_content.append(cert_content)

        return ResumeSection(
            section_name="Certifications",
            content="\n".join(certifications_content),
            priority=6,
        )

    def _calculate_match_percentage(self, skill_matches: list[SkillMatch]) -> float:
        if not skill_matches:
            return 0.0

        total_score = sum(match.match_score for match in skill_matches if match.user_has_skill)
        max_possible_score = len(skill_matches)

        return (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0.0

    def _generate_tailoring_notes(self, skill_matches: list[SkillMatch], job_description: JobDescription) -> list[str]:
        notes = []

        # Missing critical skills
        missing_skills = [
            match.skill
            for match in skill_matches
            if not match.user_has_skill
            and any(
                req.skill_or_requirement.lower() in match.skill.lower()
                for req in job_description.requirements
                if req.importance_weight >= 0.8
            )
        ]

        if missing_skills:
            notes.append(f"Consider developing skills in: {', '.join(missing_skills[:3])}")

        # Strong matches to highlight
        strong_matches = [match.skill for match in skill_matches if match.user_has_skill and match.match_score >= 0.8]

        if strong_matches:
            notes.append(f"Emphasize these strong skill matches: {', '.join(strong_matches[:3])}")

        # Industry keywords to include
        if job_description.responsibilities:
            notes.append("Include keywords from job responsibilities in your descriptions")

        return notes

    def process(self, state: dict[str, Any]) -> dict[str, Any]:
        return self.generate_resume(state)  # type: ignore
