# Gaussian 16 keyword data used by the Route Builder and main dialog.

# --- Methods ------------------------------------------------------------

DFT_METHODS = [
    "B3LYP",
    "B3PW91",
    "PBE1PBE",
    "PBEPBE",
    "BLYP",
    "BP86",
    "CAM-B3LYP",
    "wB97XD",
    "wB97X",
    "wB97",
    "M062X",
    "M06",
    "M06L",
    "M06HF",
    "APFD",
    "B97D3",
    "TPSSTPSS",
    "MN15",
    "MN15L",
    "BHandHLYP",
    "HSEH1PBE",
    "LC-wPBE",
    "O3LYP",
    "X3LYP",
]

DOUBLE_HYBRID_METHODS = [
    "B2PLYP",
    "mPW2PLYP",
    "B2PLYPD3",
]

WAVEFUNCTION_METHODS = [
    "MP2",
    "MP3",
    "MP4",
    "MP4(SDQ)",
    "MP4(SDTQ)",
    "CCSD",
    "CCSD(T)",
    "QCISD",
    "QCISD(T)",
    "CISD",
    "CID",
]

HF_METHODS = [
    "HF",
    "ROHF",
    "UHF",
]

SEMI_EMPIRICAL_METHODS = [
    "AM1",
    "PM3",
    "PM6",
    "PM7",
    "ZINDO",
]

ALL_GAUSSIAN_METHODS = (
    DFT_METHODS
    + DOUBLE_HYBRID_METHODS
    + WAVEFUNCTION_METHODS
    + HF_METHODS
    + SEMI_EMPIRICAL_METHODS
)

# --- Basis sets -----------------------------------------------------------

POPLE_BASIS_SETS = [
    "STO-3G",
    "3-21G",
    "6-31G",
    "6-31G(d)",
    "6-31G(d,p)",
    "6-31+G(d)",
    "6-31+G(d,p)",
    "6-31++G(d,p)",
    "6-311G",
    "6-311G(d,p)",
    "6-311+G(d,p)",
    "6-311++G(d,p)",
    "6-311++G(2d,2p)",
    "6-311++G(3df,3pd)",
]

DUNNING_BASIS_SETS = [
    "cc-pVDZ",
    "cc-pVTZ",
    "cc-pVQZ",
    "cc-pV5Z",
    "aug-cc-pVDZ",
    "aug-cc-pVTZ",
    "aug-cc-pVQZ",
    "aug-cc-pV5Z",
]

DEF2_BASIS_SETS = [
    "def2SVP",
    "def2TZVP",
    "def2TZVPP",
    "def2QZVP",
]

ECP_BASIS_SETS = [
    "LanL2DZ",
    "LanL2MB",
    "SDD",
    "SDDAll",
    "Gen",
    "GenECP",
]

ALL_GAUSSIAN_BASIS_SETS = (
    POPLE_BASIS_SETS + DUNNING_BASIS_SETS + DEF2_BASIS_SETS + ECP_BASIS_SETS
)

# --- Solvation --------------------------------------------------------------

SOLVATION_MODELS = ["None", "PCM", "CPCM", "SMD", "IEFPCM", "Dipole"]

