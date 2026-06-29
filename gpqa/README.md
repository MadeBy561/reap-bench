# GPQA Diamond

`gpqa_bench.py` — concurrent multiple-choice eval against any OpenAI-compatible endpoint. Stdlib only, no install.

## Dataset (gated)
GPQA is gated to prevent contamination. Accept the terms at
https://huggingface.co/datasets/Idavidrein/gpqa , download **`gpqa_diamond.csv`** (the Diamond split, 198 questions),
and place it in this folder as `gpqa_diamond.csv`.

## Run
```bash
ENDPOINT=http://localhost:8000 MODEL=your-model CONC=4 python3 gpqa_bench.py      # full 198
ENDPOINT=http://localhost:8000 MODEL=your-model CONC=4 N=8 python3 gpqa_bench.py   # smoke
```
Writes `gpqa_<LABEL>.json` (accuracy + per-question gold/pred/finish/tokens).

**Env:** `ENDPOINT` (default `http://localhost:8000`), `MODEL`, `LABEL`, `CONC` (concurrency = wall-clock only,
no effect on score), `MAXTOK` (100000), `TEMP` (1.0), `TOPP` (0.95), `EFFORT` (`max`; set empty to omit
`reasoning_effort` for non-reasoning models), `API_KEY`, `N` (limit, 0=all), `CSV`.

Protocol matches NVIDIA's GLM-5.2 card: temp 1.0, top_p 0.95, max_new_tokens 100000, reasoning_effort=max.
Per-question option order is shuffled deterministically (`seed = index`) → reproducible. Answer extraction:
last `Answer: X` after `</think>`, fallback = last bare letter near the end.

NVIDIA reference (full GLM-5.2): **FP8 89.52 / NVFP4 89.39.**
