from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtCore import QRegularExpression


class GaussianSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        # Link 0 lines (%nprocshared, %mem, %chk, %oldchk, ...)
        link0_format = QTextCharFormat()
        link0_format.setForeground(QColor("#B8860B"))  # DarkGoldenRod
        link0_format.setFontWeight(QFont.Weight.Bold)
        self.rules.append((QRegularExpression(r"^%.*"), link0_format))

        # Route line(s) starting with #
        route_format = QTextCharFormat()
        route_format.setForeground(QColor("#8B0000"))  # Dark Red
        route_format.setFontWeight(QFont.Weight.Bold)
        self.rules.append((QRegularExpression(r"^#.*"), route_format))

        # Method / basis / job keyword tokens on route lines
        self.rules.append(
            (
                QRegularExpression(
                    r"\b(B3LYP|PBE1PBE|WB97XD|M062X|CAM-B3LYP|APFD|MN15|MP2|CCSD|"
                    r"CCSD\(T\)|HF|Opt|Freq|SP|IRC|Stable|ModRedundant|TS|SCRF|"
                    r"EmpiricalDispersion|Pop|NoSymm|Symmetry|TD|NMR|Polar|"
                    r"Integral|GFInput|SCF|Guess|Output)\b",
                    QRegularExpression.PatternOption.CaseInsensitiveOption,
                ),
                route_format,
            )
        )

        # --Link1-- separator
        link1_format = QTextCharFormat()
        link1_format.setForeground(QColor("#7B1FA2"))  # Purple
        link1_format.setFontWeight(QFont.Weight.Bold)
        self.rules.append(
            (
                QRegularExpression(
                    r"^--Link1--\s*$", QRegularExpression.PatternOption.CaseInsensitiveOption
                ),
                link1_format,
            )
        )

        # Comments (!)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#757575"))  # Grey
        self.rules.append((QRegularExpression(r"^!.*"), comment_format))

        # Charge/multiplicity line and $NBO / **** markers
        marker_format = QTextCharFormat()
        marker_format.setForeground(QColor("#388E3C"))  # Green
        marker_format.setFontWeight(QFont.Weight.Bold)
        self.rules.append(
            (QRegularExpression(r"^\s*-?\d+\s+\d+\s*$"), marker_format)
        )
        self.rules.append(
            (
                QRegularExpression(
                    r"^\$NBO\b.*|^\$END\b.*|^\*{4}\s*$",
                    QRegularExpression.PatternOption.CaseInsensitiveOption,
                ),
                marker_format,
            )
        )

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            match_it = pattern.globalMatch(text)
            while match_it.hasNext():
                m = match_it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
