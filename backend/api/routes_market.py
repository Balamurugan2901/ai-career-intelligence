from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.agents.market_agent import market_agent
from backend.models.database import get_db
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository
from backend.repositories.market_repository import MarketRepository
from backend.schemas.market import MarketRoleDemand, MarketIntelligenceResponse
from backend.utils.logger import logger

router = APIRouter(prefix="/market", tags=["Market Intelligence"])


@router.get("/role/{role_name}", response_model=MarketRoleDemand)
def get_market_role_demand(role_name: str):
    """
    Retrieves current market demand, top required skills, emerging tech trends,
    and responsibilities for a specific career role.
    """
    logger.info(f"Retrieving market intelligence for role: '{role_name}'")
    mkt_demand = market_agent.analyze_single_role(role_name)
    return mkt_demand


@router.post("/analyze/{candidate_id}", response_model=MarketIntelligenceResponse)
def analyze_market_for_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    """
    Analyzes market intelligence for all matched career paths of a candidate,
    persists skill requirements into SQLite DB, and returns structured demand profiles.
    """
    logger.info(f"Analyzing market intelligence for Candidate #{candidate_id}...")

    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    # Get matched career paths from database
    career_paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
    if not career_paths:
        # Default target role set if career matching has not been run yet
        role_names = ["GenAI Engineer", "AI Engineer", "ML Engineer", "Backend Developer"]
    else:
        role_names = [cp.role_name for cp in career_paths]

    # Run MarketIntelligenceAgent
    market_demands = market_agent.analyze_market_for_roles(role_names)

    # Persist market requirements to DB if career paths exist
    if career_paths:
        MarketRepository.save_market_requirements_for_career_paths(db, career_paths, market_demands)

    return MarketIntelligenceResponse(
        candidate_id=candidate_id,
        analyzed_roles_count=len(market_demands),
        market_demands=market_demands,
    )
