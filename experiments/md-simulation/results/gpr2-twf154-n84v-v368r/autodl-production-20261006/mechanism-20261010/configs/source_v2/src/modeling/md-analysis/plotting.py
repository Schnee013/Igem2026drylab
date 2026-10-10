from __future__ import annotations
import os
os.environ.setdefault('MPLCONFIGDIR', 'temp/matplotlib')
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def lineplot_by_rep(df, x, y, out: Path, title: str, ylabel: str, xlabel: str = 'Time (ns)'):
    fig, ax = plt.subplots(figsize=(7, 4), dpi=160)
    for rep, sub in df.groupby('rep'):
        ax.plot(sub[x], sub[y], lw=1.0, label=rep)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def barplot(df, x, y, out: Path, title: str, ylabel: str, limit=20):
    sub = df.head(limit)
    fig, ax = plt.subplots(figsize=(8, max(3, 0.28 * len(sub))), dpi=160)
    ax.barh(sub[x].astype(str), sub[y])
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel(ylabel)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
