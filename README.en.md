# Shot Transition Skills

> A publicly shared video-editing methodology, distilled into **6 executable agent skills** —
> plus a quantitative toolchain that **verifies claims on the exported cut**, not on the source footage.
>
> Not a "here's the theory" tutorial. This is an engineering artifact with real projects and measured data behind it.

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Content: CC BY 4.0](https://img.shields.io/badge/content-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT.md)
[![Skills](https://img.shields.io/badge/skills-6-brightgreen.svg)](skills/)

> 中文版见 [README.md](README.md)

---

## Results first

The case is a **real editing project**. The cut and the measured data ship with the repo.

### Case 01 · Family outing, 17s widescreen

[![Case 01 preview](cases/01-shot-transition-17s/shots/preview-7shots.jpg)](cases/01-shot-transition-17s/README.md)

`7 shots / 17.02s / 3840×2160 / 60fps`

A full pass through all 6 skills: the audit found **2 violations** (opposite direction within the
same scene; monotonous pacing) → fixed → re-verified.

[▶ Watch](cases/01-shot-transition-17s/demo-720p.mp4) · [Case details](cases/01-shot-transition-17s/README.md)

---

## The core claim: conclusions must come from the final artifact

The case 01 audit did not stop at "the source footage looks fine" — it ran optical-flow direction
analysis on the **exported cut** and checked it against all 6 skills. That surfaced **2 real
violations** (opposite direction inside one scene; monotonous pacing in the active shots) which
eyeballing would have missed. Only after the fix and a re-measure did both checks actually pass.

So this repo has one iron rule:

> **Any "matches / consistent / passes" conclusion must be recomputed on the exported cut.**
> Proxy metrics (source sampling windows, low-res proxies, eyeballing thumbnails) are for
> **shot selection only** — never for drawing conclusions.

It is not a slogan: every acceptance script in `tools/` reads the **exported file**, and every number
in the case reports states how it was measured.

---

## The 6 skills

Each skill follows a **R-I-C-E four-part skeleton** and ships `SKILL.md` + `test-prompts.json` + `test-results.md`.

| Skill | What it solves |
|---|---|
| [`shot-composition-spatial-rules`](skills/shot-composition-spatial-rules/SKILL.md) | Spatial rules: 30° rule / 180° rule / crossing the line |
| [`visual-variation-judgment`](skills/visual-variation-judgment/SKILL.md) | Visual variation: motion-to-motion, static-to-static |
| [`transition-matching-dual-dimension`](skills/transition-matching-dual-dimension/SKILL.md) | Transition matching on two axes: speed + direction |
| [`shot-duration-decision`](skills/shot-duration-decision/SKILL.md) | Shot duration: a three-layer framework |
| [`momentum-receive-cutting`](skills/momentum-receive-cutting/SKILL.md) | Cutting on momentum: which frame to cut on |
| [`cut-trace-dual-strategy`](skills/cut-trace-dual-strategy/SKILL.md) | Cut-trace strategy: hide the cut vs. use it (meta-strategy) |

**How they relate**: `cut-trace-dual-strategy` is the entry meta-strategy — it decides whether to
*hide* the cut or *lean into* it. The other five apply within that route.
Full relationship graph: [`docs/INDEX.md`](docs/INDEX.md).

> Methodology overview → [`docs/METHOD.md`](docs/METHOD.md) · Glossary → [`docs/GLOSSARY.md`](docs/GLOSSARY.md)
> (Chinese) · Long-form digest → [`docs/DIGEST.md`](docs/DIGEST.md)

---

## Toolchain

Scripts that actually ran on the case, covering selection → render → acceptance.

```bash
# Shot selection
python tools/scan_profile.py  <source.mov>        # full-source 6fps optical-flow scan
python tools/select_shots.py                      # hard-constraint DP selection

# Render (frame/sample-exact trims + 8ms audio fades at every join)
.\tools\render_hardcut.ps1 -Source <src> -Out <out.mp4> `
                           -Starts 3.0,67.0,... -Durations 7,4,3,3,3,6,7

# Acceptance (all read the exported cut directly)
python tools/measure_cut.py       <final.mp4>     # per-shot speed delta
python tools/measure_boundary.py  <final.mp4>     # direction on both sides of each cut
python tools/cut_profile.py       <final.mp4>     # hard cut vs. dissolve
python tools/cut_diff.py          <final.mp4>     # jump-cut risk
python tools/audio_cut_check.py   <final.mp4>     # audio clicks at cuts
python tools/verify_delivery.py   <final.mp4> <source.mov>   # full spec check
```

Requires FFmpeg + Python (numpy, opencv-python). Usage and pass/fail thresholds: [`tools/README.md`](tools/README.md).

---

## Quick start

### Use the skills

Copy the directories under `skills/` into your agent's skills directory:

```bash
cp -r skills/* <your-agent-skills-dir>/
```

### Reproduce the case

1. Set up FFmpeg and the Python deps per [`tools/README.md`](tools/README.md)
2. `scan_profile.py` → `select_shots.py` → `render_hardcut.ps1`
3. Re-run the six acceptance scripts and compare against the measured tables in the case report

---

## Repository layout

```
.
├── README.md                  # Chinese (primary)
├── README.en.md               # this file
├── LICENSE                    # code: MIT
├── LICENSE-CONTENT.md         # content: CC BY 4.0
├── ATTRIBUTION.md             # provenance & licensing (important)
├── CONTRIBUTING.md            # includes the iron rule
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── skills/                    # the 6 skills (canonical versions)
├── docs/                      # methodology / glossary / index / digest
├── cases/                     # real case (demo cut + reports + measured data)
├── tools/                     # reproducible acceptance scripts
└── tutorial/                  # shot-by-shot tutorial for the 17s cut (HTML, Chinese)
```

---

## License & attribution

Dual-licensed:

| Scope | License |
|---|---|
| Code (`tools/` — `*.py` / `*.ps1` / `*.json`) | [MIT](LICENSE) |
| Docs & content (`skills/` / `docs/` / `cases/` / `tutorial/`) | [CC BY 4.0](LICENSE-CONTENT.md) |

**Methodology source**: the 6 skills are a structured, engineered distillation of an editing
methodology shared publicly by **老登的视频日记** (Bilibili). This project is not affiliated with,
nor an official version by, the original author; all methodology IP belongs to them.
**For copyright reasons this repo does not include the third-party source video, audio, or transcript** —
only provenance and timestamps. See [`ATTRIBUTION.md`](ATTRIBUTION.md).

**Case footage**: the case uses the author's own footage. The 4K master is too large and is
**not distributed** with the repo; only the 720p demo cut lives here.

---

## Contributing

New skills, cases and tools are welcome. **Read the iron rule in [`CONTRIBUTING.md`](CONTRIBUTING.md) first** —
we don't accept "looks right" conclusions.