"""
fab_style.py -- House style for every figure: Fondation Abderrahim Bouabid colours,
Times New Roman throughout, journal typography.

The brand colour is the burgundy of the FAB wordmark, #84171D. Everything else is a warm
neutral or a tint of it, so a figure reads as one object rather than a set of competing hues.
Where a figure must separate three categories, the accents differ in lightness as well as in
hue (burgundy L*~30, bronze L*~52, sage L*~43), so they survive greyscale printing and the
common forms of colour blindness.

Both figure scripts import this:  from fab_style import *  ;  apply()
"""
import matplotlib as mpl

# ---------------------------------------------------------------- brand
FAB = "#84171D"          # Fondation Abderrahim Bouabid burgundy (sampled from the wordmark)
FAB_DARK = "#5A0F14"
FAB_MID = "#B05A5F"
FAB_PALE = "#E3C9CB"
FAB_WASH = "#F6EDEE"

# ---------------------------------------------------------------- roles used by the figures
BLUE = FAB               # primary subject: Morocco
ORANGE = "#9C6B2F"       # second category: benchmark transitions
AQUA = "#4F6B61"         # third category
INK = "#14110F"
INK2 = "#46423E"
MUTED = "#7D7872"
NEUT = "#BFBAB2"
GRID = "#E7E3DD"
RULE = "#6E6A65"         # hairline axis / reference lines

# ordinal ramp, dark (deficit) -> light
ORD = [FAB_DARK, FAB, FAB_MID, FAB_PALE]

# attainment ramp: least schooling (deep burgundy) -> most (warm stone), monochrome by design
LEVELS = {"none": "#5A0F14", "incpri": "#8E2F33", "pri": "#B5706F",
          "losec": "#D3A9A3", "upsec": "#B9AE9C", "post": "#6F6A5E"}

SERIF = ["Times New Roman", "Times", "STIX Two Text", "DejaVu Serif"]


def apply():
    """Set the house rcParams. Call once, before any figure is built."""
    mpl.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 400, "savefig.bbox": "tight",
        "figure.facecolor": "white", "axes.facecolor": "white",
        # typography: one serif family for every mark on the page, maths included
        "font.family": "serif", "font.serif": SERIF,
        # mathtext in the same face, so a bold run-in "Figure 12." matches the title
        "mathtext.fontset": "custom", "mathtext.rm": "Times New Roman",
        "mathtext.bf": "Times New Roman:bold", "mathtext.it": "Times New Roman:italic",
        "font.size": 9.5, "axes.titlesize": 10.5, "axes.labelsize": 9.5,
        "axes.titleweight": "normal", "axes.titlelocation": "left", "axes.titlepad": 7,
        "axes.labelcolor": INK, "text.color": INK,
        # frame: two hairlines, nothing else
        "axes.edgecolor": RULE, "axes.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.color": INK2, "ytick.color": INK2,
        "xtick.labelsize": 8.8, "ytick.labelsize": 8.8,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3.2, "ytick.major.size": 3.2,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "legend.frameon": False, "legend.fontsize": 8.8, "legend.handlelength": 1.6,
        "legend.borderaxespad": 0.3, "legend.labelspacing": 0.35,
        "grid.color": GRID, "grid.linewidth": 0.5, "grid.linestyle": "-", "axes.grid": False,
        "lines.linewidth": 1.3, "patch.linewidth": 0.6,
        "pdf.fonttype": 42, "ps.fonttype": 42,          # embed real glyphs, not outlines
    })


def figtitle(fig, number, title, subtitle=None, x=0.0, y=1.0):
    """Journal-style heading: 'Figure 13.' in bold, the title in roman, a subtitle in italic."""
    fig.text(x, y, f"Figure {number}.", ha="left", va="bottom",
             fontsize=10.5, fontweight="bold", color=INK)
    off = 0.052 + 0.012 * len(f"Figure {number}.")
    fig.text(x + off, y, title, ha="left", va="bottom", fontsize=10.5, color=INK)
    if subtitle:
        fig.text(x, y - 0.045, subtitle, ha="left", va="bottom",
                 fontsize=9.2, color=INK2, style="italic")


