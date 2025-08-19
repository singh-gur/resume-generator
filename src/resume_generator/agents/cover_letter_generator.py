from typing import Any

from langchain.schema import BaseMessage

from resume_generator.agents.base import BaseAgent
from resume_generator.models.schemas import (
    GeneratedCoverLetter,
    JobDescription,
    JobListing,
    SkillMatch,
    UserProfile,
)
from resume_generator.workflows.state import WorkflowState


class CoverLetterGeneratorAgent(BaseAgent):
    def generate_cover_letter(self, state: WorkflowState) -> WorkflowState:
        try:
            user_profile = state.get("user_profile")
            job_skill_matches = state.get("job_skill_matches")
            match_threshold = state.get("match_threshold") or 0.0

            if not user_profile or not job_skill_matches:
                state["errors"] = state.get("errors", []) + ["Missing required data for cover letter generation"]
                return state

            # Generate a cover letter for each job listing
            all_generated_cover_letters = []
            for job_match in job_skill_matches:
                job_listing = job_match["job_listing"]
                skill_matches = job_match["skill_matches"]

                generated_cover_letter = self._create_tailored_cover_letter(
                    user_profile,  # type: ignore
                    job_listing,  # type: ignore
                    skill_matches,  # type: ignore
                )
                all_generated_cover_letters.append(generated_cover_letter)

            # Filter based on match threshold
            filtered_cover_letters = [cl for cl in all_generated_cover_letters if cl.match_percentage >= match_threshold]

            # Note: Filtering results are logged in CLI, not in agent output

            state["generated_cover_letters"] = filtered_cover_letters
            state["step_completed"] = state.get("step_completed", []) + ["cover_letter_generation"]

        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Cover letter generation error: {str(e)}"]

        return state

    def _create_tailored_cover_letter(
        self,
        user_profile: UserProfile,
        job_listing: JobListing,
        skill_matches: list[SkillMatch],
    ) -> GeneratedCoverLetter:
        # Generate customized cover letter content
        cover_letter_content = self._generate_cover_letter_content(user_profile, job_listing, skill_matches)

        # Calculate match percentage
        match_percentage = self._calculate_match_percentage(skill_matches)

        # Generate tailoring notes
        tailoring_notes = self._generate_tailoring_notes(skill_matches, job_listing)

        # Create a JobDescription equivalent from JobListing for compatibility
        job_description_equivalent = self._create_job_description_from_listing(job_listing)

        return GeneratedCoverLetter(
            user_profile=user_profile,
            job_description=job_description_equivalent,
            skill_matches=skill_matches,
            cover_letter_content=cover_letter_content,
            tailoring_notes=tailoring_notes,
            match_percentage=match_percentage,
        )

    def _create_job_description_from_listing(self, job_listing: JobListing) -> JobDescription:
        """Convert JobListing to JobDescription for compatibility with existing schema."""
        requirements = []

        return JobDescription(
            title=job_listing.title,
            company=job_listing.company,
            location=job_listing.location,
            job_type=job_listing.job_type,
            salary_range=job_listing.salary,
            description=job_listing.description or "",
            responsibilities=[],
            requirements=requirements,
            preferred_qualifications=[],
            company_culture=None,
            benefits=[],
        )

    def _generate_cover_letter_content(
        self,
        user_profile: UserProfile,
        job_listing: JobListing,
        skill_matches: list[SkillMatch],
    ) -> str:
        system_message = """
        You are an expert cover letter writer. Create compelling body paragraphs for a professional cover letter that:
        1. Opens with a strong hook that shows genuine interest in the role and company
        2. Clearly connects the candidate's experience and skills to the job requirements
        3. Tells a story that demonstrates value and impact
        4. Shows knowledge of the company and role
        5. Uses specific examples and quantifiable achievements when possible
        6. Maintains a professional yet engaging tone throughout
        7. Ends with a strong call to action
        8. Is 3-4 paragraphs of body content only
        
        IMPORTANT FORMATTING REQUIREMENTS:
        - Generate ONLY the main body paragraphs of the cover letter
        - Do NOT include date, recipient information, salutation (Dear...), or signature
        - Do NOT include placeholder text like [Date], [Name], or [Address]
        - Do NOT include any debug information, analysis notes, or meta-commentary
        - Do NOT start with "Dear" or any greeting - jump straight into the first paragraph
        - Do NOT include any header lines or contact information
        - The output should be just the paragraph content, ready to be inserted into a business letter template
        - Separate paragraphs with double line breaks
        
        Content Structure:
        - Opening paragraph: Express interest and briefly introduce yourself
        - Middle paragraph(s): Highlight relevant experience and achievements that match job requirements
        - Closing paragraph: Reiterate interest and request for interview
        
        Focus on the skills and experiences that best match the job requirements and show concrete value.
        """

        # Get top matching skills for emphasis
        top_skills = [match.skill for match in skill_matches if match.user_has_skill and match.match_score > 0.7][:5]

        # Get most relevant experience
        most_recent_experience = user_profile.experience[0] if user_profile.experience else None

        user_message = f"""
        Write the body paragraphs for a cover letter for the following job application.
        
        Job Information:
        - Job Title: {job_listing.title}
        - Company: {job_listing.company}
        - Location: {job_listing.location or "Not specified"}
        
        Candidate Information:
        - Name: {user_profile.full_name}
        - Email: {user_profile.contact_info.email}
        - Current/Recent Position: {most_recent_experience.position if most_recent_experience else "Not specified"}
        - Professional Summary: {user_profile.professional_summary or "No existing summary"}
        - Top Relevant Skills: {", ".join(top_skills) if top_skills else "Skills available in profile"}
        - Years of Experience: {len(user_profile.experience)} positions
        
        Job Description/Requirements:
        {job_listing.description[:800] if job_listing.description else "No detailed description available"}
        
        Most Relevant Experience:
        {most_recent_experience.description if most_recent_experience else "No recent experience listed"}
        
        Key Achievements:
        {
            "; ".join(most_recent_experience.key_achievements[:3])
            if most_recent_experience and most_recent_experience.key_achievements
            else "No specific achievements listed"
        }
        
        Create personalized, compelling body paragraphs that demonstrate why this candidate is perfect for this role.
        Generate only the main content paragraphs - no date, salutation, or signature.
        """

        messages = self.create_prompt(system_message, user_message)
        response = self.llm.invoke(messages)

        response_content = response.content if isinstance(response, BaseMessage) else str(response)
        return response_content  # type: ignore

    def _calculate_match_percentage(self, skill_matches: list[SkillMatch]) -> float:
        if not skill_matches:
            return 0.0

        total_score = sum(match.match_score for match in skill_matches if match.user_has_skill)
        max_possible_score = len(skill_matches)

        return (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0.0

    def _generate_tailoring_notes(self, skill_matches: list[SkillMatch], job_listing: JobListing) -> list[str]:
        notes = []

        # Missing critical skills
        missing_skills = [match.skill for match in skill_matches if not match.user_has_skill and match.match_score < 0.3]

        if missing_skills:
            notes.append(f"Consider highlighting transferable skills or learning interest in: {', '.join(missing_skills[:3])}")

        # Strong matches to emphasize
        strong_matches = [match.skill for match in skill_matches if match.user_has_skill and match.match_score >= 0.8]

        if strong_matches:
            notes.append(f"Emphasize these strong skill matches in your cover letter: {', '.join(strong_matches[:3])}")

        # Company research suggestion
        notes.append(f"Research {job_listing.company}'s recent news, values, and culture to personalize your letter")

        # Follow-up suggestion
        notes.append("Consider following up within 1-2 weeks if you don't hear back")

        return notes

    def process(self, state: dict[str, Any]) -> dict[str, Any]:
        # Convert dict to WorkflowState for the typed method
        workflow_state: WorkflowState = state  # type: ignore
        result = self.generate_cover_letter(workflow_state)
        return dict(result)
