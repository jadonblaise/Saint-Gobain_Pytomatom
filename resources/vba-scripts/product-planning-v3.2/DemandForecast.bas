Attribute VB_Name = "DemandForecast"
Option Explicit
Sub DemandForecast()

Dim WB As Workbook, MS As Workbook, NB As Workbook, SD As Workbook
Dim fname As Variant
Dim lngDF As Long, lngMS As Long, lngSD As Long, Volumen As Long
Dim LGKWB As LongLong, LGKMS As LongLong
Dim Split As Single
Dim i As Integer, j As Integer, k As Integer, Counter As Integer
Dim DDate As String, Customer As String, Ginger As String


'----- Anzeigen, Berechnungen und Events ausschalten, um Berechnung / Makro zu beschleunigen -----
With Application
        .DisplayAlerts = False
        .ScreenUpdating = False
        .EnableEvents = False
        .Calculation = xlCalculationManual
End With

'Dieses Workbook wegen Namenk�rzelung als WB setzen
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Bitte die Forecast Datei �ffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgew�hlt.", vbExclamation, "ERROR"
    Exit Sub
    End If
Set WB = Workbooks.Open(Filename:=fname, UpdateLinks:=0)

'�ffnen der Microstrategydatei un setze es als MS
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Bitte die Microstrategy Datei �ffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgew�hlt.", vbExclamation, "ERROR"
    Exit Sub
    End If
Set MS = Workbooks.Open(Filename:=fname, UpdateLinks:=0)

'�ffnen der Microstrategydatei un setze es als MS
fname = Application.GetOpenFilename("Excelmappen (*.xls;*.xlsm;*.xlsx),*.xls;*.xlsm;*.xlsx", Title:="Bitte die Shipping Plant Split Datei �ffnen")
    If fname = False Then
        MsgBox "Keine Datei ausgew�hlt.", vbExclamation, "ERROR"
    Exit Sub
    End If
Set SD = Workbooks.Open(Filename:=fname, UpdateLinks:=0)

'Neue Datei wird erstellt f�r endg�ltige Ergebnisse
Set NB = Workbooks.Add
 With NB
 .Title = "Demand Forecast"
 .Subject = "Demand Forecast"
 End With

'�berschriften definieren f�r die Ausgabe Datei
With NB.Worksheets(1)
    .Range("A1") = "Customer"
    .Range("B1") = "GingerCode"
    .Range("C1") = "Date"
    .Range("D1") = "Volumen"
    .Range("E1") = "Split"
    .Range("F1") = "Plant"
End With

'----- Falls in der Microstrategy Datei im Quell-Sheet Filter gesetzt sind, l�sche diese, um alle Kommentare kopieren zu k�nnen -----
If WB.Worksheets(1).FilterMode Then
  Sheets(1).ShowAllData
End If

'----- Falls in der Microstrategy Datei im Quell-Sheet Filter gesetzt sind, l�sche diese, um alle Kommentare kopieren zu k�nnen -----
'If MS.Worksheets(1).FilterMode Then
'  Sheets(1).ShowAllData
'End If

'Anzahl der Zeilen der Dachforecast bestimmen f�r die Schleife
lngDF = WB.Worksheets(1).Cells(Rows.Count, 3).End(xlUp).Row


'Anzahl der Zeilen der MS bestimmen f�r die Schleife
lngMS = MS.Worksheets(1).Cells(Rows.Count, 3).End(xlUp).Row

'Anzahl der Zeilen der  bestimmen f�r die Schleife
lngSD = SD.Worksheets(1).Cells(Rows.Count, 3).End(xlUp).Row

Counter = 2

'�u�ere Schleife: Geht die einzelnen Zeilen in der Forecast durch
For i = 2 To lngDF

'Kopieren der Daten aus der Forecast Datei
LGKWB = WB.Worksheets(1).Range("C" & i).Value
DDate = WB.Worksheets(1).Range("D" & i).Value
Customer = WB.Worksheets(1).Range("B" & i).Value
Volumen = WB.Worksheets(1).Range("E" & i).Value

'1. innere Schleife: Geht die einzelnen Zeilen in der MS Datei durch
    For j = 2 To lngMS

    LGKMS = MS.Worksheets(1).Range("C" & j).Value
    'Abfrage LGK Forecast = LGK MS -> Somit werden alle Ginger Codes(und andere Daten) f�r den richtigen Kunden und richtigen LG rauskopiert
        If LGKWB = LGKMS Then
        Ginger = MS.Worksheets(1).Range("D" & j).Value
        Split = MS.Worksheets(1).Range("G" & j).Value

        NB.Worksheets(1).Range("A" & Counter).Value = Customer
        NB.Worksheets(1).Range("B" & Counter).Value = Ginger
        NB.Worksheets(1).Range("C" & Counter).Value = DDate
        NB.Worksheets(1).Range("D" & Counter).Value = Volumen
        NB.Worksheets(1).Range("E" & Counter).Value = Split

        '2. innere Schleife: Um das richtige Werk aus der Plant Split Datei zuweisen zu k�nnen, Vergleich mit dem Gingercode
            For k = 2 To lngSD
                If SD.Worksheets(1).Range("B" & k).Value = Ginger Then
                NB.Worksheets(1).Range("F" & Counter).Value = SD.Worksheets(1).Range("E" & k).Value
                End If
            Next k

        Counter = Counter + 1

        End If
    Next j

Next i
'Speicher der Erzeugten Datei
NB.SaveAs Filename:="Demand Forecast.xlsx", FileFormat:=51

'Schlie�en der anderen Dateien
WB.Close SaveChanges:=False
NB.Close SaveChanges:=False
SD.Close SaveChanges:=False
MS.Close SaveChanges:=False

'----- Anzeigen, Berechnungen und Events wieder einschalten -----
With Application
        .DisplayAlerts = True
        .ScreenUpdating = True
        .EnableEvents = True
        .Calculation = xlCalculationAutomatic
End With

End Sub
