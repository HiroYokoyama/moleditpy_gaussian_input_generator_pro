# MoleditPy Gaussian Input Generator Pro

[![Tests](https://github.com/HiroYokoyama/moleditpy_gaussian_input_generator_pro/actions/workflows/tests.yml/badge.svg)](https://github.com/HiroYokoyama/moleditpy_gaussian_input_generator_pro/actions/workflows/tests.yml)
[![Downloads](https://img.shields.io/github/downloads/HiroYokoyama/moleditpy_gaussian_input_generator_pro/total)](https://github.com/HiroYokoyama/moleditpy_gaussian_input_generator_pro/releases)

An advanced **Gaussian 16 Input Generator** plugin for **MoleditPy**, designed to streamline the creation of Gaussian `.gjf`/`.com` calculation input files with a focus on usability, automation, and multi-job (`--Link1--`) workflows.

Repo: [https://github.com/HiroYokoyama/moleditpy_gaussian_input_generator_pro](https://github.com/HiroYokoyama/moleditpy_gaussian_input_generator_pro)

---

## Key Features

- **Route Builder** — tabbed GUI covering methods, job types, solvation, dispersion, TD-DFT, and other advanced route options
- **Real-time Preview** — generated route line and full `.gjf` file update instantly as you make changes
- **Round-trip Parsing** — reopen the Route Builder on an existing route and settings are restored into the UI
- **Link 0 Automation** — `%nprocshared`, `%mem`, `%chk` (auto-named from the saved filename), optional `%oldchk`
- **Additional Job (`--Link1--`)** — append a second job that reads the checkpoint (`Geom=Check Guess=Read`) or copies the current geometry
- **Z-Matrix Output** — emit coordinates as Cartesian, Gaussian Z-matrix, or Z-matrix with a `Variables:` section
- **Interactive Constraints & Scans** — click atoms in the MoleditPy 3D viewer to define ModRedundant freeze/scan lines (distance/angle/dihedral); `Opt=ModRedundant` is added to the route automatically
- **Tail Templates** — one-click insertion of `ModRedundant`, `Gen`/`GenECP` basis blocks, `$NBO`, connectivity, and `--Link1--` stubs
- **Syntax Highlighting** — `.gjf` files get colour-coded Link 0 lines, route keywords, and job separators
- **Session Persistence** — last-used settings are saved and restored between sessions
- **Preset Management** — save/apply/delete named configuration presets, plus a global "Auto Suffix" toggle

---

## Job Types

| Job | Gaussian route keyword |
|-----|-------------------------|
| Single Point Energy | `SP` *(default, no keyword)* |
| Geometry Optimisation | `Opt` |
| Frequency | `Freq` |
| Opt + Freq | `Opt Freq` |
| Transition State | `Opt=(TS,CalcFC,NoEigenTest)` |
| Scan (relaxed coordinate) | `Opt=ModRedundant` |
| IRC | `IRC=(CalcFC,MaxPoints=N)` |
| Stability Analysis | `Stable` |

---

## Supported Methods

### DFT
B3LYP, PBE1PBE (PBE0), PBEPBE, BLYP, BP86, CAM-B3LYP, ωB97XD, ωB97X, M062X, M06, M06L, APFD, B97D3, TPSSTPSS, MN15, MN15L, BHandHLYP, HSEH1PBE, LC-ωPBE, O3LYP, X3LYP, and more

### Double Hybrid
B2PLYP, mPW2PLYP, B2PLYPD3

### Wavefunction
MP2, MP3, MP4, CCSD, CCSD(T), QCISD, QCISD(T), CISD, CID

### Hartree-Fock
HF, ROHF, UHF

### Semi-Empirical
AM1, PM3, PM6, PM7, ZINDO

---

## Basis Sets

- **Pople**: 6-31G(d), 6-31+G(d,p), 6-311+G(d,p), 6-311++G(2d,2p), 6-311++G(3df,3pd), …
- **Dunning**: cc-pVDZ/TZ/QZ/5Z, aug-cc-pVDZ/TZ/QZ/5Z
- **Karlsruhe (def2)**: def2SVP, def2TZVP, def2TZVPP, def2QZVP
- **ECP / Gen**: LanL2DZ, LanL2MB, SDD, SDDAll, Gen, GenECP

---

## Solvation & Dispersion

- **Implicit solvation (SCRF)**: PCM, CPCM, SMD, IEFPCM, Dipole — with a full Gaussian solvent name list
- **Dispersion corrections**: GD2, GD3, GD3BJ, PFD

---

## Properties

| Property | Route keyword |
|----------|---------------|
| Population analysis | `Pop=NBO / NBORead / Hirshfeld / MK / CHelpG / Reg / Full` |
| Current density | `Density=Current` |
| Symmetry control | `Symmetry=Loose` / `NoSymm` |
| Integration grid | `Integral(FineGrid/UltraFine/SuperFine)` |
| TD-DFT | `TD=(NStates=N,Singlets/Triplets/50-50,Root=N)` |
| NMR shielding | `NMR=GIAO` |
| Polarizability | `Polar` |
| Wavefunction output | `Output=WFN` / `Output=WFX` (writes the `.wfn`/`.wfx` filename line automatically) |
| SCF convergence | `SCF=(XQC,Tight)` |
| Initial guess | `Guess=Mix` / `Guess=Read` |

---

## Tail Templates

One-click insertion of annotated templates:

`ModRedundant (Freeze/Scan)` · `Basis Set (Gen)` · `Effective Core Potential (GenECP)` · `NBO Analysis ($NBO)` · `Link1 (Multiple Jobs)` · `Connectivity (Geom=Connectivity)`

---

## Selected Examples

### 1 — Standard geometry optimisation + frequency (DFT-D3BJ, SMD water)

Route line produced by the Builder:

```gjf
%nprocshared=8
%mem=16GB
%chk=molecule.chk
#P B3LYP/6-31G(d) EmpiricalDispersion=GD3BJ Opt Freq SCRF=(SMD,Solvent=Water)

Title

0 1
 ...coordinates...
```

> Dispersion and solvation together in a single click; the preview updates live.

---

### 2 — Transition-state search with tight convergence

```gjf
#P wB97XD/def2TZVP Opt=(TS,CalcFC,NoEigenTest,VeryTight) Freq=NoRaman
  SCRF=(SMD,Solvent=Acetonitrile) Integral(UltraFine)
```

> Builder sets TS job type, CalcFC, VeryTight opt, and UltraFine grid from separate dropdowns — no manual typing required.

---

### 3 — Bond-length relaxed scan (ModRedundant, interactive picking)

Click two atoms in the MoleditPy 3D viewer → they appear as a Distance row in the Constraints/Scan table. Check **Scan**, set steps to 10 and step size to 0.05 Å.

Tail section auto-populated:

```gjf
#P B3LYP/6-31G(d) Opt=ModRedundant

...

B 3 7 S 10 0.05
```

> Rows removed or edited in the builder table are **removed or corrected** in the tail automatically (two-way sync, new in v1.0.0).

---

### 4 — NBO charge analysis with automatic `$NBO` tail

Select `Pop=NBORead` in the Builder → the tail section automatically gains:

```gjf
#P B3LYP/6-31G(d) Pop=NBORead

...

$NBO
  BNDIDX NBOSUM
$END
```

> The plugin detects `Pop=NBORead` in the route and inserts the `$NBO` block for you.

---

### 5 — TD-DFT excited states (5 singlets, CAM-B3LYP)

```gjf
#P CAM-B3LYP/aug-cc-pVDZ TD=(NStates=5,Singlets) SCRF=(PCM,Solvent=Acetonitrile)
```

> TD-DFT tab covers NStates, Singlets/Triplets/50-50, and Root; solvation is added simultaneously from the Solvation tab.

---

### 6 — Two-job Opt → Freq on checkpoint (`--Link1--`)

Enable **Additional Job (--Link1--)** to chain a frequency run on the optimised geometry without re-running the optimisation:

```gjf
%nprocshared=8
%mem=16GB
%chk=molecule.chk
#P B3LYP/6-31G(d) Opt

Title

0 1
 ...coordinates...

--Link1--
%oldchk=molecule.chk
%chk=molecule.chk
#P B3LYP/6-31G(d) Freq Geom=Check Guess=Read

Frequency on checkpoint

0 1
```

> `%chk` / `%oldchk` are wired automatically; only the route and title of the second job need editing.

---

## Installation

1. Ensure MoleditPy is installed.
2. Download the plugin from the [MoleditPy Plugin Explorer](https://hiroyokoyama.github.io/moleditpy-plugins/explorer/?q=Gaussian+Input+Generator+Pro) into your MoleditPy plugins directory, or copy the `gaussian_input_generator_pro/` folder directly into your plugins directory:
   - **Windows**: `C:\Users\<YourName>\.moleditpy\plugins\`
   - **Linux / macOS**: `~/.moleditpy/plugins/`
3. Restart MoleditPy — **Gaussian Input Generator Pro** will appear in the Plugins menu.

---

## Usage

1. Open a molecule in MoleditPy.
2. Launch **Gaussian Input...** from the Plugins menu.
3. Configure Link 0 resources, the route line (or use the **Builder...**), title, charge/multiplicity, and any tail input.
4. Optionally enable **Additional Job (--Link1--)** for a chained calculation (e.g. Opt followed by Freq on the checkpoint).
5. Review the **Input Preview** on the right — it updates in real time and is directly editable.
6. Click **Save Gaussian Input File...** to write the `.gjf` file. `%chk=` is rewritten to match the saved filename automatically.

---

## Testing

```bash
cd moleditpy_gaussian_input_generator_pro
python -m pytest tests/ -v
```

All tests run headlessly — PyQt6 and RDKit are stubbed, no GUI or network required. `tests/test_api.py` and `tests/test_plugin_integration.py` additionally exercise the real `PluginContext` when the main MoleditPy app repo is present as a sibling directory.

---

## Dependencies

- **PyQt6** — graphical interface
- **RDKit** — molecular geometry and property handling

---

## License & Disclaimer

Licensed under the GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.
Provided *as is* without warranty. Users are responsible for validating outputs before use in publications or production workflows. Please [open an issue](https://github.com/HiroYokoyama/moleditpy_gaussian_input_generator_pro/issues) if you find a bug.
