# SciCode

SciCode generates scientific code and **executes it against gold test cases**, so it's run via the official
harness (don't reinvent the scorer). This folder is setup notes only.

## Setup
```bash
git clone https://github.com/scicode-bench/SciCode.git
cd SciCode && pip install -e .
# Download the numeric test data (gold outputs) and save as eval/data/test_data.h5,
# from the SciCode authors' Google Drive (linked in their README):
#   https://drive.google.com/drive/folders/1W5GZW6_bdiDAiipuFMqdUhvUaHIj6-pR
```
The problem set auto-downloads from `SciCode1/SciCode` on first run.

## Run (against your endpoint)
```bash
cd eval/inspect_ai
export OPENAI_BASE_URL=http://localhost:8000/v1
export OPENAI_API_KEY=dummy
inspect eval scicode.py --model openai/your-model \
    -T with_background=true --max-connections 4 \
    --temperature 1.0 --top-p 0.95 --max-tokens 64000
```
- `with_background=true` matches NVIDIA's setting — their **49.85** is the with-background **subproblem** accuracy.
- NVIDIA reference (full GLM-5.2): **FP8 49.85 / NVFP4 49.04** (subproblem).
- Heavy run: 338 subproblems × generation × local code execution — budget hours; verify the exact inspect flags
  against `eval/inspect_ai/README.md` (its CLI shifts between versions).

## Results (subproblem accuracy — 65 problems / 291 subproblems, with-background)

| Model | subproblem | main-problem (fully solved) | run |
|---|:-:|:-:|---|
| [REAP-594B](https://huggingface.co/madeby561/GLM-5.2-Int8Mix-NVFP4-REAP-594B) (200 experts) | **47.77%** (139/291) | 16.92% (11/65) | 65/65, 0 errors |
| [REAP-504B-term](https://huggingface.co/madeby561/GLM-5.2-NVFP4-REAP-504B-term) (168 experts) | **44.67%** (130/291) | 10.77% (7/65) | 65/65, 0 errors |
| full GLM-5.2 NVFP4 / FP8 *(NVIDIA ref)* | 49.04 / 49.85 | — | — |

REAP-594B lands ~1.3 pts under full NVFP4; the deeper-pruned 504B-term ~4.4 under (the cost of 256→168 vs 256→200 experts). Settings: `with_background=true`, temperature 1.0, top_p 0.95, max_tokens 64000.
