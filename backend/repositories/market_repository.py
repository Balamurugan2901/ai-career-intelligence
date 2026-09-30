from typing import List
from sqlalchemy.orm import Session

from backend.models.career import CareerPath, CareerRequirement
from backend.models.skill import Skill
from backend.schemas.market import MarketRoleDemand
from backend.services.skill_normalizer import skill_normalizer
from backend.utils.logger import logger


class MarketRepository:
    """Database repository for market requirement operations."""

    @classmethod
    def save_market_requirements_for_career_paths(
        cls,
        db: Session,
        career_paths: List[CareerPath],
        market_demands: List[MarketRoleDemand],
    ) -> int:
        """
        Saves required market skills into career_requirements for candidate career paths.
        """
        saved_count = 0
        try:
            demand_map = {m.role_name.lower(): m for m in market_demands}

            for cp in career_paths:
                role_key = cp.role_name.lower()
                mkt_data = demand_map.get(role_key)
                if not mkt_data:
                    continue

                # Clear previous requirements for this path
                db.query(CareerRequirement).filter(CareerRequirement.career_path_id == cp.id).delete()
                db.flush()

                # Process top required skills
                for skill_name in mkt_data.top_required_skills:
                    norm_name = skill_normalizer.normalize_skill(skill_name)
                    skill_obj = db.query(Skill).filter(Skill.normalized_name == norm_name.lower()).first()
                    if not skill_obj:
                        skill_obj = Skill(name=norm_name, normalized_name=norm_name.lower(), category="market_required")
                        db.add(skill_obj)
                        db.flush()

                    req = CareerRequirement(
                        career_path_id=cp.id,
                        skill_id=skill_obj.id,
                        demand_level=mkt_data.demand_level,
                        importance="Required",
                    )
                    db.add(req)
                    saved_count += 1

            db.commit()
            logger.info(f"Saved {saved_count} market career requirement records in DB.")
            return saved_count
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving market requirements to DB: {e}")
            raise e
