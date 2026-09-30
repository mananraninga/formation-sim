#!/usr/bin/env python3
"""formation-sim — run a local multi-agent formation demo."""

from __future__ import annotations

from sim import FormationSim
from viz import animate

from src.sim import FormationSim
from src.viz import animate


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simulated agents share pose and hold a shape.")
    p.add_argument("--n", type=int, default=6, help="number of agents")
    p.add_argument("--shape", default="triangle", choices=["line", "triangle", "square", "circle"])
    p.add_argument("--change-to", default="square", help="shape after mid-run switch; empty to disable")
    p.add_argument("--drop-rate", type=float, default=0.2, help="probability a pose packet is lost")
    p.add_argument("--seconds", type=float, default=16.0)
    p.add_argument("--scale", type=float, default=3.0)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--save", default="", help="optional path to save mp4/gif if ffmpeg available")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    change = args.change_to.strip() or None
    sim = FormationSim(
        n=args.n,
        shape=args.shape,
        scale=args.scale,
        drop_rate=args.drop_rate,
        seed=args.seed,
    )
    frames = sim.run(seconds=args.seconds, change_to=change, change_at=args.seconds * 0.45)
    anim = animate(sim, frames)
    if args.save:
        anim.save(args.save)
        print(f"wrote {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
