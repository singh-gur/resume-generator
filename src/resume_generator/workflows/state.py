from typing import TypedDict

from resume_generator.models.schemas import (
    GeneratedCoverLetter,
    GeneratedResume,
    JobDescription,
    JobMatches,
    SkillMatch,
    UserProfile,
)


class WorkflowState(TypedDict):
    user_profile_raw: str | None
    user_profile_json: str | None
    job_description_raw: str | None
    user_profile: UserProfile | None
    job_description: JobDescription | None
    job_matches: JobMatches | None
    job_skill_matches: list[dict] | None  # List of {job_listing, skill_matches} dicts
    skill_matches: list[SkillMatch] | None  # Kept for backwards compatibility
    generated_resume: GeneratedResume | None  # Kept for backwards compatibility
    generated_resumes: list[GeneratedResume] | None  # New field for multiple resumes
    generated_cover_letter: GeneratedCoverLetter | None  # Single cover letter for backwards compatibility
    generated_cover_letters: list[GeneratedCoverLetter] | None  # New field for multiple cover letters
    errors: list[str]
    step_completed: list[str]
    job_search_location: str | None
    job_sites: list[str] | None
    max_results: int | None
    hours_old: int | None
    search_term: str | None
    match_threshold: float | None
