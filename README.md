# Prompt Regression Suite

A framework for treating prompt templates as versioned, testable artifacts with regression coverage, consistency scoring, and failure detection across input variations.

## Why Prompt Brittleness Matters

In production AI systems, prompts are code. Small changes in user input can cause unexpected behavior, leading to incorrect outputs, security vulnerabilities, or inconsistent user experience. This suite helps identify and mitigate brittleness by testing prompts against diverse input variations, ensuring robustness before deployment.

## Behavioral Contracts

A behavioral contract defines the expected behavior of a prompt template. It includes:

- **must_not_contain**: Forbidden phrases that indicate uncertainty or hallucination
- **must_use_context**: Ensures output draws from provided context
- **max_length_tokens**: Limits output length
- **refusal_trigger**: Expected response when information is unavailable
- **must_be_one_of**: For classification, restricts to valid labels
- **must_start_with**: For formatting requirements

## Running with Mock Responder

No API key required. The mock responder simulates LLM behavior deterministically.

```bash
python main.py run --template qa_v1 --use-mock
python main.py run --all
python main.py report
```

## Plugging in OpenAI or Another LLM

Modify `runner/runner.py` to use the actual API instead of mock. Set `use_mock=False` and provide API key.

For OpenAI:
```python
import openai
response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
output = response.choices[0].message.content
```

## Example Brittleness Report

*(Run the suite to generate actual reports)*

## Adding a New Prompt Template

1. Create `templates/template_new.yaml` with id, template string, and contract.
2. Add base inputs to `variants/generate_catalog.py`.
3. Regenerate `variants/variant_catalog.json`.
4. Run the suite.

## Style Notes

- All scoring is deterministic given fixed inputs.
- Mock uses fixed seed for reproducibility.
- Type annotations throughout.
- No external LLM calls in default mode.