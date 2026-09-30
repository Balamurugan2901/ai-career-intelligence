# Prompt Engineering & Guardrail Mechanics

Prompt engineering across the platform's agents follows strict principles to enforce structural JSON compliance, prevent hallucination of numerical metrics, and maintain high reasoning quality.

---

## 1. Principles of Prompt Design

1. **Schema Enforcement via Pydantic**: Every prompt instructing an LLM agent explicitly embeds the exact Pydantic JSON schema expected (`schema.model_json_schema()`).
2. **Markdown Block Cleanup**: Raw LLM output is post-processed by `GeminiProvider._clean_json_string()` to strip markdown code fence formatting (```json ... ```) prior to JSON validation.
3. **Strict Separation of Data & Logic**: Prompts never ask the LLM to invent candidate numbers or fit percentages. Fit percentages are calculated in Python via `career_matcher.py` and passed into subsequent prompt contexts.
4. **No Rote Memorization Scripts**: Interview prompt guidelines explicitly forbid verbatim scripted answers, requiring STAR structural frameworks and trade-off evaluation rubrics instead.

---

## 2. Guardrails Against Hallucination

- **Strict Schema Fallback**: If an LLM returns non-JSON or invalid schema fields, `GeminiProvider.generate_json` catches `ValidationError` or `JSONDecodeError` and falls back cleanly to pre-validated schema mock objects in `DEMO_MODE=true` or error mode.
- **Role & Scope Boundaries**: Prompts specify system roles (e.g. *"You are an expert AI Career Advisor and Senior Technical Recruiter..."*), scoping output strictly to technical assessment and learning design.

---

## 3. Fallback Mechanics

When `DEMO_MODE=true` or when Google Gemini API quotas are exhausted, `GeminiProvider` activates fallback generation:

```python
if self.demo_mode or not self.api_key:
    return self._generate_mock_json(schema)
```

This guarantees 100% UI functionality and API stability during offline demonstrations or automated test execution.
