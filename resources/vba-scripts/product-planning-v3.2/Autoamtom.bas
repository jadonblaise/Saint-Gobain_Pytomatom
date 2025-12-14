Attribute VB_Name = "Autoamtom"
Option Explicit
Sub Automatom()

    Dim lngRow As Long, StockRow As Long, langRow As Long, i As Long
    Dim TodayDate As String, strFolder As String, stFolder As String, StaktPfad As String, MSTRPfad As String, stckFolder As String, DaptPfad As String, FolderStock As String
    Dim fname As Variant, sopen As Variant, finame As Variant
    Dim WB As Workbook, Dakt As Workbook, Davt As Workbook, Stakt As Workbook, Stkt As Workbook, WBS As Workbook, MSTRdata As Workbook, ORDERM As Workbook, Dapt As Workbook
    Dim wksht As Worksheet
    Dim qta As QueryTable
    Dim lob As ListObject
    Dim kwo As Byte '---> ausreichend, da kwo max. zwischen 1 bis 53 liegen kann
    Dim tablRow As ListObject
    Dim SID As String, Adres As String

'----- Anzeigen, Berechnungen und Events ausschalten, um Berechnung / Makro zu beschleunigen -----
With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
End With

'----- Variable WB die Datei "Workbench PPS" zuweisen -----
Set WB = ThisWorkbook

FolderStock = WB.Sheets("Laufwerkspfade").Range("F34").Value
strFolder = WB.Sheets("Laufwerkspfade").Range("F26").Value



'----- Tagesaktuelle Datei aus MSTR öffnen // nur Excelmappen im Explorer anzeigen -----
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Heruntergeladene, tagesaktuelle Datei öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set Dakt = Workbooks.Open(Filename:=fname, UpdateLinks:=0)


'----- Letzte befüllte Zelle in Spalte 1 (A) finden und Anzahl aller Zellen von unten nach oben zählen -----
lngRow = Dakt.Sheets(1).Cells(Rows.Count, 3).End(xlUp).Row

