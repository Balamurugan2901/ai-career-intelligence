from typing import Optional, Tuple
from sqlalchemy.orm import Session

from backend.models.candidate import User, Resume, CandidateProfile
from backend.models.skill import Skill, CandidateSkill
from backend.schemas.candidate import CandidateProfileSchema
from backend.services.skill_normalizer import skill_normalizer
from backend.utils.logger import logger


class CandidateRepository:
    """Database repository for candidate profile operations."""

    @classmethod
    def save_resume_and_profile(
        cls,
        db: Session,
        filename: str,
        file_type: str,
        raw_text: str,
        profile_schema: CandidateProfileSchema,
        user_id: Optional[int] = None,
    ) -> Tuple[Resume, CandidateProfile]:
        """
        Persists raw resume and parsed candidate profile into database.
        Ensures normalized skills are created without duplication.
        """
        try:
            # 1. Create or lookup user
            if not user_id:
                existing_user = None
                if profile_schema.email:
                    existing_user = db.query(User).filter(User.email == profile_schema.email).first()
                
                if existing_user:
                    user_id = existing_user.id
                else:
                    user = User(email=profile_schema.email, name=profile_schema.name)
                    db.add(user)
                    db.flush()
                    user_id = user.id

            # 2. Save Resume record
            resume = Resume(
                user_id=user_id,
                filename=filename,
                file_type=file_type,
                raw_text=raw_text,
            )
            db.add(resume)
            db.flush()

            # 3. Save CandidateProfile record
            profile = CandidateProfile(
                resume_id=resume.id,
                name=profile_schema.name,
                professional_summary=profile_schema.professional_summary,
                years_of_experience=profile_schema.years_of_experience,
                profile_json=profile_schema.model_dump(),
            )
            db.add(profile)
            db.flush()

            # 4. Save normalized candidate skills
            all_skills = profile_schema.skills.all_skills_list()
            for skill_name in all_skills:
                norm_name = skill_normalizer.normalize_skill(skill_name)

                # Look up existing skill or create new
                skill_obj = db.query(Skill).filter(Skill.normalized_name == norm_name.lower()).first()
                if not skill_obj:
                    skill_obj = Skill(name=norm_name, normalized_name=norm_name.lower(), category="general")
                    db.add(skill_obj)
                    db.flush()

                candidate_skill = CandidateSkill(
                    profile_id=profile.id,
                    skill_id=skill_obj.id,
                    proficiency_level="Intermediate",
                )
                db.add(candidate_skill)

            db.commit()
            db.refresh(resume)
            db.refresh(profile)

            logger.info(f"Successfully saved Resume #{resume.id} and Profile #{profile.id} in DB.")
            return resume, profile
        except Exception as e:
            db.rollback()
            logger.error(f"Error persisting candidate profile to DB: {e}")
            raise e

    @classmethod
    def get_profile_by_id(cls, db: Session, profile_id: int) -> Optional[CandidateProfile]:
        """Queries CandidateProfile by ID."""
        return db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()

    @classmethod
    def get_resume_by_id(cls, db: Session, resume_id: int) -> Optional[Resume]:
        """Queries Resume by ID."""
        return db.query(Resume).filter(Resume.id == resume_id).first()