# ---------------------------------------------------------------- label placement
# A scatter of 150 countries cannot be labelled by hand: two labels at the same height
# end up printed on top of each other (Morocco and Jordan in F1a, Poland and the Moroccan
# cohort in F2). These two helpers measure the text that has actually been drawn and move
# it out of the way, so no label ever lands on another.
import matplotlib.patheffects as _pe
from matplotlib.transforms import Bbox as _Bbox


def halo(artist, lw=2.8, color="white"):
    """Knock a white outline out from under text, so a label stays readable over the cloud."""
    artist.set_path_effects([_pe.withStroke(linewidth=lw, foreground=color)])
    return artist


def _grow(bb, p):
    return _Bbox.from_extents(bb.x0 - p, bb.y0 - p, bb.x1 + p, bb.y1 + p)


def _overlap(a, b):
    w = min(a.x1, b.x1) - max(a.x0, b.x0)
    h = min(a.y1, b.y1) - max(a.y0, b.y0)
    return w * h if w > 0 and h > 0 else 0.0


def reserve_point(ax, xy, boxes, r=9.0):
    """Keep a marker's own area free, not just the labels already drawn.

    Without this a label slides under the Morocco marker, which is drawn on top of it
    (Jordan sat beneath the diamond in F1a). r is a half-width in typographic points.
    """
    x, y = ax.transData.transform(xy)
    rp = r * ax.figure.dpi / 72.0
    boxes.append(_Bbox.from_extents(x - rp, y - rp, x + rp, y + rp))


def reserve_span(ax, xy0, xy1, boxes, w=3.0):
    """Keep a drawn line's corridor free, so no label is printed across it."""
    (x0, y0), (x1, y1) = ax.transData.transform([xy0, xy1])
    wp = w * ax.figure.dpi / 72.0
    boxes.append(_Bbox.from_extents(min(x0, x1) - wp, min(y0, y1) - wp,
                                    max(x0, x1) + wp, max(y0, y1) + wp))


def reserve(artist, boxes, pad=1.5):
    """Mark the space an already-placed label occupies, so later labels avoid it."""
    boxes.append(_grow(artist.get_window_extent(artist.figure.canvas.get_renderer()), pad))
    return artist


# clockwise from the usual position: right, left, below-right, below-left, above, below
CANDIDATES = [(5, 3, "left", "baseline"), (-5, 3, "right", "baseline"),
              (5, -10, "left", "baseline"), (-5, -10, "right", "baseline"),
              (0, 9, "center", "baseline"), (0, -15, "center", "baseline")]


def place_label(ax, xy, text, boxes, cands=CANDIDATES, pad=1.5, **kw):
    """Annotate xy at the first offset whose drawn text box hits nothing already placed.

    boxes is the running list of occupied rectangles in display space; seed it with reserve()
    for the labels that must not move. If every candidate collides the least-bad one is used,
    so a country is never silently dropped. Axis limits must be final before calling: the
    measurement happens in display space.
    """
    best = None
    for dx, dy, ha, va in cands:
        t = ax.annotate(text, xy=xy, xytext=(dx, dy), textcoords="offset points",
                        ha=ha, va=va, **kw)
        bb = _grow(t.get_window_extent(ax.figure.canvas.get_renderer()), pad)
        ov = sum(_overlap(bb, b) for b in boxes)
        if ov == 0:
            boxes.append(bb)
            return t
        if best is None or ov < best[0]:
            best = (ov, dx, dy, ha, va)
        t.remove()
    _, dx, dy, ha, va = best
    t = ax.annotate(text, xy=xy, xytext=(dx, dy), textcoords="offset points",
                    ha=ha, va=va, **kw)
    return reserve(t, boxes, pad)
