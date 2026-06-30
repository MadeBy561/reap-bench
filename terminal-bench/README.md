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
   harbor run -c leaderboard.glm52-reap.yaml --timeout-multiplier 6 -o jobs/<model>
   ```
Concurrency (`n_concurrent_trials`) is wall-clock only — never affects the score. Big tasks pull large
container images on first run; `--timeout-multiplier 6` keeps the per-task agent timeout near AA's 2h floor
(see Methodology). Full 89 × 3 repeats at `max` effort is a long run — expect many hours / overnight.

## Methodology (matches Artificial Analysis)
Mirrors the [AA TerminalBench-v2-1 protocol](https://artificialanalysis.ai/evaluations/terminalbench-v2-1):
full 89 tasks, Terminus-2, **pass@1 averaged over 3 repeats**.
- **Agent: Terminus-2** (the harness's reference agent), `temperature 1`.
- **Reasoning effort = each model's top tier.** AA runs every model at its top tier
  (Claude `max`, GPT `xhigh`); GLM-5.2 exposes `high`/`max`, so we use **`max`** — the faithful assumption.
- **3 repeats, pass@1** (`n_attempts: 3`) — each task is run 3 times; harbor's `compute_pass_at_k`
  reports **pass@1**, which is exactly AA's "pass@1 averaged over 3 repeats." (Read the **pass@1** stat,
  not pass@3.) Use `n_attempts: 1` + `task_names:` for a quick head-to-head smoke on a subset.
- **≤250 episodes** (`max_turns: 250`) — AA's episode cap (an "episode" = one review-state-then-act turn).
- **Output cap lifted** (`max_output_tokens: 120000`) — `max` effort can think ~70k tokens before acting;
  a 40k cap silently truncates turns and tanks the score.
- **Per-task agent timeout = 2h** (AA: 7,200 s, or the task's own if longer). harbor expresses timeouts as a
  **multiplier on each task's own** timeout (`--timeout-multiplier`), not an absolute floor — there's no single
  `max(7200, own)` knob. Use a multiplier large enough that every task clears ~2h (`--timeout-multiplier 6`
  is a good default for this set); AA notes these limits "predominantly limit stuck loops," so the floor
  rarely binds on a healthy run.
- **Local Docker** instead of AA's hosted E2B sandbox — the *tasks* are identical (same pinned sha),
  only the execution host differs.

## Resuming an interrupted run
A full 89 × 3 run takes hours — if it dies (sleep, crash, Ctrl-C), **re-run the identical command with the
same `-o <job_dir>`** and harbor resumes. It detects the existing job, **keeps every completed trial**
(skips it — pass *or* fail), and re-runs only the unfinished ones. Caveats:
- **Trial-level, not episode-level.** A trial = one task × one repeat. A task that was mid-episode when killed
  has no `result.json` → its dir is wiped and it restarts from episode 0 (no within-task checkpoint).
- **Config must be byte-identical** — change effort/temp/`n_attempts`/task set and it refuses
  (`cannot be resumed with a different config`). Use a new `-o` dir for a different config.
- A completed-but-**failed** trial counts as done and is **not** re-run on resume (that's the point of the
  3 repeats + `retry.max_retries`, which handle flakes *during* the live run).

## litellm gotcha (important)
For `model_name: openai/<id>`, litellm **ignores** `OPENAI_API_BASE`/`OPENAI_BASE_URL` env and hits
`api.openai.com`. You **must** also set `api_base:` inside `kwargs:` (see the template). Symptom if you miss
it: 401s / "model not found" against OpenAI instead of your endpoint.

## Results
See the top-level [README](../README.md) for the unified REAP results table. Terminal-Bench rows
(REAP-594B / 504B-term / 0xSero) land here as they finish.
