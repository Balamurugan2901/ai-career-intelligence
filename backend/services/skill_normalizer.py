from typing import List, Dict


class SkillNormalizer:
    """Service for canonicalizing skill names and deduplicating skill lists."""

    # Map of lowercase aliases to canonical skill representation
    SKILL_ALIASES: Dict[str, str] = {
        # Programming Languages
        "python": "Python",
        "python 3": "Python",
        "python programming": "Python",
        "py": "Python",
        "js": "JavaScript",
        "javascript": "JavaScript",
        "es6": "JavaScript",
        "ts": "TypeScript",
        "typescript": "TypeScript",
        "cpp": "C++",
        "c++": "C++",
        "c#": "C#",
        "c sharp": "C#",
        "golang": "Go",
        "go lang": "Go",
        "sql": "SQL",
        "structured query language": "SQL",

        # Frameworks & Libraries
        "react": "React",
        "react.js": "React",
        "reactjs": "React",
        "node": "Node.js",
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "pytorch": "PyTorch",
        "torch": "PyTorch",
        "tf": "TensorFlow",
        "tensorflow": "TensorFlow",
        "scikit-learn": "Scikit-Learn",
        "sklearn": "Scikit-Learn",
        "scikitlearn": "Scikit-Learn",

        # Databases
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "sqlite": "SQLite",
        "sqlite3": "SQLite",
        "mongo": "MongoDB",
        "mongodb": "MongoDB",
        "redis": "Redis",
        "mysql": "MySQL",

        # Cloud & DevOps
        "aws": "AWS",
        "amazon web services": "AWS",
        "gcp": "Google Cloud Platform",
        "google cloud": "Google Cloud Platform",
        "azure": "Microsoft Azure",
        "docker": "Docker",
        "k8s": "Kubernetes",
        "kubernetes": "Kubernetes",
        "git": "Git",
        "github": "GitHub",

        # AI / ML / GenAI
        "ml": "Machine Learning",
        "machine learning": "Machine Learning",
        "dl": "Deep Learning",
        "deep learning": "Deep Learning",
        "cv": "Computer Vision",
        "computer vision": "Computer Vision",
        "nlp": "Natural Language Processing",
        "natural language processing": "Natural Language Processing",
        "genai": "Generative AI",
        "generative ai": "Generative AI",
        "llm": "Large Language Models",
        "llms": "Large Language Models",
        "large language models": "Large Language Models",
        "rag": "RAG (Retrieval-Augmented Generation)",
        "retrieval augmented generation": "RAG (Retrieval-Augmented Generation)",
        "retrieval-augmented generation": "RAG (Retrieval-Augmented Generation)",
        "langchain": "LangChain",
        "llama-index": "LlamaIndex",
        "llamaindex": "LlamaIndex",
        "vector db": "Vector Databases",
        "vector databases": "Vector Databases",
        "vector search": "Vector Databases",
        "chromadb": "ChromaDB",
        "chroma": "ChromaDB",
        "pinecone": "Pinecone",
    }

    @classmethod
    def normalize_skill(cls, skill: str) -> str:
        """Returns canonical representation of a skill string."""
        if not skill:
            return ""

        clean_skill = skill.strip()
        lower_skill = clean_skill.lower()

        # Check in alias mapping
        if lower_skill in cls.SKILL_ALIASES:
            return cls.SKILL_ALIASES[lower_skill]

        # Standard title case format for unmatched skills
        if len(clean_skill) <= 4:
            return clean_skill.upper()  # e.g., HTML, CSS, SQL, AWS
        return clean_skill.title()

    @classmethod
    def normalize_skill_list(cls, skills: List[str]) -> List[str]:
        """Normalizes and deduplicates a list of skill strings while preserving order."""
        if not skills:
            return []

        normalized = []
        seen = set()

        for s in skills:
            norm = cls.normalize_skill(s)
            if norm and norm.lower() not in seen:
                seen.add(norm.lower())
                normalized.append(norm)

        return normalized


# Singleton instance
skill_normalizer = SkillNormalizer()
