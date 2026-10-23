# Input generation audit — 2026-10-24

Scope: production Python modules, keyword/catalog data, generation, input
recovery, Cartesian/internal coordinates, charge/spin checks, constraints,
resource and checkpoint handling, presets/project persistence, save/submit and
window lifecycle. Review combines source reading and documentation comparison
with targeted regressions and the complete repository test suite.

## Shared fixes

- Export host Angstrom coordinates in the length units selected by the job.
  Gaussian radian Z-matrices convert angular values as well.
- Keep ghost labels in the custom-symbol property used by writers and electron
  counting; imported ghosts must not become real atoms after Refresh.
- Refuse nonfinite coordinate data and fall back from undefined linear Z-matrix
  reference planes rather than writing NaN values.
- Validate the spin range as well as electron/spin parity. This is a necessary
  electron-count check, not a prediction of the ground-state multiplicity.
- Recover existing methods/bases without injecting the builder's default basis.
- Preserve full imported/edited source and optional JSON input_text behavior.

## Gaussian fixes

- Checkpoint geometry modes honor the required omission of input sections,
  including Geom=(...,AllCheck) option lists and general-basis tails.
- Link1 does not reapply Job 1's OldChk source, which would replace the updated
  checkpoint. Checkpoint selection produces a Geom=Check job when omitted.
- Copy-coordinate jobs use Job 2's units; explicit checkpoint keywords omit
  redundant coordinates even if the Copy control was left selected.
- Job 2 emits its own WFN/WFX filename. Preserve uppercase .CHK extensions.
- TS selection no longer silently adds NoEigenTest; explicitly supplied
  NoEigenTest remains available. Correct catalog Opt=CalcHess to Opt=CalcFC and
  the M062X method spelling.

## Primary sources

- [Gaussian Inc. GaussView 6 documentation](https://gaussian.com/wp-content/uploads/dl/gv6.pdf), especially the checkpoint-data and calculation-setup keyword tables.
- [Gaussian route reference](https://gaussian.com/route/)
- [Gaussian Geom reference](https://gaussian.com/geom/)
- [Gaussian Units reference](https://gaussian.com/units/)
- [Gaussian Opt reference](https://gaussian.com/opt/)

Some Gaussian web pages returned HTTP 403/502 during this audit. The indexed
official GaussView manual provided the accessible checkpoint keyword mapping;
individual blocked pages are listed as references, not claimed as fetched.

## Limits

Neither the licensed Gaussian executable nor an ORCA executable was run in this
workspace. Passing these checks validates the generator behavior covered, not
every engine-version/method/basis/ECP combination. Complex syntax outside the
recovered controls remains authoritative source text; explicitly refreshing can
discard unsupported instructions. Examples/templates require user-specific
geometry, active-space, basis/ECP and resource choices.

No private input, host settings or calculation data are used as fixtures.

## Validation result

- Full local suite: 641 passed, with real PySide6/RDKit installed.
- Ruff E4/E7/E9/F/I checks and changed-file formatting pass; Python 3.9 syntax parsing passes. Broader workspace lint rules retain pre-existing logging/broad-catch style findings.
