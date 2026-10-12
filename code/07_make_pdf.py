"""
07_make_pdf.py -- Render the two synthesis notes to PDF via pandoc + XeLaTeX.
Source .md files are left untouched; substitutions happen on a temp copy.
"""
import os, re, shutil, subprocess, tempfile

HERE  = os.path.dirname(os.path.abspath(__file__))
NOTES = os.path.abspath(os.path.join(HERE, "..", "notes"))

PREAMBLE = r"""
\usepackage{etoolbox}
\usepackage{booktabs}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{fancyhdr}
\definecolor{accent}{HTML}{84171D}  % Fondation Abderrahim Bouabid burgundy
\definecolor{rule}{HTML}{B6B1A9}
\definecolor{ink2}{HTML}{46423E}

% headings in the same accent blue as the figures
\titleformat{\section}{\sffamily\large\bfseries\color{accent}}{\thesection}{0pt}{}
\titleformat{\subsection}{\sffamily\normalsize\bfseries\color{black}}{\thesubsection}{0pt}{}
\titleformat{\subsubsection}{\sffamily\small\bfseries\color{ink2}}{\thesubsubsection}{0pt}{}
\titlespacing*{\section}{0pt}{16pt}{6pt}
\titlespacing*{\subsection}{0pt}{12pt}{4pt}

% tables: smaller, never overfull
\AtBeginEnvironment{longtable}{\footnotesize}
\AtBeginEnvironment{tabular}{\footnotesize}
\setlength{\tabcolsep}{4.5pt}
\renewcommand{\arraystretch}{1.18}

% pull-quote: accent rule on the left
\renewenvironment{quote}
  {\begin{list}{}{\leftmargin=1.1em\rightmargin=0.6em}\item[]%
   \color{black}\setlength{\parskip}{4pt}%
   \makebox[0pt][r]{\textcolor{accent}{\rule[-0.6em]{2.5pt}{2.3em}}\hspace{0.7em}}\ignorespaces}
  {\end{list}}

\pagestyle{fancy}\fancyhf{}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhead[L]{\footnotesize\sffamily\color{ink2}\shorttitle}
\fancyhead[R]{\footnotesize\sffamily\color{ink2}\nouppercase{\leftmark}}
\fancyfoot[C]{\footnotesize\sffamily\color{ink2}\thepage}
\setlength{\headheight}{14pt}
"""

def preprocess(src, lang):
    """Charter covers the Unicode glyphs natively; only fix what LaTeX would mangle."""
    s = open(src, encoding="utf-8").read()
    s = s.replace("$", chr(92) + "$")            # currency must never be read as math
    s = s.replace(chr(0x1D49), "^e^")            # MODIFIER LETTER SMALL E -> real superscript
    s = s.replace("R" + chr(0xB2), "R^2^")       # R-squared -> real superscript
    if lang == "fr":                             # French: no break between a number and %
        s = re.sub(r"(\d)\s%", lambda m: m.group(1) + chr(0xA0) + "%", s)
    return s

DOCS = [
    ("note_de_synthese_FR.md", "note_de_synthese_FR.pdf", "fr",
     "Le Maroc peut-il se démocratiser ?",
     "Ce que disent réellement les données sur le capital humain — note de synthèse",
     "A. Salaheddine", "Septembre 2026", "Sommaire"),
    ("synthesis_note_EN.md", "synthesis_note_EN.pdf", "en",
     "Can Morocco Democratise?",
     "What the human-capital data actually say — a synthesis note",
     "A. Salaheddine", "September 2026", "Contents"),
]


for md, pdf, lang, title, subtitle, author, date, toctitle in DOCS:
    src = os.path.join(NOTES, md)
    body = preprocess(src, lang)
    # drop the markdown title block; the LaTeX title page carries it
    body = re.sub(r"\A# .*?\n## .*?\n\n\*\*.*?\*\*\n", "", body, flags=re.S)
    tmp = os.path.join(tempfile.gettempdir(), md)
    open(tmp, "w", encoding="utf-8").write(body)

    short = "Le Maroc peut-il se démocratiser ?" if lang == "fr" else "Can Morocco Democratise?"
    pre_path = os.path.join(tempfile.gettempdir(), f"preamble_{lang}.tex")
    open(pre_path, "w", encoding="utf-8").write(
        "\\newcommand{\\shorttitle}{%s}\n" % short + PREAMBLE)

    cmd = [
        "pandoc", tmp, "-o", os.path.join(NOTES, pdf),
        "--pdf-engine=xelatex", "--from", "markdown+superscript+pipe_tables",
        "--shift-heading-level-by=-1",
        "--toc", "--toc-depth=1",
        "-V", f"lang={lang}",
        "-V", "geometry:margin=2.3cm",
        "-V", "fontsize=11pt",
        "-V", "linestretch=1.15",
        "-V", "mainfont=Charter",
        "-V", "sansfont=Helvetica Neue",
        "-V", "monofont=Menlo",
        "-V", "colorlinks=true", "-V", "linkcolor=accent", "-V", "urlcolor=accent",
        "-V", f"title={title}", "-V", f"subtitle={subtitle}",
        "-V", f"author={author}", "-V", f"date={date}",
        "-V", f"toc-title={toctitle}",
        "-H", pre_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(f"FAILED {pdf}\n{r.stderr[-2500:]}")
    else:
        p = os.path.join(NOTES, pdf)
        print(f"  wrote {pdf}  ({os.path.getsize(p)/1024:.0f} KB)")
