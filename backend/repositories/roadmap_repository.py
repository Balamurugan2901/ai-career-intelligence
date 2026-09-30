from typing import Optional, List
from sqlalchemy.orm import Session

from backend.models.roadmap import Roadmap, RoadmapItem
from backend.schemas.roadmap import (
    LearningRoadmapResponse,
    RoadmapPhaseSchema,
    RoadmapItemSchema,
)
from backend.utils.logger import logger


class RoadmapRepository:
    """Database repository for Roadmap persistence operations."""

    @classmethod
    def save_roadmap(
        cls,
        db: Session,
        profile_id: int,
        target_role: str,
        roadmap_res: LearningRoadmapResponse,
    ) -> Roadmap:
        """
        Saves Roadmap master record and RoadmapItem records to SQLite database.
        Clears previous roadmap entries for candidate + target_role before writing.
        """
        try:
            # Delete previous roadmap for this candidate and target role
            db.query(Roadmap).filter(
                Roadmap.profile_id == profile_id,
                Roadmap.target_role == target_role,
            ).delete()
            db.flush()

            roadmap = Roadmap(
                profile_id=profile_id,
                target_role=target_role,
            )
            db.add(roadmap)
            db.flush()

            for phase in roadmap_res.phases:
                for item in phase.items:
                    r_item = RoadmapItem(
                        roadmap_id=roadmap.id,
                        phase_number=phase.phase_number,
                        phase_name=phase.phase_name,
                        skill_name=item.skill,
                        why_it_matters=item.why_it_matters,
                        what_to_learn=item.what_to_learn,
                        prerequisites=item.prerequisites,
                        practical_task=item.practical_task,
                        mini_project=item.mini_project,
                        validation_method=item.validation_method,
                        estimated_effort=item.estimated_effort,
                    )
                    db.add(r_item)

            db.commit()
            db.refresh(roadmap)
            logger.info(f"Successfully saved Roadmap #{roadmap.id} for Profile #{profile_id} ({target_role}) in DB.")
            return roadmap
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving roadmap to DB: {e}")
            raise e

    @classmethod
    def get_roadmap_by_candidate_id(
        cls,
        db: Session,
        profile_id: int,
        target_role: Optional[str] = None,
    ) -> Optional[Roadmap]:
        """Queries active Roadmap model for a candidate profile ID."""
        query = db.query(Roadmap).filter(Roadmap.profile_id == profile_id)
        if target_role:
            query = query.filter(Roadmap.target_role == target_role)
        return query.order_by(Roadmap.id.desc()).first()
