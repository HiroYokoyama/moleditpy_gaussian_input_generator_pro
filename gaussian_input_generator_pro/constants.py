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
