"""Closed-loop formation sim with optional packet loss and a mid-run shape change."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from .agent import Agent
from .formation import assign_slots, slot_offsets
from .radio import Radio


@dataclass
class Frame:
    t: float
    positions: np.ndarray
    targets: np.ndarray
    shape: str
    delivered: int
    attempted: int


class FormationSim:
    def __init__(
        self,
        n: int = 6,
        shape: str = "triangle",
        scale: float = 3.0,
        drop_rate: float = 0.15,
        dt: float = 0.05,
        seed: int = 0,
    ):
        self.n = n
        self.shape = shape
        self.scale = scale
        self.dt = dt
        self.rng = np.random.default_rng(seed)
        self.radio = Radio(drop_rate=drop_rate, rng=self.rng)
        self.agents: List[Agent] = []
        for i in range(n):
            pos = self.rng.uniform(-8, 8, size=2)
            vel = self.rng.normal(0, 0.3, size=2)
            self.radio.register(i)
            self.agents.append(Agent(aid=i, pos=pos, vel=vel, radio=self.radio))
        self.t = 0.0
        self.offsets = slot_offsets(shape, n, scale)

    def set_shape(self, shape: str) -> None:
        self.shape = shape
        self.offsets = slot_offsets(shape, self.n, self.scale)

    def _targets(self) -> np.ndarray:
        positions = np.stack([a.pos for a in self.agents])
        # assignment uses truth positions so the *geometry* is well-defined;
        # each agent still steers using only its own estimate of the centroid.
        assign = assign_slots(positions, self.offsets)
        world_slots = np.zeros_like(positions)
        for a in self.agents:
            c = a.estimated_centroid()
            world_slots[a.aid] = c + self.offsets[assign[a.aid]]
        return world_slots

    def step(self) -> Frame:
        ids = list(range(self.n))
        delivered = 0
        attempted = 0
        for a in self.agents:
            attempted += self.n - 1
            delivered += a.broadcast(self.t, ids)
        for a in self.agents:
            a.sense()
        targets = self._targets()
        for a in self.agents:
            a.step(targets[a.aid], self.dt)
        self.t += self.dt
        positions = np.stack([a.pos for a in self.agents])
        return Frame(
            t=self.t,
            positions=positions,
            targets=targets,
            shape=self.shape,
            delivered=delivered,
            attempted=attempted,
        )

    def run(self, seconds: float, change_to: str | None = None, change_at: float = 6.0) -> list[Frame]:
        frames = []
        steps = int(seconds / self.dt)
        changed = False
        for _ in range(steps):
            if change_to and not changed and self.t >= change_at:
                self.set_shape(change_to)
                changed = True
            frames.append(self.step())
        return frames
