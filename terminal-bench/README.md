# Terminal-Bench 2.1

Agentic coding/CLI benchmark — 89 hard, real container tasks (debug async code, recover a corrupted
git repo, crack a hash, fix a vuln…). This is the eval behind the
[Artificial Analysis TerminalBench-v2-1 leaderboard](https://artificialanalysis.ai/evaluations/terminalbench-v2-1)
and the [official tbench.ai leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.1).

Unlike GPQA/SciCode (single-shot accuracy), Terminal-Bench runs a full **agent** (Terminus-2) in a Docker
container against your model's endpoint — so it measures *code output quality + tool use*, which is the axis
the heavily-pruned REAPs are actually built for and where narrow accuracy benches (SciCode) undersell them.

The **harness** ([harbor](https://github.com/laude-institute/harbor)) and the **dataset**
(`terminal-bench/terminal-bench-2-1`, pinned by sha) are third-party — install/reference them, don't vendor
them here. This folder is just the **endpoint config + methodology** to point harbor at a REAP served on an
OpenAI-compatible endpoint (vLLM/SGLang), matched to the leaderboard settings.

## Setup
```bash
uv tool install harbor          # or: pip install harbor
# Docker must be running (each task spins up a container).
```
The 2.1 dataset auto-pulls from Harbor Hub on first run (pinned by the `ref:` sha in the config).

## Run
1. Serve your model on an OpenAI-compatible endpoint (e.g. vLLM `--port 5001`, model id `GLM-5.2`).
2. Copy `leaderboard.template.yaml`, set your endpoint in the three `REPLACE-ENDPOINT` spots
   (and the model id if it isn't `GLM-5.2`).
3. ```bash
   export OPENAI_API_KEY=dummy
   harbor run -c leaderboard.glm52-reap.yaml --timeout-multiplier 10 -o jobs/<model>
   ```
Concurrency (`n_concurrent_trials`) is wall-clock only — never affects the score. Big tasks pull large
container images on first run; `--timeout-multiplier 10` keeps slow local boxes from timing out the agent.

## Methodology (matches the leaderboard)
- **Agent: Terminus-2** (the harness's reference agent), `temperature 1`.
- **Reasoning effort = each model's top tier.** The leaderboard runs every model at its top tier
  (Claude `max`, GPT `xhigh`); GLM-5.2 exposes `high`/`max`, so we use **`max`** — the faithful assumption.
- **5 attempts/task** (`n_attempts: 5`) — the leaderboard's pass methodology; the headline number is over 5.
  Use `n_attempts: 1` + `task_names:` for a quick head-to-head smoke on a subset.
- **Output cap lifted** (`max_output_tokens: 120000`) — `max` effort can think ~70k tokens before acting;
  a 40k cap silently truncates turns and tanks the score.
- **Local Docker** instead of the leaderboard's hosted runner — the *tasks* are identical (same pinned sha),
  only the execution host differs.

## litellm gotcha (important)
For `model_name: openai/<id>`, litellm **ignores** `OPENAI_API_BASE`/`OPENAI_BASE_URL` env and hits
`api.openai.com`. You **must** also set `api_base:` inside `kwargs:` (see the template). Symptom if you miss
it: 401s / "model not found" against OpenAI instead of your endpoint.

## Results
See the top-level [README](../README.md) for the unified REAP results table. Terminal-Bench rows
(REAP-594B / 504B-term / 0xSero) land here as they finish.
