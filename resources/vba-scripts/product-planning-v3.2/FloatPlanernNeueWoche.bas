Attribute VB_Name = "FloatPlanernNeueWoche"
Option Explicit

Sub FloatPlaner_NeueWoche()

'
' Float-Planer für eine neue Woche inkl. aller Artikel anhand von Vorlage aufbauen
'


' ----- Variablen definieren -----
    Dim fname As Variant
    Dim Dakt As Workbook, WB As Workbook, MSTRdata As Workbook
    Dim strFolder As String, DaktPfad As String, MSTRdataPfad As String
    Dim lngRow As Long, i As Long
    Dim wks As Worksheet
    Dim qt As QueryTable
    Dim lo As ListObject
    Dim kw As Byte '---> ausreichend, da KW max. zwischen 1 bis 53 liegen kann
    Dim tblRow As ListObject
    Dim SGID As String, Adress As String

    With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
    End With

Adress = InputBox("Bitte geben Sie den Onedrive Pfad ein" & Chr(13) & Chr(13) & Chr(13) & "als Beispiel könnte es so aussehen" & Chr(13) & Chr(13) & "C:\Users\  SGID \Saint-Gobain\GI Data - All\", "One Drive Pfad")



' ---- Setze Variable "Dakt" gleich der aktuell geöffneten Mappe (soeben heruntergeladene Mappe des BO-Berichts)  -----
    Set WB = ThisWorkbook

    strFolder = WB.Sheets("Laufwerkspfade").Range("F14").Value

   ' C:\Users\R6356327\Desktop\Float-Planer_KW28 AF_mit Formeln (Repariert).xlsm

'----- Datei öffnen // nur Excelmappen im Explorer anzeigen -----
    DaktPfad = WB.Sheets("Laufwerkspfade").Range("F12").Value
    Set Dakt = Workbooks.Open(DaktPfad)

    Application.Calculate
    Dakt.Sheets("Start").Range("C16") = Adress
    kw = Dakt.Sheets("Float Planung").Range("Z5").Value

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
        .Range("$A$1:$AU$" & lngRow).AutoFilter Field:=18, Criteria1:="NONE", Operator:=xlAnd
        .Range("$A$1:$AU$" & lngRow).AutoFilter Field:=21, Criteria1:=Array("<>22", "<>27", "<>28", "<>30", "<>49", "<>53", "<>58", "<>61"), Operator:=xlAnd
        .Range("$A$1:$AU$" & lngRow).AutoFilter Field:=31, Criteria1:="<>1001", Operator:=xlAnd
    '----- Kopiere alle sichtbaren(!) Daten in Spalte B und füge sie in den Floatplaner ab Zelle E7 ein -----
        .Range("C2:C" & lngRow).SpecialCells(xlCellTypeVisible).Copy
    End With
    Dakt.Sheets("Float Planung").Range("E7").PasteSpecial Paste:=xlPasteValuesAndNumberFormats

    '----- Zähle alle befüllten Zeilen in "Float Planung", Spalte 5 (E) und wandle die als Text gespeicherten Zahlen in Zahlen um -----
    lngRow = Dakt.Worksheets("Float Planung").Cells(Rows.Count, 5).End(xlUp).Row
    With Dakt.Sheets("Float Planung").Range("E7:E" & lngRow)
    .NumberFormat = "General"
    .Value = .Value
    End With


    MSTRdata.Close SaveChanges:=False
    Set MSTRdata = Nothing


    '----- Kopiere die Formel von A7 bis D&lngRow (letzte gezählte Zeile), sowie von F7 bis CN&lngRow -----
    With Dakt.Sheets("Float Planung")
        .Range("A7:D7").Copy
        .Range("A7:D" & lngRow).PasteSpecial xlPasteFormulas

        .Range("F7:CN7").Copy
        .Range("F7:CN" & lngRow).PasteSpecial xlPasteFormulas

         '---- Formate von erster Produktzeile auf alle neu eingefügten Zeilen übertragen -----
        .Rows("7:7").Copy
        .Rows("7:" & lngRow).EntireRow.PasteSpecial Paste:=xlPasteFormats
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
    With Dakt.Sheets("Float Planung")
        .Range("B7:D" & lngRow).Copy
        .Range("B7").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        .Range("F7:R" & lngRow).Copy
        .Range("F7").PasteSpecial Paste:=xlPasteValuesAndNumberFormats
        '---- Formate von erster Produktzeile auf alle neu eingefügten Zeilen übertragen -----
        .Rows("7:7").Copy
        .Rows("7:" & lngRow).EntireRow.PasteSpecial Paste:=xlPasteFormats
    End With

    Application.CutCopyMode = False

    '----- nicht mehr benötigte Abfragen + Verbindungen "Consumption" und "Sales" löschen -----
    With Dakt
        .Queries("Consumption").Delete
        .Connections("Abfrage - Consumption").Delete
        .Queries("Sales").Delete
        .Connections("Abfrage - Sales").Delete
        '----- Conso + Sales löschen, da Verbräuche bereits als Festwerte übernommen -----
        .Worksheets("Consumption ü. 6 Monate").Delete
        .Worksheets("Sales ü. 6 Monate").Delete
    End With

    '----- Anzahl Zeilen der Tabellen in "MTS Production" und "MAG Verbrauch" zählen, um ISO-KW-Formel zu kopieren -----
  '  Set tblRow = Dakt.Worksheets("MTS Verbrauch").ListObjects("Prod_Planning").ListRows.Count
  '      .Range("A2").Copy


   ' Dakt.Worksheets("MAG Verbrauch").ListObjects("Cons_Planning").ListRows.Count


    '----- speichere die aufbereitete Vorlage unter den Ordnerpfad von strFolder unter den Namen "Float-Planer_KW"+ Wert der Kalenderwoche als .xlsx -----
    Dakt.SaveAs Filename:=strFolder & "Float-Planer_KW" & kw & ".xlsx", FileFormat:=51
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
