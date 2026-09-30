from backend.services.skill_normalizer import skill_normalizer, SkillNormalizer


def test_normalize_single_skill():
    """Verifies canonical skill name mapping."""
    assert SkillNormalizer.normalize_skill("python 3") == "Python"
    assert SkillNormalizer.normalize_skill("PYTHON") == "Python"
    assert SkillNormalizer.normalize_skill("react.js") == "React"
    assert SkillNormalizer.normalize_skill("ml") == "Machine Learning"
    assert SkillNormalizer.normalize_skill("genai") == "Generative AI"
    assert SkillNormalizer.normalize_skill("rag") == "RAG (Retrieval-Augmented Generation)"


def test_normalize_skill_list():
    """Verifies list normalization and deduplication."""
    raw_skills = ["Python 3", "python", "Py", "React", "ReactJS", "FastAPI", "SQL"]
    normalized = skill_normalizer.normalize_skill_list(raw_skills)
    assert normalized == ["Python", "React", "FastAPI", "SQL"]
