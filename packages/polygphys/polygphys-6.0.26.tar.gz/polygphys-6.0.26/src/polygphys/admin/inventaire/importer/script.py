#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-

import sys

from datetime import datetime as dt

import numpy as np

from pandas import ExcelWriter, DataFrame, read_excel

from polygphys.outils.base_de_donnees import BaseTableau


def main():
    nom = open('nom.txt').read().split('\n')[0].strip()
    mdp = open('nom.txt').read().split('\n')[1].strip()
    adresse = f'mysql+pymysql://{nom}:{mdp}@132.207.44.77:3306/inventaire2022'

    # On s'attends à:
    # $ python script.py "chemin_du_fichier"
    # argv == ['script.py', 'chemin_du_fichier']
    if len(sys.argv) != 2:
        # raise Exception('Soit trop, soit pas assez d\'arguments.')
        chemin = 'test.xlsx'
    else:
        chemin = sys.argv[-1]

    tables = [('compagnies', 'idcompagnies', 'A:D'),
              ('equipement', 'idequipement', 'A:F'),
              ('etageres', 'idetageres', 'A:C'),
              ('rangement', 'idrangement', 'A:C')]

    nom_fichier = f"inventaire {str(dt.now()).replace(':', '_')}.xlsx"
    with ExcelWriter(nom_fichier) as sortie_excel:
        for table, nom_index, usecols in tables:
            print(table)
            tableau = BaseTableau(adresse, table, nom_index)

            # Charger vers la base de données
            # fichier_excel = read_excel(chemin,
            #                            sheet_name=table,
            #                            index_col=nom_index,
            #                            usecols=usecols)
            # fichier_excel = fichier_excel.replace({np.nan: None})
            # tableau.màj(fichier_excel)

            # Télécharger les données les plus récentes
            tableau.to_excel(sortie_excel, table)


if __name__ == '__main__':
    main()
