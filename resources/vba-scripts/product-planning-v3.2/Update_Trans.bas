Attribute VB_Name = "Update_Trans"
Sub Update_Trans()


' ----- Variablen definieren -----
    Dim fname As Variant
    Dim Dakt As Workbook, WB As Workbook, MSTRdata As Workbook
    Dim strFolder As String, DaktPfad As String, MSTRdataPfad As String, ORDERM As Workbook, MTO As Workbook
    Dim lngRow As Long, i As Long
    Dim wks As Worksheet
    Dim qt As QueryTable
    Dim lo As ListObject
    Dim kw As Byte '---> ausreichend, da KW max. zwischen 1 bis 53 liegen kann
    Dim Masterx As Byte, Orderx As Byte, Stockx As Byte, MTOx As Byte
    Dim tblRow As ListObject

'Hintgerundabläufe bzw. -berechnung ausschalten
    With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
        .AskToUpdateLinks = False
    End With

'Definiton der Binärvaribalen

If ActiveSheet.OLEObjects("MasterD_MAG").Object.Value = True Then
    Masterx = 1
    Else
    Masterx = 0
End If

If ActiveSheet.OLEObjects("OrderM_MAG").Object.Value = True Then
    Orderx = 1
    Else
    Orderx = 0
End If

If ActiveSheet.OLEObjects("Stock_MAG").Object.Value = True Then
    Stockx = 1
    Else
    Stockx = 0
End If

If ActiveSheet.OLEObjects("MTO_MAG").Object.Value = True Then
    MTOx = 1
    Else
    MTOx = 0
End If

'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'-------------------------------------------------Master-Datei--------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------


If Masterx = 1 Then

'
' MAG-Planer für eine neue Woche inkl. aller Artikel anhand von Vorlage aufbauen


' ---- Setze Variable "Dakt" gleich der aktuell geöffneten Mappe (soeben heruntergeladene Mappe des BO-Berichts)  -----
    Set WB = ThisWorkbook

    strFolder = WB.Sheets("Laufwerkspfade").Range("F18").Value

   ' C:\Users\R6356327\Desktop\Float-Planer_KW28 AF_mit Formeln (Repariert).xlsm

'----- Vorlagendatei öffnen // nur Excelmappen im Explorer anzeigen -----
    DaktPfad = WB.Sheets("Laufwerkspfade").Range("F16").Value
    Set Dakt = Workbooks.Open(DaktPfad)

    Application.Calculate

    kw = Dakt.Sheets("Planung").Range("AD12").Value

'----- MSTR Planer öffnen -----
    MSTRdataPfad = WB.Sheets("Laufwerkspfade").Range("F10").Value
    Set MSTRdata = Workbooks.Open(MSTRdataPfad)


'---- falls Filter im Blatt "Products" vorhanden, dann Filter entfernen und alle Daten anzeigen -----
        If MSTRdata.Worksheets("Products").FilterMode Then
        Sheets("Products").ShowAllData
        End If