'----- für genannte Spalten alle Zellen ab der 2. Zeile von Text in Zahlen ohne führende Nullen umwandeln -----
With Dakt.Sheets(1)
    With .Range("A2:A" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("Q2:Q" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With .Range("G2:G" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With Range("H2:H" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With Range("V2:V" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With Range("W2:W" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
    With Range("X2:X" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With
End With


TodayDate = Format(Date, "dd.mm.yyyy")

'----- Tabellenblatt 1 umbenennen (Ordermanagement) -----
Dakt.Sheets(1).Name = "Ordermanagement"


'----- leeres Tabellenblatt am Ende einfügen (für Daten des Vortags) -----
Dakt.Worksheets.Add After:=Worksheets(Worksheets.Count)

'----- leeres Tabellenblatt Stock  am Ende einfügen (für Daten des Vortags) -----
With Dakt
    .Sheets.Add After:=Sheets(Worksheets.Count)
    .ActiveSheet.Name = "Stock"
    .Sheets.Add After:=Sheets(Worksheets.Count)
    .ActiveSheet.Name = "Produktionsprogram"
    .Sheets.Add After:=Sheets(Worksheets.Count)
    .ActiveSheet.Name = TodayDate
End With

'-------------------------------------------------------------------------------------
'Produktionsprogramm einfügen---------------------------------------------------------
DaptPfad = WB.Sheets("Laufwerkspfade").Range("F32").Value
        Set Dapt = Workbooks.Open(DaptPfad)

'----Funktionen Rechnen lassen
Application.Calculate

'---Copy Paste als Festwerte

Dapt.Sheets("HTOM").Range("A1:D93").Copy
Dakt.Sheets("Produktionsprogram").Range("A1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

'----- schließe Produktionsprogramm ohne zu speichern  -----
    Dapt.Close SaveChanges:=False
    Set Dapt = Nothing



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
        lngRow = Davt.Worksheets(1).Cells(Rows.Count, 3).End(xlUp).Row
        'kopiere Auftragsnummmer in die
        '----- kopiere Hilfsspalte, Kommentare etc. aus alter Datei -----
        Davt.Worksheets(1).Range("AB1:AI" & lngRow).Copy
        '----- kopierten Bereich in neue Datei, Blatt2 als Festwerte einfügen
        Dakt.Worksheets(2).Range("A1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        '----- kopiere Hilfsspalte, Kommentare etc. aus alter Datei -----
        Davt.Worksheets(1).Range("C1:C" & lngRow).Copy
        '----- kopierten Bereich in neue Datei, Blatt2 als Festwerte einfügen
        Dakt.Worksheets(2).Range("F1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        '----- kopiere Hilfsspalte, Kommentare etc. aus alter Datei -----
        Davt.Worksheets(1).Range("Y1:Y" & lngRow).Copy
        '----- kopierten Bereich in neue Datei, Blatt2 als Festwerte einfügen
        Dakt.Worksheets(2).Range("G1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

'----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        Davt.Close SaveChanges:=False
    End If
        Set Davt = Nothing

'----- Überschriften aus Tabelle mit SVERWEIS (Blatt2) kopieren und als ergänzende Überschriften in Blatt1 einfügen -----
Dakt.Worksheets(2).Range("A1:G1").Copy
Dakt.Worksheets(1).Range("AB1:AH1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

'----- Format der Überschriften auf eingefügte Überschriften übertragen -----
With Dakt.Worksheets(1)
    .Range("AA1").Copy
    .Range("AB1:AH1").PasteSpecial Paste:=xlPasteFormats
    .Range("A1") = "KW"
    .Range("U1") = "Class"
    .Range("AI1") = "Stock Count"
    .Range("AJ1") = "OTIF Predictor"
    .Range("AK1") = "Planned production date"
    .Range("AL1") = "Planned production week"
    With .Range("AJ1:AL1").Interior
        .PatternColorIndex = xlAutomatic
        .ThemeColor = xlThemeColorAccent4
        .TintAndShade = 0.599993896298105
        .PatternTintAndShade = 0
    End With
End With

With Dakt.Worksheets(1).Rows("1:1")
        .HorizontalAlignment = xlLeft
        .VerticalAlignment = xlTop
        .WrapText = True
        .Orientation = 0
        .AddIndent = False
        .IndentLevel = 0
        .ShrinkToFit = False
        .ReadingOrder = xlContext
        .MergeCells = False
End With

'----- Zwischenablage leeren (Arbeitsspeicher freigeben) -----
'---------------------------------------------------------------
'---------------------------------------------------------------
'---------------------------------------------------------------


'--- Setze Variable "Stkt" gleich der aktuell geöffneten Mappe (soeben heruntergeladene Mappe des BO-Berichts)  -----
    Set WBS = ThisWorkbook

    stFolder = WBS.Sheets("Laufwerkspfade").Range("F28").Value

   ' C:\Users\R6356327\Desktop\Float-Planer_KW28 AF_mit Formeln (Repariert).xlsm

'----- Datei öffnen // nur Excelmappen im Explorer anzeigen -----
    StaktPfad = WBS.Sheets("Laufwerkspfade").Range("F38").Value
    Set Stkt = Workbooks.Open(StaktPfad)

'Stock Import

If Stkt.Worksheets("Stock").FilterMode Then
        Sheets("Stock").ShowAllData
End If

langRow = Stkt.Sheets("Stock").Cells(Rows.Count, 2).End(xlUp).Row
Stkt.Sheets("Stock").Range("B2:AM" & langRow).Cells.Clear

finame = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Orion Lagerbestand öffnen")
    If finame = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set ORDERM = Workbooks.Open(Filename:=finame, UpdateLinks:=0)
'----- Falls in der zu öffnenden Datei im Quell-Sheet Filter gesetzt sind, lösche diese, um alle Kommentare kopieren zu können -----
        If ORDERM.Worksheets(1).FilterMode Then
        Sheets(1).ShowAllData
        End If

        langRow = ORDERM.Worksheets(1).Cells(Rows.Count, 1).End(xlUp).Row

        '----- Filtere den Lagerbestand --> keine Qualität 22 + keine Deckscheiben (Paketierung 1001) & <>Herkunft LAMI -----
        With ORDERM.Worksheets(1)
            With .Range("F2:F" & langRow)
                    .NumberFormat = "General"
                    .Value = .Value
            End With
            .Rows("1:1").AutoFilter
            .Range("A1:AL" & langRow).AutoFilter Field:=8, Criteria1:="<>1001", Operator:=xlAnd
            '----- alle übriggebliebenen nicht ausgeblendeten Zeilen (Floatprodukte) kopieren...  -----
            .Range("A2:AL" & langRow).SpecialCells(xlCellTypeVisible).Copy
        End With
        '----- ...und in den Floatplaner übertragen -----
        Stkt.Worksheets("Stock").Range("B2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats


'----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        ORDERM.Close SaveChanges:=False
    End If
        Set ORDERM = Nothing

langRow = Stkt.Worksheets("Stock").Cells(Rows.Count, 2).End(xlUp).Row
With Stkt.Worksheets("Stock")
    .Range("A2").Copy
    .Range("A2:A" & langRow).PasteSpecial Paste:=xlPasteFormulas
End With

Application.Calculate

'Stock Import End

    Application.Calculate
    'Stkt.Sheets("Start").Range("C16") = Adres

'----- MSTR Planer öffnen -----
    MSTRPfad = WBS.Sheets("Laufwerkspfade").Range("F10").Value
    Set MSTRdata = Workbooks.Open(MSTRPfad)


'---- falls Filter im Blatt "Products" vorhanden, dann Filter entfernen und alle Daten anzeigen -----
    If MSTRdata.Worksheets("Products").FilterMode Then
        Sheets("Products").ShowAllData
    End If

'----- Zähle die ausgefüllten Zeilen, Spalte 1 und setze einen Filter in Spalte B auf Verpackung "027" -----
    langRow = MSTRdata.Worksheets("Products").Cells(Rows.Count, 1).End(xlUp).Row

    With MSTRdata.Sheets("Products")
        With .Range("U2:U" & langRow)
                .NumberFormat = "General"
                .Value = .Value
        End With
        .Range("$A$1:$AU$" & langRow).AutoFilter Field:=2, Criteria1:="027", Operator:=xlAnd
        .Range("$A$1:$AU$" & langRow).AutoFilter Field:=31, Criteria1:="<>1001", Operator:=xlAnd
    '----- Kopiere alle sichtbaren(!) Daten in Spalte B und füge sie in den Floatplaner ab Zelle E7 ein -----
        .Range("C2:C" & langRow).SpecialCells(xlCellTypeVisible).Copy
    End With
    Stkt.Sheets("Float Planung").Range("B2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

    '----- Zähle alle befüllten Zeilen in "Float Planung", Spalte 5 (E) und wandle die als Text gespeicherten Zahlen in Zahlen um -----
    langRow = Stkt.Worksheets("Float Planung").Cells(Rows.Count, 2).End(xlUp).Row
    With Stkt.Sheets("Float Planung").Range("B2:B" & langRow)
    .NumberFormat = "General"
    .Value = .Value
    End With


    MSTRdata.Close SaveChanges:=False
    Set MSTRdata = Nothing


    '----- Kopiere die Formel von A7 bis D&langRow (letzte gezählte Zeile), sowie von F7 bis CN&langRow -----
    With Stkt.Sheets("Float Planung")
        .Range("A2").Copy
        .Range("A2:A" & langRow).PasteSpecial xlPasteFormulas

        .Range("C2:R2").Copy
        .Range("C2:R" & langRow).PasteSpecial xlPasteFormulas

         '---- Formate von erster Produktzeile auf alle neu eingefügten Zeilen übertragen -----
        .Rows("2:2").Copy
        .Rows("2:" & langRow).EntireRow.PasteSpecial Paste:=xlPasteFormats
    End With

    '----- alle Formeln berechnen -----
    Application.Calculate


    Set qta = Nothing
    Set wksht = Nothing
    Set lob = Nothing



    '----- alle nur als Wert benötigte Formeln kopieren und als Festwerte einfügen; muss nach Aktualisierung der Abfragen erfolgen,
    '----- da die Werte aus den Abfragen teilweise als Festwerte eingefügt werden.
    With Stkt.Sheets("Float Planung")
        .Range("A2:A" & langRow).Copy
        .Range("A2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("C2:R" & langRow).Copy
        .Range("C2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        '---- Formate von erster Produktzeile auf alle neu eingefügten Zeilen übertragen -----
        .Rows("2:2").Copy
        .Rows("2:" & langRow).EntireRow.PasteSpecial Paste:=xlPasteFormats
    End With

    Application.CutCopyMode = False

    '----- nicht mehr benötigte Abfragen + Verbindungen "Consumption" und "Sales" löschen -----
    With Stkt
        .Queries("Consumption").Delete
        .Connections("Abfrage - Consumption").Delete
        .Queries("Sales").Delete
        .Connections("Abfrage - Sales").Delete
        '----- Conso + Sales löschen, da Verbräuche bereits als Festwerte übernommen -----

    End With

    '----- Anzahl Zeilen der Tabellen in "MTS Production" und "MAG Verbrauch" zählen, um ISO-kwo-Formel zu kopieren -----
  '  Set tablRow = Stkt.Worksheets("MTS Verbrauch").ListObjects("Prod_Planning").ListRows.Count
  '      .Range("A2").Copy


   ' Stkt.Worksheets("MAG Verbrauch").ListObjects("Cons_Planning").ListRows.Count


    '----- speichere die aufbereitete Vorlage unter den Ordnerpfad von stFolder unter den Namen "Float-Planer_kwo"+ Wert der Kalenderwoche als .xlsx -----
    'Stkt.SaveAs Filename:=FolderStock & "Stock" & ".xlsx", FileFormat:=51
    '----- schließe die Vorlage ohne zu speichern (damit sie als Vorlage erhalten bleibt) -----
    Stkt.SaveAs Filename:=FolderStock & "Stock" & ".xlsx", FileFormat:=51
    Stkt.Close SaveChanges:=False
    Set Stkt = Nothing






'---------------------------------------------------------------
'---------------------------------------------------------------
'---------------------------------------------------------------
'------------------------------------------------
'Import Stock
sopen = WBS.Sheets("Laufwerkspfade").Range("F36").Value

    Set Stakt = Workbooks.Open(Filename:=sopen, UpdateLinks:=0)

StockRow = Stakt.Sheets("Float Planung").Cells(Rows.Count, 1).End(xlUp).Row

Stakt.Sheets("Float Planung").Range("$A$1:$R$" & StockRow).AutoFilter Field:=14, Criteria1:="<>0", Operator:=xlAnd
Stakt.Sheets("Float Planung").Range("A1:R" & (StockRow + 1)).SpecialCells(xlCellTypeVisible).Copy
Dakt.Sheets("Stock").Range("A1").PasteSpecial Paste:=xlPasteValues
Stakt.Close SaveChanges:=False
'Import Stock End
'------------------------------------------------
Application.CutCopyMode = False


'----- Letzte befüllte Zelle in Spalte 1 (A) finden und Anzahl aller Zellen von unten nach oben zählen -----
lngRow = Dakt.Worksheets(1).Cells(Rows.Count, 1).End(xlUp).Row

'----- Formeln ab Spalte Y einfügen und im selben Schritt bis zur letzten Zeile ausfüllen -----
With Dakt.Worksheets(1)
    .Range("AB2:AB" & lngRow).FormulaR1C1 = "=RC[-21]&RC[-4]"
    .Range("AC2:AC" & lngRow).FormulaR1C1 = _
        "=VLOOKUP(RC28,Tabelle1!C1:C5,2,FALSE)"
    .Range("AD2:AD" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,3,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,3,FALSE),""""))"
    .Range("AE2:AE" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,4,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,4,FALSE),""""))"
    .Range("AF2:AF" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,5,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,5,FALSE),""""))"
    .Range("AG2:AG" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,6,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,6,FALSE),""""))"
    .Range("AH2:AH" & lngRow).FormulaR1C1 = _
        "=IF(IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,7,FALSE),"""")=0,"""",IFERROR(VLOOKUP(RC28,Tabelle1!C1:C7,7,FALSE),""""))"
    .Range("AI2:AI" & lngRow).FormulaR1C1 = _
        "=IFERROR(IF(RC[-33]=R[-1]C[-33],R[-1]C-RC[-8],VLOOKUP(RC[-33],Stock!C[-34]:C[-18],14,FALSE)-RC[-8]),-1.001)"
    .Range("AK2:AK" & lngRow).FormulaR1C1 = _
        "=IFERROR(IF(RC[-2]>=(-0.5),"""",IF(OR(RC[-27]=""BI STADIP"",RC[-27]=""STD SILENCE""),"""",IF(OR(RC[-27]=""PLANILUX"",RC[-27]=""DIAMANT""),VLOOKUP((RC[-27]&RC[-23]),Produktionsprogram!C[-36]:C[-33],4,FALSE),VLOOKUP(RC[-25],Produktionsprogram!C[-36]:C[-33],4,0)))),""NOK"")"
    .Range("AJ2:AJ" & lngRow).FormulaR1C1 = _
        "=IFERROR(IF(RC[-1]>=(-0.5),""OK"",IF(RC[1]=""NOK"",""NOK"",IF(OR(((RC[1])+1)<=RC3,RC[1]="" ""),""NP"",""NOK""))),""NP"")"
    .Range("AL2:AL" & lngRow).FormulaR1C1 = "=IFERROR(WEEKNUM(RC[-1]),"""")"


End With

'---Bedingte Formatierung Automatom---

With Dakt.Worksheets(1).Range("AJ2:AJ" & lngRow)
    .FormatConditions.Add Type:=xlExpression, Formula1:="=AJ2= (""OK"")"
    .FormatConditions(1).Interior.Color = RGB(146, 208, 80)
    .FormatConditions.Add Type:=xlExpression, Formula1:="=AJ2= (""NOK"")"
    .FormatConditions(2).Interior.Color = RGB(255, 0, 0)
    .FormatConditions.Add Type:=xlExpression, Formula1:="=UND(AJ2=""NP"";(C2-HEUTE())<=14)"
    .FormatConditions(3).Interior.Color = RGB(255, 134, 1)
    .FormatConditions.Add Type:=xlExpression, Formula1:="=UND(AJ2=""NP"";(C2-HEUTE())>14)"
    .FormatConditions(4).Interior.Color = RGB(255, 255, 0)
End With




'----- alle Formeln berechnen lassen (da Anfangs autmatische Berechnung ausgeschaltet, um Makro zu beschleunigen -----
Application.Calculate


With Dakt.Worksheets(1)
    .Range("AB1:AL" & lngRow).Copy
    .Range("AB1:AL" & lngRow).PasteSpecial Paste:=xlPasteValuesAndNumberFormats '
End With

'---- Datum auf "kurz" + Hilfsspalte ausblenden -----
With Dakt.Worksheets(1)
    .Columns("AD:AD").NumberFormat = "d/m/yy;@"
    .Columns("AB:AB").EntireColumn.Hidden = True
    .Columns("B:B").EntireColumn.Hidden = True
    .Columns("AG:AG").NumberFormat = "d/m/yyyy;@"
    .Columns("AG:AG").EntireColumn.Hidden = True
    .Columns("AH:AH").NumberFormat = "00;@"
    .Columns("AH:AH").EntireColumn.Hidden = True
    .Columns("AI:AI").EntireColumn.Hidden = True
    .Columns("AJ:AJ").NumberFormat = "d/m/yyyy;@"
    .Columns("AK:AK").NumberFormat = "d/m/yyyy;@"
End With


'----- bedingte Formatierung inkl. Formel --> wenn frühestest Versanddatum> Ladedatum, dann markiere Versanddatum organe-----
With Dakt.Worksheets(1)
    .Activate
    .Range("AD2").Activate
       With ActiveCell
        .FormatConditions.Add Type:=xlExpression, Formula1:="=UND(AD2<>"""";C2<AD2)"
        .FormatConditions(1).Interior.Color = 49407
        End With
'----- bedingte Formatierung auf gesamte Spalte übertragen -----
    .Range("AD2").Copy
    .Range("AD2:AD" & lngRow).PasteSpecial Paste:=xlPasteFormats
End With

'----- bedingte Formatierung inkl. Formel --> Vergleich Ladedatum mit Vortrag, dann markiere Versanddatum organe-----
With Dakt.Worksheets(1)
    .Activate
    .Range("C2").Activate
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
    .Range("Y2").Activate
       With ActiveCell
        .FormatConditions.Add Type:=xlExpression, Formula1:="=UND(AH2<>"""";Y2<>AH2)"
        .FormatConditions(1).Interior.Color = 49407
        End With
'----- bedingte Formatierung auf gesamte Spalte übertragen -----
    .Range("Y2").Copy
    .Range("Y2:Y" & lngRow).PasteSpecial Paste:=xlPasteFormats

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

'----Spaltenbreit anpassen----
With Dakt.Worksheets(1)
    .Columns("A:A").ColumnWidth = 4#
    .Columns("C:C").ColumnWidth = 8.6
    .Columns("E:E").ColumnWidth = 9.6
    .Columns("F:F").ColumnWidth = 8.15
    .Columns("G:G").ColumnWidth = 7.8
    .Columns("H:H").ColumnWidth = 7.4
    .Columns("I:I").ColumnWidth = 4.6
    .Columns("K:K").ColumnWidth = 6.3
    .Columns("L:L").ColumnWidth = 8.6
    .Columns("M:M").ColumnWidth = 9.7
    .Columns("N:N").ColumnWidth = 4.45
    .Columns("O:O").ColumnWidth = 3.15
    .Columns("Q:Q").ColumnWidth = 2.45
    .Columns("R:R").ColumnWidth = 5.3
    .Columns("S:S").ColumnWidth = 7.15
    .Columns("U:U").ColumnWidth = 2
    .Columns("V:V").ColumnWidth = 4.15
    .Columns("W:W").ColumnWidth = 4
    .Columns("X:X").ColumnWidth = 9.6
    .Columns("Y:Y").ColumnWidth = 4.45
    .Columns("Z:Z").ColumnWidth = 6.15
    .Columns("AA:AA").ColumnWidth = 6.3
    .Columns("AC:AC").ColumnWidth = 6.6
    .Columns("AJ:AJ").ColumnWidth = 7.3
    .Columns("AK:AL").ColumnWidth = 8.8
End With

'---Zeilenhöhe anpassen---

With Dakt.Worksheets(1)
    .Rows(1).RowHeight = 60
End With

'----- heutiges Datum ermitteln und Datei automatisch unter heutigem Datum im Standardordner speichern -----
Dakt.SaveAs Filename:=strFolder & TodayDate & " G035 Auftragsbestand.xlsx", FileFormat:=51
Dakt.SaveAs Filename:=strFolder & "G035 Auftragsbestand.xlsx", FileFormat:=51
'Dakt.SaveAs Filename:=strFolder & "Testdatei.xlsx", FileFormat:=51
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
