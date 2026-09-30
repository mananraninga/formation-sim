"""Single agent. Control uses only last-heard neighbor poses plus own state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np

from .radio import PosePacket, Radio


@dataclass
class Agent:
    aid: int
    pos: np.ndarray
    vel: np.ndarray
    radio: Radio
    max_speed: float = 4.0
    max_accel: float = 8.0
    last_seen: Dict[int, PosePacket] = field(default_factory=dict)

    def sense(self) -> None:
        for pkt in self.radio.recv(self.aid):
            self.last_seen[pkt.sender_id] = pkt

    def broadcast(self, t: float, others: list[int]) -> int:
        pkt = PosePacket(
            sender_id=self.aid,
            t=t,
            x=float(self.pos[0]),
            y=float(self.pos[1]),
            vx=float(self.vel[0]),
            vy=float(self.vel[1]),
        )
        return self.radio.broadcast(pkt, others)

    def estimated_centroid(self) -> np.ndarray:
        pts = [self.pos.copy()]
        for pkt in self.last_seen.values():
            pts.append(np.array([pkt.x, pkt.y], dtype=float))
        return np.mean(pts, axis=0)

    def step(self, target: np.ndarray, dt: float) -> None:
        err = target - self.pos
        # PD toward slot; damping kills orbiting
        desired_v = 2.2 * err
        speed = np.linalg.norm(desired_v)
        if speed > self.max_speed:
            desired_v *= self.max_speed / speed
        accel = (desired_v - self.vel) / max(dt, 1e-3)
        a_norm = np.linalg.norm(accel)
        if a_norm > self.max_accel:
            accel *= self.max_accel / a_norm
        self.vel = self.vel + accel * dt
        v_norm = np.linalg.norm(self.vel)
        if v_norm > self.max_speed:
            self.vel *= self.max_speed / v_norm
        self.pos = self.pos + self.vel * dt
