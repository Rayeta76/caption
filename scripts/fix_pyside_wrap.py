from pathlib import Path

p = Path(__file__).resolve().parents[1] / "src/gui/database_gui_pyside.py"
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
start = next(i for i, line in enumerate(lines) if line.startswith("class DatabaseManagerAppPyside"))
header = lines[:start]
body = lines[start:]
if header and header[-1].strip() == "if PYSIDE6_AVAILABLE:":
    print("Already wrapped")
    raise SystemExit(0)
out = header + ["\nif PYSIDE6_AVAILABLE:\n"] + ["    " + ln for ln in body]
p.write_text("".join(out), encoding="utf-8")
print("Wrapped", len(body), "lines")
