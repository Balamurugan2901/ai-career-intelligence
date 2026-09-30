# Developer & Contribution Guidelines

Developer documentation for building, extending, and testing components within the **AI Career Intelligence & Growth Platform**.

---

## 1. Project Directory Structure

```
ai-career-intelligence/
├── backend/
│   ├── agents/            # Independent AI agents (Resume, Career, Market, Gap, Roadmap, Project, Interview)
│   ├── api/               # FastAPI route handlers
│   ├── models/            # SQLAlchemy database models & schemas
│   ├── orchestration/     # CareerAnalysisPipeline workflow engine
│   ├── prompts/           # External agent prompt templates
│   ├── repositories/      # Database access abstraction layers
│   ├── schemas/           # Pydantic data validation schemas
│   ├── services/          # Pure Python engines (matcher, gap analyzer, market reference, skill normalizer)
│   ├── utils/             # Logging & helper utilities
│   ├── config.py          # Centralized environment settings
│   └── main.py            # FastAPI application entry point
├── data/
│   ├── market_reference/  # Local market benchmark dataset (roles.json)
│   └── sample_resumes/    # Synthetic candidate test resume fixtures
├── docs/                  # Technical documentation suite
├── frontend/
│   ├── services/          # ApiClient service
│   ├── views/             # Modular Streamlit page views
│   ├── styles.py          # Dark glassmorphism CSS design system
│   └── app.py             # Streamlit entry point
├── tests/                 # Full automated unit, route & resilience test suite
├── .env.example           # Environment template
├── .gitignore             # Git exclusions
├── requirements.txt       # Python dependencies
└── run.py                 # Single-command application launcher
```

---

## 2. Guidelines for Adding a New Agent

1. **Create Pydantic Schema**: Add request/response schemas in `backend/schemas/`.
2. **Create External Prompt**: Store prompt template in `backend/prompts/<agent_name>/`.
3. **Build Agent Class**: Implement agent in `backend/agents/<agent_name>_agent.py` using `llm_service`. Include fallback generation for `DEMO_MODE=true`.
4. **Register in Pipeline**: Add step to `CareerAnalysisPipeline.execute()` in `backend/orchestration/pipeline.py`.
5. **Add API Endpoint**: Add route in `backend/api/` and register in `backend/main.py`.
6. **Add Unit Tests**: Write tests in `tests/test_<agent_name>_agent.py` and `tests/test_routes_<agent_name>.py`.
