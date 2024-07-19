#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Bibliothèques standards
import datetime

import tkinter as tk

from pathlib import Path

# PIPy
import sqlalchemy as sqla

# Bibliothèques maison
from polygphys.outils.config import FichierConfig
from polygphys.outils.base_de_donnees import BaseDeDonnées, BaseTableau
from polygphys.outils.base_de_donnees.dtypes import column

from polygphys.outils.interface_graphique import InterfaceHandler
from polygphys.outils.interface_graphique.tableau import Formulaire
from polygphys.outils.interface_graphique.tkinter import tkHandler

class FeuilleDeTempsConfig(FichierConfig):

    def default(self) -> str:
        return (Path(__file__).parent / 'heures.cfg').open().read()

class FeuilleDeTemps(BaseTableau):
    colonnes_standard = (column('index', int, primary_key=True),
                         column('payeur', str),
                         column('date', datetime.datetime),
                         column('description', str),
                         column('demandeur', str),
                         column('heures', float),
                         column('atelier', bool),
                         column('precision_dept', str),
                         column('autres', str))

    def __init__(self, adresse: str, reflect: bool = True):
        nom_table = 'heures'

        metadata = sqla.MetaData()
        db = BaseDeDonnées(adresse, metadata)

        if reflect:
            moteur = db.create_engine()
            metadata.reflect(moteur)
        else:
            sqla.Table(nom_table,
                       metadata,
                       *self.colonnes_standard)

        super().__init__(db, nom_table)

class FormulaireDeTemps(Formulaire):

    def __init__(self, handler: InterfaceHandler, feuille: FeuilleDeTemps):
        super().__init__(handler, feuille.db, feuille.nom_table)


def main():
    import logging
    
    chemin = Path('~/Documents/Polytechnique/Heures').expanduser()
    logging.info(f'{chemin=}')
    config = FeuilleDeTempsConfig(chemin / 'heures.cfg')
    logging.info(f'{config=}')

    adresse = config.get('bd', 'adresse')
    logging.info(f'{adresse=}')

    feuille_de_temps = FeuilleDeTemps(adresse)
    logging.info('Feuille de temps configurée.')

    racine = tk.Tk()
    handler = tkHandler(racine)
    formulaire = FormulaireDeTemps(handler, feuille_de_temps)
    formulaire.grid(0, 0)
    logging.info('Interface configurée.')

    racine.mainloop()

if __name__ == '__main__':
    main()
