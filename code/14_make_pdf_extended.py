"""
14_make_pdf_extended.py -- Render notes/extended_analysis.md to PDF (pandoc + XeLaTeX), with the
figures embedded as vector PDFs. Same typography as 07_make_pdf.py, which is left untouched.
The .md source is not modified: substitutions happen on a temporary copy, and the PDF is written
to a temporary directory, checked, then moved into notes/ (Desktop sync once truncated a direct write).
"""
import os, re, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
NOTES, FIG = os.path.join(ROOT, "notes"), os.path.join(ROOT, "figures")
SRC, OUT = os.path.join(NOTES, "extended_analysis.md"), os.path.join(NOTES, "extended_analysis.pdf")

TITLE = "Two Electorates and One Unelected Executive"
SUBTITLE = "Cohorts, human capital and the prospects for a parliamentary monarchy in Morocco — an extended, disaggregated analysis"
AUTHOR, DATE = "A. Salaheddine", "September 2026"

PREAMBLE = r"""
\newcommand{\shorttitle}{Two Electorates and One Unelected Executive}
\usepackage{etoolbox}
\usepackage{booktabs}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{fancyhdr}
\definecolor{accent}{HTML}{84171D}  % Fondation Abderrahim Bouabid burgundy
\definecolor{rule}{HTML}{B6B1A9}
\definecolor{ink2}{HTML}{46423E}
\titleformat{\section}{\sffamily\large\bfseries\color{accent}}{\thesection}{0pt}{}
\titleformat{\subsection}{\sffamily\normalsize\bfseries\color{black}}{\thesubsection}{0pt}{}
\titleformat{\subsubsection}{\sffamily\small\bfseries\color{ink2}}{\thesubsubsection}{0pt}{}
\titlespacing*{\section}{0pt}{16pt}{6pt}
\titlespacing*{\subsection}{0pt}{12pt}{4pt}
\AtBeginEnvironment{longtable}{\footnotesize}
\AtBeginEnvironment{tabular}{\footnotesize}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.15}
\renewenvironment{quote}
  {\begin{list}{}{\leftmargin=1.1em\rightmargin=0.6em}\item[]%
   \color{black}\setlength{\parskip}{4pt}%
   \makebox[0pt][r]{\textcolor{accent}{\rule[-0.6em]{2.5pt}{2.3em}}\hspace{0.7em}}\ignorespaces}
  {\end{list}}
\renewenvironment{abstract}{\small\noindent\textsf{\textbf{\color{accent}Abstract.}}\ }{\par\medskip}
\pagestyle{fancy}\fancyhf{}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhead[L]{\footnotesize\sffamily\color{ink2}\shorttitle}
\fancyhead[R]{\footnotesize\sffamily\color{ink2}\nouppercase{\leftmark}}
\fancyfoot[C]{\footnotesize\sffamily\color{ink2}\thepage}
\setlength{\headheight}{14pt}
% keep a figure from being stranded at the foot of a page (needspace.sty's logic, inlined)
\makeatletter
\newcommand{\Needspace}[1]{\par\penalty-100\begingroup
  \setlength{\dimen@}{#1}\dimen@ii\pagegoal\advance\dimen@ii-\pagetotal
  \ifdim\dimen@>\dimen@ii\ifdim\dimen@ii>\z@\vfil\fi\break\fi\endgroup}
\makeatother
"""

def preprocess(text):
    # the title block is carried by the LaTeX title page; the abstract goes to the metadata
    body = text[text.index("## Abstract"):]
    abstract, body = body.split("\n---\n", 1)
    abstract = abstract.replace("## Abstract", "").strip()
    body = body.replace("$", "\\$")                                  # currency, never math
    body = body.replace("≥", "\\ensuremath{\\geq}").replace("≤", "\\ensuremath{\\leq}")
    body = body.replace("⅛", "\\ensuremath{\\tfrac{1}{8}}").replace("∈", "\\ensuremath{\\in}")
    # keep headings with what follows them, and table captions with their tables
    lines, keep = body.split("\n"), []
    for i, l in enumerate(lines):
        if l.startswith("#"):
            j = i + 1
            while j < len(lines) and not lines[j].strip(): j += 1
            nxt = lines[j] if j < len(lines) else ""
            keep += ["\\Needspace{%s\\textheight}" % ("0.55" if nxt.startswith("![](") else "0.18"), ""]
        elif l.startswith("**Table"):
            keep += ["\\Needspace{0.4\\textheight}", ""]
        keep.append(l)
    body = "\n".join(keep)
    # figures: never stranded at a page foot; absolute paths to the vector versions
    body = re.sub(r"^(!\[\]\(\.\./figures/)", r"\\Needspace{0.45\\textheight}\n\n\1", body, flags=re.M)
    body = re.sub(r"\]\(\.\./figures/(F\d+_[A-Za-z_]+)\.png\)",
                  lambda m: "](" + os.path.join(FIG, m.group(1) + ".pdf") + ")", body)
    abstract = abstract.replace("$", "\\$")
    return abstract, body

abstract, body = preprocess(open(SRC, encoding="utf-8").read())
tmpd = tempfile.mkdtemp()
md = os.path.join(tmpd, "extended_analysis.md"); open(md, "w", encoding="utf-8").write(body)
meta = os.path.join(tmpd, "meta.yaml")
open(meta, "w", encoding="utf-8").write("abstract: |\n" + "\n".join("  " + l for l in abstract.splitlines()) + "\n")
pre = os.path.join(tmpd, "preamble.tex"); open(pre, "w", encoding="utf-8").write(PREAMBLE)
pdf_tmp = os.path.join(tmpd, "extended_analysis.pdf")

cmd = ["pandoc", md, "-o", pdf_tmp, "--pdf-engine=xelatex",
       "--from", "markdown+superscript+pipe_tables+raw_tex",
       "--metadata-file", meta, "--shift-heading-level-by=-1", "--toc", "--toc-depth=2",
       "-V", "lang=en", "-V", "geometry:margin=2.2cm", "-V", "fontsize=11pt", "-V", "linestretch=1.12",
       "-V", "mainfont=Charter", "-V", "sansfont=Helvetica Neue", "-V", "monofont=Menlo",
       "-V", "colorlinks=true", "-V", "linkcolor=accent", "-V", "urlcolor=accent",
       "-V", f"title={TITLE}", "-V", f"subtitle={SUBTITLE}", "-V", f"author={AUTHOR}", "-V", f"date={DATE}",
       "-V", "toc-title=Contents", "-H", pre]
r = subprocess.run(cmd, capture_output=True, text=True)
warn = [l for l in r.stderr.splitlines() if "Missing character" in l or "WARNING" in l]
if r.returncode:
    raise SystemExit("pandoc failed:\n" + r.stderr[-3000:])
size = os.path.getsize(pdf_tmp)
assert size > 200_000, f"PDF suspiciously small ({size} bytes)"
shutil.move(pdf_tmp, OUT)
print(f"  wrote {os.path.relpath(OUT, ROOT)}  ({size/1e6:.1f} MB)")
for w in sorted(set(warn)): print("  ", w)
