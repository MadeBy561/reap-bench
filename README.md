# reap-bench

Run NVIDIA's published **GLM-5.2 accuracy axes** against **any OpenAI-compatible chat endpoint** (vLLM, SGLang, …) —
a fast way to measure what a REAP prune / quantization costs vs the full model, without long agentic sweeps.

## Results

Full-model reference is from the `nvidia/GLM-5.2-NVFP4` model card; the **REAP** row is measured *with this harness*.

| Model | GPQA Diamond | SciCode | IFBench | τ²-Bench Telecom |
|---|:-:|:-:|:-:|:-:|
| GLM-5.2 FP8 — full *(NVIDIA ref)* | 89.52 | 49.85 | 74.95 | 97.9 |
| GLM-5.2 NVFP4 — full *(NVIDIA ref)* | 89.39 | 49.04 | 75.81 | 98.25 |
| [**GLM-5.2-Int8Mix-NVFP4-REAP-594B**](https://huggingface.co/madeby561/GLM-5.2-Int8Mix-NVFP4-REAP-594B) · ~22% expert prune | **86.87** | **47.77** | — | — |
| [**GLM-5.2-NVFP4-REAP-504B-term**](https://huggingface.co/madeby561/GLM-5.2-NVFP4-REAP-504B-term) · ~34% expert prune | — | 44.67 | — | — |

REAP-594B GPQA Diamond: **172/198 correct, 0 errors** — within ~2.5 pts of the full model (~97% retention) despite pruning ~22% of the experts.

SciCode (with-background, official `inspect_ai` scorer, subproblem accuracy): **REAP-594B 47.77% (139/291)** — only ~1.3 below full NVFP4 (49.04); **REAP-504B-term 44.67% (130/291)** — ~4.4 below, the cost of the deeper 256→168 prune. Both 65/65 samples, 0 errors (fully-solved problems: 594B 11/65, term 7/65). IFBench / τ²-Bench Telecom pending.

**Intelligence lost vs full NVFP4** (relative % drop — same quant, so this isolates the *prune* cost):

| Benchmark | full NVFP4 | REAP-594B (% lost) | REAP-504B-term (% lost) |
|---|:-:|:-:|:-:|
| GPQA Diamond | 89.39 | 86.87 (**−2.8%**) | — |
| SciCode | 49.04 | 47.77 (**−2.6%**) | 44.67 (**−8.9%**) |

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