GAUSSIAN_SOLVENTS = [
    "Water",
    "Acetonitrile",
    "Methanol",
    "Ethanol",
    "IsoQuinoline",
    "Quinoline",
    "Chloroform",
    "DiChloroMethane",
    "DiChloroEthane",
    "CarbonTetraChloride",
    "Benzene",
    "Toluene",
    "Chlorobenzene",
    "NitroBenzene",
    "CycloHexane",
    "Aniline",
    "Acetone",
    "TetraHydroFuran",
    "DiMethylSulfoxide",
    "Argon",
    "Krypton",
    "Xenon",
    "n-Octanol",
    "1,1,1-TriChloroEthane",
    "1,1,2-TriChloroEthane",
    "1,2,4-TriMethylBenzene",
    "1,2-DiBromoEthane",
    "1,2-EthaneDiol",
    "1,4-Dioxane",
    "1-Bromo-2-MethylPropane",
    "1-BromoOctane",
    "1-BromoPentane",
    "1-BromoPropane",
    "1-Butanol",
    "1-ChloroHexane",
    "1-ChloroPentane",
    "1-ChloroPropane",
    "1-Decanol",
    "1-FluoroOctane",
    "1-Heptanol",
    "1-Hexanol",
    "1-Hexene",
    "1-Hexyne",
    "1-IodoButane",
    "1-IodoHexaDecane",
    "1-IodoPentane",
    "1-IodoPropane",
    "1-NitroPropane",
    "1-Nonanol",
    "1-Pentanol",
    "1-Pentene",
    "1-Propanol",
    "2,2,2-TrifluoroEthanol",
    "2,2,4-TrimethylPentane",
    "2,4-DimethylPentane",
    "2,4-DimethylPyridine",
    "2,6-DimethylPyridine",
    "2-BromoPropane",
    "2-Butanol",
    "2-ChloroButane",
    "2-Heptanone",
    "2-Hexanone",
    "2-MethoxyEthanol",
    "2-Methyl-1-Propanol",
    "2-Methyl-2-Propanol",
    "2-MethylPentane",
    "2-MethylPyridine",
    "2-NitroPropane",
    "2-Octanone",
    "2-Pentanone",
    "2-Propanol",
    "2-Propen-1-ol",
    "3-MethylPyridine",
    "3-Pentanone",
    "4-Heptanone",
    "4-Methyl-2-Pentanone",
    "4-MethylPyridine",
    "5-Nonanone",
    "AceticAcid",
    "AcetoPhenone",
    "a-ChloroToluene",
    "Anisole",
    "Benzaldehyde",
    "BenzoNitrile",
    "BenzylAlcohol",
    "BromoBenzene",
    "BromoEthane",
    "Bromoform",
    "Butanal",
    "ButanoicAcid",
    "ButanoNitrile",
    "Butanone",
    "ButylAmine",
    "ButylEthanoate",
    "CarbonDiSulfide",
    "Cis-1,2-DimethylCyclohexane",
    "Cis-Decalin",
    "CycloHexanone",
    "CycloPentane",
    "CycloPentanol",
    "CycloPentanone",
    "Decalin-mixture",
    "DiBromoMethane",
    "DiButylEther",
    "DiEthylAmine",
    "DiethylEther",
    "DiEthylSulfide",
    "DiIodoMethane",
    "DiIsoPropylEther",
    "DiMethylDiSulfide",
    "DiPhenylEther",
    "DiPropylAmine",
    "e-1,2-DiChloroEthene",
    "e-2-Pentene",
    "EthaneThiol",
    "EthylBenzene",
    "EthylEthanoate",
    "EthylMethanoate",
    "EthylPhenylEther",
    "FluoroBenzene",
    "Formamide",
    "FormicAcid",
    "Heptane",
    "HexanoicAcid",
    "IodoBenzene",
    "IodoEthane",
    "IodoMethane",
    "IsoPropylBenzene",
    "m-Cresol",
    "m-Xylene",
    "Mesitylene",
    "MethylBenzoate",
    "MethylButanoate",
    "MethylCycloHexane",
    "MethylEthanoate",
    "MethylMethanoate",
    "MethylPropanoate",
    "n-ButylBenzene",
    "n-Decane",
    "n-Dodecane",
    "n-HexaDecane",
    "n-Hexane",
    "N-MethylAniline",
    "N-MethylFormamide-mixture",
    "N,N-DiMethylAcetamide",
    "N,N-DiMethylFormamide",
    "NitroEthane",
    "NitroMethane",
    "n-Nonane",
    "n-Octane",
    "n-PentaDecane",
    "n-Pentane",
    "n-Undecane",
    "o-ChloroToluene",
    "o-Cresol",
    "o-DiChloroBenzene",
    "o-NitroToluene",
    "o-Xylene",
    "p-IsoPropylToluene",
    "p-Xylene",
    "Pentanal",
    "PentanoicAcid",
    "PentylAmine",
    "PentylEthanoate",
    "PerFluoroBenzene",
    "Propanal",
    "PropanoicAcid",
    "PropanoNitrile",
    "PropylAmine",
    "PropylEthanoate",
    "Pyridine",
    "sec-ButylBenzene",
    "tert-ButylBenzene",
    "TetraChloroEthene",
    "TetraHydroThiophene-S,S-Dioxide",
    "Tetralin",
    "Thiophene",
    "Thiophenol",
    "trans-Decalin",
    "TriButylPhosphate",
    "TriChloroEthene",
    "TriEthylAmine",
    "Xylene-mixture",
    "z-1,2-DiChloroEthene",
]

