Attribute VB_Name = "MAGPlanerTagesdaten"
Option Explicit

Sub MAGPlaner_Tagesdaten()


'©
'Programmiert von: René Sagert
'SGGD Köln-Porz 2018-2021

'
' Lagerbestand + OM auffrischen
'


' ----- Variablen definieren -----
    Dim fname As Variant
    Dim WB As Workbook, Dakt As Workbook, ORDERM As Workbook
    Dim lngRow As Long, i As Long
    Dim NewButton As Object
    Dim Date1 As String, Date2 As String, wbName As String
    Dim SGID As String, Adress As String

' ---- Setze Variable "WB" gleich der aktuell geöffneten Mappe -----
    Set WB = ThisWorkbook

    With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
    End With


'----- aktuellen MAG-Planer öffnen -----
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="aktuellen MAG-Planer öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set Dakt = Workbooks.Open(Filename:=fname, UpdateLinks:=0)

 If Dakt.Worksheets("Ordermanagement").FilterMode Then
        Sheets("Ordermanagement").ShowAllData
 End If


lngRow = Dakt.Sheets("Ordermanagement").Cells(Rows.Count, 3).End(xlUp).Row
Dakt.Sheets("Ordermanagement").Range("C2:AF" & lngRow).Cells.Clear
'----- auch Formeln, aber erst ab der 3. Zeile löschen, damit die Formel kopiert werden kann -----
Dakt.Sheets("Ordermanagement").Range("A3:B" & lngRow).Cells.Clear

fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="aktuelles Ordermanagement öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set ORDERM = Workbooks.Open(Filename:=fname, UpdateLinks:=0)
'----- Falls in der zu öffnenden Datei im Quell-Sheet Filter gesetzt sind, lösche diese, um alle Kommentare kopieren zu können -----
        If ORDERM.Worksheets(1).FilterMode Then
        Sheets(1).ShowAllData
        End If

        lngRow = ORDERM.Worksheets(1).Cells(Rows.Count, 1).End(xlUp).Row

        '----- Filtere das OM --> keine Beschichtung + keine Qualität 22, um alle Float Produkte zu erfassen -----
        With ORDERM.Worksheets(1)
            With .Range("O2:O" & lngRow)
                    .NumberFormat = "General"
                    .Value = .Value
            End With
            .Rows("1:1").AutoFilter
            .Range("A1:AD" & lngRow).AutoFilter Field:=10, Criteria1:="<>NONE"
            .Range("A1:AD" & lngRow).AutoFilter Field:=15, Criteria1:="<>22", Operator:=xlAnd
            '----- ausgeblendete Spalten ("Hilfsspalte") wieder einblenden (morgens beim Aufbereiten automatisch ausgeblendet) -----
            .Columns.Hidden = False
            '----- alle übriggebliebenen nicht ausgeblendeten Zeilen (Floatprodukte) kopieren...  -----
            .Range("A2:AD" & lngRow).SpecialCells(xlCellTypeVisible).Copy
        End With
        '----- ...und in den MAGplaner übertragen -----
        Dakt.Worksheets("Ordermanagement").Range("C2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats


'----- im Hintergrund geöffnete Datei schließen, ohne zu speichern -----
        ORDERM.Close SaveChanges:=False
    End If
        Set ORDERM = Nothing


If Dakt.Worksheets("Stock").FilterMode Then
        Sheets("Stock").ShowAllData
End If

lngRow = Dakt.Sheets("Stock").Cells(Rows.Count, 2).End(xlUp).Row
Dakt.Sheets("Stock").Range("B2:AM" & lngRow).Cells.Clear

fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Orion Lagerbestand öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set ORDERM = Workbooks.Open(Filename:=fname, UpdateLinks:=0)
'----- Falls in der zu öffnenden Datei im Quell-Sheet Filter gesetzt sind, lösche diese, um alle Kommentare kopieren zu können -----
        If ORDERM.Worksheets(1).FilterMode Then
        Sheets(1).ShowAllData
        End If

        lngRow = ORDERM.Worksheets(1).Cells(Rows.Count, 1).End(xlUp).Row

        '----- Filtere den Lagerbestand --> keine Qualität 22 + keine Deckscheiben (Paketierung 1001) & <>Herkunft LAMI -----
        With ORDERM.Worksheets(1)
            With .Range("F2:F" & lngRow)
                    .NumberFormat = "General"
                    .Value = .Value
            End With
            .Rows("1:1").AutoFilter
            .Range("A1:AL" & lngRow).AutoFilter Field:=8, Criteria1:="<>1001", Operator:=xlAnd
            .Range("A1:AL" & lngRow).AutoFilter Field:=6, Criteria1:="<>22", Operator:=xlAnd
            .Range("A1:AL" & lngRow).AutoFilter Field:=20, Criteria1:="<>A6", Criteria2:="<>LAMI", Operator:=xlAnd
            '----- alle übriggebliebenen nicht ausgeblendeten Zeilen (Floatprodukte) kopieren...  -----
            .Range("A2:AL" & lngRow).SpecialCells(xlCellTypeVisible).Copy
        End With
        '----- ...und in den Floatplaner übertragen -----
        Dakt.Worksheets("Stock").Range("B2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats


'----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        ORDERM.Close SaveChanges:=False
    End If
        Set ORDERM = Nothing

'----- Formeln im Floatplaner Tabellenblatt Ordermanagement in Spalte A:B herunterkopieren -----
lngRow = Dakt.Worksheets("Ordermanagement").Cells(Rows.Count, 3).End(xlUp).Row
With Dakt.Worksheets("Ordermanagement")
    .Range("A2:B2").Copy
    .Range("A2:B" & lngRow).PasteSpecial Paste:=xlPasteFormulas
End With

'----- Formeln im Floatplaner Tabellenblatt Stock in Spalte A herunterkopieren -----
lngRow = Dakt.Worksheets("Stock").Cells(Rows.Count, 2).End(xlUp).Row
With Dakt.Worksheets("Stock")
    .Range("A2").Copy
    .Range("A2:A" & lngRow).PasteSpecial Paste:=xlPasteFormulas
End With

Application.Calculate

End If

    With Application
        .DisplayAlerts = True
        .ScreenUpdating = True
        .EnableEvents = True
        .Calculation = xlCalculationAutomatic
    End With

End
End Sub
