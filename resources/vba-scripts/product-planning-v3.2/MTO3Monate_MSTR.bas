Attribute VB_Name = "MTO3Monate_MSTR"

Option Explicit

Sub MTO3MonateMSTR()

'©
'Programmiert von: René Sagert
'SGGD Köln-Porz 2018-2021

'
' MTO > 3 Monate aufbereiten
'


' ----- Variablen definieren -----
    Dim fname As Variant
    Dim WB As Workbook, Dakt As Workbook, CPclose As Workbook
    Dim lngRow As Long, i As Long
    Dim NewButton As Object
    Dim Date1 As String, Date2 As String, wbName As String


    With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
    End With

' ---- Setze Variable "Dakt" gleich der heruntergeladenen, neuen MTO-Datei  -----
   fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Heruntergeladene MTO-Datei öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set Dakt = Workbooks.Open(Filename:=fname, UpdateLinks:=0)


'----- Tabelle "order book" --> Spalte B in Zahl umwandeln -----
lngRow = Dakt.Sheets(2).Cells(Rows.Count, 1).End(xlUp).Row
With Dakt.Sheets(2)
    With .Range("B2:B" & lngRow)
         .NumberFormat = "General"
         .Value = .Value
    End With
    .Name = "order book"
End With


    lngRow = Dakt.Sheets(1).Cells(Rows.Count, 1).End(xlUp).Row
    With Dakt.Worksheets(1)
        .Columns("B:B").Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove
        .Range("B1").FormulaR1C1 = "Bestandsdatum"
        .Range("B2:B" & lngRow).Value = Date
        .Range("B2:B" & lngRow).NumberFormat = "m/d/yyyy"
        .Columns("B:B").EntireColumn.AutoFit
        .Name = "MTO Critical"
    End With


    With Dakt.Worksheets(1).Range("A1:AK" & lngRow).Font
        .Name = "Calibri"
        .Size = 10
    End With

    lngRow = Dakt.Sheets(2).Cells(Rows.Count, 1).End(xlUp).Row
    With Dakt.Worksheets(2).Range("A1:AK" & lngRow).Font
        .Name = "Calibri"
        .Size = 10
    End With

    Dakt.Sheets.Add(After:=Sheets(Sheets.Count)).Name = "593"




        '----- Standardverzeichnis für FileDialog vorgeben (siehe nächster Schritt) -----
    Call ChDrive("M")
    Call ChDir("M:\000_alle\PPS\04 MTO Management")

    ChDir "M:\000_alle\PPS\04 MTO Management"

