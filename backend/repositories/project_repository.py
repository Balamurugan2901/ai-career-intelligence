from typing import List
from sqlalchemy.orm import Session

from backend.models.roadmap import ProjectRecommendation
from backend.schemas.projects import ProjectItemSchema
from backend.utils.logger import logger


class ProjectRepository:
    """Database repository for ProjectRecommendation persistence operations."""

    @classmethod
    def save_project_recommendations(
        cls,
        db: Session,
        profile_id: int,
        projects: List[ProjectItemSchema],
    ) -> List[ProjectRecommendation]:
        """
        Saves recommended portfolio project records to SQLite database.
        Clears previous recommendations for candidate prior to saving new run.
        """
        try:
            # Delete previous project recommendations for candidate
            db.query(ProjectRecommendation).filter(
                ProjectRecommendation.profile_id == profile_id
            ).delete()
            db.flush()

            records = []
            for item in projects:
                rec = ProjectRecommendation(
                    profile_id=profile_id,
                    project_title=item.project_title,
                    difficulty=item.difficulty,
                    problem_statement=item.problem_statement,
                    why_this_project=item.why_this_project,
                    skills_covered=item.skills_covered,
                    expected_features=item.expected_features,
                    technology_stack=item.technology_stack,
                    learning_outcomes=item.learning_outcomes,
                    resume_value=item.resume_value,
                    suggested_extensions=item.suggested_extensions,
                )
                db.add(rec)
                records.append(rec)

            db.commit()
            logger.info(f"Saved {len(records)} ProjectRecommendation records for Profile #{profile_id} in DB.")
            return records
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving project recommendations to DB: {e}")
            raise e

    @classmethod
    def get_project_recommendations_by_candidate_id(
        cls,
        db: Session,
        profile_id: int,
    ) -> List[ProjectRecommendation]:
        """Queries ProjectRecommendation records for a candidate profile ID."""
        return (
            db.query(ProjectRecommendation)
            .filter(ProjectRecommendation.profile_id == profile_id)
            .all()
        )