DISPERSION_OPTIONS = ["None", "GD3", "GD3BJ", "GD2", "PFD"]

# --- Job types / options ----------------------------------------------------

JOB_TYPES = [
    "Optimization + Freq (Opt Freq)",
    "Optimization Only (Opt)",
    "Frequency Only (Freq)",
    "Single Point Energy (SP)",
    "Transition State Opt (Opt=TS)",
    "Scan (ModRedundant)",
    "IRC",
    "Stability Analysis (Stable)",
]

OPT_OPTIONS = [
    "Tight",
    "VeryTight",
    "CalcFC",
    "CalcAll",
    "ModRedundant",
]

FREQ_OPTIONS = ["Raman", "NoRaman", "VCD", "Anharmonic"]

POP_OPTIONS = ["None", "NBO", "NBORead", "Hirshfeld", "MK", "CHelpG", "Reg", "Full"]

GRID_OPTIONS = ["Default", "FineGrid", "UltraFine", "SuperFine"]

SCF_GUESS_OPTIONS = ["Default", "Mix", "Read"]

# --- Tail templates ---------------------------------------------------------

TAIL_TEMPLATES = {
    "ModRedundant (Freeze/Scan)": (
        "! Format: [Action] [Indices/Atoms] [Options]\n"
        "! B i j F           : Freeze bond between atom i and j\n"
        "! A i j k S 10 1.0  : Scan angle i-j-k, 10 steps, 1.0 deg each\n"
        "! D i j k l R       : Release dihedral constraint\n"
        "B 1 2 F\n"
    ),
    "Basis Set (Gen)": (
        "! Format for Gen/GenECP:\n"
        "! [Atoms] 0\n"
        "! [Basis Set Name]\n"
        "! ****\n"
        "C H O 0\n"
        "6-31G(d)\n"
        "****\n"
        "Fe 0\n"
        "LanL2DZ\n"
        "****\n\n"
    ),
    "Effective Core Potential (GenECP)": (
        "! Appended at the very end after basis sets if GenECP used\n"
        "Fe 0\n"
        "LanL2DZ\n"
    ),
    "NBO Analysis ($NBO)": (
        "! Requires Pop=NBORead in route\n$NBO\n  BNDIDX NBOSUM\n$END\n\n"
    ),
    "Link1 (Multiple Jobs)": (
        "\n--Link1--\n"
        "%Chk=filename.chk\n"
        "#P Freq Geom=Check Guess=Read\n"
        "\n"
        "Frequency calculation\n"
        "\n"
        "0 1\n"
    ),
    "Connectivity (Geom=Connectivity)": (
        "! Required if Geom=Connectivity is in route line\n"
        "1 2 1.0 3 1.0\n"
        "2 1 1.0\n"
        "3 1 1.0\n"
    ),
}

