

COLOR =[[0, 0, 255],
        [0, 255, 0],
        [120, 0, 20],
        [120, 0, 225],
        [80, 120, 0],
        [255, 0, 0],
        [150, 255, 0],
        [150, 160, 255],
        [200, 80, 160],
        [250, 80, 0],
        [250, 129, 202],
        [121, 140, 90],
        [74, 41, 221],
        [88, 218, 141],
        [23, 69, 163],
        [170, 56, 33],
        [18, 195, 56],
        [80, 80, 0],
        [0, 255, 80]]

# TODO fait doublon avec OS
# mais permet d'avoir toujours la même couleur sur un os
EDGES = [   (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (3, 1),
            (4, 2),
            (1, 2),
            (5, 6),
            (5, 7),  # bras gauche
            (5, 11),
            (6, 8),  # bras droit
            (6, 12),
            (7, 9),  # avant bras gauche
            (8, 10), # avant bras droit
            (11, 12),
            (11, 13),
            (12, 14),
            (13, 15),
            (14, 16)]

NAMES = {   'nez': 0,
            'oeuil gauche': 1,
            'oeuil droit': 2,
            'oreille gauche': 3,
            'oreille droit': 4,
            'epaule gauche': 5,
            'epaule droit': 6,
            'coude gauche': 7,
            'coude droit': 8,
            'poignet gauche': 9,
            'poignet droit': 10,
            'hanche gauche': 11,
            'hanche droit': 12,
            'genou gauche': 13,
            'genou droit': 14,
            'cheville gauche': 15,
            'cheville droit': 16}

OS = {   'nez oeuil gauche': (0, 1),
         'nez oeuil droit':  (0, 2),
         'nez oreille gauche': (0, 3),
         'nez oreille droit': (0, 4),
         'oreille gauche oeuil gauche': (3, 1),
         'oreille oeuil droit': (4, 2),
         'oeuil oeuil droit': (1, 2),
         'epaules': (5, 6),
         'bras gauche': (5, 7),
         'epaule hanche gauche': (5, 11),
         'bras droit': (6, 8),
         'epaule hanche droit': (6, 12),
         'avant bras gauche': (7, 9),
         'avant bras droit': (8, 10),
         'hanches': (11, 12),
         'femur gauche': (11, 13),
         'femur droit': (12, 14),
         'tibia gauche': (13, 15),
         'tibia droit': (14, 16)}

ACTIONS = {
            0: {'bras droit':  (170, 190), 'avant bras droit':  (70, 90)},
            1: {'bras gauche': (-10, 10), 'avant bras gauche': (70, 90)},
            2: {'bras droit':  (170, 190), 'avant bras droit':  (170, 190)},
            3: {'bras gauche': (-10, 10), 'avant bras gauche': (-10, 10)},
            4: {'bras droit': (170, 190), 'avant bras droit': (260, 280)},
            5: {'bras gauche': (-10, 10), 'avant bras gauche': (70, 90)},
            6: {'bras droit': (250, 270), 'avant bras droit': (190, 210)},
            7: {'bras gauche': (70, 90), 'avant bras gauche': (70, 90)},
            8: {'bras droit': (210, 230), 'avant bras droit': (210, 230)},
            9: {'bras gauche': (35, 55), 'avant bras gauche': (35, 55)},
            10: {'bras droit': (70, 90), 'avant bras droit': (70, 90)},
            11: {'bras gauche': (-80, -60), 'avant bras gauche': (-80, -60)},
            12: {'bras droit': (130, 150), 'avant bras droit': (130, 150)},
            13: {'bras gauche': (-55, -35), 'avant bras gauche': (-55, -35)},
            14: {'femur droit': (220, 240), 'tibia droit': (220, 240)},
            15: {'femur gauche': (40, 60), 'tibia gauche': (40, 60)}
            }

COMBINAISONS = {16: (0, 3),
                17: (0, 5),
                18: (0, 7),
                19: (2, 9),
                20: (2, 11),
                21: (2, 13),
                22: (1, 2),
                23: (1, 4),
                24: (1, 6),
                25: (3, 8),
                26: (3, 10),
                27: (3, 12),
                28: (14, 2),
                29: (14, 3),
                30: (14, 0),
                31: (14, 1),
                32: (15, 0),
                33: (15, 1),
                34: (15, 2),
                35: (15, 3)
                }