#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dessiner un chemin de profondeur constante."""

from datetime import date
from pathlib import Path

from xml.etree import ElementTree as ET

import svg.path

import numpy as np

import matplotlib
from matplotlib import pyplot

import gcode

# Régler l'origine
# On assume que l'origine est au coin supérieur gauche, contre la plaque
# sacrificielle.
# î
# .->---------------.
# |                 |
# |                 |
# .-----------------.

namespace = {'svg': 'http://www.w3.org/2000/svg'}  # Pour le SVG


def extraire_chemins(fichier_svg: Path,  # Entrée
                     résolution: float = 0.1,  # mm
                     paramètres: dict = None):
    if paramètres is not None:
        résolution = float(paramètres.get('Résolution (mm)', résolution))

    # Aller chercher les chemins dans le fichier SVG
    document_svg = ET.parse(fichier_svg)
    chemins_svg = [svg.path.parse_path(c.attrib['d'])
                   for c in document_svg.findall('.//svg:path', namespace)]

    chemins = []
    for chemin in chemins_svg:
        longueur = int(chemin.length() / résolution)

        xs, ys = [], []
        for i in range(longueur + 1):
            index = i / longueur
            point = chemin.point(index)
            x, y = point.real, point.imag
            xs.append(x/10)
            ys.append(y/10)
        chemins.append([xs, ys])

    return chemins


def extraire_gcode(chemins: list[list[list[float]]],  # Entrée
                   # Paramètres de programme
                   z_0: float = 10,  # mm, niveau de déplacement rapide
                   vitesse_de_rotation: float = 10000,  # tr/min
                   avance: float = 800,  # mm/min
                   paramètres: dict = None):
    if paramètres is not None:
        prof_usinage = float(paramètres.get('Profondeur d\'usinage (mm)', 0))
        hauteur_rapide = float(paramètres.get(
            'Hauteur de déplacement rapide (mm)', 0))
        prof_brut = float(paramètres.get('Profondeur du brut (mm)', 0))
        z_0 = hauteur_rapide + prof_brut
        niveau_usinage = prof_brut - prof_usinage
        vitesse_de_rotation = float(paramètres.get(
            'Vitesse de rotation (rpm)', vitesse_de_rotation))
        avance = float(paramètres.get('Avance (mm/min)', avance))

    # Début du programme
    # Réglages de base
    programme = gcode.initialiser(
        chemins[0][0][0], chemins[0][0][0], z_0, vitesse_de_rotation, avance)

    for xs, ys in chemins:
        programme += gcode.fraisage(xs[:1] + xs,
                                    ys[:1] + ys,
                                    [z_0] + [niveau_usinage for i in xs] + [z_0])

    # Fin & arrêt du programme
    programme += gcode.fin()

    return str(programme)


def extraire_graphique(chemins: list[list[list[float]]]):
    for i, (xs, ys) in enumerate(chemins):
        pyplot.plot(xs, ys, '-')

        if i < (len(chemins) - 1):
            dernier = xs[-1], ys[-1]
            suivant = chemins[i + 1]
            premier = suivant[0][-1], suivant[1][-1]
            pyplot.plot([dernier[0], premier[0]],
                        [dernier[1], premier[1]],
                        '--', color='gray')


def main():
    fichier = input('fichier: ')
    if not fichier:
        fichier = 'eg/dessin.svg'

    chemins = extraire_chemins(fichier)
    gcode = extraire_gcode(chemins)

    matplotlib.style.use('seaborn')
    pyplot.gca().set_aspect('equal')

    extraire_graphique(chemins)

    with open(Path(__file__).parent / 'eg' / 'parcours {date.today()}.iso', 'w') as f:
        f.write(gcode)

    pyplot.savefig(Path(__file__).parent / 'eg' /
                   'parcours {date.today()}.svg')
    pyplot.show()


if __name__ == '__main__':
    main()
