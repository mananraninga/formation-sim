"""Unreliable pose radio.

Agents do not read each other's memory. They only see packets that
survived drop_rate. This is the whole point of the exercise.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np


@dataclass(frozen=True)
class PosePacket:
    sender_id: int
    t: float
    x: float
    y: float
    vx: float
    vy: float


class Radio:
    def __init__(self, drop_rate: float = 0.0, rng: Optional[np.random.Generator] = None):
        if not 0.0 <= drop_rate <= 1.0:
            raise ValueError("drop_rate must be in [0, 1]")
        self.drop_rate = drop_rate
        self.rng = rng or np.random.default_rng(0)
        self._inbox: Dict[int, List[PosePacket]] = {}

    def register(self, agent_id: int) -> None:
        self._inbox.setdefault(agent_id, [])

    def broadcast(self, packet: PosePacket, recipients: List[int]) -> int:
        """Send packet to recipients. Returns number of successful deliveries."""
        delivered = 0
        for rid in recipients:
            if rid == packet.sender_id:
                continue
            if self.rng.random() < self.drop_rate:
                continue
            self._inbox.setdefault(rid, []).append(packet)
            delivered += 1
        return delivered

    def recv(self, agent_id: int) -> List[PosePacket]:
        msgs = self._inbox.get(agent_id, [])
        self._inbox[agent_id] = []
        return msgs
