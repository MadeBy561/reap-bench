# reap-bench

Run NVIDIA's published **GLM-5.2 accuracy axes** against **any OpenAI-compatible chat endpoint** (vLLM, SGLang, …) —
a fast way to measure what a REAP prune / quantization costs vs the full model, without long agentic sweeps.

Reference numbers (full GLM-5.2, from the `nvidia/GLM-5.2-NVFP4` model card):

| Precision | GPQA Diamond | SciCode | IFBench | τ²-Bench Telecom |
|---|:-:|:-:|:-:|:-:|
| GLM-5.2 FP8 (baseline) | 89.52 | 49.85 | 74.95 | 97.9 |
| GLM-5.2 NVFP4 | 89.39 | 49.04 | 75.81 | 98.25 |

Protocol: temperature 1.0, top_p 0.95; GPQA Diamond `max_new_tokens=100000`, others `64000`.

## Status
- ✅ **GPQA Diamond** — ready, self-contained (`gpqa/`)
- ✅ **SciCode** — ready via the official harness (`scicode/`)
- ⏳ IFBench, τ²-Bench Telecom — coming

## Quickstart (GPQA Diamond)
1. Serve your model on an OpenAI-compatible endpoint (e.g. `vllm serve … --port 8000`).
2. Get the dataset — GPQA is **gated**: accept terms at https://huggingface.co/datasets/Idavidrein/gpqa ,
   then place `gpqa_diamond.csv` in `gpqa/`.
3. Run:
   ```bash
   cd gpqa
   ENDPOINT=http://localhost:8000 MODEL=your-model-name CONC=4 python3 gpqa_bench.py
   ```
See [`gpqa/README.md`](gpqa/README.md) and [`scicode/README.md`](scicode/README.md) for details + env knobs.

## Notes
- NVIDIA didn't publish their exact sub-settings (e.g. SciCode with/without background, which IFBench metric),
  so results are **legitimate but only loosely comparable** to their table — match the settings noted in each subfolder.
- Concurrency never changes a score (each item is independent) — it's purely throughput.

## License
MIT (this repo's orchestration code). The benchmark **datasets and official harnesses keep their own licenses** —
GPQA (`Idavidrein/gpqa`), SciCode ([scicode-bench/SciCode](https://github.com/scicode-bench/SciCode)) — see each subfolder.
