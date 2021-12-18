
from time import time, sleep
from threading import Thread

import cv2
import numpy as np

from names import COMBINAISONS, ACTIONS, OS, NAMES, EDGES, COLOR
from my_movenet import Movenet



class GesturesDetection(Movenet):
    """Détection des gestes"""

    def __init__(self, conn, current_dir, config):

        Movenet.__init__(self, current_dir)

        self.move_conn = conn
        self.current_dir = current_dir
        self.config = config
        self.zoom = None
        self.move_loop = 1
        self.gestures_block = 0
        self.t_gest = time()
        self.nbr_gest = 0
        self.threshold_m = float(self.config['move']['threshold'])

        self.move_conn_loop = 1
        if self.move_conn:
            self.gestures_detection_receive_thread()

        # Tous les angles
        self.angles = {}
        # Etat de toutes les actions
        self.actions = {}

        cv2.namedWindow('Movenet', cv2.WND_PROP_FULLSCREEN)

    def gestures_detection_receive_thread(self):
        print("Lancement du thread receive dans gestures_detection")
        t_move = Thread(target=self.gestures_detection_receive)
        t_move.start()

    def gestures_detection_receive(self):
        while self.move_conn_loop:
            if self.move_conn.poll():
                data = self.move_conn.recv()
                if data:
                    if data[0] == 'quit':
                        print("Alerte: Quit reçu dans gestures_detection")
                        self.move_loop = 0
                        self.move_conn_loop = 0
                        self.gestures_block = 0
                        self.movenet_close()

                    elif data[0] == 'zoom':
                        self.main(data[1])

                    elif data[0] == 'threshold':
                        print('threshold reçu dans movenet:', data[1])
                        self.threshold_m = data[1]

            sleep(0.001)

    def run(self):
        while self.move_loop:

            if self.gestures_block:
                if self.zoom is not None:
                    if self.zoom.any():
                        # FPS
                        self.nbr_gest += 1
                        cv2.imshow('Movenet', self.zoom)
                        self.gestures_block = 0

                        # Calcul du FPS, affichage toutes les 10 s
                        if time() - self.t_gest > 10:
                            print("FPS Movenet =", int(self.nbr_gest/10))
                            self.t_gest, self.nbr_gest = time(), 0

            k = cv2.waitKey(1)
            # Pour quitter
            if k == 27:  # Esc
                self.move_conn.send(['quit', 1])
                print("Quit envoyé de GesturesDetection")

        cv2.destroyAllWindows()

    def main(self, zoom):
        """Traitement d'une image reçue
        Le squelette est défini dans self.movenet_keypoints
        Affichage du squelette,
        récupération des angles,
        détection des gestes
        """

        if not self.gestures_block:
            self.gestures_block = 1
            if zoom is not None:
                # Actualise les movenet_keypoints
                self.skeleton_detection(zoom, self.threshold_m)

                # L'affichage se fait avec self.zoom, maintenant je
                # peux l'actualiser
                self.zoom = zoom

                # Détection des gestes
                self.draw_keypoints_edges()
                self.get_all_angles()
                # # self.draw_angles()
                self.draw_text()
                actions = self.detect_actions()
                self.send_actions(actions)

    def send_actions(self, actions):
        """actions = {0: 1, 1: 0, 2: 0, 3: 0, .... 15: 0}
        """
        msg = []
        for k, v in actions.items():
            if v:
                msg.append(k)
        if msg:
            self.move_conn.send(['action', msg])

    def draw_keypoints_edges(self):
        """
        keypoints = [None, [200, 300], None, [100, 700], ...] = 17 items
        L'index correspond aux valeurs dans NAMES
        """
        # Dessin des points détectés
        for point in self.movenet_keypoints:
            if point:
                x = int(point[0])
                y = int(point[1])
                cv2.circle(self.zoom, (x, y), 4, color=(0,0,255), thickness=-1)

        # Dessin des os
        for i, (a, b) in enumerate(EDGES):
            """EDGES = (   (0, 1)
            keypoints[0] = [513, 149]
            """
            if not self.movenet_keypoints[a] or not self.movenet_keypoints[b]:
                continue
            ax = int(self.movenet_keypoints[a][0])
            ay = int(self.movenet_keypoints[a][1])
            bx = int(self.movenet_keypoints[b][0])
            by = int(self.movenet_keypoints[b][1])
            cv2.line(self.zoom, (ax, ay), (bx, by), COLOR[i], 2)

    def get_angle(self, p1, p2):
        """Angle entre horizontal et l'os
        origin p1
        p1 = numéro d'os
        tg(alpha) = y2 - y1 / x2 - x1
        """
        alpha = None

        if self.movenet_keypoints[p1] and self.movenet_keypoints[p2]:
            x1, y1 = self.movenet_keypoints[p1][0], self.movenet_keypoints[p1][1]
            x2, y2 = self.movenet_keypoints[p2][0], self.movenet_keypoints[p2][1]
            if x2 - x1 != 0:
                tg_alpha = (y2 - y1) / (x2 - x1)
                if x2 > x1:
                    alpha = int((180/np.pi) * np.arctan(tg_alpha))
                else:
                    alpha = 180 - int((180/np.pi) * np.arctan(tg_alpha))
        return alpha

    def draw_text(self):
        """Affichage de la moyenne des profondeurs et x du personnage vert"""
        d = {   "Confiance": self.threshold_m}

        i = 0
        for key, val in d.items():
            text = key + " : " + str(val)
            cv2.putText(self.zoom,  # image
                        text,
                        (30, 50*i+50),  # position
                        cv2.FONT_HERSHEY_SIMPLEX,  # police
                        0.6,  # taille police
                        (0, 255, 0),  # couleur
                        2)  # épaisseur
            i += 1

    def get_all_angles(self):
        """angles = {'tibia droit': 128}
        origine = 1er de OS (14, 16)
        angles idem cercle trigo
        """
        angles = {}
        for os, (p1, p2) in OS.items():
            angles[os] = self.get_angle(p1, p2)

        self.angles = angles

    def draw_angles(self):
        """dessin des valeurs d'angles
        angles = {'tibia droit': 128}
        """
        for os, (p1, p2) in OS.items():
            if self.movenet_keypoints[p1] and self.movenet_keypoints[p1]:
                alpha = self.angles[os]
                if alpha:
                    u = int((self.movenet_keypoints[p1][0] + self.movenet_keypoints[p2][0])/2)
                    v = int((self.movenet_keypoints[p1][1] + self.movenet_keypoints[p2][1])/2)
                    cv2.putText(self.zoom,                  # image
                                str(alpha),                 # text
                                (u, v-20),                  # position
                                cv2.FONT_HERSHEY_SIMPLEX,   # police
                                0.5,                          # taille police
                                (0, 255, 255),              # couleur
                                2)                          # épaisseur

    def detect_actions(self):
        """
        ACTIONS = {0: {'bras droit':  (170, 190), 'avant bras droit':  (70, 90)},
        COMBINAISONS = {16: (0, 3),
        actions = {0: 0 ou 1}
        """

        actions = {}

        # ACTIONS
        for action, val in ACTIONS.items():
            # val = {'bras droit':  (-15, 15), 'avant bras droit':  (70, 90)}
            act = 0

            for os, (mini, maxi) in val.items():
                if self.angles[os]:
                    if mini < self.angles[os] < maxi:
                        act = 1
                    actions[action] = act
                else:
                    actions[action] = 0

        return actions


def gestures_detection_run(conn, current_dir, config):

    gd = GesturesDetection(conn, current_dir, config)
    gd.run()
