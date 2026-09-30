from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from backend.agents.resume_agent import resume_agent
from backend.models.database import get_db
from backend.repositories.candidate_repository import CandidateRepository
from backend.schemas.candidate import CandidateProfileSchema, CandidateUploadResponse
from backend.services.resume.parser import ResumeParser, ResumeParserError
from backend.utils.logger import logger

router = APIRouter(prefix="/resume", tags=["Resume Intelligence"])


@router.post("/upload", response_model=CandidateUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Endpoint for uploading PDF or DOCX resumes.
    Performs local text extraction, structured CandidateProfile generation via LLM,
    skill normalization, and database persistence.
    """
    logger.info(f"Received resume upload request: filename='{file.filename}'")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file missing filename.")

    try:
        content = await file.read()
        
        # 1. Local Text Extraction
        raw_text, ext = ResumeParser.parse_bytes(file.filename, content)

        # 2. Agent Intelligence Profile Analysis & Skill Normalization
        profile_schema = resume_agent.analyze_resume(raw_text, filename=file.filename)

        # 3. Database Persistence
        resume_record, profile_record = CandidateRepository.save_resume_and_profile(
            db=db,
            filename=file.filename,
            file_type=ext,
            raw_text=raw_text,
            profile_schema=profile_schema,
        )

        return CandidateUploadResponse(
            resume_id=resume_record.id,
            candidate_id=profile_record.id,
            filename=file.filename,
            file_type=ext,
            profile=profile_schema,
        )

    except ResumeParserError as e:
        logger.warning(f"Resume parsing validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during resume processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the uploaded resume. Please try again.",
        )


@router.get("/candidate/{candidate_id}", response_model=CandidateProfileSchema)
def get_candidate_profile(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves structured candidate profile by candidate ID."""
    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    if profile_record.profile_json:
        return CandidateProfileSchema.model_validate(profile_record.profile_json)

    # Fallback response construction if JSON was not stored
    return CandidateProfileSchema(
        name=profile_record.name or "Candidate",
        professional_summary=profile_record.professional_summary or "",
        years_of_experience=profile_record.years_of_experience or 0.0,
    )
