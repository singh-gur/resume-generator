from typing import TypedDict

from resume_generator.models.schemas import (
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
    skill_matches: list[SkillMatch] | None
    generated_resume: GeneratedResume | None
    errors: list[str]
    step_completed: list[str]
    job_search_location: str | None
    job_sites: list[str] | None
    max_results: int | None
    hours_old: int | None
