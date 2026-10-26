# Programming anharmonic potentials in a superconducting harmonic oscillator

Analysis code for the paper *Programming anharmonic potentials in a superconducting harmonic
oscillator*. The notebooks take the raw single-shot data of every gate to the reconstructed
forces and potentials, the statistical tests and the figure panels, and print every number
quoted in the main text and the Supplemental Material (SM).

## Contents

The notebooks are numbered in the order their results appear in the paper.

| file | what it does | paper |
|---|---|---|
| `01_cubic.ipynb` | cubic gate $V=0.6X^3$, coherent probes | Fig. 2(a,b); SM *Cubic gate* |
| `02_symmetric_double_well.ipynb` | symmetric double well $V=0.1X^4-0.3X^2$, coherent probes | Fig. 3(a); SM *Double-well gates* |
| `03_asymmetric_double_well.ipynb` | asymmetric double well $V=0.1X^4-0.3X^2+0.1X$, three scans | Fig. 3(a); SM *Double-well gates* |
| `04_broken_double_well.ipynb` | broken double well $V=0.1X^4-0.3X^2+0.6X$, coherent probes | Fig. 3(a); SM *Double-well gates* |
| `05_morse.ipynb` | Morse gate with position-compressed probes | Fig. 4; SM *Morse gate*, *Probe compression and bandwidth* |
| `06_operator_errors.ipynb` | hardware-free errors of the compiled circuits | SM *Compiled-circuit errors* |
| `repeated_cubic/state_reconstruction_v1.ipynb` | state reconstruction, fidelities, Wigner negativities | Cubic section in main text |
| `mathematica/phase_gate_angles.nb` | QSP compiler: target phase → qubit rotation angles | SM *Rotation angles* |
| `extract_outputs.py` | collects the `PAPER VALUES` blocks of the executed notebooks into one text file | — |

Each notebook contains the rotation angles of the circuits it uses, as run on hardware.

Notebooks `01`–`05` share one structure, so the same quantity sits in the same section of
each:

| § | content |
|---|---|
| 0 | setup: imports and library functions |
| 1 | configuration and raw data |
| 2 | measurement: momentum scale, probe width, probe-averaged force, raw-shot bootstrap |
| 3 | compiled circuit: $K_g$ from the rotation angles run, and its exact channels |
| 4 | pointwise force reconstruction and Sim |
| 5 | band-limited target (Morse: what the band limit removes) |
| 6 | gate-specific analysis |
| 7 | acceptance and post-selection |
| 8 | agreement with Sim: band coverage and force errors |
| 9 | values quoted in the paper |
| 10 | figure panels |

## Data

Each analysis notebook reads its raw data from the folder it sits in:

| notebook | archive |
|---|---|
| `01_cubic` | `cubic_0p6.zip` |
| `02_symmetric_double_well` | `dw.zip` |
| `03_asymmetric_double_well` | folder `tilted_double_well_multiple_sets/`: `calibrations.zip` and `tdw_<j>.zip` (three scans) |
| `04_broken_double_well` | `broken_tdw.zip` |
| `05_morse` | `squeezed_morse_10dB_0.zip` |
| `repeated_cubic/state_reconstruction_v1` | `repeated_cubic/clean_data_reconstruction.zip` |

Each archive holds, for every probe centre, the single-shot outcomes of the
characteristic-function cut together with the post-selection record, plus the vacuum
calibration cuts taken before (and after) the scan (for the asymmetric well, the numbered
calibrations bracketing all three scans, with the two no-gate references, are in `calibrations.zip`); the Morse archive also holds the two
cuts of the compressed probe. `06` needs no data.

## Running

Python 3.10 or later with the packages in `requirements.txt`:

```
pip install -r requirements.txt
jupyter lab
```

Run each notebook top to bottom. To execute all of them and collect the
quoted numbers in `outcomes.txt`:

```
python extract_outputs.py --run
```

Each notebook writes its tables, figures and `paper_values.json` to its own `results_*/`
folder. With 2000 bootstrap replicas a notebook takes a few minutes; lowering `N_BOOT` in
section 1 gives a quick check.

Running the state reconstruction, fidelities, and Wigner negativities for the cubic potential:
1. The main script 'repeated_cubic/state_reconstruction_v1.ipynb' requires functions from 'TK_basics.py' (put this on the same folder).
2. Run the 'q2_CF_map_gridbase_1mode.py' script to generate and save the map for reconstruction. The map will be recalled in 'state_reconstruction_v1.ipynb'.
3. Ideal target states are stored as npz files in the 'repeated_cubic' folder and will be recalled in 'state_reconstruction_v1.ipynb'.
4. When running 'state_reconstruction_v1.ipynb', choose the corresponding target state, load the map that was generated with 'q2_CF_map_gridbase_1mode.py', and load the corresponding data. The rest of the script will post process the data and output the fidelity with command 'print(f'FidelityBI is {Fmean} +- {Fstd}')', and Wigner negativity with command 'print(f'neg is {neg_mean} +- {neg_std}')'.

## Conventions

* Fourier interval $|X|\le2$ (period $L=4$, $\gamma=\pi/2$).
* Probe attenuation $H_n=e^{-\sigma_X^2k_n^2/2}$, with the measured probe variance
  $\sigma_X^2$ (vacuum calibration cut for the coherent probes, the probe's own cut for
  the compressed probe); noise-gain cap $1/H_n\le20$.
* Uncertainties from 2000 bootstrap replicas that resample the raw single shots and draw
  each calibration from its fitted error; every replica passes through the same analysis.
* *Sim*: the compiled circuit, built from the rotation angles run, put through the same
  probe average and reconstruction as the data.
* Functional-form fits (cubic, Morse) are confined to the largest window $|X|\le W$ over which
  Sim plus the measured noise is consistent with the form (median $p\ge0.10$); the
  double-well topology is analysed on $|X|\le1.5$.

## Rotation angles

The rotation angles in the notebooks are those run on hardware. They were produced by
`mathematica/phase_gate_angles.nb`, whose comments explain each step of the compilation.
