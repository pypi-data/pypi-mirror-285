#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-
"""
Assistant d'importation de fichiers svg et Excel pour générer du code G.

Created on Wed Oct 13 09:46:37 2021

@author: ejetzer
"""

from datetime import date
from pathlib import Path
from tkinter import Tk, Frame, filedialog, Button

import tkinter as tk

import matplotlib
from matplotlib import pyplot

import script_xlsx
import script_svg


def conv(x):
    if isinstance(x, str):
        x = x.replace(',', '.')

    return float(x)


class Assistant(Frame):

    def ouvrir(self):
        self.bouton.config(fg='red', text='Sélection de fichier...')
        fichier_table = filedialog.askopenfilename(initialdir='.',
                                                   title='Sélectionnez le fichier *.xlsx ou *.svg contenant les positions des points.',
                                                   filetypes=(('Excel récent', '*.xlsx'),
                                                              ('Excel ancien',
                                                               '*.xls'),
                                                              ('Dessin SVG', '*.svg')))
        self.fichier_source = Path(fichier_table)
        self.fichier_programme = self.fichier_source.with_suffix(
            f'.{date.today()}.iso')
        self.fichier_graphique = self.fichier_source.with_suffix(
            f'.{date.today()}.svg')

        self.bouton.config(fg='red', text='Ouverture de fichier...')

        if self.fichier_source.suffix in ('.xlsx', '.xls'):
            source = script_xlsx.extraire_trous(
                self.fichier_source, paramètres=self.paramètres)
            programme = script_xlsx.extraire_gcode(
                *source, paramètres=self.paramètres)
        elif self.fichier_source.suffix == '.svg':
            source = script_svg.extraire_chemins(
                self.fichier_source, paramètres=self.paramètres)
            programme = script_svg.extraire_gcode(
                source, paramètres=self.paramètres)

        self.bouton.config(fg='red', text='Écriture de fichier...')
        with self.fichier_programme.open('w') as f:
            print(programme, file=f)

        self.bouton.config(fg='red', text='Dessin...')

        matplotlib.style.use('seaborn')
        pyplot.gca().set_aspect('equal')

        if self.fichier_source.suffix in ('.xlsx', '.xls'):
            script_xlsx.extraire_graphique(*source[:2])
        elif self.fichier_source.suffix == '.svg':
            script_svg.extraire_graphique(source)

        pyplot.savefig(self.fichier_graphique)
        pyplot.show()

        self.bouton.config(fg='green', text='Lancer')

    @property
    def paramètres(self):
        return {texte: variable.get() for texte, variable in self.variables.items() if variable.get() != ''}

    def options_g(self):
        self.étiquettes, self.variables, self.entrées = {}, {}, {}

        for texte in ('Profondeur du brut (mm)', 'Profondeur d\'usinage (mm)', 'Hauteur de déplacement rapide (mm)', 'Vitesse de rotation (rpm)', 'Avance (mm/min)', 'Résolution (mm)'):
            self.étiquettes[texte] = tk.Label(self, text=texte)
            self.variables[texte] = tk.StringVar(self)
            self.entrées[texte] = tk.Entry(
                self, textvariable=self.variables[texte])

    def grid(self, *args, **kargs):
        self.options_g()
        for i, texte in enumerate(self.étiquettes):
            self.étiquettes[texte].grid(column=0, row=i)
            self.entrées[texte].grid(column=1, row=i)

        self.bouton = Button(self, text='Lancer', fg='green',
                             command=self.ouvrir)
        self.bouton.grid(column=0, columnspan=2, row=i+1)

        super().grid(*args, **kargs)


if __name__ == '__main__':
    racine = Tk()
    # racine.geometry('400x100')
    racine.title('Assistant Charly Robot')
    assistant = Assistant(racine)
    assistant.grid(column=0, row=0)
    racine.mainloop()
