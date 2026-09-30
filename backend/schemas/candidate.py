from typing import List, Optional
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    """Education record item."""
    degree: str = Field(description="Degree name e.g. B.Tech in Computer Science")
    institution: str = Field(description="University or institution name")
    field_of_study: Optional[str] = Field(default=None, description="Major or area of study")
    start_year: Optional[str] = Field(default=None, description="Start year or date")
    end_year: Optional[str] = Field(default=None, description="Graduation year or Expected")
    grade: Optional[str] = Field(default=None, description="GPA or percentage if specified")


class WorkExperienceItem(BaseModel):
    """Work experience / internship record item."""
    job_title: str = Field(description="Role title e.g. Software Engineer Intern")
    company: str = Field(description="Company or organization name")
    duration: Optional[str] = Field(default=None, description="Duration e.g. Jun 2023 - Present")
    location: Optional[str] = Field(default=None, description="City or Remote")
    responsibilities: List[str] = Field(default_factory=list, description="Key work responsibilities")
    key_achievements: List[str] = Field(default_factory=list, description="Quantifiable accomplishments")


class ProjectItem(BaseModel):
    """Project record item."""
    title: str = Field(description="Project title")
    description: str = Field(description="Brief project overview and goal")
    technologies_used: List[str] = Field(default_factory=list, description="Technologies/tools utilized")
    link: Optional[str] = Field(default=None, description="GitHub repository or live link if available")


class CertificationItem(BaseModel):
    """Professional certification item."""
    name: str = Field(description="Certification title")
    issuing_organization: Optional[str] = Field(default=None, description="Issuer e.g. AWS, Coursera, DeepLearning.AI")
    year: Optional[str] = Field(default=None, description="Year earned")


class CategorizedSkills(BaseModel):
    """Structured breakdown of candidate technical and soft skills."""
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages e.g. Python, SQL, C++")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks e.g. FastAPI, React, PyTorch, LangChain")
    databases: List[str] = Field(default_factory=list, description="Databases e.g. PostgreSQL, SQLite, MongoDB")
    cloud_tools: List[str] = Field(default_factory=list, description="Cloud/DevOps tools e.g. AWS, Docker, Git")
    ai_ml_skills: List[str] = Field(default_factory=list, description="AI/ML topics e.g. Scikit-Learn, Computer Vision, NLP")
    genai_skills: List[str] = Field(default_factory=list, description="GenAI skills e.g. RAG, Vector Databases, Prompt Engineering")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills e.g. Problem Solving, Team Collaboration")
    other_skills: List[str] = Field(default_factory=list, description="Any unclassified technical skills")

    def all_skills_list(self) -> List[str]:
        """Returns flat list of all skills across categories."""
        combined = (
            self.programming_languages
            + self.frameworks
            + self.databases
            + self.cloud_tools
            + self.ai_ml_skills
            + self.genai_skills
            + self.soft_skills
            + self.other_skills
        )
        return list(dict.fromkeys(combined))  # Deduplicated order-preserved list


class CandidateProfileSchema(BaseModel):
    """Complete candidate profile structured schema."""
    name: Optional[str] = Field(default="Candidate", description="Full candidate name")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    professional_summary: str = Field(description="Concise 2-3 sentence executive professional summary")
    years_of_experience: float = Field(default=0.0, description="Total estimated years of experience")
    education: List[EducationItem] = Field(default_factory=list)
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    skills: CategorizedSkills = Field(default_factory=CategorizedSkills)
    notable_strengths: List[str] = Field(default_factory=list, description="Key candidate strengths identified from resume")
    missing_information: List[str] = Field(default_factory=list, description="Information gaps in the resume e.g. missing dates or links")


class CandidateUploadResponse(BaseModel):
    """API response model for POST /resume/upload."""
    resume_id: int
    candidate_id: int
    filename: str
    file_type: str
    profile: CandidateProfileSchema
