from typing import List, Optional
from sqlalchemy.orm import Session

from backend.models.skill import Skill, SkillGap
from backend.schemas.skill_gap import SkillGapItem
from backend.services.skill_normalizer import skill_normalizer
from backend.utils.logger import logger


class SkillGapRepository:
    """Database repository for SkillGap persistence."""

    @classmethod
    def save_skill_gaps(
        cls,
        db: Session,
        profile_id: int,
        target_role: str,
        gap_items: List[SkillGapItem],
    ) -> List[SkillGap]:
        """
        Saves skill gap records to SQLite database.
        Clears previous gap records for candidate + target_role before saving.
        """
        try:
            # Clear previous gap records for this role
            db.query(SkillGap).filter(
                SkillGap.profile_id == profile_id,
                SkillGap.target_role == target_role,
            ).delete()
            db.flush()

            records = []
            for item in gap_items:
                norm_name = skill_normalizer.normalize_skill(item.skill)
                skill_obj = db.query(Skill).filter(Skill.normalized_name == norm_name.lower()).first()
                if not skill_obj:
                    skill_obj = Skill(name=norm_name, normalized_name=norm_name.lower(), category="gap_analysis")
                    db.add(skill_obj)
                    db.flush()

                gap_rec = SkillGap(
                    profile_id=profile_id,
                    skill_id=skill_obj.id,
                    target_role=target_role,
                    current_level=item.current_level,
                    target_level=item.target_level,
                    priority=item.priority,
                    reason=item.reason,
                    estimated_learning_effort=item.estimated_learning_effort,
                    dependency_skills=item.dependency_skills,
                )
                db.add(gap_rec)
                records.append(gap_rec)

            db.commit()
            logger.info(f"Saved {len(records)} SkillGap records for Profile #{profile_id} ({target_role}) in DB.")
            return records
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving skill gaps to DB: {e}")
            raise e

    @classmethod
    def get_skill_gaps_by_candidate_id(
        cls,
        db: Session,
        profile_id: int,
        target_role: Optional[str] = None,
    ) -> List[SkillGap]:
        """Queries skill gap records for a candidate profile ID."""
        query = db.query(SkillGap).filter(SkillGap.profile_id == profile_id)
        if target_role:
            query = query.filter(SkillGap.target_role == target_role)
        return query.all()
