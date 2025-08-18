from datetime import date

from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    email: str
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    location: str | None = None


class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str | None = None
    graduation_date: date | None = None
    gpa: float | None = None
    relevant_coursework: list[str] = Field(default_factory=list)


class Experience(BaseModel):
    company: str
    position: str
    start_date: date | None = None
    end_date: date | None = None
    description: str
    key_achievements: list[str] = Field(default_factory=list)
    technologies_used: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str
    description: str
    technologies_used: list[str] = Field(default_factory=list)
    url: str | None = None
    achievements: list[str] = Field(default_factory=list)


class Certification(BaseModel):
    name: str
    issuer: str
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_url: str | None = None


class UserProfile(BaseModel):
    full_name: str
    contact_info: ContactInfo
    professional_summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


class JobRequirement(BaseModel):
    category: str  # e.g., "required", "preferred", "nice-to-have"
    skill_or_requirement: str
    importance_weight: float = Field(default=1.0, ge=0.0, le=1.0)


class JobDescription(BaseModel):
    title: str
    company: str
    location: str | None = None
    job_type: str | None = None  # full-time, part-time, contract, etc.
    salary_range: str | None = None
    description: str
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[JobRequirement] = Field(default_factory=list)
    preferred_qualifications: list[str] = Field(default_factory=list)
    company_culture: str | None = None
    benefits: list[str] = Field(default_factory=list)


class SkillMatch(BaseModel):
    skill: str
    user_has_skill: bool
    proficiency_level: str | None = None  # beginner, intermediate, advanced
    match_score: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)  # where this skill is demonstrated


class ResumeSection(BaseModel):
    section_name: str
    content: str
    priority: int = Field(default=1)


class JobListing(BaseModel):
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    job_url: str | None = None
    date_posted: str | None = None
    job_type: str | None = None
    salary: str | None = None
    is_remote: bool = False


class JobMatches(BaseModel):
    search_location: str
    search_keywords: list[str] = Field(default_factory=list)
    is_remote_search: bool = False
    jobs: list[JobListing] = Field(default_factory=list)
    total_results: int = 0


class GeneratedResume(BaseModel):
    user_profile: UserProfile
    job_description: JobDescription
    skill_matches: list[SkillMatch]
    customized_summary: str
    sections: list[ResumeSection]
    tailoring_notes: list[str] = Field(default_factory=list)
    match_percentage: float = Field(ge=0.0, le=100.0)


class GeneratedCoverLetter(BaseModel):
    user_profile: UserProfile
    job_description: JobDescription
    skill_matches: list[SkillMatch]
    cover_letter_content: str
    tailoring_notes: list[str] = Field(default_factory=list)
    match_percentage: float = Field(ge=0.0, le=100.0)
