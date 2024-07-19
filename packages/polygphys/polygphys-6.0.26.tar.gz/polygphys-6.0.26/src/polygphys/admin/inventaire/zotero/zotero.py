#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pathlib

from sqlalchemy import MetaData

from polygphys.outils.config import FichierConfig
from polygphys.outils.base_de_donnees import BaseDeDonnées, BaseTableau


class MigrationConfig(FichierConfig):

    def default(self):
        return (pathlib.Path(__file__).parent / 'default.cfg').open().read()


class ZoteroItems:

    def __init__(self, zotero: str, sortie: str = ''):
        self.items = BaseTableau(zotero, 'items', 'itemID')
        self.itemData = BaseTableau(zotero, 'itemData', 'itemID')
        self.itemDataValues = BaseTableau(
            zotero, 'itemDataValues', 'valueID')
        self.fieldsCombined = BaseTableau(
            zotero, 'fieldsCombined', 'fieldID')
        self.groups = BaseTableau(zotero, 'groups', 'groupID')

        self.sortie = BaseTableau(sortie, 'references', 'itemID')

    def charger(self):
        items = self.items.select()\
                    .loc[:, ['libraryID', 'key']]
        groupes = self.groups.select()
        groupes = groupes.reset_index()
        groupes = groupes.set_index(groupes.libraryID)
        group_id = groupes.loc[:, 'groupID']

        cond = items.libraryID == 1
        items.loc[cond, 'groupID'] = 0
        library_id = items.loc[~cond, 'libraryID']

        group_id = group_id.loc[library_id]
        group_id = group_id.reset_index().groupID
        group_id.index = library_id.index
        items.loc[group_id.index, 'groupID'] = group_id
        items = items.astype({'groupID': int})

        items.loc[:, 'titre'] = ''
        field_name_cond = self.fieldsCombined.db.table(
            'fieldsCombined').columns.fieldName == 'title'
        field_id = self.fieldsCombined.select(
            where=[field_name_cond]).index.to_list()[0]

        titre_cond = self.itemData.db.table(
            'itemData').columns.fieldID == field_id
        item_data = self.itemData.select(where=[titre_cond])

        for item_index, (i, titre_index) in item_data.iterrows():
            cond = self.itemDataValues.db.table(
                'itemDataValues').columns.valueID == titre_index
            titre = self.itemDataValues.select(where=[cond]).value.to_list()[0]
            items.loc[item_index, 'titre'] = titre

        def func(rangée):
            # zotero://select/library/items/76RYAHVX
            # zotero://select/groups/2511151/items/4E36ETLG
            if rangée.groupID == 0:
                return f'zotero://select/library/items/{rangée.key}'
            else:
                return f'zotero://select/groups/{rangée.groupID}/items/{rangée.key}'

        items.loc[:, 'lien'] = items.apply(func, axis=1)
        items = items.loc[:, ['key', 'groupID', 'titre', 'lien']]

        self.sortie.màj(items)

        return items
