from io import BytesIO

from apps.excelstyler.styler import ExcelSheetStyler


def styling_of_excel_sheet(
    buffer: BytesIO,
    sheet_name: str,
) -> BytesIO:
    """
    ### SG Glass Cologne-Porz - Orderbook Style
    Enhanced styling with comprehensive conditional formatting and colors.
    """

    sheet_style = ExcelSheetStyler(buffer=buffer, sheet_name=sheet_name)

    collection = [
        # Column visibility and basic setup
        sheet_style.Definition(column="__KW__"),
        sheet_style.Definition(column="__Ginger Code 17__", hide=True),
        sheet_style.Definition(column="__Sales Expected Loading Date__"),
        sheet_style.Definition(column="__Expected Loading Date - day before__"),
        sheet_style.Definition(column="__ShipTo Customer__"),
        sheet_style.Definition(column="__ShipTo Country__"),
        sheet_style.Definition(column="__Order Creation Date__"),
        sheet_style.Definition(column="__Sales Order__"),
        sheet_style.Definition(column="__Delivery Note__"),
        sheet_style.Definition(column="__Sales Order Status__"),
        sheet_style.Definition(column="__Sub-Family__"),
        sheet_style.Definition(column="__Resa Project Name__"),
        sheet_style.Definition(column="__Coating__"),
        sheet_style.Definition(column="__Tint__"),
        sheet_style.Definition(column="__Nominal Thickness__"),
        sheet_style.Definition(column="__Size__"),
        sheet_style.Definition(column="__Laminate__"),
        sheet_style.Definition(column="__Quality__"),
        sheet_style.Definition(column="__Surface Protection__"),
        sheet_style.Definition(column="__Packaging__"),
        sheet_style.Definition(column="__Pack Type__"),
        sheet_style.Definition(column="__Class__"),
        sheet_style.Definition(column="__Length__"),
        sheet_style.Definition(column="__Width__"),
        sheet_style.Definition(column="__Material Plant__"),
        sheet_style.Definition(column="__VOL__"),
        sheet_style.Definition(column="__VOL - day before__"),
        sheet_style.Definition(column="__M2__"),
        sheet_style.Definition(column="__TO__"),
        sheet_style.Definition(column="__ob_UID__", hide=True),
        sheet_style.Definition(column="__Status__"),
        sheet_style.Definition(column="__ETD__"),
        sheet_style.Definition(column="__Comment__"),
        sheet_style.Definition(column="__NP CW__"),
        sheet_style.Definition(column="__hidden_created_at__", hide=True),
        sheet_style.Definition(column="__hidden_lastmodified_at__", hide=True),
        
        # OTIF Predictor column with blue header background
        sheet_style.Definition(column="__Stock count__"),
        sheet_style.Definition(column="__OTIF Predictor__"),
        sheet_style.Definition(column="__Planned production date__"),
        sheet_style.Definition(column="__Planned production week__"),

        # === CONDITIONAL FORMATTING RULES ===
        
        # OTIF Predictor - Status based coloring
        sheet_style.Definition(
            column="__OTIF Predictor__", 
            formula='__OTIF Predictor__="OK"', 
            fill_color_hex="92d050"  # Lime green
        ),
        sheet_style.Definition(
            column="__OTIF Predictor__", 
            formula='__OTIF Predictor__="NOK"', 
            fill_color_hex="ff0000"  # Red
        ),
        sheet_style.Definition(
            column="__OTIF Predictor__", 
            formula='__OTIF Predictor__="NP"', 
            fill_color_hex="ffff00"  # Yellow (can be refined with date logic)
        ),
        # OTIF with date logic - Expected Loading Date > 14 days
        sheet_style.Definition(
            column="__OTIF Predictor__",
            formula='AND(__OTIF Predictor__="NP",__Sales Expected Loading Date__-TODAY()>14)',
            fill_color_hex="ffff00",  # Yellow
        ),
        # OTIF with date logic - Expected Loading Date <= 14 days
        sheet_style.Definition(
            column="__OTIF Predictor__",
            formula='AND(__OTIF Predictor__="NP",__Sales Expected Loading Date__-TODAY()<=14)',
            fill_color_hex="ff8601",  # Orange/Brown
        ),

        # Status column - Default to #N/V if empty (handled in post-processing)
        
        # ETD column - Brown fill if contains date or "schneiden"
        sheet_style.Definition(
            column="__ETD__",
            formula='AND(__ETD__<>"",__Sales Expected Loading Date__<__ETD__)',
            fill_color_hex="ffc000",  # Brown/Orange
            parse_to_date=[
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%Y_%m_%d",
                "%d.%m.%Y",
            ],
        ),

        # Sub-Family - STD Silence gets cyan background
        sheet_style.Definition(
            column="__Sub-Family__", 
            formula='__Sub-Family__="STD Silence"', 
            fill_color_hex="aaf8ed"  # Light cyan
        ),

        # Tint - Extra Clear gets blue background
        sheet_style.Definition(
            column="__Tint__", 
            formula='__Tint__="EXTRACL"', 
            fill_color_hex="3DC1F1"  # Blue (updated from 00ccff)
        ),

        # Surface Protection - Multiple conditions for green background
        sheet_style.Definition(
            column="__Surface Protection__", 
            formula='__Surface Protection__="EKONL"', 
            fill_color_hex="abc785"  # Dark green (updated from abc785)
        ),
        sheet_style.Definition(
            column="__Surface Protection__", 
            formula='__Surface Protection__="FILM"', 
            fill_color_hex="abc785"
        ),
        sheet_style.Definition(
            column="__Surface Protection__", 
            formula='__Surface Protection__="YESF"', 
            fill_color_hex="abc785"
        ),
        sheet_style.Definition(
            column="__Surface Protection__", 
            formula='__Surface Protection__="ALU"', 
            fill_color_hex="abc785"
        ),
        sheet_style.Definition(
            column="__Surface Protection__", 
            formula='__Surface Protection__="YESA"', 
            fill_color_hex="abc785"
        ),
        sheet_style.Definition(
            column="__Surface Protection__", 
            formula='__Surface Protection__="EASYP"', 
            fill_color_hex="abc785"
        ),
        sheet_style.Definition(
            column="__Surface Protection__", 
            formula='__Surface Protection__="NTAP+"', 
            fill_color_hex="abc785"
        ),
        sheet_style.Definition(
            column="__Surface Protection__", 
            formula='__Surface Protection__="YTAP+"', 
            fill_color_hex="abc785"
        ),
        sheet_style.Definition(
            column="__Surface Protection__",
            formula='and( __Surface Protection__ = "YES", '
            'or( __Sub-Family__ = "Planilux", '
            'or( __Sub-Family__ = "Parsol", __Sub-Family__ = "Venus" ) ) )',
            fill_color_hex="abc785",
        ),
        sheet_style.Definition(
            column="__Surface Protection__",
            formula='and( __Surface Protection__ = "NONE", __Sub-Family__ = "DIAMANT" )',
            fill_color_hex="abc785",
        ),
        # Note: NONE cases need bold font - handle in post-processing if needed

        # Width - Yellow if 2550
        sheet_style.Definition(
            column="__Width__", 
            formula="__Width__=2550", 
            fill_color_hex="ffff00"  # Yellow
        ),

        # Length - Brown if not 6000
        sheet_style.Definition(
            column="__Length__", 
            formula="__Length__<>6000", 
            fill_color_hex="ffcc99"  # Brown
        ),

        # Pack Type - Orange background variations
        sheet_style.Definition(
            column="__Pack Type__", 
            formula='left( __Pack Type__,3 ) = "11T"', 
            fill_color_hex="ff9900"  # Orange
        ),
        sheet_style.Definition(
            column="__Pack Type__", 
            formula='left( __Pack Type__,3 ) = "5T"', 
            fill_color_hex="ff9901"  # Orange variation
        ),
        sheet_style.Definition(
            column="__Pack Type__", 
            formula='left( __Pack Type__,3 ) = "12.6T"', 
            fill_color_hex="ff9902"  # Orange variation
        ),
        # Note: 5T also needs orange bold font - handle in post-processing if needed

        # Laminate - Purple if ends with 'P'
        sheet_style.Definition(
            column="__Laminate__", 
            formula='right(__Laminate__,1)="P"', 
            fill_color_hex="cc99ff"  # Purple
        ),

        # Quality - Multiple color rules
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=61", 
            fill_color_hex="e8a7a7"  # Rose/Pink
        ),
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=22", 
            fill_color_hex="617c3c"  # Keep original green
        ),
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=1", 
            fill_color_hex="ea701e"  # Keep original orange
        ),
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=72", 
            fill_color_hex="008080"  # Dark Teal
        ),
        # Note: Quality 6, 59, 60, 68, 69 need orange font - handle in post-processing
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=6", 
            font_color_hex="ffa500"  # Orange
        ),
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=59", 
            font_color_hex="ffa500"  # Orange
        ),
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=60", 
            font_color_hex="ffa500"  # Orange
        ),
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=68", 
            font_color_hex="ffa500"  # Orange
        ),
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=69", 
            font_color_hex="ffa500"  # Orange
        ),
        # Note: Quality 22 needs dark green font - handle in post-processing
        sheet_style.Definition(
            column="__Quality__", 
            formula="__Quality__=22", 
            font_color_hex="617c3c"  # Dark green
        ),

        # Class - Dark green if ORAÉ
        sheet_style.Definition(
            column="__Class__", 
            formula='__Class__="ORAÉ"', 
            fill_color_hex="9AC77C"  # Dark green
        ),
    ]

    # Header styling - light blue background for specific columns
    header = sheet_style.Header(
        wrapped=True, 
        #fill_color_hex="DDDDDD",  # Default gray
        font_color_hex="222222", 
        bold=True
    )

    # Apply all conditional formatting
    sheet_style.apply_conditional_collection(style_definitions=collection, header=header)

    # Get the buffer with all styling applied
    styled_buffer = sheet_style.get_workbook_as_buffer()
    
    # Apply additional post-processing for complex formatting
    styled_buffer = _post_process_styling(styled_buffer, sheet_name)
    
    return styled_buffer


