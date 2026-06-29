#!/usr/bin/env python3
"""
GPQA Diamond — run against any OpenAI-compatible chat endpoint (vLLM, SGLang, ...).
NVIDIA GLM-5.2 protocol: temperature 1.0, top_p 0.95, max_new_tokens 100000,
reasoning_effort=max, concurrent. Multiple-choice accuracy. Stdlib only.

  ENDPOINT=http://localhost:8000 MODEL=your-model CONC=4 python3 gpqa_bench.py        # full 198
  ENDPOINT=http://localhost:8000 MODEL=your-model CONC=4 N=8 python3 gpqa_bench.py     # quick smoke

Requires gpqa_diamond.csv (GATED — see README) in this directory.
NVIDIA reference (full GLM-5.2): FP8 89.52 / NVFP4 89.39.
"""
import json, csv, os, re, time, random, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ENDPOINT = os.environ.get("ENDPOINT", os.environ.get("BASE", "http://localhost:8000")).rstrip("/")
MODEL  = os.environ.get("MODEL", "GLM-5.2"); LABEL = os.environ.get("LABEL", "run")
CONC   = int(os.environ.get("CONC", "4"));   MAXTOK = int(os.environ.get("MAXTOK", "100000"))
TEMP   = float(os.environ.get("TEMP", "1.0")); TOPP = float(os.environ.get("TOPP", "0.95"))
EFFORT = os.environ.get("EFFORT", "max");    N = int(os.environ.get("N", "0"))
API_KEY = os.environ.get("API_KEY", "")
HERE = os.path.dirname(os.path.abspath(__file__))
CSV  = os.environ.get("CSV", os.path.join(HERE, "gpqa_diamond.csv"))
L = "ABCD"

if not os.path.exists(CSV):
    raise SystemExit(f"missing {CSV}\nDownload gpqa_diamond.csv from the gated dataset Idavidrein/gpqa (see README).")
rows = list(csv.DictReader(open(CSV)))
if N: rows = rows[:N]

def build(row, idx):
    opts = [row["Correct Answer"].strip(), row["Incorrect Answer 1"].strip(),
            row["Incorrect Answer 2"].strip(), row["Incorrect Answer 3"].strip()]
    o = [0, 1, 2, 3]; random.Random(idx).shuffle(o)        # deterministic per-question shuffle
    sh = [opts[i] for i in o]; gold = L[o.index(0)]
    p = ("Answer the following multiple choice question. The last line of your response must be exactly "
         "'Answer: $LETTER' where $LETTER is one of A, B, C, D. Think step by step first.\n\n"
         + row["Question"].strip() + "\n\n" + "\n".join(f"{L[i]}) {sh[i]}" for i in range(4)))
    return p, gold

def extract(t):
    if "</think>" in t: t = t.split("</think>", 1)[1]
    m = re.findall(r"[Aa]nswer:?\s*\(?\s*([ABCD])\b", t)
    if m: return m[-1].upper()
    m = re.findall(r"\b([ABCD])\b", t[-300:])
    return m[-1].upper() if m else None

def ask(p):
    b = {"model": MODEL, "messages": [{"role": "user", "content": p}],
         "temperature": TEMP, "top_p": TOPP, "max_tokens": MAXTOK}
    if EFFORT: b["chat_template_kwargs"] = {"reasoning_effort": EFFORT}   # GLM-style; set EFFORT="" to omit
    h = {"Content-Type": "application/json"}
    if API_KEY: h["Authorization"] = f"Bearer {API_KEY}"
    r = urllib.request.Request(ENDPOINT + "/v1/chat/completions", data=json.dumps(b).encode(), headers=h)
    d = json.loads(urllib.request.urlopen(r, timeout=7200).read()); ch = d["choices"][0]
    return (ch["message"].get("content") or ""), ch.get("finish_reason"), (d.get("usage", {}) or {})

def run_one(i):
    p, gold = build(rows[i], i); t = time.time()
    try:
        c, fin, u = ask(p); pr = extract(c)
        return {"idx": i, "gold": gold, "pred": pr, "ok": pr == gold, "finish": fin,
                "ctoks": u.get("completion_tokens"), "sec": round(time.time() - t, 1)}
    except Exception as e:
        return {"idx": i, "gold": gold, "pred": None, "ok": False, "error": repr(e)[:160], "sec": round(time.time() - t, 1)}

print(f"GPQA Diamond | {len(rows)} Q | model={MODEL} conc={CONC} effort={EFFORT} temp={TEMP} maxtok={MAXTOK}", flush=True)
res = []; t0 = time.time()
with ThreadPoolExecutor(max_workers=CONC) as ex:
    futs = [ex.submit(run_one, i) for i in range(len(rows))]; done = 0
    for f in as_completed(futs):
        r = f.result(); res.append(r); done += 1
        acc = sum(x["ok"] for x in res) / len(res)
        print(f"[{done}/{len(rows)}] q{r['idx']} {r['gold']}/{r.get('pred')} {'OK' if r['ok'] else 'x'} acc={acc:.3f}", flush=True)
res.sort(key=lambda x: x["idx"]); acc = sum(x["ok"] for x in res) / len(res)
out = {"label": LABEL, "model": MODEL, "n": len(res), "accuracy": round(acc, 4),
       "correct": sum(x["ok"] for x in res), "errors": sum(1 for x in res if x.get("error")),
       "total_sec": round(time.time() - t0, 1), "results": res}
json.dump(out, open(os.path.join(HERE, f"gpqa_{LABEL}.json"), "w"), indent=2)
print(f"\n=== GPQA Diamond {LABEL}: accuracy={acc:.4f} ({out['correct']}/{len(res)}), errors={out['errors']} ===", flush=True)
print("NVIDIA reference (full GLM-5.2): FP8 89.52 / NVFP4 89.39", flush=True)
