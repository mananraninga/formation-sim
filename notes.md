# notes — formation-sim

Date: 2026-09-23 / 2026-09-30

Question: Can agents hold a shape if they only see pose packets that sometimes vanish?

Constraint: No shared position array. Control uses last-heard packets + own state.

Refused to fake: “swarm” that reads a global numpy array.

Result: Headless run, 6 agents, triangle → square, drop_rate=0.2, 80 steps, sim stable.

Broke / shortcut: Slot *assignment* still uses true positions. Geometry stays well-posed; slot consensus is not solved.

Next measured question: Same window, GPS off — formation from range/bearing packets only (`gnss-denied`).
