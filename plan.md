Prompt Regression & Behavioral Contract Lab

A serious CI-ready framework for testing prompt changes the way software teams test code changes.

The current repo already has a good concept: prompt templates as versioned/testable artifacts, behavioral contracts, input variants, consistency scoring, brittleness reports, and deterministic mock execution. The current CLI runs templates, generates reports, and diffs prompt versions.

A few important issues:

Real OpenAI support is only TODO in Runner; non-mock mode returns "TODO: OpenAI response".
The README shows old openai.ChatCompletion.create style as an example; this should be modernized.
consistency.py loads SentenceTransformer globally at import time, which can slow CLI/tests and make lightweight usage harder.
Contract checks are useful but still basic; must_use_context relies on 4-gram overlap, which misses semantic grounding and can be brittle.
Roadmap
Phase 1 — Make it CI-grade

Add:

typed schemas
config file
modern responder interface
OpenAI responder
JSON/Markdown/JUnit outputs
regression gates
GitHub Actions
Phase 2 — Stronger behavioral contracts

Add:

JSON schema validation
regex constraints
semantic context use
refusal correctness
allowed labels
citation requirements
safety boundary checks
Phase 3 — Prompt version comparison

Add:

baseline vs candidate pass/fail diff
per-contract regression detection
severity levels
PR-friendly report
--fail-on-regression
Phase 4 — Model/provider matrix

Add:

mock
OpenAI
local/open-weight placeholder
multi-model comparison
temperature/retry controls
Phase 5 — Integration with your other repos

This can become the CI gate for:

rag-eval-harness
llm-drift-monitor
open-ended-task-agent
lora-finetune-eval

Your portfolio already emphasizes LLM planning, tool-use, SQL generation, vector retrieval, and enterprise agentic workflows , so this repo should become the prompt quality assurance layer of that ecosystem.

Claude Code prompt
You are working in my repo:
paulyonghaoli/prompt-regression-suite

Long-term goal:
Transform this repo from a lightweight prompt brittleness demo into “Prompt Regression & Behavioral Contract Lab” — a CI-ready framework for treating prompts as versioned, testable artifacts with behavioral contracts, input-variant testing, provider/model comparison, and deployment gates.

Do NOT rewrite everything at once.
Build a stable foundation first.

