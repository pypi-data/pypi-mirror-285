#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-

import schedule
import time
import traceback

from datetime import datetime
from pathlib import Path

import sqlite3
import sqlalchemy

from polygphys.admin.inventaire.zotero.zotero import MigrationConfig, ZoteroItems

def main():
        import logging
        journal = Path('~/zotero_a_inventaire.log').expanduser()
        chemin = Path('~/zotero_a_inventaire.cfg').expanduser()
        config = MigrationConfig(chemin)

        zotero = config.get('zotero', 'adresse')
        inventaire2022 = config.get('inventaire2022', 'adresse')
        nom = config.get('inventaire2022', 'nom')
        mdp = config.get('inventaire2022', 'mdp')

        inventaire2022 = inventaire2022.format(nom=nom, mdp=mdp)


        def enveloppe():
            logging.info(f'Mise à jour {datetime.now()}...')
            try:
                bd = ZoteroItems(zotero, inventaire2022)
                bd.charger()
            except (Exception, sqlite3.OperationalError, sqlalchemy.exc.OperationalError):
                with journal.open() as f:
                    traceback.print_exc(file=f)


        schedule.every(10).minutes.do(enveloppe)
        logging.info('On commence...')
        while True:
            schedule.run_pending()
            time.sleep(10)

if __name__ == '__main__':
    main()
