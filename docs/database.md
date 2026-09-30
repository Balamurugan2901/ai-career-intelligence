# Relational Database Schema & Migration Specification

The platform utilizes SQLAlchemy ORM for database abstraction. By default, SQLite is used for lightweight local execution (`career_intelligence.db`). The schema is fully compliant with PostgreSQL for production scaling.

---

## 1. Entity-Relationship Schema Overview

```
 [Users] 1 ─── N [Resumes] 1 ─── 1 [CandidateProfiles] 1 ─── N [CandidateSkills] N ─── 1 [Skills]
                                         │
                   ┌─────────────────────┼─────────────────────┐
                   │                     │                     │
                   ▼                     ▼                     ▼
          [CareerPaths]         [SkillGaps]             [Roadmaps]
                   │
                   ▼
         [MarketRequirements]   [Projects]             [InterviewQuestions]

                                [AnalysisRuns]
```

---

## 2. Table Definitions

### `users`
- `id` (INT, Primary Key)
- `email` (VARCHAR, Unique, Nullable)
- `name` (VARCHAR, Nullable)
- `created_at` (DATETIME)

### `resumes`
- `id` (INT, Primary Key)
- `user_id` (INT, Foreign Key ➔ `users.id`)
- `filename` (VARCHAR)
- `file_type` (VARCHAR)
- `raw_text` (TEXT)
- `created_at` (DATETIME)

### `candidate_profiles`
- `id` (INT, Primary Key)
- `resume_id` (INT, Foreign Key ➔ `resumes.id`)
- `name` (VARCHAR)
- `professional_summary` (TEXT)
- `years_of_experience` (FLOAT)
- `profile_json` (JSON)
- `created_at` (DATETIME)

### `skills` & `candidate_skills`
- `skills`: `id`, `name`, `normalized_name` (UNIQUE index), `category`.
- `candidate_skills`: `id`, `profile_id` (FK ➔ `candidate_profiles.id`), `skill_id` (FK ➔ `skills.id`), `proficiency_level`.

### `career_paths` & `market_requirements`
- `career_paths`: `id`, `candidate_id` (FK ➔ `candidate_profiles.id`), `role_name`, `fit_score`, `reasoning`, `matching_skills` (JSON), `missing_skills` (JSON), `recommended_next_step`.
- `market_requirements`: `id`, `career_path_id` (FK ➔ `career_paths.id`), `demand_level`, `top_required_skills` (JSON), `emerging_skills` (JSON), `avg_salary_range`, `source`, `updated_at`.

### `skill_gaps`
- `id`, `profile_id` (FK ➔ `candidate_profiles.id`), `target_role`, `skill_name`, `current_level`, `target_level`, `priority` (HIGH/MEDIUM/LOW), `gap_type`, `reason`, `estimated_learning_effort`, `dependency_skills` (JSON).

### `roadmaps` & `roadmap_phases` & `roadmap_items`
- Persists ordered 6-phase learning plans with tasks, mini-projects, effort hours, and validation criteria.

### `projects`
- `id`, `profile_id` (FK ➔ `candidate_profiles.id`), `project_title`, `difficulty`, `problem_statement`, `why_this_project`, `skills_covered` (JSON), `expected_features` (JSON), `technology_stack` (JSON), `learning_outcomes` (JSON), `resume_value`.

### `interview_questions`
- `id`, `profile_id` (FK ➔ `candidate_profiles.id`), `category`, `question`, `difficulty`, `expected_concepts` (JSON), `evaluation_points` (JSON), `model_answer_structure`.

### `analysis_runs`
- `id`, `resume_id` (FK ➔ `resumes.id`), `status` (PENDING/RUNNING/COMPLETED/FAILED), `execution_time_seconds`, `error_message`, `agents_completed` (JSON), `created_at`, `completed_at`.

---

## 3. PostgreSQL Migration Guidelines

To switch from SQLite to PostgreSQL:
1. Install `psycopg2-binary` driver.
2. Update `.env`:
   ```ini
   DATABASE_URL=postgresql://user:password@localhost:5432/career_intel_db
   ```
3. Run SQLAlchemy `init_db()` or Alembic migrations. Schema compatibility is natively maintained.