GAUSSIAN_SEARCH_CATALOG = [
    # --- Job Types & Tasks ---
    ("Job Types", "Opt", "Geometry Optimization to local minimum"),
    ("Job Types", "Freq", "Harmonic Vibrational Frequency calculation and thermochemistry"),
    ("Job Types", "Opt Freq", "Optimization followed immediately by Frequency calculation"),
    ("Job Types", "Opt=(TS,CalcFC)", "Transition State search calculating initial force constants"),
    ("Job Types", "Opt=(TS,ReadFC)", "Transition State search reading force constants from checkpoint"),
    ("Job Types", "Opt=ModRedundant", "Optimization with frozen or scanned coordinates"),
    ("Job Types", "Opt=Tight", "Tight optimization convergence criteria"),
    ("Job Types", "Opt=VeryTight", "Very tight optimization convergence criteria"),
    ("Job Types", "Opt=Loose", "Loose optimization convergence criteria (for initial structures)"),
    ("Job Types", "Opt=QST2", "Synchronous Transit-Guided Quasi-Newton TS search between 2 structures"),
    ("Job Types", "Opt=QST3", "Synchronous Transit-Guided Quasi-Newton TS search using reactant, product, and TS guess"),
    ("Job Types", "Opt=CalcHess", "Calculate exact analytical Hessian at first step"),
    ("Job Types", "Opt=Cartesian", "Optimize in Cartesian coordinates rather than redundant internals"),
    ("Job Types", "IRC", "Intrinsic Reaction Coordinate path integration from TS"),
    ("Job Types", "IRC=(Forward,RCFC)", "Follow IRC in forward direction calculating force constants"),
    ("Job Types", "IRC=(Reverse,RCFC)", "Follow IRC in reverse direction calculating force constants"),
    ("Job Types", "IRC=(CalcFC,MaxPoints=50)", "IRC path integration with 50 points and initial Hessian"),
    ("Job Types", "SP", "Single-point energy evaluation"),
    ("Job Types", "Scan", "Rigid Potential Energy Surface Scan"),
    ("Job Types", "Polar", "Electric dipole polarizabilities and hyperpolarizabilities"),
    ("Job Types", "Polar=Opt", "Compute polarizability at each optimization step"),
    ("Job Types", "HyperPolar", "Compute frequency-dependent hyperpolarizabilities"),
    ("Job Types", "NMR=GIAO", "NMR chemical shielding tensors using GIAO method"),
    ("Job Types", "NMR=CSGT", "NMR chemical shielding tensors using Continuous Set of Gauge Transformations"),
    ("Job Types", "Volume", "Compute molecular volume inside electron density contour"),
    ("Job Types", "Stable", "Test wavefunction stability (look for internal/external instabilities)"),
    ("Job Types", "Stable=Opt", "Test wavefunction stability and re-optimize to stable state if unstable"),

    # --- Methods / Functionals ---
    ("Methods / Functionals", "B3LYP", "Becke 3-parameter hybrid GGA with Lee-Yang-Parr correlation"),
    ("Methods / Functionals", "PBE1PBE", "Perdew-Burke-Ernzerhof hybrid functional (PBE0)"),
    ("Methods / Functionals", "wB97XD", "Chai-Head-Gordon range-separated hybrid with empirical dispersion"),
    ("Methods / Functionals", "wB97X", "Chai-Head-Gordon range-separated hybrid functional"),
    ("Methods / Functionals", "M06-2X", "Truhlar hybrid meta-GGA (54% HF exchange, main-group kinetics)"),
    ("Methods / Functionals", "M06", "Minnesota hybrid meta-GGA functional for transition metals"),
    ("Methods / Functionals", "M06-L", "Minnesota local pure meta-GGA functional"),
    ("Methods / Functionals", "M06-HF", "Minnesota hybrid functional with 100% HF exchange"),
    ("Methods / Functionals", "MN15", "Kohn-Sham hybrid meta-NGA functional with broad accuracy"),
    ("Methods / Functionals", "MN15-L", "Local meta-NGA functional"),
    ("Methods / Functionals", "CAM-B3LYP", "Coulomb-attenuating method range-separated hybrid"),
    ("Methods / Functionals", "LC-wPBE", "Long-range corrected PBE functional"),
    ("Methods / Functionals", "B3PW91", "Becke 3-parameter hybrid with Perdew-Wang 91 correlation"),
    ("Methods / Functionals", "BP86", "Becke 88 exchange with Perdew 86 correlation (pure GGA)"),
    ("Methods / Functionals", "BLYP", "Becke-Lee-Yang-Parr pure GGA functional"),
    ("Methods / Functionals", "PBEPBE", "Perdew-Burke-Ernzerhof non-empirical pure GGA functional"),
    ("Methods / Functionals", "HSEH1PBE", "Heyd-Scuseria-Ernzerhof screened Coulomb hybrid (HSE06)"),
    ("Methods / Functionals", "TPSSTPSS", "Tao-Perdew-Staroverov-Scuseria meta-GGA functional"),
    ("Methods / Functionals", "TPSSh", "Hybrid meta-GGA functional (10% HF exchange)"),
    ("Methods / Functionals", "APFD", "Austin-Frisch-Petersson functional with dispersion"),
    ("Methods / Functionals", "B97D3", "Becke 97 functional with Grimme D3 dispersion"),
    ("Methods / Functionals", "B2PLYP", "Grimme double-hybrid functional (includes MP2 correlation)"),
    ("Methods / Functionals", "mPW2PLYP", "Modified PW91 double-hybrid functional"),
    ("Methods / Functionals", "B2PLYPD3", "B2PLYP double-hybrid with DFT-D3 dispersion"),
    ("Methods / Functionals", "DSDPBEP86", "Dispersion-corrected, spin-component-scaled double hybrid"),
    ("Methods / Functionals", "MP2", "Second-order Møller-Plesset perturbation theory"),
    ("Methods / Functionals", "MP3", "Third-order Møller-Plesset perturbation theory"),
    ("Methods / Functionals", "MP4", "Fourth-order Møller-Plesset perturbation theory"),
    ("Methods / Functionals", "MP4(SDQ)", "MP4 excluding triple excitations"),
    ("Methods / Functionals", "CCSD", "Coupled Cluster with Single and Double excitations"),
    ("Methods / Functionals", "CCSD(T)", "Coupled Cluster with Singles, Doubles, and perturbative Triples"),
    ("Methods / Functionals", "QCISD", "Quadratic Configuration Interaction with Singles and Doubles"),
    ("Methods / Functionals", "QCISD(T)", "QCISD with perturbative Triples"),
    ("Methods / Functionals", "HF", "Hartree-Fock self-consistent field"),
    ("Methods / Functionals", "UHF", "Unrestricted Hartree-Fock for open-shell systems"),
    ("Methods / Functionals", "ROHF", "Restricted Open-Shell Hartree-Fock"),
    ("Methods / Functionals", "PM6", "Stewart PM6 semi-empirical parameterization"),
    ("Methods / Functionals", "PM7", "Stewart PM7 semi-empirical parameterization"),
    ("Methods / Functionals", "AM1", "Austin Model 1 semi-empirical method"),
    ("Methods / Functionals", "PM3", "Parameterized Model number 3 semi-empirical method"),
    ("Methods / Functionals", "CASSCF", "Complete active space multiconfiguration SCF"),

    # --- Basis Sets ---
    ("Basis Sets", "6-31G(d)", "Pople split-valence double-zeta with polarization on heavy atoms"),
    ("Basis Sets", "6-31G(d,p)", "Pople split-valence double-zeta with polarization on all atoms"),
    ("Basis Sets", "6-31+G(d)", "Pople split-valence with diffuse functions on heavy atoms"),
    ("Basis Sets", "6-31+G(d,p)", "Pople split-valence double-zeta with diffuse and polarization"),
    ("Basis Sets", "6-311G(d,p)", "Pople triple-zeta valence with polarization functions"),
    ("Basis Sets", "6-311+G(d,p)", "Pople triple-zeta valence with diffuse and polarization functions"),
    ("Basis Sets", "6-311++G(d,p)", "Pople triple-zeta with diffuse on both heavy atoms and hydrogens"),
    ("Basis Sets", "6-311++G(2d,2p)", "Pople triple-zeta with double polarization and diffuse on all atoms"),
    ("Basis Sets", "6-311++G(3df,3pd)", "Pople triple-zeta with extensive diffuse and high-angular polarization"),
    ("Basis Sets", "def2SVP", "Karlsruhe split-valence polarized basis set"),
    ("Basis Sets", "def2TZVP", "Karlsruhe triple-zeta valence polarized basis set"),
    ("Basis Sets", "def2TZVPP", "Karlsruhe triple-zeta valence double-polarized basis set"),
    ("Basis Sets", "def2QZVP", "Karlsruhe quadruple-zeta valence polarized basis set"),
    ("Basis Sets", "def2QZVPP", "Karlsruhe quadruple-zeta valence double-polarized basis set"),
    ("Basis Sets", "cc-pVDZ", "Dunning correlation-consistent double-zeta basis"),
    ("Basis Sets", "cc-pVTZ", "Dunning correlation-consistent triple-zeta basis"),
    ("Basis Sets", "cc-pVQZ", "Dunning correlation-consistent quadruple-zeta basis"),
    ("Basis Sets", "aug-cc-pVDZ", "Augmented Dunning correlation-consistent double-zeta basis"),
    ("Basis Sets", "aug-cc-pVTZ", "Augmented Dunning correlation-consistent triple-zeta basis"),
    ("Basis Sets", "aug-cc-pVQZ", "Augmented Dunning correlation-consistent quadruple-zeta basis"),
    ("Basis Sets", "LANL2DZ", "Los Alamos effective core potential with double-zeta valence"),
    ("Basis Sets", "SDD", "Stuttgart-Dresden effective core potential and basis"),
    ("Basis Sets", "Gen", "User-specified general basis set entered in input tail"),
    ("Basis Sets", "GenECP", "General basis set and pseudopotential in input tail"),
    ("Basis Sets", "STO-3G", "Minimal Pople basis set (3 Gaussian primitives per Slater orbital)"),

    # --- Solvation (SCRF) ---
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Water)", "SMD universal solvation model for water"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Acetonitrile)", "SMD universal solvation model for acetonitrile"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Methanol)", "SMD universal solvation model for methanol"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Ethanol)", "SMD universal solvation model for ethanol"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Chloroform)", "SMD universal solvation model for chloroform"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Dichloromethane)", "SMD universal solvation model for dichloromethane"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Toluene)", "SMD universal solvation model for toluene"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Tetrahydrofuran)", "SMD universal solvation model for THF"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Dimethylsulfoxide)", "SMD universal solvation model for DMSO"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Cyclohexane)", "SMD universal solvation model for cyclohexane"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Benzene)", "SMD universal solvation model for benzene"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Acetone)", "SMD universal solvation model for acetone"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=CarbonTetrachloride)", "SMD universal solvation model for carbon tetrachloride"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=N,N-Dimethylformamide)", "SMD universal solvation model for DMF"),
    ("Solvation (SCRF)", "SCRF=(SMD,Solvent=Pyridine)", "SMD universal solvation model for pyridine"),
    ("Solvation (SCRF)", "SCRF=(PCM,Solvent=Water)", "Polarizable continuum model (IEFPCM) for water"),
    ("Solvation (SCRF)", "SCRF=(PCM,Solvent=Acetonitrile)", "IEFPCM solvation for acetonitrile"),
    ("Solvation (SCRF)", "SCRF=(PCM,Solvent=Dichloromethane)", "IEFPCM solvation for DCM"),
    ("Solvation (SCRF)", "SCRF=(PCM,Solvent=Tetrahydrofuran)", "IEFPCM solvation for THF"),
    ("Solvation (SCRF)", "SCRF=(PCM,Solvent=Toluene)", "IEFPCM solvation for toluene"),
    ("Solvation (SCRF)", "SCRF=(CPCM,Solvent=Water)", "Conductor-like Polarizable Continuum Model for water"),

    # --- Dispersion Corrections ---
    ("Dispersion", "EmpiricalDispersion=GD3BJ", "Grimme DFT-D3 empirical dispersion with Becke-Johnson damping"),
    ("Dispersion", "EmpiricalDispersion=GD3", "Grimme DFT-D3 empirical dispersion with zero damping"),
    ("Dispersion", "EmpiricalDispersion=GD2", "Grimme DFT-D2 empirical dispersion correction"),
    ("Dispersion", "EmpiricalDispersion=PFD", "Petersson-Frisch dispersion model"),

    # --- Convergence, SCF & Numerical Grids ---
    ("Convergence & SCF", "SCF=XQC", "Extra quadratic convergence algorithm for difficult SCF cases"),
    ("Convergence & SCF", "SCF=Tight", "Tight SCF convergence criteria (10^-8 RMS on density matrix)"),
    ("Convergence & SCF", "SCF=VeryTight", "Very tight SCF convergence criteria"),
    ("Convergence & SCF", "SCF=QC", "Quadratively convergent SCF algorithm"),
    ("Convergence & SCF", "SCF=YQC", "Check DIIS progress and switch to QC if necessary"),
    ("Convergence & SCF", "SCF=DM", "Direct Minimization SCF orbital optimizer"),
    ("Convergence & SCF", "SCF=VShift", "Apply dynamic virtual orbital level shifting to facilitate convergence"),
    ("Convergence & SCF", "SCF=(MaxCycle=512)", "Increase maximum SCF iteration cycles to 512"),
    ("Convergence & SCF", "Integral(Grid=UltraFine)", "UltraFine pruned (99,590) numerical integration grid"),
    ("Convergence & SCF", "Integral(Grid=SuperFine)", "SuperFine pruned integration grid for high-precision DFT"),
    ("Convergence & SCF", "Integral(Grid=Fine)", "Fine integration grid (75,302)"),
    ("Convergence & SCF", "Integral(Grid=Coarse)", "Coarse integration grid (35,110) for rapid screening"),
    ("Convergence & SCF", "Guess=Read", "Read initial wavefunction guess from checkpoint file (%Chk)"),
    ("Convergence & SCF", "Guess=Mix", "Mix HOMO and LUMO to break spatial symmetry for open-shell singlets"),
    ("Convergence & SCF", "Guess=HCore", "Use diagonalized core Hamiltonian as initial guess"),
    ("Convergence & SCF", "Guess=Alter", "Manually alter orbital occupations in input tail"),
    ("Convergence & SCF", "NoSymm", "Disable all spatial symmetry constraints (useful for open-shell)"),

    # --- Population Analysis & Output ---
    ("Population & Output", "Pop=NBO6", "Natural Bond Orbital version 6 analysis"),
    ("Population & Output", "Pop=NBO7", "Natural Bond Orbital version 7 analysis"),
    ("Population & Output", "Pop=NBO", "Default Natural Bond Orbital analysis"),
    ("Population & Output", "Pop=NBORead", "NBO analysis reading $NBO options keylist in input tail"),
    ("Population & Output", "Pop=CHelpG", "Charges from Electrostatic Potentials using a Grid-based method"),
    ("Population & Output", "Pop=MK", "Merz-Kollman electrostatic potential atomic charges"),
    ("Population & Output", "Pop=Hirshfeld", "Hirshfeld atomic population and charge analysis"),
    ("Population & Output", "Pop=NaturalOrbitals", "Compute natural orbitals and their occupation numbers"),
    ("Population & Output", "Pop=Full", "Print full population analysis including all orbital contributions"),
    ("Population & Output", "GFInput", "Print basis set definition in Gaussian format in output file"),
    ("Population & Output", "GFPrint", "Print basis set details and primitive exponents"),
    ("Population & Output", "Output=WFN", "Write traditional PROAIM .wfn wavefunction file"),
    ("Population & Output", "Output=WFX", "Write extended .wfx wavefunction file for AIMAll / QTAIM"),
    ("Population & Output", "Density=Current", "Use post-SCF relaxed electron density for properties"),
    ("Population & Output", "Density=All", "Compute properties for all states / methods"),

    # --- Properties & Spectroscopy ---
    ("Properties & Advanced", "TD(NStates=10)", "Time-dependent DFT calculation for 10 excited states"),
    ("Properties & Advanced", "TD(Singlets,NStates=10)", "TD-DFT for 10 singlet excited states"),
    ("Properties & Advanced", "TD(Triplets,NStates=10)", "TD-DFT for 10 triplet excited states"),
    ("Properties & Advanced", "TD(50-50,NStates=10)", "TD-DFT for both singlet and triplet states"),
    ("Properties & Advanced", "TD(Root=1)", "Optimize geometry or compute properties for the 1st excited state"),
    ("Properties & Advanced", "TDA", "Tamm-Dancoff Approximation for TD-DFT"),
    ("Properties & Advanced", "CIS", "Configuration Interaction Singles for excited states"),
    ("Properties & Advanced", "ZINDO", "Zerner INDO semi-empirical spectroscopy calculation"),
    ("Properties & Advanced", "NMR=GIAO", "NMR magnetic shielding tensors via GIAO"),
    ("Properties & Advanced", "Polar", "Static dipole polarizability and optical properties"),
]