'----- Zähle die ausgefüllten Zeilen, Spalte 1 und setze einen Filter in Spalte B auf Verpackung "027" -----
    lngRow = MSTRdata.Worksheets("Products").Cells(Rows.Count, 1).End(xlUp).Row

    With MSTRdata.Sheets("Products")
        With .Range("U2:U" & lngRow)
                .NumberFormat = "General"
                .Value = .Value
        End With
        .Range("$A$1:$AU$" & lngRow).AutoFilter Field:=2, Criteria1:="027", Operator:=xlAnd
        .Range("$A$1:$AU$" & lngRow).AutoFilter Field:=16, Criteria1:="<>FLOAT", Criteria2:="<>SURF TR", Operator:=xlAnd
        .Range("$A$1:$AU$" & lngRow).AutoFilter Field:=17, Criteria1:="<>DECORGLASS", Criteria2:="<>WIRED", Operator:=xlAnd
        '.Range("$A$1:$AU$" & lngRow).AutoFilter Field:=18, Criteria1:="<>NONE", Operator:=xlAnd
        '.Range("$A$1:$AU$" & lngRow).AutoFilter Field:=21, Criteria1:="<>22", Operator:=xlAnd
    '----- Kopiere alle sichtbaren(!) Daten in Spalte B und füge sie in den Floatplaner ab Zelle E7 ein -----
        .Range("C2:C" & lngRow).SpecialCells(xlCellTypeVisible).Copy
    End With
    Dakt.Sheets("Planung").Range("E14").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

    '----- Zähle alle befüllten Zeilen in "Planung", Spalte 5 (E) und wandle die als Text gespeicherten Zahlen in Zahlen um -----
    lngRow = Dakt.Worksheets("Planung").Cells(Rows.Count, 5).End(xlUp).Row
    With Dakt.Sheets("Planung").Range("E4:E" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With


    MSTRdata.Close SaveChanges:=False
    Set MSTRdata = Nothing


    '----- Kopiere die Formel von A7 bis D&lngRow (letzte gezählte Zeile), sowie von F7 bis CN&lngRow -----
    With Dakt.Sheets("Planung")
        .Range("A14:D14").Copy
        .Range("A14:D" & lngRow).PasteSpecial xlPasteFormulas

        .Range("F14:CR14").Copy
        .Range("F14:CR" & lngRow).PasteSpecial xlPasteFormulas
    End With

    '----- alle Formeln berechnen -----
    Application.Calculate

    '----- alle Abfragen aktualisieren -----
    For Each wks In Dakt.Worksheets
        For Each qt In wks.QueryTables
            qt.Refresh BackgroundQuery:=False
        Next qt

        For Each lo In wks.ListObjects
            lo.QueryTable.Refresh BackgroundQuery:=False
        Next lo

    Next wks

    Set qt = Nothing
    Set wks = Nothing
    Set lo = Nothing



    '----- alle nur als Wert benötigte Formeln kopieren und als Festwerte einfügen; muss nach Aktualisierung der Abfragen erfolgen,
    '----- da die Werte aus den Abfragen teilweise als Festwerte eingefügt werden.
    With Dakt.Sheets("Planung")
        .Range("B14:D" & lngRow).Copy
        .Range("B14").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("F14:T" & lngRow).Copy
        .Range("F14").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        '---- Formate von erster Produktzeile auf alle neu eingefügten Zeilen übertragen -----
        .Rows("14:14").Copy
        .Rows("14:" & lngRow).EntireRow.PasteSpecial Paste:=xlPasteFormats
    End With

    Application.CutCopyMode = False

    '----- nicht mehr benötigte Abfragen + Verbindungen "Consumption" und "Sales" löschen -----
    With Dakt
        .Queries("Consumption").Delete
        .Connections("Abfrage - Consumption").Delete
        .Queries("Sales").Delete
        .Connections("Abfrage - Sales").Delete
        '----- Conso + Sales löschen, da Verbräuche bereits als Festwerte übernommen -----
        .Worksheets("Consumption_Monat (Basis 6 M)").Delete
        .Worksheets("Sales_Monat (Basis 6 M)").Delete
    End With




   ' Dakt.Worksheets("MAG Verbrauch").ListObjects("Cons_Planning").ListRows.Count
Else

    fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="aktuellen Transformationsplaner-Planer öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set Dakt = Workbooks.Open(Filename:=fname, UpdateLinks:=0)
    End If
End If

'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'-------------------------------------------------Ordermanagement-----------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------
'---------------------------------------------------------------------------------------------------------------------

If Orderx = 1 Then

    If Dakt.Worksheets("Ordermanagement").FilterMode Then
        Sheets("Ordermanagement").ShowAllData
 End If


lngRow = Dakt.Sheets("Ordermanagement").Cells(Rows.Count, 3).End(xlUp).Row
Dakt.Sheets("Ordermanagement").Range("C2:AF" & lngRow).Cells.Clear
'----- auch Formeln, aber erst ab der 3. Zeile löschen, damit die Formel kopiert werden kann -----
Dakt.Sheets("Ordermanagement").Range("A3:B" & lngRow).Cells.Clear

fname = WB.Sheets("Laufwerkspfade").Range("F28").Value
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
            '.Range("A1:AD" & lngRow).AutoFilter Field:=15, Criteria1:="<>22", Operator:=xlAnd
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


'----- Formeln im Floatplaner Tabellenblatt Ordermanagement in Spalte A:B herunterkopieren -----
lngRow = Dakt.Worksheets("Ordermanagement").Cells(Rows.Count, 3).End(xlUp).Row
With Dakt.Worksheets("Ordermanagement")
    .Range("A2:B2").Copy
    .Range("A2:B" & lngRow).PasteSpecial Paste:=xlPasteFormulas
End With

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

fname = WB.Sheets("Laufwerkspfade").Range("F20").Value & "ORION Bestand " & Format(Date, "yyyy_mm_dd") & ".xlsx"
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
            '.Range("A1:AL" & lngRow).AutoFilter Field:=6, Criteria1:="<>22", Operator:=xlAnd
            .Range("A1:AL" & lngRow).AutoFilter Field:=20, Criteria1:="<>A6", Criteria2:="<>A61", Operator:=xlAnd
            '----- alle übriggebliebenen nicht ausgeblendeten Zeilen (Floatprodukte) kopieren...  -----
            .Range("A2:AL" & lngRow).SpecialCells(xlCellTypeVisible).Copy
        End With
        '----- ...und in den Floatplaner übertragen -----
        Dakt.Worksheets("Stock").Range("B2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats


'----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        ORDERM.Close SaveChanges:=False
    End If
        Set ORDERM = Nothing

        '----- Formeln im Floatplaner Tabellenblatt Stock in Spalte A herunterkopieren -----
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

fname = WB.Sheets("Laufwerkspfade").Range("F30").Value
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

With Dakt.Sheets("Planung")
    .Columns("A:A").ColumnWidth = 4.9
    .Columns("B:B").ColumnWidth = 4.9
End With
'-------------------------------------------------------------------------------------------
    Dakt.Sheets("Zukäufe").Columns("A:A").NumberFormat = "dd.mm.yyyy"
     Range("E12").Select
    Selection.NumberFormat = "m/d/yyyy"

    If Masterx = 1 Then
    '----- speichere die aufbereitete Vorlage unter den Ordnerpfad von strFolder unter den Namen "Float-Planer_KW"+ Wert der Kalenderwoche als .xlsx -----
    Dakt.SaveAs Filename:=strFolder & "Transform-Planer_KW" & kw & ".xlsm", FileFormat:=52
    Dakt.SaveAs Filename:=strFolder & "Transform-Planer aktuelle Woche" & ".xlsm", FileFormat:=52
    '----- schließe die Vorlage ohne zu speichern (damit sie als Vorlage erhalten bleibt) -----
    Dakt.Close SaveChanges:=False
    Set Dakt = Nothing
End If


    With Application
        .DisplayAlerts = True
        .ScreenUpdating = True
        .EnableEvents = True
        .Calculation = xlCalculationAutomatic
    End With

End Sub
