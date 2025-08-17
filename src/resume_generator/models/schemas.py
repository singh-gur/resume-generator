from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    email: str
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    location: Optional[str] = None


class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_date: Optional[date] = None
    gpa: Optional[float] = None
    relevant_coursework: List[str] = Field(default_factory=list)


class Experience(BaseModel):
    company: str
    position: str
    start_date: date
    end_date: Optional[date] = None
    description: str
    key_achievements: List[str] = Field(default_factory=list)
    technologies_used: List[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str
    description: str
    technologies_used: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class Certification(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_url: Optional[str] = None


class UserProfile(BaseModel):
    full_name: str
    contact_info: ContactInfo
    professional_summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class JobRequirement(BaseModel):
    category: str  # e.g., "required", "preferred", "nice-to-have"
    skill_or_requirement: str
    importance_weight: float = Field(default=1.0, ge=0.0, le=1.0)


class JobDescription(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, contract, etc.
    salary_range: Optional[str] = None
    description: str
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[JobRequirement] = Field(default_factory=list)
    preferred_qualifications: List[str] = Field(default_factory=list)
    company_culture: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)


class SkillMatch(BaseModel):
    skill: str
    user_has_skill: bool
    proficiency_level: Optional[str] = None  # beginner, intermediate, advanced
    match_score: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(
        default_factory=list
    )  # where this skill is demonstrated


class ResumeSection(BaseModel):
    section_name: str
    content: str
    priority: int = Field(default=1)


class GeneratedResume(BaseModel):
    user_profile: UserProfile
    job_description: JobDescription
    skill_matches: List[SkillMatch]
    customized_summary: str
    sections: List[ResumeSection]
    tailoring_notes: List[str] = Field(default_factory=list)
    match_percentage: float = Field(ge=0.0, le=100.0)
