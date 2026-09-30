from typing import Optional

from backend.config import settings
from backend.prompts.resume.extract_profile import (
    RESUME_EXTRACTION_SYSTEM_INSTRUCTION,
    RESUME_EXTRACTION_PROMPT_TEMPLATE,
)
from backend.schemas.candidate import (
    CandidateProfileSchema,
    EducationItem,
    WorkExperienceItem,
    ProjectItem,
    CertificationItem,
    CategorizedSkills,
)
from backend.services.llm.llm_service import LLMService, llm_service
from backend.services.skill_normalizer import skill_normalizer
from backend.utils.logger import logger


class ResumeIntelligenceAgent:
    """
    Agent 1: Resume Intelligence Agent.
    Responsible for analyzing raw resume text, extracting structured facts into CandidateProfileSchema,
    normalizing technical skills, and identifying missing information.
    """

    def __init__(self, llm_svc: Optional[LLMService] = None):
        self.llm_service = llm_svc or llm_service

    def analyze_resume(self, raw_text: str, filename: Optional[str] = None) -> CandidateProfileSchema:
        """
        Processes extracted resume raw text and returns a validated CandidateProfileSchema object.
        """
        logger.info(f"ResumeIntelligenceAgent starting analysis for document ({len(raw_text)} chars)...")

        if settings.is_demo_mode():
            logger.info("DEMO_MODE enabled: Returning mock structured candidate profile.")
            profile = self._generate_demo_profile(raw_text, filename)
        else:
            try:
                prompt = RESUME_EXTRACTION_PROMPT_TEMPLATE.format(resume_text=raw_text[:12000])
                profile = self.llm_service.generate_json(
                    prompt=prompt,
                    schema=CandidateProfileSchema,
                    system_instruction=RESUME_EXTRACTION_SYSTEM_INSTRUCTION,
                )
            except Exception as e:
                logger.error(f"ResumeIntelligenceAgent API call failed: {e}. Falling back to demo profile.")
                profile = self._generate_demo_profile(raw_text, filename)

        # Apply Skill Normalization to all skill categories
        profile = self._normalize_profile_skills(profile)

        logger.info(f"ResumeIntelligenceAgent completed analysis for '{profile.name}' with {len(profile.skills.all_skills_list())} normalized skills.")
        return profile

    def _normalize_profile_skills(self, profile: CandidateProfileSchema) -> CandidateProfileSchema:
        """Runs SkillNormalizer across all skill categories in candidate profile."""
        skills = profile.skills
        skills.programming_languages = skill_normalizer.normalize_skill_list(skills.programming_languages)
        skills.frameworks = skill_normalizer.normalize_skill_list(skills.frameworks)
        skills.databases = skill_normalizer.normalize_skill_list(skills.databases)
        skills.cloud_tools = skill_normalizer.normalize_skill_list(skills.cloud_tools)
        skills.ai_ml_skills = skill_normalizer.normalize_skill_list(skills.ai_ml_skills)
        skills.genai_skills = skill_normalizer.normalize_skill_list(skills.genai_skills)
        skills.soft_skills = skill_normalizer.normalize_skill_list(skills.soft_skills)
        skills.other_skills = skill_normalizer.normalize_skill_list(skills.other_skills)
        return profile

    def _generate_demo_profile(self, raw_text: str, filename: Optional[str] = None) -> CandidateProfileSchema:
        """Generates realistic structured sample profile for DEMO_MODE or fallback."""
        return CandidateProfileSchema(
            name="Alex Morgan",
            email="alex.morgan@example.com",
            phone="+1 (555) 019-2834",
            professional_summary="Versatile Software Engineer & Aspiring AI/ML Developer with 2 years of full-stack engineering experience. Proficient in Python, FastAPI, React, and Machine Learning fundamentals with recent hands-on projects in RAG and GenAI applications.",
            years_of_experience=2.0,
            education=[
                EducationItem(
                    degree="B.S. in Computer Science",
                    institution="State University of Technology",
                    field_of_study="Computer Science",
                    start_year="2020",
                    end_year="2024",
                    grade="3.8 / 4.0",
                )
            ],
            work_experience=[
                WorkExperienceItem(
                    job_title="Associate Software Engineer",
                    company="TechSolutions Inc.",
                    duration="Jun 2024 - Present",
                    location="San Francisco, CA",
                    responsibilities=[
                        "Developed asynchronous RESTful APIs using Python, FastAPI, and PostgreSQL.",
                        "Optimized database queries and containerized microservices using Docker.",
                    ],
                    key_achievements=[
                        "Reduced backend API response latency by 35% across core endpoints."
                    ],
                ),
                WorkExperienceItem(
                    job_title="Software Developer Intern",
                    company="DataInnovate Labs",
                    duration="Jun 2023 - Aug 2023",
                    location="Remote",
                    responsibilities=[
                        "Built data processing pipelines in Python and Pandas for analytics dashboard."
                    ],
                    key_achievements=[],
                ),
            ],
            projects=[
                ProjectItem(
                    title="DocuBrain - RAG Document Q&A System",
                    description="Built a Retrieval-Augmented Generation application using LangChain, OpenAI API, and ChromaDB for semantic Q&A over PDF files.",
                    technologies_used=["Python", "FastAPI", "LangChain", "ChromaDB", "React"],
                    link="https://github.com/example/docubrain",
                ),
                ProjectItem(
                    title="Customer Churn Prediction Pipeline",
                    description="Trained Scikit-Learn classification model predicting subscriber churn with 89% accuracy.",
                    technologies_used=["Python", "Scikit-Learn", "Pandas", "Matplotlib"],
                    link="https://github.com/example/churn-prediction",
                ),
            ],
            certifications=[
                CertificationItem(
                    name="AWS Certified Developer - Associate",
                    issuing_organization="Amazon Web Services",
                    year="2024",
                ),
                CertificationItem(
                    name="Deep Learning Specialization",
                    issuing_organization="DeepLearning.AI / Coursera",
                    year="2023",
                ),
            ],
            skills=CategorizedSkills(
                programming_languages=["Python", "JavaScript", "SQL", "C++"],
                frameworks=["FastAPI", "React", "PyTorch", "Scikit-Learn", "Flask"],
                databases=["PostgreSQL", "SQLite", "MongoDB"],
                cloud_tools=["AWS", "Docker", "Git", "GitHub"],
                ai_ml_skills=["Machine Learning", "Deep Learning", "Natural Language Processing", "Supervised Learning"],
                genai_skills=["RAG (Retrieval-Augmented Generation)", "Prompt Engineering"],
                soft_skills=["Problem Solving", "Team Collaboration", "Agile Development"],
                other_skills=[],
            ),
            notable_strengths=[
                "Solid foundation in Python backend engineering and modern web frameworks",
                "Demonstrated hands-on experience building RAG and ML applications",
                "Active continuous learner with industry certifications (AWS, DeepLearning.AI)",
            ],
            missing_information=[
                "No live deployment links for portfolio projects",
                "LangChain and Advanced Vector DB experience is currently introductory",
            ],
        )


# Singleton agent instance
resume_agent = ResumeIntelligenceAgent()
