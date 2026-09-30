"""Matplotlib animation. One window, that is the demo."""

from __future__ import annotations

from typing import List

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

from .sim import FormationSim, Frame


def animate(sim: FormationSim, frames: List[Frame], interval_ms: int = 30) -> FuncAnimation:
    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    ax.set_aspect("equal")
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.set_facecolor("#0e1116")
    fig.patch.set_facecolor("#0e1116")
    ax.tick_params(colors="#8b93a7")
    for spine in ax.spines.values():
        spine.set_color("#2a3140")
    ax.grid(color="#1c2330", linestyle="--", linewidth=0.6)

    scat = ax.scatter([], [], s=70, c="#6ee7ff", zorder=3)
    tgt = ax.scatter([], [], s=30, c="#f5c542", marker="x", zorder=2)
    title = ax.set_title("", color="#e8ecf1", loc="left")

    def _init():
        scat.set_offsets(np.empty((0, 2)))
        tgt.set_offsets(np.empty((0, 2)))
        return scat, tgt, title

    def _update(i: int):
        fr: Frame = frames[i]
        scat.set_offsets(fr.positions)
        tgt.set_offsets(fr.targets)
        rate = 0.0 if fr.attempted == 0 else 100.0 * fr.delivered / fr.attempted
        title.set_text(
            f"t={fr.t:5.2f}s   shape={fr.shape:<8}   radio delivered {rate:5.1f}%"
        )
        return scat, tgt, title

    anim = FuncAnimation(
        fig,
        _update,
        init_func=_init,
        frames=len(frames),
        interval=interval_ms,
        blit=False,
        repeat=True,
    )
    fig.tight_layout()
    return anim
