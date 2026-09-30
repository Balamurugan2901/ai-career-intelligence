from typing import List
from sqlalchemy.orm import Session

from backend.models.career import CareerPath
from backend.schemas.career import CareerPathBase
from backend.utils.logger import logger


class CareerRepository:
    """Database repository for persisting and querying career path matches."""

    @classmethod
    def save_career_paths(cls, db: Session, profile_id: int, matches: List[CareerPathBase]) -> List[CareerPath]:
        """
        Saves candidate career match results into database.
        Clears previous career path entries for this candidate prior to saving new run.
        """
        try:
            # Clear existing career path matches for candidate
            db.query(CareerPath).filter(CareerPath.profile_id == profile_id).delete()
            db.flush()

            records = []
            for match in matches:
                cp = CareerPath(
                    profile_id=profile_id,
                    role_name=match.role_name,
                    fit_score=match.fit_score,
                    reasoning=match.reasoning,
                    matching_skills=match.matching_skills,
                    missing_skills=match.missing_skills,
                    recommended_next_step=match.recommended_next_step,
                )
                db.add(cp)
                records.append(cp)

            db.commit()
            logger.info(f"Successfully saved {len(records)} career path matches for Profile #{profile_id} to DB.")
            return records
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving career path matches to DB: {e}")
            raise e

    @classmethod
    def get_career_paths_by_candidate_id(cls, db: Session, profile_id: int) -> List[CareerPath]:
        """Queries career path match records for a candidate profile ID ordered by fit_score descending."""
        return (
            db.query(CareerPath)
            .filter(CareerPath.profile_id == profile_id)
            .order_by(CareerPath.fit_score.desc())
            .all()
        )
