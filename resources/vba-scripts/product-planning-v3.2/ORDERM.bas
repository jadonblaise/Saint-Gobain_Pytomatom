Attribute VB_Name = "ORDERM"
Option Explicit
Sub ORDERM()

Dim lngRow As Long
Dim TodayDate As String, strFolder As String
Dim fname As Variant
Dim WB As Workbook, Dakt As Workbook, Davt As Workbook

'----- Anzeigen, Berechnungen und Events ausschalten, um Berechnung / Makro zu beschleunigen -----
With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
End With

'----- Variable WB die Datei "Workbench PPS" zuweisen -----
Set WB = ThisWorkbook

strFolder = WB.Sheets("Laufwerkspfade").Range("F26").Value

'----- Tagesaktuelle Datei aus MSTR öffnen // nur Excelmappen im Explorer anzeigen -----
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Heruntergeladene, tagesaktuelle Datei öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set Dakt = Workbooks.Open(Filename:=fname, UpdateLinks:=0)


'----- Letzte befüllte Zelle in Spalte 1 (A) finden und Anzahl aller Zellen von unten nach oben zählen -----
lngRow = Dakt.Sheets(1).Cells(Rows.Count, 1).End(xlUp).Row

'----- für genannte Spalten alle Zellen ab der 2. Zeile von Text in Zahlen ohne führende Nullen umwandeln -----
With Dakt.Sheets(1)
    With .Range("E2:E" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With Range("F2:F" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With Range("T2:T" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With Range("U2:U" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With Range("V2:V" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With


'----- Tabellenblatt 1 umbenennen (heutiges Datum) -----
TodayDate = Format(Date, "dd.mm.yyyy")
Dakt.Sheets(1).Name = "Ordermanagement"


'----- leeres Tabellenblatt am Ende einfügen (für Daten des Vortags) -----
Dakt.Worksheets.Add After:=Worksheets(Worksheets.Count)
Dakt.Worksheets.Add After:=Worksheets(Worksheets.Count)
ActiveSheet.Name = TodayDate


'----- Datei des Vortags manuell öffnen // nur Excelmappen im Explorer anzeigen -----
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Datei des Vortags öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set Davt = Workbooks.Open(Filename:=fname, UpdateLinks:=0)

'----- Datei des Vortags speichern -----
TodayDate = Format(Date, "yyyymmdd")
Davt.SaveAs Filename:=strFolder & TodayDate & " G035 Auftragsbestand VORTAG.xlsx", FileFormat:=51

'----- Falls in der zu öffnenden Datei im Quell-Sheet Filter gesetzt sind, lösche diese, um alle Kommentare kopieren zu können -----
        If Davt.Worksheets(1).FilterMode Then
        Sheets(1).ShowAllData
        End If
        '----- zähle Zeilen in alter Datei, um zu kopierenden Bereich zu erfassen -----
        lngRow = Davt.Worksheets(1).Cells(Rows.Count, 1).End(xlUp).Row
        'kopiere Auftragsnummmer in die
        '----- kopiere Hilfsspalte, Kommentare etc. aus alter Datei -----
        Davt.Worksheets(1).Range("Z1:AD" & lngRow).Copy
        '----- kopierten Bereich in neue Datei, Blatt2 als Festwerte einfügen
        Dakt.Worksheets(2).Range("A1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        '----- kopiere Hilfsspalte, Kommentare etc. aus alter Datei -----
        Davt.Worksheets(1).Range("A1:A" & lngRow).Copy
        '----- kopierten Bereich in neue Datei, Blatt2 als Festwerte einfügen
        Dakt.Worksheets(2).Range("F1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        '----- kopiere Hilfsspalte, Kommentare etc. aus alter Datei -----
        Davt.Worksheets(1).Range("W1:W" & lngRow).Copy
        '----- kopierten Bereich in neue Datei, Blatt2 als Festwerte einfügen
        Dakt.Worksheets(2).Range("G1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

'----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        Davt.Close SaveChanges:=False
    End If
        Set Davt = Nothing

'----- Überschriften aus Tabelle mit SVERWEIS (Blatt2) kopieren und als ergänzende Überschriften in Blatt1 einfügen -----
Dakt.Worksheets(2).Range("A1:G1").Copy
Dakt.Worksheets(1).Range("Z1:AF1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

'----- Format der Überschriften auf eingefügte Überschriften übertragen -----
With Dakt.Worksheets(1)
    .Range("Y1").Copy
    .Range("Z1:AF1").PasteSpecial Paste:=xlPasteFormats
End With
'----- Zwischenablage leeren (Arbeitsspeicher freigeben) -----
Application.CutCopyMode = False

'----- Letzte befüllte Zelle in Spalte 1 (A) finden und Anzahl aller Zellen von unten nach oben zählen -----
lngRow = Dakt.Worksheets(1).Cells(Rows.Count, 1).End(xlUp).Row

'----- Formeln ab Spalte Y einfügen und im selben Schritt bis zur letzten Zeile ausfüllen -----
With Dakt.Worksheets(1)
    .Range("Z2:Z" & lngRow).FormulaR1C1 = "=RC[-21]&RC[-4]"
    .Range("AA2:AA" & lngRow).FormulaR1C1 = _
        "=VLOOKUP(RC26,Tabelle1!C1:C5,2,FALSE)"
    .Range("AB2:AB" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,3,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,3,FALSE),""""))"
    .Range("AC2:AC" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,4,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,4,FALSE),""""))"
    .Range("AD2:AD" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,5,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,5,FALSE),""""))"
    .Range("AE2:AE" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,6,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,6,FALSE),""""))"
    .Range("AF2:AF" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,7,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC26,Tabelle1!C1:C7,7,FALSE),""""))"
    .Range("AG2:AG" & lngRow).FormulaR1C1 = _
        "=RC[-28]&RC[-5]"

End With

'----- alle Formeln berechnen lassen (da Anfangs autmatische Berechnung ausgeschaltet, um Makro zu beschleunigen -----
Application.Calculate


With Dakt.Worksheets(1)
    .Range("Z1:AD" & lngRow).Copy
    .Range("Z1:AD" & lngRow).PasteSpecial Paste:=xlPasteValuesAndNumberFormats
End With

'---- Datum auf "kurz" + Hilfsspalte ausblenden -----
With Dakt.Worksheets(1)
    .Columns("AB:AB").NumberFormat = "d/m/yy;@"
    .Columns("Z:Z").EntireColumn.Hidden = True
    .Columns("AE:AE").NumberFormat = "d/m/yyyy;@"
    .Columns("AE:AE").EntireColumn.Hidden = True
    .Columns("AF:AF").NumberFormat = "00;@"
    .Columns("AF:AF").EntireColumn.Hidden = True
    .Columns("AG:AG").EntireColumn.Hidden = True
End With


'----- bedingte Formatierung inkl. Formel --> wenn frühestest Versanddatum> Ladedatum, dann markiere Versanddatum organe-----
With Dakt.Worksheets(1)
    .Activate
    .Range("AB2").Activate
       With ActiveCell
        .FormatConditions.Add Type:=xlExpression, Formula1:="=UND(AB2<>"""";A2<AB2)"
        .FormatConditions(1).Interior.Color = 49407
        End With
'----- bedingte Formatierung auf gesamte Spalte übertragen -----
    .Range("AB2").Copy
    .Range("AB2:AB" & lngRow).PasteSpecial Paste:=xlPasteFormats
End With

'----- bedingte Formatierung inkl. Formel --> Vergleich Ladedatum mit Vortrag, dann markiere Versanddatum organe-----
With Dakt.Worksheets(1)
    .Activate
    .Range("A2").Activate
       With ActiveCell
        .FormatConditions.Add Type:=xlExpression, Formula1:="=UND(AE2<>"""";A2<>AE2)"
        .FormatConditions(1).Interior.Color = 49407
        End With
'----- bedingte Formatierung auf gesamte Spalte übertragen -----
    .Range("A2").Copy
    .Range("A2:A" & lngRow).PasteSpecial Paste:=xlPasteFormats
End With

'----- bedingte Formatierung inkl. Formel --> Vergleich Volumen mit Vortag, dann markiere Versanddatum organe-----
With Dakt.Worksheets(1)
    .Activate
    .Range("W2").Activate
       With ActiveCell
        .FormatConditions.Add Type:=xlExpression, Formula1:="=UND(AF2<>"""";W2<>AF2)"
        .FormatConditions(1).Interior.Color = 49407
        End With
'----- bedingte Formatierung auf gesamte Spalte übertragen -----
    .Range("W2").Copy
    .Range("W2:W" & lngRow).PasteSpecial Paste:=xlPasteFormats
End With

'----- oberste Zeile fixieren -----
With ActiveWindow
    If .FreezePanes Then .FreezePanes = False
    .SplitColumn = 0
    .SplitRow = 1
    .FreezePanes = True
End With


'-----Filter in Zeile 1 hinzufügen -----
    '----- wenn Filter bereits vorhanden sein sollte -----
    If ActiveSheet.AutoFilterMode = True Then
    '-----keine Anweisung zwischen Then + Else --> mache nichts -----
    Else
    ActiveSheet.Range("A1").AutoFilter
    End If

    '----- OM auf Schriftart "Calibri" ändern (Schriftart in MicroStrategy nicht verfügbar) -----
    ActiveSheet.Cells.Font.Name = "Calibri"


With Dakt.Worksheets(1)
    .Columns("A:A").ColumnWidth = 8.6
    .Columns("C:C").ColumnWidth = 9.6
    .Columns("D:D").ColumnWidth = 8.15
    .Columns("F:F").ColumnWidth = 7.7
    .Columns("G:G").ColumnWidth = 4.6
    .Columns("L:L").ColumnWidth = 4.45
    .Columns("M:M").ColumnWidth = 3.15
    .Columns("O:O").ColumnWidth = 2.45
    .Columns("P:P").ColumnWidth = 5.3
    .Columns("Q:Q").ColumnWidth = 7.15
    .Columns("S:S").ColumnWidth = 2
    .Columns("T:T").ColumnWidth = 4.15
    .Columns("U:U").ColumnWidth = 4
    .Columns("V:V").ColumnWidth = 9.6
    .Columns("W:W").ColumnWidth = 4.45
    .Columns("X:X").ColumnWidth = 6.15
    .Columns("Y:Y").ColumnWidth = 6.3
End With

'----- heutiges Datum ermitteln und Datei automatisch unter heutigem Datum im Standardordner speichern -----

Dakt.SaveAs Filename:=strFolder & TodayDate & " G035 Auftragsbestand.xlsx", FileFormat:=51
Dakt.SaveAs Filename:=strFolder & "G035 Auftragsbestand.xlsx", FileFormat:=51

'----- im Hintergrund geöffnete Datei schließen -----
        Dakt.Close SaveChanges:=False
    End If
        Set Dakt = Nothing


'----- deaktivierte Funktionen (siehe Beginn des Makros) wieder zuschalten -----
With Application
        .DisplayAlerts = True
        .ScreenUpdating = True
        .EnableEvents = True
        .Calculation = xlCalculationAutomatic
End With


End Sub
