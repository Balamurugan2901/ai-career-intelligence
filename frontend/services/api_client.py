import os
import httpx
from typing import Dict, Any, Optional


class ApiClient:
    """
    HTTP Client service connecting the Streamlit Dashboard UI to the FastAPI backend endpoints.
    Provides robust timeout management, clean exception handling, and JSON serialization.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: float = 60.0):
        self.base_url = (base_url or os.getenv("BACKEND_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.timeout = timeout

    def check_health(self) -> Optional[Dict[str, Any]]:
        """Queries /health endpoint."""
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.base_url}/health")
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    def upload_resume(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Uploads candidate resume PDF/DOCX to POST /resume/upload."""
        with httpx.Client(timeout=self.timeout) as client:
            files = {"file": (filename, file_bytes, "application/pdf" if filename.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            res = client.post(f"{self.base_url}/resume/upload", files=files)
            res.raise_for_status()
            return res.json()

    def get_candidate_profile(self, candidate_id: int) -> Dict[str, Any]:
        """Fetches candidate profile schema from GET /resume/candidate/{candidate_id}."""
        with httpx.Client(timeout=self.timeout) as client:
            res = client.get(f"{self.base_url}/resume/candidate/{candidate_id}")
            res.raise_for_status()
            return res.json()

    def start_pipeline_analysis(self, candidate_id: int, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Triggers multi-agent pipeline via POST /analysis/start."""
        with httpx.Client(timeout=self.timeout) as client:
            payload = {"candidate_id": candidate_id}
            if target_role:
                payload["target_role"] = target_role
            res = client.post(f"{self.base_url}/analysis/start", json=payload)
            res.raise_for_status()
            return res.json()

    def get_analysis_status(self, analysis_id: int) -> Dict[str, Any]:
        """Queries pipeline execution state from GET /analysis/{analysis_id}."""
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{self.base_url}/analysis/{analysis_id}")
            res.raise_for_status()
            return res.json()

    def get_full_analysis(self, candidate_id: int) -> Dict[str, Any]:
        """Retrieves full aggregated 7-agent summary from GET /analysis/candidate/{candidate_id}/full."""
        with httpx.Client(timeout=self.timeout) as client:
            res = client.get(f"{self.base_url}/analysis/candidate/{candidate_id}/full")
            res.raise_for_status()
            return res.json()

    def get_career_matches(self, candidate_id: int) -> Dict[str, Any]:
        """Triggers/retrieves career match scores from POST /career/match/{candidate_id}."""
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(f"{self.base_url}/career/match/{candidate_id}")
            res.raise_for_status()
            return res.json()

    def get_market_intelligence(self, candidate_id: int) -> Dict[str, Any]:
        """Triggers/retrieves market demand insights from POST /market/analyze/{candidate_id}."""
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(f"{self.base_url}/market/analyze/{candidate_id}")
            res.raise_for_status()
            return res.json()

    def get_skill_gaps(self, candidate_id: int, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Triggers/retrieves skill gap matrix from POST /skill-gap/analyze/{candidate_id}."""
        with httpx.Client(timeout=self.timeout) as client:
            params = {"role_name": target_role} if target_role else {}
            res = client.post(f"{self.base_url}/skill-gap/analyze/{candidate_id}", params=params)
            res.raise_for_status()
            return res.json()

    def get_learning_roadmap(self, candidate_id: int, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Triggers/retrieves multi-phase learning roadmap from POST /roadmap/generate/{candidate_id}."""
        with httpx.Client(timeout=self.timeout) as client:
            params = {"role_name": target_role} if target_role else {}
            res = client.post(f"{self.base_url}/roadmap/generate/{candidate_id}", params=params)
            res.raise_for_status()
            return res.json()

    def get_project_recommendations(self, candidate_id: int, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Triggers/retrieves portfolio project recommendations from POST /projects/recommend/{candidate_id}."""
        with httpx.Client(timeout=self.timeout) as client:
            params = {"role_name": target_role} if target_role else {}
            res = client.post(f"{self.base_url}/projects/recommend/{candidate_id}", params=params)
            res.raise_for_status()
            return res.json()

    def get_interview_prep(self, candidate_id: int, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Triggers/retrieves interview prep questions from POST /interview/generate/{candidate_id}."""
        with httpx.Client(timeout=self.timeout) as client:
            params = {"role_name": target_role} if target_role else {}
            res = client.post(f"{self.base_url}/interview/generate/{candidate_id}", params=params)
            res.raise_for_status()
            return res.json()


api_client = ApiClient()
