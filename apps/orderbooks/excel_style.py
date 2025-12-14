from io import BytesIO

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import Rule
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.colors import Color
from openpyxl.styles.differential import DifferentialStyle


class ExcelSheetNotFound(Exception):
    pass


class Styler:
    def __init__(self, buffered_file: BytesIO, name_of_sheet: str):
        self.workbook: Workbook = load_workbook(buffered_file)
        try:
            self.sheet = self.workbook[name_of_sheet]
        except KeyError:
            raise ExcelSheetNotFound("Could not find sheet in passed Excel file.")

    def add_conditional(
        self,
        formula: str,
        column_char: str,
        start_in_row: int = 2,
        fill_color: str | None = None,
        font_color: str | None = None,
    ):
        """add a conditional formula to cells of a whole row
        Args:
            formula (str): excel conditional formula like A2=42 - attention: the set number has no effect and will be replaced row per row.
            column_char (str): char of the column like A, B or C.
            start_in_row (int, optional): start point for adding (if you have a header in row 1 for instance). defaults to 2.
            fill_color (str | None, optional): hex code of fill color. defaults to None.
            font_color (str | None, optional): hex cole of font color. defaults to None.
        """
        first_cell = f"{column_char}{start_in_row}"
        last_cell = f"{column_char}{self.sheet.max_row}"
        fill_style = None
        font_style = None

        if fill_color:
            fill_style = PatternFill(patternType="solid", start_color=Color(fill_color), end_color=Color(fill_color))
        if font_color:
            font_style = Font(color=Color(font_color))

        rule = Rule(
            type="expression",
            dxf=DifferentialStyle(fill=fill_style, font=font_style),
            stopIfTrue=True,
            formula=[formula],
        )

        self.sheet.conditional_formatting.add(range_string=f"{first_cell}:{last_cell}", cfRule=rule)

    def set_auto_width(self):
        """set width of columns automatically with only one call"""
        for column in self.sheet.iter_cols():
            max_recognized_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_recognized_length:
                        max_recognized_length = len(str(cell.value))
                except Exception:
                    pass
            adjusted_width = (max_recognized_length + 2) + 2
            self.sheet.column_dimensions[column_letter].width = adjusted_width


def add_styles_to_orderbook(
    buffered_file: BytesIO,
) -> Workbook:
    # method to style orderbook in defined style (SG Glass Cologne-Porz)

    styler = Styler(buffered_file=buffered_file, name_of_sheet="Ordermanagement")

    # Sub Family == 'STD Silence'
    styler.add_conditional(formula='J2="STD Silence"', column_char="J", fill_color="aaf8ed")
    # Tint == EXTRA 'CLEAR'
    styler.add_conditional(formula='M2="EXTRA CLEAR"', column_char="M", fill_color="00ccff")
    # Laminate ends with 'P'
    styler.add_conditional(formula='right(P2,1)="P"', column_char="P", fill_color="cc99ff")
    # Quality == 61
    styler.add_conditional(formula="Q2=61", column_char="Q", fill_color="e8a7a7")
    # Quality == 22
    styler.add_conditional(formula="Q2=22", column_char="Q", font_color="617c3c")
    # Quality == 1
    styler.add_conditional(formula="Q2=1", column_char="Q", font_color="ea701e")
    # Surface Protection == EKONL
    styler.add_conditional(formula='R2="EKONL"', column_char="R", fill_color="abc785")
    # Surface Protection == FILM
    styler.add_conditional(formula='R2="FILM"', column_char="R", fill_color="abc785")
    # Surface Protection == YESF
    styler.add_conditional(formula='R2="YESF"', column_char="R", fill_color="abc785")
    # Surface Protection == ALU
    styler.add_conditional(formula='R2="ALU"', column_char="R", fill_color="abc785")
    # Surface Protection == YESA
    styler.add_conditional(formula='R2="YESA"', column_char="R", fill_color="abc785")
    # Surface Protection == EASYP
    styler.add_conditional(formula='R2="EASYP"', column_char="R", fill_color="abc785")
    # Surface Protection == NTAP+
    styler.add_conditional(formula='R2="NTAP+"', column_char="R", fill_color="abc785")
    # Surface Protection == YTAP+
    styler.add_conditional(formula='R2="YTAP+"', column_char="R", fill_color="abc785")
    # Surface Protection == 'Yes' and Sub Family == 'Planilux' or 'Parsol' or 'Venus'
    styler.add_conditional(
        formula='and( R2 = "Yes", or( J2 = "Planilux", or( J2 = "Parsol", J2 = "Venus" ) ) )',
        column_char="R",
        fill_color="abc785",
    )
    # Surface Protection == 'NONE' and Sub Family == 'Diamant'
    styler.add_conditional(formula='and( R2 = "NONE", J2 = "Diamant" )', column_char="R", fill_color="abc785")
    # Pack Type starts with 11T
    styler.add_conditional(formula='left( T2,3 ) = "11T"', column_char="T", font_color="ff9900")
    # Pack Type starts with 5T
    styler.add_conditional(formula='left( T2, 2 ) = "5T"', column_char="T", font_color="ff9901")
    # Pack Type starts with 12,6T
    styler.add_conditional(formula='left( T2, 5 ) = "12.6T"', column_char="T", font_color="ff9902")
    # OTIF Predictor == OK
    styler.add_conditional(formula='AL2="OK"', column_char="AL", font_color="92d050")
    # OTIF Predictor == NOK
    styler.add_conditional(formula='AL2="NOK"', column_char="AL", font_color="ff0000")
    # OTIF Predictor - Expected Loading Date > 14 days
    # ! Attention: formula expected date in string format 'dd.mm.yyyy'
    styler.add_conditional(
        formula='AND( AL2="NP", ( TODAY() - DATE( RIGHT( C2,4 ), MID( C2,4,2 ), LEFT( C2,2 ) ) ) > 14 )',
        column_char="AL",
        font_color="ffff00",
    )
    # OTIF Predictor - Expected Loading Date <= 14 days
    # ! Attention: formula expected date in string format 'dd.mm.yyyy'
    styler.add_conditional(
        formula='AND( AL2="NP", ( TODAY() - DATE( RIGHT( C2,4 ), MID( C2,4,2 ), LEFT( C2,2 ) ) ) <= 14 )',
        column_char="AL",
        font_color="ff8601",
    )
    # Length != 6000
    styler.add_conditional(formula="V2<>6000", column_char="V", font_color="ffcc99")
    # Width == 2550
    styler.add_conditional(formula="W2=2550", column_char="W", font_color="ffff00")
    # ETD
    styler.add_conditional(
        formula="IFERROR( ( DATE( RIGHT( C2,4 ), MID( C2,4,2 ), LEFT( C2,2 ) ) < DATE( RIGHT( AD2,4 ), MID( AD2,4,2 ), LEFT( AD2,2 ) )), false)",
        column_char="AD",
        font_color="ffc000",
    )

    # set width of columns automatically
    styler.set_auto_width()

    return styler.workbook
