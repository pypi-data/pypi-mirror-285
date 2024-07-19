# -*- coding: utf-8 -*-
"""Programme de gestion et suivi d'inventaire."""

# Bibliothèques standards
import getpass
import tkinter as tk

from pathlib import Path

# Bibliothèques PIPy
import keyring

from sqlalchemy import MetaData

# Bibliothèques maison
from polygphys.outils.config import FichierConfig
from polygphys.outils.base_de_donnees import BaseDeDonnées
from polygphys.outils.interface_graphique.tableau import Tableau
from polygphys.outils.interface_graphique.tkinter.onglets import Onglets, OngletBaseDeDonnées

# Modules locaux
import modeles

# Définitions de classes


class InventaireConfig(FichierConfig):
    """Fichier de configuration de programme d'inventaire."""

    def default(self) -> str:
        """
        Retourne le contenu du fichier default.cfg contenu dans le module.

        Returns
        -------
        str
            Contenu de default.cfg.

        """
        return (Path(__file__).parent / 'default.cfg').open().read()


class TableauInventaire(Tableau):
    pass


class OngletInventaire(OngletBaseDeDonnées):

    def __init__(self, master, db, *args, config: FichierConfig = None, **kargs):
        table = 'inventaire'
        super().__init__(master, db, table, *args, config=config, **kargs)

    def build(self):
        """Construit les widgets."""
        self.canevas = tk.Canvas(self, width='50c', height='15c')
        défiler_horizontalement = tk.Scrollbar(
            self, orient='horizontal', command=self.canevas.xview)
        défiler_verticalement = tk.Scrollbar(
            self, orient='vertical', command=self.canevas.yview)
        self.canevas.configure(xscrollcommand=défiler_horizontalement.set,
                               yscrollcommand=défiler_verticalement.set)

        self.contenant = tk.Frame(self.canevas)

        self.contenant.bind('<Configure>', lambda x: self.canevas.configure(
            scrollregion=self.canevas.bbox('all')))

        self.tableau = Tableau(tkHandler(self.contenant), self.db, self.table)

        màj = tk.Button(self, text='Màj',
                        command=lambda: self.tableau.update_grid())

        importer = tk.Button(self, text='Importer',
                             command=self.importer)

        exporter = tk.Button(self, text='Exporter',
                             command=self.exporter)

        modèle = tk.Button(self, text='Modèle',
                           command=self.exporter_modèle)

        self.défiler = [défiler_horizontalement, défiler_verticalement]

        self.boutons = [màj, importer, exporter, modèle]


# Obtenir le fichier de configuration
# Un bon endroit où le placer est le répertoire racine de l'utilisateur.
fichier_config = Path('~/inventaire.cfg').expanduser()
config = InventaireConfig(fichier_config)

# Le mot de passe ne devrait pas être gardé dans le fichier de configuration.
# On utilise le module keyring pour le garder dans le trousseau.
# Le mot de passe reste accessible à tous les programmes Python,
# donc il faut faire attention à ce qu'on exécute comme code sur
# l'ordinateur.
nom = config.get('bd', 'nom')
utilisateur = config.get('bd', 'utilisateur')
mdp_id = f'polygphys.inventaire.main.bd.{nom}.{utilisateur}'
mdp = keyring.get_password('system', mdp_id)

if mdp is None:
    mdp = getpass.getpass('mdp>')
    keyring.set_password('system', mdp_id, mdp)

# On crée la structure de la base de données
metadata = créer_dbs(MetaData())

# On configure l'adresse de la base de données
adresse = f'mysql+pymysql://{utilisateur}:{mdp}@{nom}'
config.set('bd', 'adresse', adresse.replace('%', '%%'))

# On se connecte et on initialise la base de données
base_de_données = BaseDeDonnées(adresse, metadata)
base_de_données.initialiser()

# Configuration de l'interface graphique
racine = tk.Tk()
titre = config.get('tkinter', 'titre')
racine.title(titre)

# Onglets va créer l'affichage pour les tableaux et formulaires
# définis dans le fichier de configuration.
onglets = Onglets(racine, config, metadata, dialect='mysql')

# Aller!
onglets.grid(sticky='nsew')
racine.mainloop()
