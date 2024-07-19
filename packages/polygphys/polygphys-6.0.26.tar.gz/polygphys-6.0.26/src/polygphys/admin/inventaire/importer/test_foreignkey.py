# -*- coding: utf-8 -*-
"""Créé le Tue Jul  5 11:31:38 2022 par emilejetzer."""

import sqlalchemy as sqla
import pandas as pd
import numpy as np

from polygphys.outils.base_de_donnees import BaseTableau

nom, mdp = tuple(map(str.strip, open('nom.txt').read().strip().split('\n')))
adresse = 'mysql+pymysql://{nom}:{mdp}@132.207.44.77:3306/inventaire2022'
adresse = adresse.format(nom=nom, mdp=mdp)

table = BaseTableau(adresse, 'equipement', 'idequipement')
db = table.db

# equipement = db.table('equipement')
# compagnies = db.table('compagnies')
# references = db.table('references')

# # Version 1: .join
# with table.begin() as connexion:
#     énoncé = sqla.select(equipement, compagnies, references)\
#                  .join(compagnies,
#                        compagnies.c.idcompagnies == equipement.c.fournisseur)\
#                  .join(references,
#                        references.c.itemID == equipement.c.reference)
#     résultat = pd.read_sql(énoncé, connexion)

# print(résultat.head())

# test = résultat.loc[:, ['fournisseur', 'idcompagnies']]
# print(test)

# Version 2: via pandas?
equipement = table
compagnies = BaseTableau(db, 'compagnies', 'idcompagnies')
references = BaseTableau(db, 'references', 'itemID')


# Colonne pour les fournisseurs
table_de_valeurs = compagnies
colonne_de_valeurs = 'nom'

table_de_références = equipement
colonne_de_références = 'fournisseur'


def index_à_valeurs(tableau_val, col_val, tableau_réf, col_réf):
    vals = tableau_val.loc([col_val])[:, col_val]
    réfs = tableau_réf.loc([col_réf])[:, col_réf]

    vals = {idx: (vals.loc[ref] if (not np.isnan(ref) and
                                    ref is not None)
                  else None)
            for idx, ref in réfs.items()}
    vals = pd.Series(vals).sort_index()

    return vals


print(index_à_valeurs(table_de_valeurs, colonne_de_valeurs,
      table_de_références, colonne_de_références))

# for idx, (ref,) in df.iterrows():
#     if not np.isnan(ref) and ref is not None:
#         df.loc[idx, colonne_de_valeurs] = valeurs.loc[ref]

# df = df.sort_index()\
# .loc[:, colonne_de_valeurs]

# print(df)

# # Colonne pour les références
# cond_references = equipement.table.c.reference == references.table.c.itemID
# references = references.select(where=[cond_references])

# df = equipement.loc(['reference'])[:, :]
# df.loc[:, 'idequipement'] = df.index

# cond = df.loc[~df.reference.isna(), 'reference']
# references = references.loc[cond, ['lien']]

# df = df.set_index('reference')\
#        .join(references)\
#        .set_index('idequipement')\
#        .loc[:, 'lien']

# # df.to_excel('res.xlsx')
# print(df)
