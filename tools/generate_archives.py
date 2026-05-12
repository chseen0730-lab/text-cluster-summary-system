from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def _strip_vue_style_blocks(text: str) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    i = 0
    n = len(t)
    while i < n:
        s = t.find("<style", i)
        if s == -1:
            out.append(t[i:])
            break
        out.append(t[i:s])
        e = t.find("</style>", s)
        if e == -1:
            break
        i = e + len("</style>")
    return "".join(out)

def _strip_py_docstrings(text: str) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    i = 0
    n = len(t)
    while i < n:
        s1 = t.find('"""', i)
        s2 = t.find("'''", i)
        s = min([x for x in (s1, s2) if x != -1], default=-1)
        if s == -1:
            out.append(t[i:])
            break
        out.append(t[i:s])
        q = t[s:s+3]
        e = t.find(q, s + 3)
        if e == -1:
            break
        i = e + 3
    return "".join(out)

def _strip_js_block_comments(text: str) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    i = 0
    n = len(t)
    while i < n:
        s = t.find("/*", i)
        if s == -1:
            out.append(t[i:])
            break
        out.append(t[i:s])
        e = t.find("*/", s + 2)
        if e == -1:
            break
        i = e + 2
    return "".join(out)

def _strip_line_comments_and_blank_lines(text: str, *, comment_markers: tuple[str, ...]) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in t.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if any(stripped.startswith(m) for m in comment_markers):
            continue
        lines.append(line.rstrip())
    return "\n".join(lines) + ("\n" if lines else "")

def _logic_first_transform(rel: str, text: str) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    if rel.endswith(".vue"):
        t = _strip_vue_style_blocks(t)
        t = _strip_js_block_comments(t)
        t = _strip_line_comments_and_blank_lines(t, comment_markers=("//", "/*", "*", "*/", "<!--"))
        return t
    if rel.endswith(".js"):
        t = _strip_js_block_comments(t)
        t = _strip_line_comments_and_blank_lines(t, comment_markers=("//", "/*", "*", "*/"))
        return t
    if rel.endswith(".py"):
        t = _strip_line_comments_and_blank_lines(t, comment_markers=("#",))
        return t
    if rel.endswith(".md") or rel.endswith(".txt") or rel.endswith(".html") or rel.endswith(".json"):
        t = _strip_line_comments_and_blank_lines(t, comment_markers=())
        return t
    return _strip_line_comments_and_blank_lines(t, comment_markers=())


def _write_archive(out_path: Path, files: list[tuple[str, Path]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for rel, abs_path in files:
            f.write(f"/ --- {rel.replace('\\', '/')} ---\n")
            txt = _logic_first_transform(rel, _read_text(abs_path))
            f.write(txt)
            if not txt.endswith("\n"):
                f.write("\n")


def _collect_frontend() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for name in ["index.html", "package.json", "vite.config.js"]:
        p = FRONTEND / name
        if p.exists():
            files.append((str(Path("frontend") / name), p))
    src = FRONTEND / "src"
    if src.exists():
        for p in sorted(src.rglob("*")):
            if p.is_dir():
                continue
            if any(part in ("node_modules", "dist") for part in p.parts):
                continue
            if p.suffix.lower() == ".css":
                continue
            files.append((str(p.relative_to(ROOT)), p))
    return files


def _collect_backend() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for name in [
        "README.md",
        "requirements.txt",
        "app.py",
        "constants.py",
        "database.py",
        "extensions.py",
        "seed_last_7_days.py",
    ]:
        p = BACKEND / name
        if p.exists():
            files.append((str(Path("backend") / name), p))
    for p in sorted(BACKEND.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        rel = str(p.relative_to(ROOT))
        if not any(rel == r for r, _ in files):
            files.append((rel, p))
    return files


def main() -> None:
    front_files = _collect_frontend()
    back_files = _collect_backend()
    _write_archive(ROOT / "前端代码.md", front_files)
    _write_archive(ROOT / "后端代码.md", back_files)
    print(f"OK: {len(front_files)} frontend files, {len(back_files)} backend files")


if __name__ == "__main__":
    main()

