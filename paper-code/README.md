# Artifact for "Prefix Fixing and Partitioning for Shortest Linear Programs of Large Linear Layers"

This directory contains the research prototype used for the experiments in the paper.
It is a framework, not a polished library: the two methods are kept in separate
directories, with the original command-line drivers.

## Contents

- `gen_matrix.py` — random matrix generator used for the experiments.
- `bp/` — column-partitioned Boyar–Peralta optimizer.
  - `fen.py` splits a matrix into column blocks.
  - `check.py` removes all-zero and duplicate rows from the blocks.
  - `main.cpp` runs BP on each block (C++11, OpenMP).
  - `turn_right.py` remaps variables and merges the block circuits.
- `paar/` — randomized Paar (RPaar1) implementation used for the prefix-fixing
  baseline.

## Requirements

- Python 3.8+ with `numpy`
- `g++` with OpenMP support

## Quick start: partitioned BP

Generate a matrix set (optional; a 48x48 example is included):

```bash
python gen_matrix.py --n 48 --rho 0.6 --count 100 --seed 0 --out matrices.txt
```

```bash
cd bp
python fen.py                 # example_matrix.txt -> example.txt (4 blocks)
g++ -O3 -fopenmp -o main main.cpp
./main                        # writes result.txt
python turn_right.py          # writes final_result.txt
```

`final_result.txt` contains one XOR operation per line; the number of lines is
the g-XOR count of the merged circuit, including the `(l-1)m` merge gates.
The included `example_matrix.txt` is a 48x48 matrix of density 0.6
(seed 4); with four blocks the merged circuit uses 441 XOR gates.

Input format (`example_matrix.txt`):

```
<number of matrices>
<rows> <cols>
<row 0 entries separated by spaces>
...
```

`fen.py` uses `num_blocks = 4`; change it to use a different number of blocks.

### Duplicate and zero rows

The BP prototype requires every block to have distinct, non-zero rows.
`check.py` removes duplicate and all-zero rows in place; a duplicate output can
be read from the surviving wire, so removing it does not change the circuit.
An all-zero row is a constant-zero output and needs additional handling in the
merge step; the prototype does not implement it. This is why the paper applies
the partitioned method to dense layers (density >= 0.4), where all-zero rows do
not occur and the remaining duplicate rows can be removed.

## Paar / RPaar1

```bash
cd paar
python paar_deterministic_randomized.py
```

The script reads `example_matrix.txt`, runs `NUM_TRIALS_PER_MATRIX` randomized
trials per matrix, and writes the best result to `paar_results.txt`.

## Notes

- The C++ code uses 64-bit words and accepts at most 63 inputs per block.
- The reported timings in the paper were obtained with four blocks per matrix;
  the complete 10,200-matrix campaign takes 15--60 minutes on the machine
  described in the paper.
- The code is a research prototype. Paths and file names are kept close to the
  versions used to produce the tables, rather than refactored into a package.

## Citation

If you use this code, please cite the paper.

## Contact

Corresponding author: Zuowen Tan.
