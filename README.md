# Programming anharmonic potentials in a superconducting harmonic oscillator

Analysis code for the paper *Programming anharmonic potentials in a superconducting harmonic
oscillator*. The notebooks take the raw single-shot data of every gate to the reconstructed
forces and potentials, the statistical tests and the figure panels, and print every number
quoted in the main text and the Supplemental Material (SM).

## Contents

| file | what it does | paper |
|---|---|---|
| `01_symmetric_double_well.ipynb` | symmetric double well $V=0.1X^4-0.3X^2$, coherent probes | Fig. 3(a); SM *Double-well gates* |
| `02_asymmetric_double_well.ipynb` | asymmetric double well $V=0.1X^4-0.3X^2+0.1X$, three scans | Fig. 3(a); SM *Double-well gates* |
| `03_morse.ipynb` | Morse gate with position-compressed probes; exports the curves for `06` | Fig. 4(a,b); SM *Morse gate*, *Probe compression and bandwidth* |
| `04_cubic.ipynb` | cubic gate $V=0.6X^3$, coherent probes | Fig. 2(a,b); SM *Cubic gate* |
| `05_broken_double_well.ipynb` | broken double well $V=0.1X^4-0.3X^2+0.6X$, coherent probes | Fig. 3(a); SM *Double-well gates* |
| `06_morse_figure.ipynb` | draws main-text Fig. 4 and the supplementary Morse figure | Fig. 4; SM *Morse gate* |
| `07_operator_errors.ipynb` | hardware-free errors of the compiled circuits | SM *Compiled-circuit errors* |
| `mathematica/phase_gate_angles.nb` | QSP compiler: target phase → qubit rotation angles | SM *Rotation angles* |
| `extract_outputs.py` | collects the `PAPER VALUES` blocks of the executed notebooks into one text file | — |

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
| 8 | agreement with Sim on the measured points |
| 9 | values quoted in the paper |
| 10 | figure panels (Morse: export for `06`) |

## Data

Each analysis notebook reads one archive of raw data from the folder it sits in:

| notebook | archive |
|---|---|
| `01_symmetric_double_well` | `dw.zip` |
| `02_asymmetric_double_well` | `tilted_double_well_multiple_sets.zip` |
| `03_morse` | `squeezed_morse_10dB_0.zip` |
| `04_cubic` | `cubic_0p6.zip` |
| `05_broken_double_well` | `broken_tdw.zip` |

Each archive holds, for every probe centre, the single-shot outcomes of the
characteristic-function cut together with the post-selection record, plus the vacuum
calibration cuts taken before (and after) the scan; the Morse archive also holds the two
cuts of the compressed probe. `06` reads the export of `03`, and `07` needs no data.

## Running

Python 3.10 or later with the packages in `requirements.txt`:

```
pip install -r requirements.txt
jupyter lab
```

Run each notebook top to bottom, `03` before `06`. To execute all of them and collect the
quoted numbers in `outcomes.txt`:

```
python extract_outputs.py --run
```

Each notebook writes its tables, figures and `paper_values.json` to its own `results_*/`
folder. With 2000 bootstrap replicas a notebook takes a few minutes; lowering `N_BOOT` in
section 1 gives a quick check.

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
That notebook also documents a factor of $\pi$ in the phase of the complementary
polynomial that the angle extraction omits as written: including it gives an alternative
angle set whose circuit reproduces the Fourier-truncated gate more closely, with a smaller
phase error and a larger amplitude error.
