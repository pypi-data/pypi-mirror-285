#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour faire des trous à des endroits particuliers sur une plaque.

Premier jet, ligne de commande.

Created on Wed Oct 13 09:46:37 2021

@author: ejetzer
"""

from datetime import date

from matplotlib import pyplot

# Régler l'origine
# On assume que l'origine est au coin supérieur gauche
# î
# .->---------------.
# |                 |
# |                 |
# .-----------------.

fichier = f'programme {date.today()}.iso'

with open(fichier, 'w') as f:
    print('G71', file=f)  # mm
    print('T1', file=f)  # Outil 1
    print('S10000', file=f)  # tr/min
    print('F800', file=f)  # mm/min

# Entrer les points
modèle = """
G0 X{} Y{} Z1.
G1 Z-1.
G4 F1
G1 Z1."""

xs, ys = [], []
with open(fichier, 'a') as f:
    while (xy := input('x,y = ')):
        x, y = [float(z) for z in xy.split(',')]
        xs.append(x)
        ys.append(y)

        print(modèle.format(x, y), file=f)

pyplot.plot(xs, ys, '+')
pyplot.show()
