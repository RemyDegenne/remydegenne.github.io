#!/usr/bin/env python3
r"""Static consistency checks for the blueprint sources.

Checks, over blueprint/src/content.tex and blueprint/src/chapters/*.tex:
  * every \begin{env} has a matching \end{env} (per file, stack-based);
  * labels are unique across files;
  * every label mentioned in \uses{...}, \proves{...}, \ref{...} is defined somewhere;
  * every chapter file that content.tex \inputs exists, and vice versa;
  * every \cite key exists in bib.bib.
Exit status 1 if any problem is found.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "blueprint" / "src"
files = [ROOT / "content.tex"] + sorted((ROOT / "chapters").glob("*.tex"))

label_re = re.compile(r"\\label\{([^}]*)\}")
uses_re = re.compile(r"\\(?:uses|proves)\{([^}]*)\}")
ref_re = re.compile(r"\\(?:ref|eqref|autoref|cref)\{([^}]*)\}")
cite_re = re.compile(r"\\cite[tp]?\{([^}]*)\}")
env_re = re.compile(r"\\(begin|end)\{([^}]*)\}")
input_re = re.compile(r"\\input\{([^}]*)\}")

problems = []
labels = {}
used = {}
cites = set()

for f in files:
    text = f.read_text(encoding="utf-8")
    # strip comments
    lines = [re.sub(r"(?<!\\)%.*", "", ln) for ln in text.splitlines()]
    text_nc = "\n".join(lines)
    # environments
    stack = []
    for i, ln in enumerate(lines, 1):
        for m in env_re.finditer(ln):
            kind, env = m.group(1), m.group(2)
            if kind == "begin":
                stack.append((env, i))
            else:
                if not stack:
                    problems.append(f"{f.name}:{i}: \\end{{{env}}} without begin")
                elif stack[-1][0] != env:
                    problems.append(
                        f"{f.name}:{i}: \\end{{{env}}} closes \\begin{{{stack[-1][0]}}} (line {stack[-1][1]})")
                    stack.pop()
                else:
                    stack.pop()
    for env, i in stack:
        problems.append(f"{f.name}:{i}: unclosed \\begin{{{env}}}")
    # labels
    for i, ln in enumerate(lines, 1):
        for m in label_re.finditer(ln):
            lab = m.group(1).strip()
            if lab in labels:
                problems.append(f"{f.name}:{i}: duplicate label {lab} (also in {labels[lab]})")
            labels[lab] = f"{f.name}:{i}"
        for m in uses_re.finditer(ln):
            for lab in m.group(1).split(","):
                lab = lab.strip()
                if lab:
                    used.setdefault(lab, []).append(f"{f.name}:{i}")
        for m in ref_re.finditer(ln):
            for lab in m.group(1).split(","):
                lab = lab.strip()
                if lab:
                    used.setdefault(lab, []).append(f"{f.name}:{i}")
        for m in cite_re.finditer(ln):
            for key in m.group(1).split(","):
                cites.add(key.strip())
    if f.name == "content.tex":
        inputs = [ROOT / (p if p.endswith(".tex") else p + ".tex") for p in input_re.findall(text_nc)]
        for p in inputs:
            if not p.exists():
                problems.append(f"content.tex inputs missing file {p.relative_to(ROOT)}")
        chap_files = set(p.name for p in inputs)
        for g in (ROOT / "chapters").glob("*.tex"):
            if g.name not in chap_files:
                problems.append(f"chapters/{g.name} is not \\input by content.tex")

for lab, where in used.items():
    if lab not in labels:
        problems.append(f"undefined label {lab} used at {where[0]}" + (f" (+{len(where)-1} more)" if len(where) > 1 else ""))

bib = (ROOT / "bib.bib").read_text(encoding="utf-8") if (ROOT / "bib.bib").exists() else ""
bibkeys = set(re.findall(r"@\w+\{([^,\s]+)\s*,", bib))
for key in sorted(cites):
    if key not in bibkeys:
        problems.append(f"unknown bib key {key}")

print(f"{len(files)} files, {len(labels)} labels, {len(used)} referenced labels, {len(cites)} cite keys")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  " + p)
    sys.exit(1)
print("OK")