'----- Datei der vorherigen Sitzung manuell öffnen // nur Excelmappen im Explorer anzeigen -----
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Vorherige MTO Datei öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set WB = Workbooks.Open(Filename:=fname, UpdateLinks:=0)
'----- Falls in der zu öffnenden Datei im Quell-Sheet Filter gesetzt sind, lösche diese, um alle Kommentare kopieren zu können -----
        If WB.Worksheets("MTO Critical").FilterMode Then
        Sheets("MTO Critical").ShowAllData
        End If

        lngRow = Cells(Rows.Count, 1).End(xlUp).Row

        lngRow = WB.Worksheets("SVerweis").Cells(Rows.Count, 2).End(xlUp).Row
        WB.Worksheets("SVerweis").Range("A2:AK" & lngRow).ClearContents


        Sheets(Array("SVerweis", "Reason Codes", "Historic Data")).Copy After:= _
        Dakt.Sheets(Dakt.Sheets.Count)

        WB.Worksheets("MTO Critical").Range("AC2:AH" & lngRow).Copy
        Dakt.Worksheets("SVerweis").Range("B2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        Application.CutCopyMode = False
        Dakt.Worksheets("SVerweis").Columns(2).NumberFormat = "General"


        WB.Worksheets("MTO Critical").Range("K2:K" & lngRow).Copy
        Dakt.Worksheets("SVerweis").Range("A2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        Application.CutCopyMode = False



'----- Überschriften aus alter Datei in neue Datei kopieren -----
    WB.Sheets("Historic Data").Range("X1:AH1").Copy
    Dakt.Worksheets("MTO Critical").Range("X1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    Application.CutCopyMode = False

    Dakt.Worksheets("MTO Critical").Activate
    lngRow = Cells(Rows.Count, 1).End(xlUp).Row

    With ActiveSheet
        .Range("Q2:Q" & lngRow).FormulaLocal = "=WENNFEHLER(SVERWEIS(K:K;'593'!A:AL;34;FALSCH);"""")"
        .Range("X2:X" & lngRow).FormulaLocal = "=WENNFEHLER(SVERWEIS(D:D;'order book'!A:P;12;FALSCH);"""")"
        .Range("Y2:Y" & lngRow).FormulaLocal = "=WENNFEHLER(SVERWEIS(D:D;'order book'!A:P;2;FALSCH);"""")"
        .Range("Z2:Z" & lngRow).FormulaLocal = "=WENNFEHLER(SUMMEWENN('order book'!A:O;'MTO Critical'!D:D;'order book'!O:O);"""")"
        .Range("AA2:AA" & lngRow).FormulaLocal = "=WENNFEHLER(SVERWEIS(D:D;'order book'!A:P;3;FALSCH);"""")"
        .Range("AB2:AB" & lngRow).FormulaLocal = "=WENNFEHLER(SVERWEIS(D:D;'order book'!A:P;4;FALSCH);"""")"

        .Range("AC2:AC" & lngRow).FormulaLocal = "=SVERWEIS($K:$K;SVerweis!$A:$G;2;FALSCH)"
        .Range("AD2:AD" & lngRow).FormulaLocal = "=SVERWEIS(AC:AC;'Reason Codes'!$A:$B;2;FALSCH)"
        .Range("AE2:AE" & lngRow).FormulaLocal = "=WENNFEHLER(SVERWEIS($K:$K;SVerweis!$A:$G;4;FALSCH);"""")"
        .Range("AF2:AF" & lngRow).FormulaLocal = "=WENNFEHLER(SVERWEIS($K:$K;SVerweis!$A:$G;5;FALSCH);"""")"
        .Range("AG2:AG" & lngRow).FormulaLocal = "=WENNFEHLER(SVERWEIS($K:$K;SVerweis!$A:$G;6;FALSCH);"""")"
        .Range("AH2:AH" & lngRow).FormulaLocal = "=WENNFEHLER(SVERWEIS($K:$K;SVerweis!$A:$G;7;FALSCH);"""")"

        .Range("Y2:Y" & lngRow).NumberFormat = "General"
        .Range("AB2:AB" & lngRow).NumberFormat = "d/m;@"
        .Range("AF2:AF" & lngRow).NumberFormat = "d/m;@"
    End With

        '----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        WB.Close SaveChanges:=False
    End If
        Set WB = Nothing




    lngRow = ActiveWorkbook.Sheets("Historic Data").Cells(Rows.Count, 2).End(xlUp).Row
    If Worksheets("Historic Data").AutoFilterMode Then Worksheets("Historic Data").AutoFilterMode = False

    With Dakt.Worksheets("Historic Data")
        .Range("B2:B" & lngRow).NumberFormat = "m/d/yyyy"
   '     .Columns("B:B").TextToColumns Destination:=Range("B1"), DataType:=xlDelimited, _
        TextQualifier:=xlDoubleQuote, ConsecutiveDelimiter:=False, Tab:=True, _
        Semicolon:=False, Comma:=False, Space:=False, Other:=False, FieldInfo _
        :=Array(1, 4), TrailingMinusNumbers:=True
        .Columns("B:B").EntireColumn.AutoFit
    End With


    Dakt.Worksheets("MTO Critical").Activate
    lngRow = Cells(Rows.Count, 2).End(xlUp).Row
    Range("B2:B" & lngRow).Value = Date - 1
    Range("A2:AG" & lngRow).Copy

     Worksheets("Historic Data").Activate
    '----- letzte befüllte Zeile in "Historic Data" finden und Daten unterhalb (+1) einfügen -----
     lngRow = Cells(Rows.Count, 1).End(xlUp).Row
     Range("A" & lngRow + 1).PasteSpecial Paste:=xlPasteValuesAndNumberFormats
     Application.CutCopyMode = False


'----- Variable lngRow neuen Wert zuweisen, um dynamischen Datenbereich für die zu erzeugende PivotTabelle zu erfassen -----
    lngRow = Worksheets("Historic Data").Cells(Rows.Count, 1).End(xlUp).Row



    Application.Calculation = xlCalculationAutomatic
'----- Tabelle "MTO Critical" & "Historic Data" mit Namen versehen, damit automatische Aktualisierung der Pivot mit neuem Datum automatisch bei Aktualisieren der Pivot geschehen kann -----
'----- https://groups.google.com/forum/#!topic/microsoft.public.de.excel/l7sKsw1ucHM  -----

    Worksheets("MTO Critical").Activate
    ActiveWorkbook.Names.Add Name:="Critical", RefersToR1C1:= _
        "=OFFSET('MTO Critical'!R1C1,,,COUNTA('MTO Critical'!C1),COUNTA('MTO Critical'!R1))"

    Worksheets("Historic Data").Activate
    ActiveWorkbook.Names.Add Name:="Historic2", RefersToR1C1:= _
        "=OFFSET('Historic Data'!R1C1,,,COUNTA('Historic Data'!C1),COUNTA('Historic Data'!R1))"

    Application.Calculation = xlCalculationManual


'----- Tabellenblatt mit Name "EntwicklungMaßnahmen" hinzufügen -----
    Worksheets.Add.Name = "EntwicklungMaßnahmen"

'----- PivotTabelle unter Berücksichtigung des zuvor erzeugten dynamischen Bereichs "Historic" erzeugen -----
    ActiveWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:= _
           "Critical", Version:=6).CreatePivotTable _
        TableDestination:="EntwicklungMaßnahmen!R1C1", TableName:="PivotTable1", _
        DefaultVersion:=6


      Worksheets("EntwicklungMaßnahmen").Activate
'----- Felder in der PivotTabelle automatisch zuweisen -----
    With ActiveSheet.PivotTables("PivotTable1")
        .PivotFields("Datum").Orientation = xlColumnField

'----- PivotItems("0") und ("(blank)") können Fehler verursachen. Resume Next bis Ende des WITH-Blocks, um diesen abzufangen -----
    On Error Resume Next
        With .PivotFields("Wer")
        .Orientation = xlRowField
        .Position = 1
        .PivotItems("0").Visible = False
       ' .PivotItems("#N/A").Visible = False
        .PivotItems("(blank)").Visible = False
        End With

'----- Standard der Fehlerroutine wieder einschalten -----
    On Error GoTo 0

        With .PivotFields("Aktion")
        .Orientation = xlRowField
        .Position = 2
        End With

        .AddDataField ActiveSheet.PivotTables("PivotTable1").PivotFields("ID Sheet ID"), "Anzahl von ID Sheet ID", xlCount
        .ShowDrillIndicators = False
        .PivotFields("Wer").ShowDetail = True
        .TableStyle2 = "PivotStyleDark2"
    End With


'----- Tabellenblatt mit Name "EntwicklungMengen" hinzufügen -----
    Worksheets.Add.Name = "EntwicklungMengen"

'----- PivotTabelle unter Berücksichtigung des zuvor erzeugten dynamischen Bereichs "Historic" erzeugen -----
    ActiveWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:= _
           "Historic2", Version:=6).CreatePivotTable _
        TableDestination:="EntwicklungMengen!R1C1", TableName:="PivotTable2", _
        DefaultVersion:=6

        Date1 = Date - 94
        Date2 = Date

    With ActiveSheet.PivotTables("PivotTable2")
        .PivotFields("Bestandsdatum").Orientation = xlColumnField
        .PivotFields("Material Com Desc").Orientation = xlPageField
        .PivotFields("Aktion").Orientation = xlRowField

        .AddDataField ActiveSheet.PivotTables("PivotTable2").PivotFields("Stock TO"), "Summe von Stock TO", xlSum
        .PivotCache.Refresh
        .PivotFields("Bestandsdatum").ClearAllFilters
        .PivotFields("Summe von Stock TO").NumberFormat = "0"
        .RowGrand = False
        .PivotFields("Bestandsdatum").PivotFilters.Add Type:=xlDateBetween, Value1:=Date1, Value2:=Date2
     End With

    ActiveSheet.Columns("B:ZZ").EntireColumn.AutoFit


    '----- Tabellenblatt mit Name "Pivot" hinzufügen -----
    Worksheets.Add.Name = "Pivot"

'----- PivotTabelle unter Berücksichtigung des zuvor erzeugten dynamischen Bereichs "Historic" erzeugen -----
    ActiveWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:= _
           "Critical", Version:=6).CreatePivotTable _
        TableDestination:="Pivot!R1C1", TableName:="PivotTable3", _
        DefaultVersion:=6

    With ActiveSheet.PivotTables("PivotTable3")
        With .PivotFields("Aktion")
        .Orientation = xlPageField
        .ClearAllFilters
        .CurrentPage = "#N/A"
        End With
        With .PivotFields("Aktion")
        .Orientation = xlPageField
        .Position = 1
        End With
        With .PivotFields("Sub-Family DESC")
                .Orientation = xlRowField
              '  .Position = 2
        End With
        With .PivotFields("Ginger Code 17 ID")
        .Orientation = xlRowField
        '.Position = 3
        End With
        .AddDataField ActiveSheet.PivotTables("PivotTable3").PivotFields("Stock TO"), "Summe von Stock TO", xlSum
        .PivotFields("Summe von Stock TO").NumberFormat = "0"
        .PivotFields("Ginger Code 17 ID").AutoSort xlDescending, "Ginger Code 17 ID"
    End With

    ActiveSheet.PivotTables("PivotTable3").PivotFields("Aktion").ClearAllFilters
    ActiveSheet.PivotTables("PivotTable3").PivotFields("Aktion").CurrentPage = _
        "#N/A"


    '----- Alte Datensätze aus "Historic Data" löschen, die nicht mehr in aktueller Liste vorhanden sind bzw. älter als 93 Tage sind -----
    Dakt.Worksheets("Historic Data").Activate
    lngRow = Worksheets("Historic Data").Cells(Rows.Count, 1).End(xlUp).Row

    '----- Hilfsspalten einfügen --> welche GBS sind nicht mehr aktuell?
    With ActiveSheet
      .Range("AH1").Value = "löschen"
      .Range("AI1").Value = "Unique?"
      .Range("AH2:AH" & lngRow).FormulaLocal = "=SVERWEIS(K2;'MTO Critical'!K:K;1;FALSCH)"
      .Range("AI2:AI" & lngRow).FormulaLocal = "=ZÄHLENWENN($K$2:K2;K2)=ZÄHLENWENN(K:K;K2)"
    End With

    ActiveSheet.Columns("AH:AI").Copy
    ActiveSheet.Range("AH1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

    Application.CutCopyMode = False


    '----- alle GBS löschen, die älter 93 Tage sind und doppelt vorkommen + nicht in den Versand gehen --> alles außer _
    aktuellsten Kommentar löschen (längere Rückverfolgbarkeit unnötig) -----
    If ActiveSheet.AutoFilterMode Then ActiveSheet.AutoFilterMode = False

    With ActiveSheet
        .Rows("1:1").AutoFilter
        .Range("A1").AutoFilter Field:=2, Criteria1:="<" & CLng(Date) - 93
        .Range("A1").AutoFilter Field:=28, Criteria1:="#NV"
        .Range("A1").AutoFilter Field:=35, Criteria1:="FALSCH"
    End With

    lngRow = Worksheets("Historic Data").Cells(Rows.Count, 1).End(xlUp).Row

    ActiveSheet.Range("AI:AI").RemoveDuplicates Columns:=1, Header:=xlYes

    If lngRow > 1 Then

        With ActiveSheet
            .Rows("1:1").Hidden = True
            .UsedRange.SpecialCells(xlCellTypeVisible).Delete
            .Rows("1:1").Hidden = False
            .ShowAllData
        End With
    Else
    ActiveSheet.ShowAllData
    End If


    '----- Hilfsspalten löschen -----
    With ActiveSheet
        .Columns("AH:AI").Delete
        .Range("A1").Select
    End With


    ActiveWorkbook.Worksheets("MTO Critical").Activate
    ActiveSheet.Rows("1:1").AutoFilter
    On Error Resume Next
    Sheets("MTO Critical").Range("$A$1:$AH$" & lngRow).AutoFilter Field:=29, Criteria1:="#NV"
    On Error GoTo 0


    ActiveWorkbook.RefreshAll

    Range("T1").Copy
    Range("X1:AH1").PasteSpecial Paste:=xlPasteFormats, Operation:=xlNone, _
        SkipBlanks:=False, Transpose:=False
    Application.CutCopyMode = False


'----- Button "Sitzung beenden" hinzufügen, um per zugewiesenem Makro Blatt "Historic Data" + Pivottabelle zu aktualisieren ------
    ActiveSheet.Buttons.Add(2170.25, 0.75, 150, 54).Select
        With Selection
        .OnAction = "SitzungBeenden3"
        .Caption = "Sitzung beenden"
        .Font.Bold = True
        .Placement = xlFreeFloating
        .PrintObject = False
        End With

    Range("A1").Select

    Sheets("EntwicklungMengen").Select
    ActiveWindow.Zoom = 115

End If


With Application
        .DisplayAlerts = True
        .ScreenUpdating = True
        .EnableEvents = True
        .Calculation = xlCalculationAutomatic
        .CutCopyMode = False
End With


End
End Sub

Sub SitzungBeenden3()

    Dim lngRow As Long, lngRow2 As Long, lCnt As Long
    Dim Dakt As Workbook
    Dim objMail As Object, nachricht As Object
    Dim spath As String, sname As String, scomplete As String
    Dim Date1 As String, Date2 As String, strbody As String, Signature As String
    Dim p As PivotTable
    Dim ws As Worksheet


    Set Dakt = ActiveWorkbook
    Date1 = Date - 63
    Date2 = Date


    With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
    End With

    spath = Dakt.Path
    sname = Dakt.Name
    scomplete = Dakt.Path + "\" + Dakt.Name


    On Error GoTo Fehlermeldung


    Sheets("MTO Critical").Activate
    If ActiveSheet.FilterMode Then
        Sheets("MTO Critical").ShowAllData
        End If


    lngRow = Cells(Rows.Count, 2).End(xlUp).Row
    Range("A2:AH" & lngRow).Copy

    Worksheets("Historic Data").Activate
    '----- letzte befüllte Zeile in "Historic Data" finden und Daten unterhalb (+1) einfügen -----
         lngRow = Cells(Rows.Count, 1).End(xlUp).Row
         Range("A" & lngRow + 1).PasteSpecial Paste:=xlPasteValuesAndNumberFormats
         Application.CutCopyMode = False

    '----- Datum der eingefügten Daten auf heutiges Datum setzen -----
    lngRow2 = Cells(Rows.Count, 2).End(xlUp).Row
    Range("B" & lngRow + 1).Value = Date
    Range("B" & lngRow + 1).AutoFill Destination:=Range("B" & lngRow + 1 & ":B" & lngRow2), Type:=xlFillCopy


'----- PivoTabelle mit neuem / erweitertem Datenbereich aktualisieren -----
    For Each ws In Dakt.Worksheets
        For Each p In ws.PivotTables
            p.PivotCache.Refresh
        Next
    Next

    ActiveWorkbook.RefreshAll

    Worksheets("EntwicklungMengen").Columns("A:ZZ").EntireColumn.AutoFit


'----- Button "Sitzung beenden" löschen, damit Ausführung nicht mehrfach passieren kann -----
    Worksheets("MTO Critical").Activate
    ActiveSheet.Shapes.Range(Array("Button 1")).Delete

    Sheets("EntwicklungMengen").Select

    With Application
        .CutCopyMode = False
        .DisplayAlerts = True
        .ScreenUpdating = True
        .EnableEvents = True
    End With

            Set objMail = CreateObject("Outlook.Application")
            Set nachricht = objMail.CreateItem(0)

            strbody = "<BODY style=font-size:11pt;font-family:Calibri>Hallo zusammen,<p>als Nachbereitung der heutigen MTO > 3 Monate -Sitzung nachfolgend ein Überblick über die Entwicklung (Maßnahmen + Mengen) + der Link zur Arbeitsdatei.<p><p>Entwicklung Maßnahmen:<p><p>Entwicklung Mengen:<p><p><a href='file:///" & scomplete & "'>" & sname & "</a><p><p></BODY>"

            '---- neue E-Mail anlegen -----

            With nachricht
                .Display
            End With
                Signature = nachricht.HTMLBody

            With nachricht
                .To = "MTO3Monate"
                .Recipients.ResolveAll
                .Subject = "MTO > 3 Monate; " & Date
                .HTMLBody = strbody & Signature
                .Display
            End With


'----- alle Variablen leeren -----
End

Exit Sub


'----- Sprungmarke "Fehlermeldung" --> Warnmeldung inkl. Errorcode & -beschreibung ausgeben -----
Fehlermeldung:
MsgBox "Es ist ein Fehler aufgetreten. Die Prozedur wurde abgebrochen." & Chr(13) & _
"Bitte wenden Sie sich an Ihren Administrator" & Chr(13) & Chr(13) & "Fehlercode: " & Err.Number & " - " & Err.Description, vbCritical

End

End Sub
