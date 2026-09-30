from typing import Optional, List
from sqlalchemy.orm import Session

from backend.models.candidate import CandidateProfile
from backend.models.interview import AnalysisRun
from backend.utils.logger import logger


class AnalysisRepository:
    """Database repository for AnalysisRun queries."""

    @classmethod
    def get_analysis_run_by_id(cls, db: Session, analysis_id: int) -> Optional[AnalysisRun]:
        """Queries AnalysisRun record by ID."""
        return db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()

    @classmethod
    def get_latest_run_for_candidate(cls, db: Session, candidate_id: int) -> Optional[AnalysisRun]:
        """Queries latest AnalysisRun for candidate."""
        profile = db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()
        if not profile:
            return None

        return (
            db.query(AnalysisRun)
            .filter(AnalysisRun.resume_id == profile.resume_id)
            .order_by(AnalysisRun.id.desc())
            .first()
        )