def _post_process_styling(buffer: BytesIO, sheet_name: str) -> BytesIO:
    """
    Post-process the Excel file for styling that can't be done with conditional formatting:
    - Font colors and bold text
    - Special header backgrounds (blue for OTIF/Planned columns)
    - Status default values (#N/V)
    - Cell-level font size adjustments
    """
    try:
        from openpyxl import load_workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        buffer.seek(0)
        wb = load_workbook(buffer)
        ws = wb[sheet_name]

        # Freeze header row
        ws.freeze_panes = ws.cell(row=2, column=1).coordinate

        # Hide Excel gridlines (UI lines)
        ws.sheet_view.showGridLines = False

        # ✅ Remove ALL borders from the entire sheet
        no_border = Border(
            left=Side(style=None),
            right=Side(style=None),
            top=Side(style=None),
            bottom=Side(style=None),
        )

        for row in ws.iter_rows():
            for cell in row:
                cell.border = no_border

        
        # Get header positions
        headers = {str(cell.value).strip().lower(): idx + 1 for idx, cell in enumerate(ws[1]) if cell.value}
        
        # Column indices
        status_col = headers.get("status")
        otif_col = headers.get("otif predictor")
        planned_date_col = headers.get("planned production date")
        planned_week_col = headers.get("planned production week")
        surface_prot_col = headers.get("surface protection")
        pack_type_col = headers.get("pack type")
        quality_col = headers.get("quality")
        
        # Define font styles
        orange_font = Font(color="ffb222", bold=True, size=9)
        dark_green_font = Font(color="006400", bold=True, size=9)
        bold_font_9 = Font(bold=True, size=9)
        
        # Special header background - light blue for OTIF and Planned columns
        light_blue_fill = PatternFill(start_color="B7E3F3", end_color="B7E3F3", fill_type="solid")
        
        for cell in ws[1]:
            header_value = str(cell.value).strip().lower() if cell.value else ""
            if header_value in ["otif predictor", "planned production date", "planned production week"]:
                cell.fill = light_blue_fill
            # Set header font size
            cell.font = Font(size=10, bold=True)
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        
        # Data rows: apply font size and special formatting
        data_alignment = Alignment(horizontal="left", vertical="top", wrap_text=False)
        
        for row in ws.iter_rows(min_row=2):
            # Set base font size for all cells
            for cell in row:
                if not cell.font or cell.font.size != 9:
                    cell.font = Font(size=9)
                cell.alignment = data_alignment
            
            # Status column - set #N/V if empty
            if status_col:
                cell = row[status_col - 1]
                if not cell.value or str(cell.value).strip() == "":
                    cell.value = "#N/V"
            
            # Surface Protection - Bold font if NONE
            if surface_prot_col:
                cell = row[surface_prot_col - 1]
                if str(cell.value).strip().upper() == "NONE":
                    cell.font = bold_font_9
            
            # Pack Type - Orange bold font if starts with 5T
            if pack_type_col:
                cell = row[pack_type_col - 1]
                if cell.value and str(cell.value).strip().upper().startswith("5T"):
                    cell.font = orange_font
            
            # Quality - Font colors for specific values
            if quality_col:
                cell = row[quality_col - 1]
                try:
                    qval = int(cell.value)
                    if qval == 22:
                        cell.font = dark_green_font
                    elif qval in {6, 59, 60, 68, 69}:
                        cell.font = orange_font
                except (ValueError, TypeError):
                    pass
        
        # Save back to buffer
        output_buffer = BytesIO()
        wb.save(output_buffer)
        output_buffer.seek(0)
        return output_buffer
        
    except ImportError:
        # If openpyxl is not available, return original buffer
        return buffer
    except Exception as e:
        # If any error occurs in post-processing, log and return original
        import logging
        log = logging.getLogger(__name__)
        log.warning(f"Post-processing styling failed: {e}. Returning original buffer.")
        buffer.seek(0)
        return buffer