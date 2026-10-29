
from xml.sax.saxutils import escape

USERNAME = "wawaHyun"          # shown as "<username>@github"
# BIRTHDAY = (1991, 4, 18)             # (year, month, day) -> used for "Uptime"

ABOUT = [
    ("OS", "Windows, macOS, Linux"),
    # ("Uptime", None),  # filled automatically from BIRTHDAY
    ("Host", "Day job ≠ dev"),
    ("IDE", "VS Code, IntelliJ"),
]
LANGUAGES = [
    ("Code", "Java, Spring, React, Python, JS"),
    ("Markup", "HTML, CSS, Markdown"),
    ("Human", "Korean, English, Japanese"),
]
HOBBIES = [
    ("Soft", "Side projects"),
    ("Hard", "all things handmade"),
]
CONTACT = [
   ("Twitter", "@yomankum"),
    ("Fastest", "Twitter DM"),
    ("GitHub", USERNAME),
]

ASCII_FILE = "ascii.txt"
# ----------------------------------------------------------------------------

LINE_W = 44          # width (chars) of the right-hand info column
ART_X, INFO_X = 15, 555
ART_FONT, ART_LH = 12, 13      # ASCII art font size / line height (px)
INFO_FONT, INFO_LH = 14, 20
WIDTH = 985

THEMES = {
    "dark_mode": dict(bg="#161b22", fg="#c9d1d9", art="#8b949e",
                      key="#ffa657", value="#a5d6ff", cc="#616e7f",
                      add="#3fb950", dele="#f85149"),
    "light_mode": dict(bg="#f6f8fa", fg="#24292f", art="#57606a",
                       key="#953800", value="#0a3069", cc="#c2cfde",
                       add="#1a7f37", dele="#cf222e"),
}


# def uptime(today):
#     """Years / months / days since BIRTHDAY, e.g. '26 years, 9 months, 3 days'."""
#     by, bm, bd = BIRTHDAY
#     y, m, d = today.year - by, today.month - bm, today.day - bd
#     if d < 0:
#         m -= 1
#         prev_month = today.month - 1 or 12
#         prev_year = today.year if today.month > 1 else today.year - 1
#         days_in_prev = (
#             31 if prev_month in (1, 3, 5, 7, 8, 10, 12)
#             else 30 if prev_month != 2
#             else 29 if (prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0))
#             else 28
#         )
#         d += days_in_prev
#     if m < 0:
#         y -= 1
#         m += 12
#     plural = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
#     return f"{plural(y, 'year')}, {plural(m, 'month')}, {plural(d, 'day')}"


def _row(label, value, vid=None):
    """One 'Label: ........ value' line as SVG tspans with a fixed width."""
    value = str(value)
    head = f"{label}:"
    dots = max(2, LINE_W - len(head) - len(value) - 2)
    id_attr = f' id="{vid}"' if vid else ""
    return (
        f'<tspan class="key">{escape(label)}</tspan>:'
        f' <tspan class="cc">{"." * dots}</tspan> '
        f'<tspan class="value"{id_attr}>{escape(value)}</tspan>'
    )


def _section(title):
    return f'<tspan class="key">{escape(title)}</tspan> <tspan class="cc">{"-" * (LINE_W - len(title) - 1)}</tspan>'


def info_lines(stats, today):
    """Return the list of right-hand column lines (already tspan markup)."""
    from datetime import date
    today = today or date.today()
    out = [f'<tspan class="key">{escape(USERNAME)}</tspan>@<tspan class="key">github</tspan> '
           f'<tspan class="cc">{"-" * (LINE_W - len(USERNAME) - 8)}</tspan>']
    for label, value in ABOUT:
        out.append(_row(label, uptime(today) if value is None else value,
                        "age_data" if value is None else None))
    out.append("")
    for label, value in LANGUAGES:
        out.append(_row(f"Lang.{label}", value))
    out.append("")
    for label, value in HOBBIES:
        out.append(_row(f"Hobby.{label}", value))
    out.append("")
    out.append(_section("Contact"))
    for label, value in CONTACT:
        out.append(_row(label, value))
    out.append("")
    out.append(_section("GitHub Stats"))
    s = stats
    out.append(_row("Repos", s["repos"], "repo_data"))
    out.append(_row("Contributed", s["contrib"], "contrib_data"))
    out.append(_row("Stars", s["stars"], "star_data"))
    out.append(_row("Commits", s["commits"], "commit_data"))
    out.append(_row("Followers", s["followers"], "follower_data"))
    return out


def build(stats, today=None, out_dir="."):
    art = open(f"{out_dir}/{ASCII_FILE}", encoding="utf-8").read().rstrip("\n").split("\n")
    info = info_lines(stats, today)
    height = max(len(art) * ART_LH, len(info) * INFO_LH) + 50

    for name, c in THEMES.items():
        art_svg = "\n".join(
            f'<tspan x="{ART_X}" y="{30 + i * ART_LH}">{escape(line)}</tspan>'
            for i, line in enumerate(art)
        )
        info_svg = "\n".join(
            f'<tspan x="{INFO_X}" y="{30 + i * INFO_LH}">{line}</tspan>'
            for i, line in enumerate(info)
        )
        svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,'DejaVu Sans Mono',monospace" width="{WIDTH}px" height="{height}px" font-size="{INFO_FONT}px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {c['key']};}}
.value {{fill: {c['value']};}}
.addColor {{fill: {c['add']};}}
.delColor {{fill: {c['dele']};}}
.cc {{fill: {c['cc']};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{WIDTH}px" height="{height}px" fill="{c['bg']}" rx="15"/>
<text x="{ART_X}" y="30" fill="{c['art']}" font-size="{ART_FONT}px" xml:space="preserve">
{art_svg}
</text>
<text x="{INFO_X}" y="30" fill="{c['fg']}" xml:space="preserve">
{info_svg}
</text>
</svg>
"""
        with open(f"{out_dir}/{name}.svg", "w", encoding="utf-8") as f:
            f.write(svg)


if __name__ == "__main__":
    build(dict(repos=0, contrib=0, stars=0, commits=0, followers=0))
    print("wrote dark_mode.svg and light_mode.svg")
