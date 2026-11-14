"""Rebuild the go-skill-icons output locally, byte-for-byte in layout.

Mirrors generateSvg()/parseShortNames() from LelouchFR/skill-icons api/index.go:
  - each icon is a 256x256 SVG, placed on a 300px grid (44px gutter trimmed)
  - output is scaled so one icon renders at 48px
  - themed icons resolve to <name>-<theme>; default theme is "auto"
"""
import math, pathlib, sys

SRC = pathlib.Path("LelouchFR_skill-icons/assets")
OUT = pathlib.Path("/mnt/user-data/outputs/assets")
ONE_ICON, SCALE = 48, 48 / (300 - 44)

def load():
    return {p.stem.lower(): p.read_text() for p in SRC.glob("*.svg")}

ICONS = load()
THEMED = {k.rsplit("-", 1)[0] for k in ICONS if k.endswith(("-dark", "-light", "-auto"))}

def resolve(name, theme):
    if name in THEMED:
        return f"{name}-{theme}"
    if name in ICONS:
        return name
    raise SystemExit(f"MISSING icon: {name}")

def compose(names, per_line, theme="auto"):
    keys = [resolve(n, theme) for n in names]
    length = min(per_line * 300, len(keys) * 300) - 44
    height = math.ceil(len(keys) / per_line) * 300 - 44
    w, h = int(length * SCALE), int(height * SCALE)
    parts = [f'<svg width="{w}" height="{h}" viewBox="0 0 {length} {height}" fill="none" '
             f'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">']
    for i, k in enumerate(keys):
        x, y = (i % per_line) * 300, (i // per_line) * 300
        parts.append(f'<g transform="translate({x}, {y})">{ICONS[k]}</g>')
    parts.append("</svg>")
    return "\n".join(parts)

DEVSETUP = "linux,fedora,arch,gnome,bash,alacritty,obsidian,c,python,docker,git,github,jupyter,vscode".split(",")
DESKILLS = ("numpy,pandas,sqlserver,mysql,postgresql,clickhouse,mongodb,redis,kafka,flink,hadoop,hive,"
            "spark,airflow,dbtlabs,iceberg,delta,databricks,snowflake,azure,fabric,aws,pbi,seaborn").split(",")

(OUT / "devsetup.svg").write_text(compose(DEVSETUP, 7))
(OUT / "de-skills.svg").write_text(compose(DESKILLS, 8))
for fname, name in [("icon-website", "safari"), ("icon-airflow", "airflow"),
                    ("icon-linkedin", "linkedin"), ("icon-gmail", "gmail")]:
    (OUT / f"{fname}.svg").write_text(compose([name], 15, theme="dark"))

# individual icons (auto theme, i.e. what the service served by default)
for n in sorted(set(DEVSETUP + DESKILLS + ["safari", "linkedin", "gmail"])):
    (OUT / "icons" / f"{n}.svg").write_text(ICONS[resolve(n, "auto")])
print("done")
