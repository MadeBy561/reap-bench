# reap-bench

Measure what a REAP prune / quantization costs vs the full model — against **any OpenAI-compatible chat
endpoint** (vLLM, SGLang, …). NVIDIA's published **accuracy axes** (GPQA / SciCode / IFBench / τ²) for a fast
read, plus **Terminal-Bench 2.1** — the agentic coding eval the pruned models are actually built for.

## Results

Full-model reference is from the `nvidia/GLM-5.2-NVFP4` model card; the **REAP** row is measured *with this harness*.

| Model | GPQA Diamond | SciCode | IFBench | τ²-Bench Telecom | Terminal-Bench 2.1 |
|---|:-:|:-:|:-:|:-:|:-:|
| GLM-5.2 FP8 — full *(NVIDIA ref)* | 89.52 | 49.85 | 74.95 | 97.9 | — |
| GLM-5.2 NVFP4 — full *(NVIDIA ref)* | 89.39 | 49.04 | 75.81 | 98.25 | — |
| [**GLM-5.2-Int8Mix-NVFP4-REAP-594B**](https://huggingface.co/madeby561/GLM-5.2-Int8Mix-NVFP4-REAP-594B) · ~22% expert prune | **86.87** | **47.77** | — | — | — |
| ↳ *intelligence lost vs full NVFP4* | **−2.8%** | **−2.6%** | — | — | — |
| [**GLM-5.2-NVFP4-REAP-504B-term**](https://huggingface.co/madeby561/GLM-5.2-NVFP4-REAP-504B-term) · ~34% expert prune | — | 44.67 | — | — | — |
| ↳ *intelligence lost vs full NVFP4* | — | **−8.9%** | — | — | — |
| [0xSero/GLM-5.2-504B](https://huggingface.co/0xSero/GLM-5.2-504B) · prior-art NVFP4 REAP | 68.18 † | — | — | — | — |
| ↳ *intelligence lost vs full NVFP4* | **−23.7%** | — | — | — | — |

REAP-594B GPQA Diamond: **172/198 correct, 0 errors** — within ~2.5 pts of full NVFP4 (~97% retention) despite pruning ~22% of the experts. SciCode (with-background, subproblem accuracy): **REAP-594B 47.77% (139/291)**, **REAP-504B-term 44.67% (130/291)** — both 65/65 samples, 0 errors (fully-solved problems: 594B 11/65, term 7/65). **Intelligence lost** = relative drop vs full NVFP4 (same quant → isolates the prune): the deeper 256→168 prune (term, −8.9% SciCode) costs ~3× the 256→200 prune (594B, −2.6%). IFBench / τ²-Bench Telecom pending.

The prior-art **0xSero/GLM-5.2-504B** REAP scores **68.18% (135/198, 0 errors)** on the same harness/protocol. **†** Of its 198 questions, **35 (17.7%) hit the 100k-token cap (`length`) without producing an answer** — vs only **10/198 (5.1%) for REAP-594B** — so a large part of the gap is non-termination (the model thinking past the budget), not pure reasoning. The score is legitimate under the standard protocol; the footnote just flags that the termination axis is doing a lot of the work here.

Protocol: temperature 1.0, top_p 0.95; GPQA Diamond `max_new_tokens=100000`, others `64000`.

## Status
- ✅ **GPQA Diamond** — ready, self-contained (`gpqa/`)
- ✅ **SciCode** — ready via the official harness (`scicode/`)
- ✅ **Terminal-Bench 2.1** — config + methodology ready via the [harbor](https://github.com/laude-institute/harbor) harness (`terminal-bench/`); REAP runs pending
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
See [`gpqa/README.md`](gpqa/README.md), [`scicode/README.md`](scicode/README.md), and
[`terminal-bench/README.md`](terminal-bench/README.md) for details + env knobs.

## Notes
- NVIDIA didn't publish their exact sub-settings (e.g. SciCode with/without background, which IFBench metric),
  so results are **legitimate but only loosely comparable** to their table — match the settings noted in each subfolder.
- Concurrency never changes a score (each item is independent) — it's purely throughput.

## License
MIT (this repo's orchestration code). The benchmark **datasets and official harnesses keep their own licenses** —
GPQA (`Idavidrein/gpqa`), SciCode ([scicode-bench/SciCode](https://github.com/scicode-bench/SciCode)),
Terminal-Bench ([harbor](https://github.com/laude-institute/harbor) + the `terminal-bench/terminal-bench-2-1` dataset) — see each subfolder.
