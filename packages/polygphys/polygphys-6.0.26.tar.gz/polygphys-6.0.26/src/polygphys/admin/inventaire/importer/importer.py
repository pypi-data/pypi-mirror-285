# -*- coding: utf-8 -*-
"""Créé le Tue Jul  5 10:52:58 2022 par emilejetzer."""

from pathlib import Path

import numpy as np
import pandas as pd

from pandas import ExcelWriter

from polygphys.outils.config import FichierConfig
from polygphys.outils.base_de_donnees import BaseTableau, BaseDeDonnées


class ImporterConfig(FichierConfig):

    def default(self):
        return (Path(__file__).parent / 'default.cfg').open().read()


class VueInventaire:
    noms_tables = (('bris', 'idbris'),
                   ('commande', 'idcommande'),
                   ('commandes_ouvertes', 'idcommande_ouverte'),
                   ('compagnies', 'idcompagnies'),
                   ('emprunt', 'idemprunt'),
                   ('equipement', 'idequipement'),
                   ('etageres', 'idetageres'),
                   ('locaux', 'idlocaux'),
                   ('personnes', 'idpersonnes'),
                   ('rangement', 'idrangement'),
                   ('references', 'itemID'),
                   ('responsables', 'idresponsables'))

    def __init__(self, adresse):
        self.tableaux, self.db = {}, None

        for nom, ind in self.noms_tables:
            if self.db is None:
                t = BaseTableau(adresse, nom, ind)
                self.db = t.db
            else:
                t = BaseTableau(self.db, nom, ind)

            self.tableaux[nom] = t

    def charger(self, fichier: Path):
        dfs = pd.read_excel(fichier)
        for nom_table, table_df in dfs.items():
            table_df = table_df.replace({np.nan: None})
            self.tableaux[nom_table].màj(table_df)

    def télécharger(self, fichier: Path):
        with ExcelWriter(fichier) as f:
            for nom, table in self.tableaux.items():
                table.to_excel(f, table.nom_table)

    def index_à_valeurs(self,
                        nom_réfs: str,
                        col_réfs: str,
                        nom_vals: str,
                        col_vals: str) -> pd.Series:
        vals = self.tableaux[nom_vals].loc([col_vals])[:, col_vals]
        réfs = self.tableaux[nom_réfs].loc([col_réfs])[:, col_réfs]

        def val(réf: int) -> str:
            if not np.isnan(réf) and réf is not None:
                return vals.loc[réf]
            else:
                return None

        vals = {idx: val(réf) for idx, réf in réfs.items()}
        vals = pd.Series(vals).sort_index()

        return vals

    def vue(self) -> pd.DataFrame:
        df = self.tableaux['equipement'].select(['nom'])
        df.loc[:, 'nom_fournisseur'] = self.index_à_valeurs('equipement',
                                                            'fournisseur',
                                                            'compagnies',
                                                            'nom')
        return df

    def valeur_étrangère(self, index: int, clé: str) -> pd.Series:
        réf = self.tableaux['equipement'].loc([clé])[index, clé]

        if réf is None:
            return None

        if clé == 'fournisseur' or clé == 'fabricant':
            tableau = 'compagnies'
        elif clé == 'reference':
            tableau = 'references'
        else:
            raise KeyError(
                f'self.tableaux["equipement"] n\' a pas de clé étrangère pour la colonne {clé!r}.')

        rangée = self.tableaux[tableau].loc()[réf, :]

        return rangée

    def référence_externe(self, index: int, tableau: str) -> pd.Series:
        if tableau == 'responsable':
            cond = self.tableaux['responsables'].table.c['item'] == index

        clé = self.tableaux['responsables']\
            .loc(['responsable'], where=[cond])[:, 'responsable']\
            .iloc[0]
        rangée = self.tableaux['personnes'].loc()[clé, :]
        return rangée


class Vue(BaseTableau):

    def __init__(self,
                 db: BaseDeDonnées,
                 table: str,
                 index_col: str = 'index',
                 valeurs_étrangères: dict[str, tuple[str]] = {},
                 références_externes: dict[str, tuple[tuple[str]]] = tuple()):
        super().__init__(db, table, index_col)

        self.valeurs_étrangères = {col: BaseTableau(self.db,
                                                    table,
                                                    index_col)
                                   for col, (table, index_col)
                                   in valeurs_étrangères.items()}
        self.références_externes = None

    def colonne_étrangère(self,
                          réfs: pd.Series,
                          vals: pd.Series) -> pd.Series:

        def val(réf: int) -> str:
            if not isinstance(réf, (np.number, int, float)):
                return réf
            elif not np.isnan(réf) and réf is not None:
                return vals.loc[réf]
            else:
                return None

        vals = {idx: val(réf) for idx, réf in réfs.items()}
        vals = pd.Series(vals).sort_index()

        return vals

    def colonnes_étrangères(self) -> pd.DataFrame:
        df = self.df

        for col, tab in self.valeurs_étrangères.items():
            réfs = self.loc([col])[:, col]

            col2s = tab.columns
            for col2 in col2s:
                vals = tab.loc([col2])[:, col2]
                df.loc[:, f'{col}_{col2}'] = self.colonne_étrangère(
                    réfs, vals)

        return df

    def valeur_étrangère(self, index: int, clé: str) -> pd.Series:
        réf = self.loc([clé])[index, clé]

        if réf is None:
            return None

        rangée = self.valeurs_étrangères[clé].loc()[réf, :]
        return rangée

    def référence_externe(self, index: int, col: str) -> pd.Series:
        pass
        # tab_réf, tab_val = self.références_externes[col]
        # cond = tab_réf.table.c[tab_réf.index_col] == index
        # clé = tab_réf.loc([col], where=[cond])[:, col]\
        #     .iloc[0]
        # rangée = tab_val.loc()[clé, :]
        # return rangée


class VueInventaire(Vue):

    def __init__(self, db: BaseDeDonnées):
        nom_table = 'equipement'
        index_col = 'idequipement'

        valeurs_étrangères = {'fournisseur': ('compagnies', 'idcompagnies'),
                              'fabricant': ('compagnies', 'idcompagnies'),
                              'reference': ('references', 'itemID')}

        # références_externes = {'responsable': (('responsables', 'idresponsables', 'item', 'responsable'),
        #                                        ('personnes', 'idpersonnes'))}

        super().__init__(db, nom_table, index_col, valeurs_étrangères)


if __name__ == '__main__':
    nom, mdp = tuple(
        map(str.strip, open('nom.txt').read().strip().split('\n')))
    adresse = 'mysql+pymysql://{nom}:{mdp}@132.207.44.77:3306/inventaire2022'
    adresse = adresse.format(nom=nom, mdp=mdp)

    vue = VueInventaire(adresse)
    # vue.vue()

    print(vue.valeur_étrangère(2, 'fournisseur'))
    #print(vue.référence_externe(67, 'responsable'))

    df = vue.colonnes_étrangères()
    df.to_excel('colonnes_étrangères.xlsx')
