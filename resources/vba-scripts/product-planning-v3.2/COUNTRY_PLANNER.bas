Attribute VB_Name = "COUNTRY_PLANNER"
Option Explicit

Sub MSTR_DATA_COUNTRY_PLANNER()


Dim fname As Variant
Dim lngRow As Long
Dim Dakt As Workbook, WB As Workbook
Dim strFolder As String


'----- Anzeigen, Berechnungen und Events ausschalten, um Berechnung / Makro zu beschleunigen -----
With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
End With

Set WB = ThisWorkbook

strFolder = "\\CDENSPOR001FS.ZB.IF.ATCSG.NET\Departments\000_alle\PPS\01 Cockpit Planner\"

fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="MSTR COUNTRY PLANNER ÖFFNEN")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set Dakt = Workbooks.Open(Filename:=fname, UpdateLinks:=0)


'----- Letzte befüllte Zelle in Spalte 1 (A) finden und Anzahl aller Zellen von unten nach oben zählen -----
lngRow = Dakt.Sheets("Stock").Cells(Rows.Count, 1).End(xlUp).Row

'----- für genannte Spalten alle Zellen ab der 2. Zeile von Text in Zahlen ohne führende Nullen umwandeln -----
With Dakt.Sheets("Stock")
    With .Range("C2:C" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With


lngRow = Dakt.Sheets("Order Book").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("Order Book")
    With .Range("C2:C" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("E2:E" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With


lngRow = Dakt.Sheets("Purchases").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("Purchases")
    With .Range("A2:A" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("D2:D" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With


Dakt.Sheets("Production").Rows("1:1").Delete Shift:=xlUp
lngRow = Dakt.Sheets("Production").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("Production")
    With .Range("B2:B" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With


lngRow = Dakt.Sheets("Consumption").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("Consumption")
    With .Range("F2:F" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With


lngRow = Dakt.Sheets("Sales").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("Sales")
    With .Range("D2:D" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("E2:E" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With



lngRow = Dakt.Sheets("Stock Histo").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("Stock Histo")
    With .Range("B2:B" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With


lngRow = Dakt.Sheets("Products").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("Products")
    With .Range("C2:C" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("J2:J" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("K2:K" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("AC2:AC" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("AD2:AD" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With


lngRow = Dakt.Sheets("Customer").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("Customer")
    With .Range("A2:A" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With



lngRow = Dakt.Sheets("ShipTo SoldTo").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("ShipTo SoldTo")
    With .Range("A2:A" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With



lngRow = Dakt.Sheets("Order Management_Porz").Cells(Rows.Count, 1).End(xlUp).Row

With Dakt.Sheets("Order Management_Porz")
    With .Range("E2:E" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("F2:F" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("T2:T" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("U2:U" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("V2:V" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With

'----- Kreuztabelle aufbereiten, um zu jeden 027er einen passenden 002er Materialcode zu haben -----
    '----- Ginger17 Code ausschneiden und nach als neue Spalte B einfügen, damit SVERWEIS im Folgenden funktioniert -----
    With Dakt.Sheets("Products")
        .Columns("N:N").Cut
        .Columns("B:B").Insert Shift:=xlToRight
    End With

'----- neues Tabellenblatt erstellen mit Namen "Kreuztabelle" -----
Dakt.Sheets.Add(After:=Sheets(Sheets.Count)).Name = "Kreuztabelle"
    If Dakt.Worksheets("Products").FilterMode Then
        Sheets("Products").ShowAllData
    End If

    lngRow = Dakt.Worksheets("Products").Cells(Rows.Count, 1).End(xlUp).Row

    '----- alle 027er Codes in "Products" filtern + kopieren + in "Kreuztabelle" einfügen -----
    With Dakt
        With .Sheets("Products").Range("$A$1:$AU$" & lngRow)
                .AutoFilter Field:=3, Criteria1:="027"
        End With
        .Sheets("Products").Range("B1:B" & lngRow).SpecialCells(xlCellTypeVisible).Copy
        With .Sheets("Kreuztabelle")
                .Range("A1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
                '----- Spalte B mit Überschrift "IL Material" versehen -----
                .Range("B1").FormulaLocal = "IL Material"
        End With
    End With

    '----- Zwischenablage leeren (Kopierte Werte löschen), um Arbeitsspeicher freizugeben ---> Beschleunigung -----
    Application.CutCopyMode = False

    '----- Anzahl der befüllten Zeilen in "Kreuztabelle" Spalte A zählen -----
    lngRow = Dakt.Worksheets("Kreuztabelle").Cells(Rows.Count, 1).End(xlUp).Row

    '----- Formel in Spalte B einfügen und bis zur untersten gezählten Zeile ausfüllen; anschließend als Festwert einfügen -----
    With Dakt.Worksheets("Kreuztabelle")
        .Range("B2:B" & lngRow).FormulaLocal = _
                "=WENN(SVERWEIS(Kreuztabelle!A:A;Products!B:C;2;FALSCH)=""002"";SVERWEIS(Kreuztabelle!A:A;Products!B:D;3;FALSCH);"""")"
        .Range("A1:B" & lngRow).Copy
        .Range("A1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    End With

    If Dakt.Worksheets("Products").FilterMode Then
        Sheets("Products").ShowAllData
    End If

    '----- ursprüngliche Sortierung der Spalten unter "Products" wiederherstellen -----
        With Dakt.Sheets("Products")
        .Columns("B:B").Cut
        .Columns("O:O").Insert Shift:=xlToRight
    End With

'----- "Products" aufrufen
Dakt.Sheets("Products").Activate

'----- Datei automatisch speichern -----
Dakt.SaveAs Filename:=strFolder & "000_MSTR_DATA_COUNTRY_GERMANY_Planner_aktuell.xlsx", FileFormat:=51

'----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        Dakt.Close SaveChanges:=False
    End If
        Set Dakt = Nothing


With Application
        .DisplayAlerts = True
        .ScreenUpdating = True
        .EnableEvents = True
        .Calculation = xlCalculationAutomatic
End With

End
End Sub
