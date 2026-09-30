"""Slot geometry. Each agent is assigned a target offset from the formation centroid."""

from __future__ import annotations

import numpy as np


SHAPES = ("line", "triangle", "square", "circle")


def slot_offsets(shape: str, n: int, scale: float) -> np.ndarray:
    if n < 1:
        raise ValueError("need at least one agent")
    shape = shape.lower()
    if shape not in SHAPES:
        raise ValueError(f"unknown shape {shape!r}")

    if shape == "line":
        xs = np.linspace(-scale, scale, n) if n > 1 else np.array([0.0])
        return np.stack([xs, np.zeros(n)], axis=1)

    if shape == "circle":
        if n == 1:
            return np.zeros((1, 2))
        theta = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
        return np.stack([scale * np.cos(theta), scale * np.sin(theta)], axis=1)

    if shape == "triangle":
        verts = np.array(
            [
                [0.0, scale],
                [-scale * 0.866, -scale * 0.5],
                [scale * 0.866, -scale * 0.5],
            ]
        )
        return _distribute_on_polygon(verts, n)

    # square, CCW from bottom-left
    verts = np.array(
        [
            [-scale, -scale],
            [scale, -scale],
            [scale, scale],
            [-scale, scale],
        ]
    )
    return _distribute_on_polygon(verts, n)


def _distribute_on_polygon(verts: np.ndarray, n: int) -> np.ndarray:
    if n <= len(verts):
        return verts[:n].copy()
    # walk the perimeter and place n points evenly by arc length
    closed = np.vstack([verts, verts[0]])
    seg = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    total = float(seg.sum())
    step = total / n
    out = np.zeros((n, 2))
    d = 0.0
    si = 0
    acc = 0.0
    for i in range(n):
        target = i * step
        while si < len(seg) - 1 and acc + seg[si] < target:
            acc += seg[si]
            si += 1
        local = 0.0 if seg[si] == 0 else (target - acc) / seg[si]
        out[i] = closed[si] + local * (closed[si + 1] - closed[si])
        _ = d
    return out


def assign_slots(positions: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    """Greedy nearest-slot assignment so agents do not all rush the same vertex."""
    n = len(positions)
    used = set()
    assign = np.zeros(n, dtype=int)
    # farthest agents first — slightly more stable than index order
    order = np.argsort(-np.linalg.norm(positions - positions.mean(axis=0), axis=1))
    for i in order:
        d = np.linalg.norm(offsets - positions[i], axis=1)
        for j in np.argsort(d):
            if int(j) not in used:
                assign[i] = int(j)
                used.add(int(j))
                break
    return assign
