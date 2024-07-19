# -*- coding: utf-8 -*-

class GProgramme(list):

    def __str__(self):
        return '\n'.join(self)


def initialiser(x_0: float = 0,
                y_0: float = 0,
                z_0: float = 0,
                vitesse_de_rotation: float = 10000,
                avance: float = 800):
    programme = GProgramme()
    programme.append('G71')  # Unités métriques (mmm)
    programme.append('T1')  # Outils 1 (seul outil permis sur une CHarly Robot)
    programme.append(f'S{vitesse_de_rotation}')  # tr/min
    programme.append(f'F{avance}')  # mm/min
    programme.append(f'G90')  # Coordonnées absolues

    programme.append(f'G0 X{x_0:.4f} Y{y_0:.4f} Z{z_0:.4f}')

    return programme


def déplacer(xs: list[float],
             ys: list[float],
             zs: list[float]):
    programme = [f'G0 X{x:.4f} Y{y:.4f} Z{z:.4f}' for x,
                 y, z in zip(xs, ys, zs)]
    return GProgramme(programme)


def perçage(x: float,  # Position en x (mm)
            y: float,  # Position en y (mm)
            z: float,  # Hauteur de déplacement (mm)
            dz: float):  # Profondeur d'usinage
    programme = GProgramme()
    programme.append(f'G0 X{x:.4f} Y{y:.4f} Z{z:.4f}')
    programme.append(f'G0 X{x:.4f} Y{y:.4f} Z{z-dz:.4f}')
    programme.append(f'G0 X{x:.4f} Y{y:.4f} Z{z:.4f}')

    return programme


def fraisage(xs: list[float],  # Positions en x (mm)
             ys: list[float],  # Positions en y (mm)
             zs: list[float],  # Hauteurs d'usinage (mm)
             dz: float = 1.0):  # Décalage de travail (mm)
    return déplacer(xs[:1], ys[:1], [zs[0]+dz]) +\
        déplacer(xs, ys, zs) +\
        déplacer(xs[-1:], ys[-1:], [zs[-1]+dz])


def fin():
    return GProgramme(['M5',  # Arrêt de la broche
                       'M2'])  # Fin de programme
