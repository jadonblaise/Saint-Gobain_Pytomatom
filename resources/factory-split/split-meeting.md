

# Split-Meeting

Porz:
    QM und Tonnage


Torgau:
    Platte und Pakete

neue Spalte:
    gefüllt mit:
        0 oder 1 -> Paket verfügbar oder nicht verfügbar. Vollständig und
            verfügbar im Lager und für die Auftragsrechnung geeignet.
        wenn

            "Paket.-Typ" 1001 ist ein Coversheet.

            Spalte "Paket.-Typ"
                die rechten 3 Zeichen -> Anzahl der Scheiben die in einem Paket sein sollten
                die erste Zahl bedeutet:
                    {
                        1: 2,8 t Paketierung,
                        2: 11t,
                        3: 12.6t,
                        4: 5.6t,
                        5: englische Paketierung,
                        6: englische Paketierung,
                        7: 2t,
                        8: alles was nicht ins Raster passt oder nicht einem geteilten Bandmaß entspricht
                    }
            exakter Vergleich mit Spalte "Lagernde Menge" ==      # da das Bruchrisiko nicht berücksichtigt wird, nehmen wir auch die matches mit mehr nicht
            dann Prüfung "GBS-Status" is Verfügbar -> 1


            neue Spalte: Gesamtsumme Pro "SAP-Produkt" aggregiert -> Summe an Paketen, die aus dem Lager bereitsgestellt werden kann

.. dann schauen wieviel nach der Ordnung bereitgestellt werden kann
