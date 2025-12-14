Attribute VB_Name = "VSGPlanerNeueWoche"
Option Explicit

Sub VSGPlaner_NeueWoche()


'©
'Programmiert von: René Sagert
'SGGD Köln-Porz 2018-2021

'

' ----- Variablen definieren -----
    Dim fname As Variant
    Dim Dakt As Workbook, WB As Workbook, MSTRdata As Workbook, DatVw As Workbook
    Dim strFolder As String, DaktPfad As String, MSTRdataPfad As String
    Dim lngRow As Long, i As Long
    Dim wks1 As Worksheet, wks2 As Worksheet, wks As Worksheet
    Dim qt As QueryTable
    Dim lo As ListObject
    Dim kw As Byte '---> ausreichend, da KW max. zwischen 1 bis 53 liegen kann
    Dim tblRow As ListObject


    With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
    End With


' ---- Setze Variable "WB" gleich der aktuell geöffneten Mappe (Makro-Sammelmappe)  -----
    Set WB = ThisWorkbook

    '----- Variable strFolder
    strFolder = WB.Sheets("Laufwerkspfade").Range("F24").Value


'----- Vorlagendatei öffnen // nur Excelmappen im Explorer anzeigen -----
    DaktPfad = WB.Sheets("Laufwerkspfade").Range("F22").Value
    Set Dakt = Workbooks.Open(DaktPfad)

    Application.Calculate


    '-----Blatt "Validierungen" muss gelöscht werden, damit es beim QuerryUpdate später im Makro keinen Fehler gibt -----
    '----- das Blatt "Validierungen" wird später wieder eingefügt (aus Datei der Vorwoche kopiert) -----
    For Each wks2 In Dakt.Worksheets
        If wks2.Name = "Validierungen" Then
        Sheets("Validierungen").Delete
    End If
    Next

    '----- übernimm die aktuelle Kalenderwoche in die Variable "kw" -----
    kw = Dakt.Sheets("VSG Planung").Range("AA4").Value

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
        .Range("$A$1:$AU$" & lngRow).AutoFilter Field:=21, Criteria1:="22", Operator:=xlAnd
    '----- Kopiere alle sichtbaren(!) Daten in Spalte B und füge sie in den Floatplaner ab Zelle E7 ein -----
        .Range("C2:C" & lngRow).SpecialCells(xlCellTypeVisible).Copy
    End With
    Dakt.Sheets("VSG Planung").Range("F6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

    '----- Zähle alle befüllten Zeilen in "MAG Planung", Spalte 6 (F) und wandle die als Text gespeicherten Zahlen in Zahlen um -----
    lngRow = Dakt.Worksheets("VSG Planung").Cells(Rows.Count, 6).End(xlUp).Row
    With Dakt.Sheets("VSG Planung").Range("F6:F" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With


    MSTRdata.Close SaveChanges:=False
    Set MSTRdata = Nothing


    '----- Kopiere die Formel von A6 bis D&lngRow (letzte gezählte Zeile), sowie von F7 bis CN&lngRow -----
    With Dakt.Sheets("VSG Planung")
        .Range("A6:E6").Copy
        .Range("A6:E" & lngRow).PasteSpecial xlPasteFormulas

        .Range("G6:CP6").Copy
        .Range("G6:CP" & lngRow).PasteSpecial xlPasteFormulas
    End With

'----- VSG Planer der Vorwoche öffnen, um Planungsdaten zu übernehmen -----
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Planungsdatei der Vorwoche öffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgewählt.", vbExclamation, "ERROR"
    Exit Sub
    Else
    Set DatVw = Workbooks.Open(Filename:=fname, UpdateLinks:=0)
'----- Falls in der zu öffnenden Datei im Quell-Sheet Filter gesetzt sind, lösche diese, um alle Kommentare kopieren zu können -----
        If DatVw.Worksheets("VSG Planung").FilterMode Then
        Sheets("VSG Planung").ShowAllData
        End If

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

'----- "Klassifizierungen" wird in Vorlage geleert und später aus der Vorwoche übernommen, damit die Tabelle immer auf dem neusten Stand ist -----
    Dakt.Worksheets("Klassifizierungen").Cells.Clear

        DatVw.Sheets("Klassifizierungen").Range("A1:Z999").Copy
        Dakt.Worksheets("Klassifizierungen").Range("A1").PasteSpecial xlPasteAll
        '---- Daten aus alter Datei von "Folgewoche" kopieren... -----
        DatVw.Sheets("Produktion Folgewoche").Range("A1:B99").Copy


        '----- ....und in neuer Datei unter "aktuelle Woche" einfügen -----
        With Dakt
            With .Worksheets("Produktion aktuelle Woche")
                 .Range("A1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
            End With
            .Worksheets("Produktion Folgewoche").Range("A2:B99").Cells.Clear
        End With


        '----- Daten aus alter Datei, aktuelle Woche +3 in neue Datei "Folgewoche" kopieren -----
        lngRow = DatVw.Worksheets("VSG Planung").Cells(Rows.Count, 8).End(xlUp).Row
        With DatVw.Worksheets("VSG Planung")
                .Rows("5:5").AutoFilter
                .Range("A5:CP" & lngRow).AutoFilter Field:=40, Criteria1:="<>0"
                .Range("F6:F" & lngRow).SpecialCells(xlCellTypeVisible).Copy
        End With


        Dakt.Worksheets("Produktion Folgewoche").Range("A2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

        DatVw.Worksheets("VSG Planung").Range("AN6:AN" & lngRow).SpecialCells(xlCellTypeVisible).Copy
        Dakt.Worksheets("Produktion Folgewoche").Range("B2").PasteSpecial Paste:=xlPasteValuesAndNumberFormats


    With DatVw.Sheets("VSG Planung")
        .ShowAllData
        .Range("F6:F" & lngRow).Copy
    End With
    Dakt.Sheets("Wochenplanung").Range("A1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats


    DatVw.Sheets("VSG Planung").Range("AT6:AT" & lngRow).Copy
    Dakt.Sheets("Wochenplanung").Range("B1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    DatVw.Sheets("VSG Planung").Range("AZ6:AZ" & lngRow).Copy
    Dakt.Sheets("Wochenplanung").Range("C1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    DatVw.Sheets("VSG Planung").Range("BF6:BF" & lngRow).Copy
    Dakt.Sheets("Wochenplanung").Range("D1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    DatVw.Sheets("VSG Planung").Range("BL6:BL" & lngRow).Copy
    Dakt.Sheets("Wochenplanung").Range("E1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    DatVw.Sheets("VSG Planung").Range("BR6:BR" & lngRow).Copy
    Dakt.Sheets("Wochenplanung").Range("F1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    DatVw.Sheets("VSG Planung").Range("BX6:BX" & lngRow).Copy
    Dakt.Sheets("Wochenplanung").Range("G1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    DatVw.Sheets("VSG Planung").Range("CD6:CD" & lngRow).Copy
    Dakt.Sheets("Wochenplanung").Range("H1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    DatVw.Sheets("VSG Planung").Range("CJ6:CJ" & lngRow).Copy
    Dakt.Sheets("Wochenplanung").Range("I1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    DatVw.Sheets("VSG Planung").Range("CP6:CP" & lngRow).Copy
    Dakt.Sheets("Wochenplanung").Range("J1").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

    '----- alle Formeln berechnen -----
    Application.Calculate


    '---- alle Planungswerte ab "Planung Folgewoche"+1 als Festwerte einfügen -----
    lngRow = Dakt.Worksheets("VSG Planung").Cells(Rows.Count, 6).End(xlUp).Row
    With Dakt.Worksheets("VSG Planung")
        .Range("AN6:AN" & lngRow).Copy
        .Range("AN6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("AT6:AT" & lngRow).Copy
        .Range("AT6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("AZ6:AZ" & lngRow).Copy
        .Range("AZ6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("BF6:BF" & lngRow).Copy
        .Range("BF6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("BL6:BL" & lngRow).Copy
        .Range("BL6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("BR6:BR" & lngRow).Copy
        .Range("BR6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("BX6:BX" & lngRow).Copy
        .Range("BX6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("CD6:CD" & lngRow).Copy
        .Range("CD6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("CP6:CP" & lngRow).Copy
        .Range("CP6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
    End With


    DatVw.Sheets("Validierungen").Copy After:=Dakt.Sheets(Dakt.Sheets.Count)

    '----- im Hintergrund geöffnete alte Datei schließen, ohne zu speichern -----
        DatVw.Close SaveChanges:=False
    End If
        Set DatVw = Nothing

    '----- alle nur als Wert benötigte Formeln kopieren und als Festwerte einfügen; muss nach Aktualisierung der Abfragen erfolgen,
    '----- da die Werte aus den Abfragen teilweise als Festwerte eingefügt werden.
    With Dakt.Sheets("VSG Planung")
        .Range("B6:B" & lngRow).Copy
        .Range("B6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("D6:E" & lngRow).Copy
        .Range("D6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("G6:S" & lngRow).Copy
        .Range("G6").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        '---- Formate von erster Produktzeile auf alle neu eingefügten Zeilen übertragen -----
        .Rows("6:6").Copy
        .Rows("6:" & lngRow).EntireRow.PasteSpecial Paste:=xlPasteFormats
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


    '----- speichere die aufbereitete Vorlage unter den Ordnerpfad von strFolder unter den Namen "VSG-Planer_KW"+ Wert der Kalenderwoche als .xlsx -----
    Dakt.SaveAs Filename:=strFolder & "VSG-Planer_KW" & kw & ".xlsx", FileFormat:=51
    '----- schließe die Vorlage ohne zu speichern (damit sie als Vorlage erhalten bleibt) -----
    Dakt.Close SaveChanges:=False
    Set Dakt = Nothing


    With Application
        .DisplayAlerts = True
        .ScreenUpdating = True
        .EnableEvents = True
        .Calculation = xlCalculationAutomatic
    End With


End
End Sub
