import logging
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from zipfile import BadZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import Rule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.styles.colors import Color
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.worksheet.worksheet import Worksheet

from .exceptions import ExcelFileFormatWrong, ExcelSheetNotFound


DEFAULT_HEADER_ROWS = 1
MAX_EXCEL_SHEET_ROW_COUNT = 1_048_576

log = logging.getLogger("django.ordermanagement")


class ExcelSheetStyler:
    """With passing a collection of 'Definition's style will be executed on Excel sheet.
    With passing a 'Header' object you can style the defined header rows.
    Please pass first the Header and afterwards a collection of Definitions to avoid unexpected results."""

    @dataclass
    class Definition:
        """### Style class to define "Excel Conditional Formatting' for one column.
        - `column` (str):
            - Can be the column letter like 'A'
            - or a name in the column header (first row on sheet)
        embedded with underlines like '__Column Name__'.
        - `formula` (str | None) (default is None):
            - Defines a formula in Excel style like ' A2="whatever" ' - with this
        definition the row index will adjusted automatically to fill all cells
        in the whole column.
            - But there is another way: use header names (first row of sheet)
            like '__column Name__' to describe a formula
        such as ' __Column Name__="whatever" '.
        - `fill_color_hex` (str | None) (default is None): Background color
        of a cell - format is hexadecimal.
        - `font_color_hex` (str | None) (default is None): Color of font
        in a cell - format is hexadecimal.
        - `hide` (bool) (default is False): To hide a entire column (not
        visible but included formulas are working).
        - `auto_width` (bool) (default is True): To adjust the width of a
        column automatically to the largest column's cell content.
        - `width_factor` (bool) (default is 1): to correct set width
        (sometimes needed in special scenarios).
        - `parse_to_date` (list[str]) (default is None): With passing a list
        including schemas a method will try to parse them into date type.
        """

        column: str
        formula: str | None = None
        fill_color_hex: str | None = None
        font_color_hex: str | None = None
        hide: bool = False
        auto_width: bool = True
        width_factor: float = 1
        parse_to_date: list[str] | None = None

    @dataclass
    class Header:
        """### Style class to set styling of Excel Sheet's defined header area
        - `wrapped`: to collapse text with spaces between words
        (By aware: has effect on column width calculation)
        - `fill_color_hex` (str | None) (default is None): Background color
        of a cell - format is hexadecimal.
        - `font_color_hex` (str | None) (default is None): Color of font
        in a cell - format is hexadecimal.
        - `bold` (bool) (default is True): Font weight (bold or not).
        """

        wrapped: bool = True
        fill_color_hex: str | None = None
        font_color_hex: str | None = None
        bold: bool = True

    def __init__(self, buffer: BytesIO, sheet_name: str, count_of_header_rows: int = DEFAULT_HEADER_ROWS):
        """
        - `buffer` (ByteeIO): Excel File.
        - `sheet_name`: (str): name of sheet to style.
        - `count_of_header_rows` (int) (default is 1): to exclude these rows from styling.
        But be aware: formulas are only use the first row for recognize column letter by naming.
        - Exceptions: `ExcelSheetNotFound` if sheet not available (wrong naming or wrong file format).
        """
        try:
            self.workbook: Workbook = load_workbook(buffer)
            self.workbook.iso_dates = True
            self.sheet: Worksheet = self.workbook[sheet_name]
        except BadZipFile as exc:
            raise ExcelFileFormatWrong(f"Could not read file. {exc=}")
        except KeyError as exc:
            raise ExcelSheetNotFound(f"Could not find sheet in passed Excel file. {exc=}")
        self.first_row_of_content = (
            count_of_header_rows
            if count_of_header_rows >= 0 and count_of_header_rows < MAX_EXCEL_SHEET_ROW_COUNT
            else DEFAULT_HEADER_ROWS
        ) + 1
        self.mapping: dict[str, str] = self._build_header_letter_mapping(sheet=self.sheet)
        self.style_log: list[dict] = []
        self.header_content_is_wrapped = False

    def apply_conditional_collection(
        self,
        style_collection: list[Definition] | None = None,
        header: Header | None = None,
        style_definitions: list[Definition] | None = None,
    ):
        """### Apply an 'Excel Conditional Formatting' collection.
        Pass header to style defined header area."""
        if header:
            self.style_header(header_style=header)
        definitions = style_collection if style_collection is not None else style_definitions or []
        for definition in definitions:
            self.apply_conditional(definition=definition)

    def apply_conditional(self, definition: Definition | None = None, style: Definition | None = None) -> bool:
        """### Apply a single 'Excel Conditional Formatting' on entire column's cells.
        - `style` (Definition): class with different settings to style.
        returns True or False by errors.
        """
        definition = definition or style
        if definition is None:
            return False
        if not self._column_letter_is_valid(definition=definition):
            return False
        self._set_conditional_format(definition=definition)
        self._set_auto_width(definition=definition)
        self._hide_column(definition=definition)
        self._parse_to_date(definition=definition)
        self._set_style_log(definition=definition)
        return True

    def style_header(self, header_style: Header):
        """### Style header of Excel by passing Header object.
        - Attention: Method (over)writes 'header_content_is_wrapped' attribute,
        is important later for calculating width of columns."""
        if self.first_row_of_content != 0:
            self.header_content_is_wrapped = header_style.wrapped
            # hint: used index here for area (e.g. "1:5") is Excel like (starts with 1)
            for cells in self.sheet[f"1:{self.first_row_of_content - 1}"]:
                if not isinstance(cells, tuple):
                    # hint: cells in area of "1:2" are packed in tuples - in area "1:1" are not (single cell).
                    cells = (cells,)
                for cell in cells:
                    cell.alignment = Alignment(wrap_text=header_style.wrapped)
                    cell.font = self._set_font_style(
                        font_color_hex=header_style.font_color_hex, bold=header_style.bold
                    )
                    cell.fill = self._set_fill_style(fill_color_hex=header_style.fill_color_hex)

    def get_workbook_as_buffer(self) -> BytesIO:
        """Save styled workbook into a new buffer."""
        new_buffer = BytesIO()
        self.workbook.save(new_buffer)
        return new_buffer

    def _set_style_log(self, definition: Definition):
        """remember the order of used styles in a list (for debugging)."""
        self.style_log.append(definition.__dict__)

    def _set_conditional_format(self, definition: Definition) -> None:
        """set conditional expression"""
        if not definition.formula:
            return
        column_letter = self._get_column_letter(column_name=definition.column)
        first_cell = f"{column_letter}{self.first_row_of_content}"
        last_cell = f"{column_letter}{self.sheet.max_row}"
        font_style = self._set_font_style(font_color_hex=definition.font_color_hex)
        fill_style = self._set_fill_style(fill_color_hex=definition.fill_color_hex)
        formula = self._set_letter_row_index(formula=definition.formula)
        rule = Rule(
            type="expression",
            dxf=DifferentialStyle(fill=fill_style, font=font_style),
            stopIfTrue=True,
            formula=[formula],
        )
        try:
            self.sheet.conditional_formatting.add(range_string=f"{first_cell}:{last_cell}", cfRule=rule)
        except TypeError as exc:
            log.warning(f"Could not transform excel {definition=} {exc=}")
        
    def _parse_to_date(self, definition: Definition) -> None:
        """Try to parse values in a column into date type.
        Will silently move on if it cannot - cell by cell."""
        if definition.parse_to_date is None:
            return
        schemas = definition.parse_to_date
        column_letter = self._get_column_letter(column_name=definition.column)
        for row_index in range(self.first_row_of_content, self.sheet.max_row +1):
            cell = self._get_cell_value(column_letter=column_letter, row_index=row_index)
            value = cell.value
            for schema in schemas:
                try:
                    cell.value = datetime.strptime(value, schema).date()
                    break
                except ValueError:
                    # TODO: logging...
                    pass
                except TypeError:
                    # TODO: logging...
                    pass

    def _get_cell_value(self, column_letter: str, row_index: int):
        """Value of a cell."""
        value = self.sheet[f"{column_letter}{row_index}"]
        return value

    def _set_font_style(self, font_color_hex: str | None, bold: bool = False):
        """set font style pattern to style font in cells.
        With passing None default value will be set."""
        return (
            Font(color=Color(font_color_hex), bold=bold)
            if font_color_hex
            else Font(
                color=Color("000000"),  # black
            )
        )

    def _set_fill_style(self, fill_color_hex: str | None):
        """Create pattern for fill color in cells.
        With passing None default value will be set."""
        return (
            PatternFill(
                patternType="solid",
                start_color=Color(fill_color_hex),
                end_color=Color(fill_color_hex),
            )
            if fill_color_hex
            else PatternFill(
                patternType="solid",
                start_color=Color("FFFFFF"),
                end_color=Color("FFFFFF"),  # white
            )
        )

    def _set_auto_width(self, definition: Definition) -> None:
        """Set width of column automatically."""
        if not definition.auto_width:
            return
        column_letter = self._get_column_letter(column_name=definition.column)
        adjusted_width = self._get_maximum_length_cell(self.sheet[column_letter], minimum=0) + 4
        self.sheet.column_dimensions[column_letter].width = adjusted_width * definition.width_factor

    def _hide_column(self, definition: Definition) -> None:
        """Hide a whole column."""
        if not definition.hide:
            return
        column_letter = self._get_column_letter(column_name=definition.column)
        self.sheet.column_dimensions[column_letter].hidden = True

    def _get_maximum_length_cell(self, column, minimum: int = 0, recalibration: float = 0.85) -> int:
        """Get the maximum length of a cell value in a column.
        Be aware that wrapping the header content will be have an effect of the calculated width
        ('wrapped' is an attribute of 'Header' objects - with execution it will be set).
        - `recalibration` (float): adjustment of calculated value (make columns bigger or smaller)
        - `minimum` (int): minimal width of a column
        - `column`: column itself."""
        max_length = self._get_maximum_length_header(column=column, minimum=minimum)
        max_length = self._get_maximum_length_content(column=column, minimum=max_length)
        return int(max_length * recalibration)

    def _get_maximum_length_content(self, column, minimum: int) -> int:
        """get max length of content column area."""
        max_length = minimum
        for pos in range(self.first_row_of_content, len(column)):
            cell_value = column[pos].value
            cell_value = (
                self._shrink_datetime(cell_value=cell_value) if isinstance(cell_value, datetime) else cell_value
            )
            value_length = len(str(cell_value)) if cell_value else minimum
            max_length = value_length if value_length > max_length else max_length
        return max_length

    def _get_maximum_length_header(self, column, minimum: int) -> int:
        """get max length of header column area - regarding to whether header is wrapped or not."""
        max_length = minimum
        for pos in range(0, self.first_row_of_content - 1):
            cell_value = column[pos].value
            for value_part in self.get_header_cell_value(cell_value=cell_value):
                value_length = len(str(value_part)) if cell_value else minimum
                max_length = value_length if value_length > max_length else max_length
        return max_length

    def get_header_cell_value(self, cell_value) -> list[str]:
        """returns list with strings inside - if header set to be wrapped value will be splitted."""
        if self.header_content_is_wrapped:
            return str(cell_value).split() if cell_value else [cell_value]
        else:
            return [str(cell_value)]

    def _shrink_datetime(self, cell_value: datetime) -> str:
        """to ignore 00:00:00 in datetime to calculate length of cell."""
        value_date: datetime = cell_value
        no_time: bool = value_date.second == 0 and value_date.minute == 0 and value_date.hour == 0
        return value_date.strftime("%m-%d-%Y") if no_time else str(value_date)

    def _build_header_letter_mapping(self, sheet: Worksheet) -> dict:
        """create mapping dict with values of first row and there column letter -> {"entry of cell": "letter", ...}.
        If there will be an empty cell between it will not be present in mapping -> |foo|   |bar| will be `{"A": "foo", "C": "bar"}`. Double entries (same cell content) are
        present but only the last -> |foo|bar|foo| will be `{"B": "bar", "C": "foo"}`.
        """
        mapping = {col[0].value: col[0].column_letter for col in sheet.iter_cols()}
        mapping.pop(None, None)
        return mapping

    def _set_letter_row_index(self, formula: str):
        """replace column names and set letters + start row instead
        like: __col-name__ -> DD2 (2 is first row set with instantiation of Styler)"""
        for name in self.mapping:
            formula = formula.replace(f"__{name}__", f"{self.mapping[name]}{self.first_row_of_content}")
        return formula

    def _get_column_letter(self, column_name: str) -> str:
        """get letter by column name - name must be embedded in '__' like '__NAME__'.
        if name is not embedded method will pass given value as column letter."""
        if column_name.find("__", 0) != -1 and column_name.find("__", 1) != -1:
            return self.mapping.get(column_name.replace("__", ""), column_name)
        return column_name

    def _column_letter_is_valid(self, definition: Definition | None = None, style: Definition | None = None) -> bool:
        """is defined column reachable or not (True/False)"""
        definition = definition or style
        if definition is None:
            return False
        column_letter = self._get_column_letter(column_name=definition.column)
        try:
            self.sheet[column_letter]
        except TypeError:
            return False
        except ValueError:
            return False
        return True
