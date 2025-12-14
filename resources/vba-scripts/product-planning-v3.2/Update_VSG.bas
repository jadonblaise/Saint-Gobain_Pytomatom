Attribute VB_Name = "Update_VSG"
Sub Update_VSG()


' ----- Variablen definieren -----
    Dim fname As Variant
    Dim WB As Workbook, Dakt As Workbook, ORDERM As Workbook
    Dim lngRow As Long, i As Long
    Dim NewButton As Object
    Dim Date1 As String, Date2 As String, wbName As String
    Dim Masterx As Byte, Orderx As Byte, Stockx As Byte, MTOx As Byte


' ---- Setze Variable "WB" gleich der aktuell geöffneten Mappe -----
    Set WB = ThisWorkbook

    With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
    End With

If ActiveSheet.OLEObjects("OrderM_VSG").Object.Value = True Then
Orderx = 1
Else
Orderx = 0
End If

If ActiveSheet.OLEObjects("Stock_VSG").Object.Value = True Then
Stockx = 1
Else
Stockx = 0
End If

If ActiveSheet.OLEObjects("MTO_VSG").Object.Value = True Then
MTOx = 1
Else
MTOx = 0
End If




'----- aktuellen VSG-Planer öffnen -----
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="aktuellen VSG-Planer öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set Dakt = Workbooks.Open(Filename:=fname, UpdateLinks:=0)

 If Dakt.Worksheets("Ordermanagement").FilterMode Then
        Sheets("Ordermanagement").ShowAllData
 End If

'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'-------------------------------------------------Ordermanagement-----------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------

If Orderx = 1 Then
lngRow = Dakt.Sheets("Ordermanagement").Cells(Rows.Count, 3).End(xlUp).Row
'Dakt.Sheets("Ordermanagement").Columns("C:AG").Delete
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

        '----- Filtere das OM --> nur Qualität 22, um alle VSG Produkte zu erfassen -----
        With ORDERM.Worksheets(1)
            With .Range("O2:O" & lngRow)
                    .NumberFormat = "General"
                    .Value = .Value
            End With
            .Rows("1:1").AutoFilter
            .Range("A1:AL" & lngRow).AutoFilter Field:=17, Criteria1:="22"
            '----- ausgeblendete Spalten ("Hilfsspalte") wieder einblenden (morgens beim Aufbereiten automatisch ausgeblendet) -----
            .Columns.Hidden = False
            '----- alle übriggebliebenen nicht ausgeblendeten Zeilen (Floatprodukte) kopieren...  -----
            .Range("A1:AL" & lngRow).SpecialCells(xlCellTypeVisible).Copy
        End With
        '----- ...und in den MAGplaner übertragen -----
        Dakt.Worksheets("Ordermanagement").Range("A1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats


'----- im Hintergrund geöffnete Datei schließen, ohne zu speichern -----
        ORDERM.Close SaveChanges:=False
    End If
        Set ORDERM = Nothing

End If

'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'--------------------------------------------------Stock--------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------


If Stockx = 1 Then


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
            .Range("A1:AL" & lngRow).AutoFilter Field:=6, Criteria1:="22", Operator:=xlAnd
            .Range("A1:AL" & lngRow).AutoFilter Field:=20, Criteria1:="<>A6", Criteria2:="<>COAT, Operator:=xlAnd"
            '----- alle übriggebliebenen nicht ausgeblendeten Zeilen (Floatprodukte) kopieren...  -----
            .Range("A2:AL" & lngRow).SpecialCells(xlCellTypeVisible).Copy
        End With
        '----- ...und in den Floatplaner übertragen -----
        Dakt.Worksheets("Stock").Range("B2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats


'----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        ORDERM.Close SaveChanges:=False
    End If
        Set ORDERM = Nothing


lngRow = Dakt.Worksheets("Stock").Cells(Rows.Count, 2).End(xlUp).Row
With Dakt.Worksheets("Stock")
    .Range("A2").Copy
    .Range("A2:A" & lngRow).PasteSpecial Paste:=xlPasteFormulas
End With

Application.Calculate


End If


'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'-------------------------------------------------------MTO-----------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------


If MTOx = 1 Then

'-------------------------------------------------------------------------------------------

'Öffnen von MTO Crtical

fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="aktuelle Stock Doctrine Daily Report im Ordner MTO Management öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set MTO = Workbooks.Open(Filename:=fname, UpdateLinks:=0)
'----- Falls in der zu öffnenden Datei im Quell-Sheet Filter gesetzt sind, lösche diese, um alle Kommentare kopieren zu können -----

End If


If MTO.Worksheets("MTO Critical").FilterMode Then
        Sheets("MTO Critical").ShowAllData
        End If

        lngRow = MTO.Worksheets("MTO Critical").Cells(Rows.Count, 1).End(xlUp).Row

        With MTO.Worksheets("MTO Critical")
            With .Range("F2:F" & lngRow)
                    .NumberFormat = "General"
                    .Value = .Value
            End With
            .Rows("1:1").AutoFilter
            .Range("A1:AL" & lngRow).AutoFilter Field:=13, Criteria1:="=< 12 months", Operator:=xlOr, Criteria2:="=> 12 months"
            '----- alle übriggebliebenen nicht ausgeblendeten Zeilen (Floatprodukte) kopieren...  -----
            .Range("A2:AL" & lngRow).SpecialCells(xlCellTypeVisible).Copy
        End With
        '----- ...und in den Floatplaner übertragen -----
        Dakt.Worksheets("MTO Critical").Range("A2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        Sheets("MTO Critical").Rows(3).AutoFilter

'----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        MTO.Close SaveChanges:=False
    End If
        Set MTO = Nothing



'-------------------------------------------------------------------------------------------

End If

Application.Calculate


    With Application
        .DisplayAlerts = True
        .ScreenUpdating = True
        .EnableEvents = True
        .Calculation = xlCalculationAutomatic
    End With

End
End Sub
