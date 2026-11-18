#!/usr/bin/env python3
"""Generate random square binary matrices for the experiments.

Example:
    python gen_matrix.py --n 64 --rho 0.6 --count 100 --seed 0 --out matrices.txt
"""
import argparse
import random


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=64, help="matrix dimension")
    ap.add_argument("--rho", type=float, default=0.6, help="density")
    ap.add_argument("--count", type=int, default=100, help="number of matrices")
    ap.add_argument("--seed", type=int, default=0, help="random seed")
    ap.add_argument("--out", default="matrices.txt", help="output file")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    with open(args.out, "w") as f:
        f.write(f"{args.count}\n")
        for _ in range(args.count):
            f.write(f"{args.n} {args.n}\n")
            for _ in range(args.n):
                f.write(" ".join("1" if rng.random() < args.rho else "0" for _ in range(args.n)))
                f.write("\n")


if __name__ == "__main__":
    main()
