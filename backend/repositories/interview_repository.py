from typing import List
from sqlalchemy.orm import Session

from backend.models.interview import InterviewQuestion
from backend.schemas.interview import InterviewCategorySchema
from backend.utils.logger import logger


class InterviewRepository:
    """Database repository for InterviewQuestion persistence operations."""

    @classmethod
    def save_interview_questions(
        cls,
        db: Session,
        profile_id: int,
        categories: List[InterviewCategorySchema],
    ) -> List[InterviewQuestion]:
        """
        Saves interview questions to SQLite database.
        Clears previous question records for candidate before saving fresh set.
        """
        try:
            # Clear existing interview questions for candidate
            db.query(InterviewQuestion).filter(
                InterviewQuestion.profile_id == profile_id
            ).delete()
            db.flush()

            records = []
            for cat in categories:
                for q_item in cat.questions:
                    iq = InterviewQuestion(
                        profile_id=profile_id,
                        category=cat.category_name,
                        question=q_item.question,
                        difficulty=q_item.difficulty,
                        expected_concepts=q_item.expected_concepts,
                        evaluation_points=q_item.evaluation_points,
                        model_answer_structure=q_item.model_answer_structure,
                    )
                    db.add(iq)
                    records.append(iq)

            db.commit()
            logger.info(f"Saved {len(records)} InterviewQuestion records for Profile #{profile_id} in DB.")
            return records
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving interview questions to DB: {e}")
            raise e

    @classmethod
    def get_interview_questions_by_candidate_id(
        cls,
        db: Session,
        profile_id: int,
    ) -> List[InterviewQuestion]:
        """Queries InterviewQuestion records for a candidate profile ID."""
        return (
            db.query(InterviewQuestion)
            .filter(InterviewQuestion.profile_id == profile_id)
            .all()
        )
