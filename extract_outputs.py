#!/usr/bin/env python3
"""Collect the text outputs of the executed notebooks into one file.

Usage
    python extract_outputs.py                       # every *.ipynb in this folder
    python extract_outputs.py a.ipynb b.ipynb ...   # these notebooks
    python extract_outputs.py --run [notebooks]     # execute each first, in its own folder
    python extract_outputs.py -o outcomes.txt       # output file (default: outcomes.txt)

The file starts with the PAPER VALUES block of every notebook (every number quoted in
the paper), then each notebook's outputs cell by cell under its section headings.
Images are replaced by "[figure]", long tables are kept whole, and errors are
reported with their traceback.
"""
import argparse, json, re, sys, time
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def run_notebook(path, timeout):
    import nbformat
    from nbclient import NotebookClient
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(nb, timeout=timeout, kernel_name="python3",
                            resources={"metadata": {"path": str(Path(path).parent)}},
                            allow_errors=True)
    t = time.time()
    client.execute()
    nbformat.write(nb, path)
    return time.time() - t


def text_of(output):
    kind = output.get("output_type")
    if kind == "stream":
        return "".join(output.get("text", ""))
    if kind in ("execute_result", "display_data"):
        data = output.get("data", {})
        if "image/png" in data or "image/svg+xml" in data:
            return "[figure]"
        if "text/plain" in data:
            return "".join(data["text/plain"])
        return ""
    if kind == "error":
        tb = "\n".join(output.get("traceback", []))
        return f"!!! ERROR {output.get('ename')}: {output.get('evalue')}\n{ANSI.sub('', tb)}"
    return ""


def extract(path):
    nb = json.loads(Path(path).read_text(encoding="utf-8"))
    values, body, errors = [], [], []
    executed = 0
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", ""))
        if cell["cell_type"] == "markdown":
            heads = [l for l in src.splitlines() if l.startswith("#")]
            if heads:
                body.append("\n" + "\n".join(heads))
            continue
        if cell.get("execution_count") is not None:
            executed += 1
        outs = [text_of(o) for o in cell.get("outputs", [])]
        outs = [o for o in outs if o.strip()]
        if not outs:
            continue
        txt = ANSI.sub("", "\n".join(outs)).rstrip()
        first = next((l for l in src.splitlines() if l.strip() and not l.strip().startswith("#")), "")
        body.append(f"--- cell {i}: {first[:70]}\n{txt}")
        if "!!! ERROR" in txt:
            errors.append(i)
        m = re.search(r"===== PAPER VALUES: .*?=====\n.*?===== END PAPER VALUES: .*?=====", txt, re.S)
        if m:
            values.append(m.group(0))
    head = (f"##### {Path(path).name}   ({executed} code cells executed"
            + (f"; ERRORS in cells {errors}" if errors else "") + ")")
    return head, values, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notebooks", nargs="*")
    ap.add_argument("-o", "--out", default="outcomes.txt")
    ap.add_argument("--run", action="store_true", help="execute the notebooks first")
    ap.add_argument("--timeout", type=int, default=7200)
    a = ap.parse_args()
    paths = [Path(p) for p in a.notebooks] or sorted(
        p for p in Path(".").glob("*.ipynb") if not p.name.startswith("."))
    if not paths:
        sys.exit("no notebooks found")
    if a.run:
        for p in paths:
            print(f"running {p} ...", flush=True)
            print(f"   done in {run_notebook(p, a.timeout):.0f} s", flush=True)
    heads, allvals, bodies = [], [], []
    for p in paths:
        h, v, b = extract(p)
        heads.append(h)
        allvals.append((h, v))
        bodies.append((h, b))
    lines = ["OUTCOMES of the analysis notebooks", ""] + heads + ["", "=" * 78,
             "PAPER VALUES", "=" * 78]
    for h, v in allvals:
        lines += ["", h] + (v if v else ["(no PAPER VALUES block found)"])
    lines += ["", "=" * 78, "FULL OUTPUTS", "=" * 78]
    for h, b in bodies:
        lines += ["", "#" * 78, h, "#" * 78] + b
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: {len(paths)} notebooks, "
          f"{sum(len(v) for _, v in allvals)} PAPER VALUES blocks")


if __name__ == "__main__":
    main()