Current repo:
- templates/*.yaml define prompt templates and contracts
- variants/variant_catalog.json defines input variants
- runner/runner.py runs variants through a mock responder
- scoring/contract_checker.py checks behavioral contracts
- scoring/consistency.py computes semantic consistency
- scoring/brittleness_report.py writes report
- versioning/differ.py compares versions
- main.py exposes run, run-all, report, diff, mock

==================================================
PHASE 1 TARGET — CI-READY PROMPT REGRESSION FOUNDATION
==================================================

Main objectives:
1. Add typed schemas and validation
2. Add a proper responder interface
3. Implement modern OpenAI responder without breaking mock mode
4. Strengthen behavioral contracts
5. Add baseline-vs-candidate regression gates
6. Add machine-readable outputs
7. Add JUnit output for CI
8. Add tests and GitHub Actions
9. Keep deterministic mock mode as default

==================================================
PART 1 — CONFIG FILE
==================================================

Add config.yaml.

Example:

paths:
  templates_dir: templates
  variants_file: variants/variant_catalog.json
  results_dir: results

runner:
  provider: mock
  model: mock-v1
  temperature: 0.0
  max_tokens: 300
  timeout_seconds: 30
  retries: 2

openai:
  api_key_env: OPENAI_API_KEY
  model: gpt-4o-mini

embedding:
  model_name: all-MiniLM-L6-v2
  lazy_load: true

gates:
  min_contract_pass_rate: 0.95
  min_consistency_score: 0.85
  max_regression_count: 0
  fail_on_high_severity: true

output:
  write_json: true
  write_markdown: true
  write_junit: true

Update CLI:
python main.py run --template qa_v1 --config config.yaml
python main.py run-all --config config.yaml
python main.py report --template qa_v1 --config config.yaml
python main.py diff --v1 qa_v1 --v2 qa_v2 --config config.yaml
python main.py gate --baseline qa_v1 --candidate qa_v2 --config config.yaml

Preserve current commands as much as possible.

==================================================
PART 2 — TYPED SCHEMAS
==================================================

Create:
schemas.py or prompt_suite/schemas.py

Define dataclasses or Pydantic models:

PromptTemplate:
- id: str
- template: str
- contract: BehavioralContract
- metadata: dict optional

BehavioralContract:
- must_not_contain: list[str]
- must_use_context: bool
- max_length_tokens: int optional
- refusal_trigger: str optional
- must_be_one_of: list[str] optional
- must_start_with: str optional
- must_match_regex: str optional
- must_be_valid_json: bool optional
- json_schema: dict optional
- required_citations: bool optional
- semantic_similarity_to_reference: float optional

InputVariant:
- variant_type: str
- base_id: optional str/int
- inputs: dict[str, str]
- metadata: dict optional

RunResult:
- template_id
- variant_type
- input_hash
- inputs
- prompt
- output
- timestamp
- provider
- model
- latency_ms optional
- token_usage optional
- error optional
- contract_result optional

Validation:
- template id required
- template string required
- all required template placeholders appear in inputs
- variant catalog references valid template ids
- contract fields have valid types
- must_be_one_of cannot be empty

Add tests for invalid templates and invalid variant catalog.

==================================================
PART 3 — RESPONDER INTERFACE
==================================================

Create:
runner/responders.py

Define:

class BaseResponder:
    def respond(prompt: str, *, template_id: str, variant_type: str, metadata: dict) -> Response

Response:
- text
- provider
- model
- latency_ms
- token_usage
- error

Implement:
- MockResponderAdapter wrapping current mock
- OpenAIResponder using modern OpenAI v1 client
- EchoResponder for tests

Important:
- Mock remains default.
- OpenAI is optional.
- If OpenAI SDK/key missing, fail gracefully with clear message.
- Non-mock mode must no longer return TODO text.

==================================================
PART 4 — RUNNER IMPROVEMENT
==================================================

Update runner/runner.py.

Requirements:
- Use BaseResponder interface
- Validate template and variants before execution
- Preserve deterministic input hashing
- Record provider/model/latency/error
- Continue running when one variant fails
- Save per-run metadata:
  - timestamp
  - git commit if available
  - Python version
  - provider
  - model
  - config hash
  - template id
  - variant count

Outputs:
results/runs/{template_id}_{timestamp}/run_results.jsonl
results/runs/{template_id}_{timestamp}/run_metadata.json
results/results_{template_id}.json for backward compatibility

==================================================
PART 5 — CONTRACT CHECKER UPGRADE
==================================================

Update scoring/contract_checker.py.

Add checks:
1. must_match_regex
2. must_be_valid_json
3. json_schema subset validation if simple
4. required_citations
5. semantic_context_use optional
6. exact label mode with whitespace normalization
7. refusal correctness with better keyword overlap heuristic
8. severity per violation

Return ContractResult:
- status: pass/partial/fail
- score: numeric 0-1
- violations: list
- reasons: list[str]
- severity: low/medium/high

Do not remove existing contract behavior.

Add tests for every contract type.

==================================================
PART 6 — LAZY EMBEDDING MODEL
==================================================

Current scoring/consistency.py loads SentenceTransformer globally at import.

Refactor:
- no model load at import time
- create EmbeddingScorer class
- lazy load only when consistency scoring is called
- allow mock embedding scorer in tests

Add config model name.

==================================================
PART 7 — SEMANTIC CONSISTENCY IMPROVEMENT
==================================================

Improve consistency scoring:
- group outputs by base_id
- compute mean pairwise similarity
- report min/mean/max by group
- identify most inconsistent group
- handle errors/empty outputs

Output:
ConsistencyResult:
- overall_score
- is_brittle
- per_group_scores
- worst_group
- threshold

==================================================
PART 8 — REGRESSION GATE
==================================================

Create:
scoring/regression_gate.py

Compare baseline results vs candidate results.

Detect:
- newly failed contract cases
- severity increases
- consistency score drop
- pass-rate drop
- output format regressions
- allowed-label regressions
- latency increase if available

Output:
RegressionGateResult:
- passed: bool
- regression_count
- improvement_count
- unchanged_count
- high_severity_regressions
- summary
- failing_cases

CLI:
python main.py gate --baseline qa_v1 --candidate qa_v2
or compare result files:
python main.py gate --baseline-file results/results_qa_v1.json --candidate-file results/results_qa_v2.json

Support:
--fail-on-regression

Exit non-zero when gate fails.

==================================================
PART 9 — REPORTING IMPROVEMENT
==================================================

Update brittleness report.

Add:
- executive summary
- contract pass rate
- numeric contract score
- consistency score
- fail rate by variant type
- fail rate by contract type
- severity breakdown
- top damaging variants
- suggested hardening actions
- CI gate status
- limitations

Write:
- results/brittleness_report.md
- results/report_{template_id}.json

==================================================
PART 10 — VERSION DIFF IMPROVEMENT
==================================================

Improve versioning/differ.py.

Include:
- pass/fail changes
- output semantic shift
- contract score delta
- consistency delta
- top regressions
- top improvements
- variant-level diff table
- recommendation:
  - safe_to_promote
  - needs_review
  - block_deploy

==================================================
PART 11 — JUNIT OUTPUT
==================================================

Create:
reporting/junit.py

Write:
results/junit_{template_id}.xml

Each variant should become a testcase.
Failed contract becomes testcase failure.
Errors become testcase error.

This allows GitHub Actions / CI systems to display prompt failures like unit test failures.

==================================================
PART 12 — MOCK RESPONDER SCENARIOS
==================================================

Improve mock responder.

Add deterministic scenario modes:
- stable
- brittle_typo
- prompt_injection_failure
- format_failure
- refusal_failure
- label_drift
- verbose_drift

CLI:
python main.py run --template qa_v1 --provider mock --mock-scenario format_failure

Keep current mock behavior as default.

==================================================
PART 13 — VARIANT GENERATION IMPROVEMENT
==================================================

Improve variants/generate_catalog.py.

Variant types:
- paraphrase
- typo
- casing
- whitespace
- irrelevant_context
- missing_context
- prompt_injection
- long_input
- adversarial_instruction
- multilingual_light
- format_stress

Keep generation deterministic.
Do not use external APIs for variant generation.

Add tests for generated catalog shape.

==================================================
PART 14 — CI
==================================================

Add GitHub Actions:

.github/workflows/ci.yml

Run:
- pip install -r requirements.txt
- pytest -v
- python main.py run-all --use-mock
- python main.py report --template qa_v1
- optionally python main.py gate --baseline qa_v1 --candidate qa_v2 --fail-on-regression

If model download for sentence-transformers is flaky:
- allow tests to use mock embedding scorer
- keep full consistency scoring as optional integration test

==================================================
PART 15 — REQUIREMENTS / PACKAGING
==================================================

Review dependencies.

If requirements.txt exists, ensure it includes:
- click
- PyYAML
- sentence-transformers
- scikit-learn
- numpy
- pytest

OpenAI should be optional if possible.
Consider pyproject.toml with extras:
- core
- llm
- dev

Do not make OpenAI mandatory for mock mode.

==================================================
PART 16 — README UPDATE
==================================================

Update README but keep concise.

Add:
- positioning: prompt regression and behavioral contract testing
- quick start
- behavioral contracts
- variant testing
- CI gate
- JUnit output
- OpenAI provider setup
- mock scenarios
- roadmap
- limitations

Modernize the OpenAI example.
Do not use old openai.ChatCompletion.create style.

==================================================
PART 17 — DOCS
==================================================

Create docs/ROADMAP.md.

Roadmap:
v0: deterministic mock prompt brittleness report
v1: schemas + responder interface + CI outputs
v2: richer behavioral contracts
v3: baseline-vs-candidate regression gates
v4: model/provider matrix
v5: LLM-as-judge contracts
v6: RAG/agent prompt regression
v7: production prompt QA dashboard

Create docs/REFERENCES.md.

Include annotated references/topics:
- prompt engineering as software artifact
- regression testing
- metamorphic testing
- adversarial prompt injection testing
- LLM evaluation
- behavioral contracts
- CI/CD for AI systems
- prompt/version drift
- OpenAI Evals / Promptfoo / DeepEval style tools

For each:
- key idea
- what this repo borrows
- future work

Create docs/INTEGRATIONS.md.

Explain integration with:
- rag-eval-harness
- llm-drift-monitor
- open-ended-task-agent
- lora-finetune-eval

==================================================
PART 18 — TESTS
==================================================

Add pytest tests for:
- template schema validation
- variant schema validation
- fill_template missing placeholder error
- input hash stability
- mock responder scenarios
- contract checks
- semantic consistency with mock embeddings
- regression gate pass/fail
- JUnit output generation
- report generation
- CLI smoke tests using Click CliRunner

Do not require real OpenAI calls in tests.

==================================================
ENGINEERING CONSTRAINTS
==================================================

- Preserve deterministic mock mode.
- No secrets.
- OpenAI optional.
- Keep outputs reproducible.
- Avoid huge dependencies.
- Keep code modular and readable.
- Add type hints.
- Do not overclaim that semantic similarity equals correctness.
- Do not silently pass failed LLM calls.
- Make failures visible and CI-friendly.
- Keep backward compatibility where practical.

==================================================
FINAL COMMANDS TO RUN
==================================================

After implementation, run:

pytest -v
python main.py run-all --use-mock
python main.py report --template qa_v1

If implemented:
python main.py gate --baseline qa_v1 --candidate qa_v2 --fail-on-regression

Then summarize:
- files changed
- new architecture
- contracts added
- CI outputs added
- tests added
- commands run
- remaining TODOs

The strongest positioning is:

Prompts are production artifacts.
This repo tests whether a prompt change is safe to deploy.

That is more impressive than “prompt engineering examples,” and it fits directly with MLOps/LLMOps work.