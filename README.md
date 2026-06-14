# Amanda Webb Social Media Content Audit

A hard, multimodal agent-evaluation task built around the Amanda Webb persona. The task asks an agent to review showcase materials against current Instagram posts and Spotify playlists, determine what is ready, identify items that need fixes or must be held, and select the strongest eligible Instagram performer using reach with saves as the tie-breaker.

The task is review-only. A successful agent must gather and reconcile evidence without modifying supplied files or connected account data.

## Task Classification

- **L1 category:** Creative Media
- **L2 category:** Social Media Content Audit
- **Difficulty:** Hard
- **Task type:** Multimodal reconciliation
- **Modalities:** Text, image, audio, and document
- **Required APIs:** Instagram and Spotify
- **Distractor APIs:** LinkedIn, Reddit, and Twitch

## Evaluation Focus

The task evaluates whether an agent can:

- Reconcile local showcase materials with live-style API records.
- Distinguish eligible content from items requiring correction or approval.
- Compare Instagram performance using the specified ranking rule.
- Verify Spotify playlist and track state.
- Produce a short, actionable audit in the Amanda Webb persona.
- Respect the review-only boundary and avoid account mutations.
- Ignore unrelated evidence exposed through distractor services.

## Bundle Structure

```text
sanjeev_amanda_webb
|-- prompt.txt
|-- task.yaml
|-- persona/
|   |-- AGENTS.md
|   |-- MEMORY.md
|   `-- SOUL.md
|-- data/
|   `-- Multimodal task inputs
|-- mock_data/
|   |-- instagram-api/
|   |-- spotify-api/
|   |-- linkedin-api/
|   |-- reddit-api/
|   `-- twitch-api/
|-- rubric.json
|-- test_outputs.py
|-- test_weights.json
|-- golden_steer_flow.md
```

## Grading

The bundle contains two complementary grading layers:

- **Deterministic tests:** 12 weighted tests covering Instagram and Spotify evidence retrieval, expected content state, mutation guards, and distractor-service avoidance.
- **Rubric evaluation:** 23 criteria assessing the quality, completeness, accuracy, concision, and persona alignment of the final response.

Positive deterministic-test weight totals 29. Mutation and distractor penalties total -7. The rubric score totals 42.

## Quality Control

The task has been checked for:

- Prompt, input, and mock-data consistency.
- Ground-truth and value-lock consistency.
- Rubric coverage and scoring balance.
- Deterministic test validity and weight-key bijection.
- Required API coverage and distractor handling.
- Mutation protection for review-only behavior.
- AI-generated image and artifact quality requirements.

The final test-output QC report records **0 findings** and a **PASS** verdict across all 21 defect classes and seven cross-cutting checks.

## Usage

Place the task directory in the evaluation repository's expected input location, preserving its internal structure. The harness should load `prompt.txt`, seed the persona from `persona/`, stage files from `data/`, mount API overrides from `mock_data/`, and evaluate the response with the files under `tests/`.

Do not include generated Python cache directories such as `__pycache__/` or `*.pyc` files in the Git commit.

## Status

**Task generation: Complete**  
**Quality control: Passed**  
**Ready for repository integration: Yes**
