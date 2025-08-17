from typing import List, Optional, TypedDict
from resume_generator.models.schemas import (
    UserProfile,
    JobDescription,
    SkillMatch,
    GeneratedResume,
    JobMatches,
)


class WorkflowState(TypedDict):
    user_profile_raw: Optional[str]
    job_description_raw: Optional[str]
    user_profile: Optional[UserProfile]
    job_description: Optional[JobDescription]
    job_matches: Optional[JobMatches]
    skill_matches: Optional[List[SkillMatch]]
    generated_resume: Optional[GeneratedResume]
    errors: List[str]
    step_completed: List[str]
