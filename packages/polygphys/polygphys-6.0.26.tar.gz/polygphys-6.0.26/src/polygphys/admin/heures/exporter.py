#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Bibliothèques standards
import datetime
import time

from pathlib import Path

# Bibliothèques PIPy
import pandas as pd
import getpass
import keyring
import schedule

# Bibliothèques maison
from polygphys.outils.reseau import DisqueRéseau
from polygphys.outils.journal import Repository
from polygphys.outils.base_de_donnees import BaseTableau

from polygphys.admin.heures.heures import FeuilleDeTempsConfig, FeuilleDeTemps


def main():
    chemin = Path('~/Documents/Polytechnique/Heures').expanduser()
    config = FeuilleDeTempsConfig(chemin / 'heures.cfg')

    adresse = config.get('bd', 'adresse')

    feuille_de_temps = FeuilleDeTemps(adresse)

    url = config.get('export', 'disque')
    chemin = Path(config.get('export', 'montage')).expanduser()
    nom = config.get('export', 'nom')

    mdp = keyring.get_password('system', f'exporter_heures_{nom}')
    if mdp is None:
        mdp = getpass.getpass('mdp: ')
        keyring.set_password('system', f'exporter_heures_{nom}', mdp)
    
    with DisqueRéseau(url, chemin, 'J', nom, mdp) as d:
        git = Repository(d.chemin)

        fichier_excel = next(d.chemin.glob(config.get('export', 'fichier')))

        condition = feuille_de_temps.db.table('heures').columns.exporte == False
        nouvelles_entrées = feuille_de_temps.select(where=[condition])

        colonnes = config.getlist('export', 'db')
        à_exporter = nouvelles_entrées.loc[:, colonnes]
        conversions = config['conversion']
        à_exporter = à_exporter.rename(columns=conversions)

        if not à_exporter.empty:
            colonnes = config.getlist('export', 'xlsx')
            ajouts = filter(lambda x: x not in à_exporter.columns, colonnes)
            
            for colonne in ajouts:
                if colonne in config['export'].keys():
                    à_exporter.loc[:, colonne] = config.get('export', colonne)
                else:
                    à_exporter.loc[:, colonne] = None

            à_exporter = à_exporter.loc[:, colonnes]

            vieilles_entrées = pd.read_excel(fichier_excel)
            toutes_entrées = pd.concat((vieilles_entrées, à_exporter),
                                       ignore_index=True)\
                               .sort_values(by=['Date', 'Payeur', 'Demandeur'])\
                               .reset_index(drop=True)
            
            toutes_entrées.to_excel(fichier_excel,
                                    sheet_name=f'feuille de temps {datetime.date.today()}',
                                    index=False)

            nouvelles_entrées.loc[:, 'exporte'] = True
            git.add(str(fichier_excel))
            
            feuille_de_temps.update(nouvelles_entrées)
            git.commit(f'Màj automatisée le {datetime.datetime.now()}')

if __name__ == '__main__':
        schedule.every().day.at('17:00').do(main)

        main()
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print('Fin.')
