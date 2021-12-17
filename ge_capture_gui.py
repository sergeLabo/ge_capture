
"""
Interface graphique pour GE Capture
"""


import os
from time import sleep
from pathlib import Path
from multiprocessing import Process, Pipe
from threading import Thread
from datetime import datetime
import json

import kivy
kivy.require('2.0.0')
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock

from oscpy.client import OSCClient

from posenet_realsense import posenet_realsense_run
from gestures_detection import gestures_detection_run

k = 1
WS = (int(720*k), int(720*k))
Window.size = WS



class MainScreen(Screen):
    """Ecran principal, l'appli s'ouvre sur cet écran
    root est le parent de cette classe dans la section <MainScreen> du kv
    """

    # Attribut de class, obligatoire pour appeler root.titre dans kv
    titre = StringProperty("toto")
    enable = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Trop fort: permet d'accéder à la class GE_CaptureApp
        self.app = App.get_running_app()

        # Pour le Pipe
        self.p1_conn = None  # De posenet realsense
        self.p3_conn = None  # De Movenet
        self.kivy_receive_loop = 1

        # Pour ne lancer qu'une fois les processus
        self.enable = False

        self.titre = "GE Capture"

        ip = self.app.config.get('osc', 'ip')
        port = int(self.app.config.get('osc', 'port'))
        self.osc_client = OSCClient(ip, port)
        self.datas = []  # A enregister dans un json
        self.save_in_json = 0

        Clock.schedule_once(self.set_run_on, 1.0)

        print("Initialisation du Screen MainScreen ok")

    def set_run_on(self, dt):
        """Start automatique"""
        self.ids.run.state = "down"
        self.run_ge_capture()

    def kivy_receive_thread(self):
        t_kivy = Thread(target=self.kivy_receive)
        t_kivy.start()

    def kivy_receive(self):
        while self.kivy_receive_loop:
            sleep(0.0001)

            # De posenet realsense
            if self.p1_conn is not None:
                if self.p1_conn.poll():
                    try:
                        data1 = self.p1_conn.recv()
                    except:
                        data1 = None

                    if data1 is not None:
                        # Relais des depth
                        if data1[0] == 'depth':
                            self.osc_client.send_message(b'/depth', [data1[1]])
                            if self.save_in_json:
                                self.datas.append(('/depth', [data1[1]]))

                        # Relais des zoom
                        if data1[0] == 'zoom':
                            self.p3_conn.send(['zoom', data1[1]])

                        if data1[0] == 'quit':
                            print("\nQuit reçu dans Kivy de Posenet Realsense ")
                            self.quit()

            # De Movenet
            if self.p3_conn is not None:
                if self.p3_conn.poll():
                    try:
                        data3 = self.p3_conn.recv()
                    except:
                        data3 = None

                    if data3 is not None:

                        # Actions ['action', k]
                        if data3[0] == 'action':
                            self.osc_client.send_message(b'/action', [data3[1]])
                            if self.save_in_json:
                                self.datas.append(('/action', [data3[1]]))

                        if data3[0] == 'quit':
                            print("Quit reçu dans Kivy de Movenet")
                            self.quit()

    def quit(self):
        self.p1_conn.send(['quit', 1])
        self.p3_conn.send(['quit', 1])
        self.kivy_receive_loop = 0
        self.app.do_quit()

    def run_ge_capture(self):
        if not self.enable:
            print("Lancement de 3 processus:")

            current_dir = str(Path(__file__).parent.absolute())
            print("Dossier courrant:", current_dir)

            # Posenet et Realsense
            self.p1_conn, child_conn1 = Pipe()
            self.p1 = Process(target=posenet_realsense_run, args=(child_conn1,
                                                             current_dir,
                                                             self.app.config, ))
            self.p1.start()
            print("Posenet Realsense lancé ...")

            # Movenet
            self.p3_conn, child_conn3 = Pipe()
            self.p3 = Process(target=gestures_detection_run, args=(child_conn3,
                                                              current_dir,
                                                              self.app.config, ))
            self.p3.start()
            print("Gestures Detection lancé ...")

            self.enable = True
            self.kivy_receive_thread()
            print("Kivy tourne ...")



class Reglage(Screen):

    brightness = NumericProperty(0)
    contrast = NumericProperty(0)

    brightness_contrast = NumericProperty(0)
    threshold_p = NumericProperty(0.8)

    profondeur_mini = NumericProperty(1500)
    profondeur_maxi = NumericProperty(4000)

    largeur_maxi = NumericProperty(500)
    threshold_m = NumericProperty(0.8)

    pile_size = NumericProperty(12)
    lissage = NumericProperty(11)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Initialisation du Screen Settings")

        self.app = App.get_running_app()
        self.brightness = float(self.app.config.get('pose', 'brightness'))
        self.contrast = float(self.app.config.get('pose', 'contrast'))

        self.brightness_contrast = int(self.app.config.get('pose', 'brightness_contrast'))
        self.threshold_p = float(self.app.config.get('pose', 'threshold'))

        self.profondeur_mini = int(self.app.config.get('pose', 'profondeur_mini'))
        self.profondeur_maxi = int(self.app.config.get('pose', 'profondeur_maxi'))

        self.largeur_maxi = int(self.app.config.get('pose', 'largeur_maxi'))
        self.threshold_m = float(self.app.config.get('move', 'threshold'))

        self.pile_size = int(self.app.config.get('pose', 'pile_size'))
        self.lissage = int(self.app.config.get('pose', 'lissage'))

        Clock.schedule_once(self.set_switch, 0.5)

    def set_switch(self, dt):
        """Les objets graphiques ne sont pas encore créé pendant le init,
        il faut lancer cette méthode plus tard
        le switch est setter à 1 si 1 dans la config
        """

        if self.brightness_contrast == 1:
            self.ids.brightness_contrast.active = 1

    def do_slider(self, iD, instance, value):

        scr = self.app.screen_manager.get_screen('Main')

        if iD == 'brightness':
            self.brightness = round(value, 2)

            self.app.config.set('pose', 'brightness', self.brightness)
            self.app.config.write()

            if scr.p1_conn:
                scr.p1_conn.send(['brightness', self.brightness])

        if iD == 'contrast':
            self.contrast = round(value, 2)

            self.app.config.set('pose', 'contrast', self.contrast)
            self.app.config.write()

            if scr.p1_conn:
                scr.p1_conn.send(['contrast', self.contrast])

        if iD == 'threshold_p':
            # Maj de l'attribut
            self.threshold_p = round(value, 2)
            # Maj de la config
            self.app.config.set('pose', 'threshold', self.threshold_p)
            # Sauvegarde dans le *.ini
            self.app.config.write()

            # Envoi de la valeur au process enfant
            if scr.p1_conn:
                scr.p1_conn.send(['threshold', self.threshold_p])

        if iD == 'threshold_m':
            # Maj de l'attribut
            self.threshold_m = round(value, 2)
            # Maj de la config
            self.app.config.set('move', 'threshold', self.threshold_m)
            # Sauvegarde dans le *.ini
            self.app.config.write()

            # Envoi de la valeur au process enfant
            if scr.p3_conn:
                scr.p3_conn.send(['threshold', self.threshold_m])

        if iD == 'profondeur_mini':
            self.profondeur_mini = int(value)

            self.app.config.set('pose', 'profondeur_mini', self.profondeur_mini)
            self.app.config.write()

            if scr.p1_conn:
                scr.p1_conn.send(['profondeur_mini', self.profondeur_mini])

        if iD == 'profondeur_maxi':
            self.profondeur_maxi = int(value)

            self.app.config.set('pose', 'profondeur_maxi', self.profondeur_maxi)
            self.app.config.write()

            if scr.p1_conn:
                scr.p1_conn.send(['profondeur_maxi', self.profondeur_maxi])

        if iD == 'largeur_maxi':
            self.largeur_maxi = int(value)

            self.app.config.set('pose', 'largeur_maxi', self.largeur_maxi)
            self.app.config.write()
            if scr.p1_conn:
                scr.p1_conn.send(['largeur_maxi', self.largeur_maxi])

        if iD == 'pile_size':
            self.pile_size = int(value)

            self.app.config.set('pose', 'pile_size', self.pile_size)
            self.app.config.write()

            if scr.p1_conn:
                scr.p1_conn.send(['pile_size', self.pile_size])

        if iD == 'lissage':
            self.lissage = int(value)
            if self.lissage >= self.pile_size:
                self.lissage = self.pile_size - 1
            self.app.config.set('pose', 'lissage', self.lissage)
            self.app.config.write()

            if scr.p1_conn:
                scr.p1_conn.send(['lissage', self.lissage])

    def on_switch_brightness_contrast(self, instance, value):
        scr = self.app.screen_manager.get_screen('Main')
        if value:
            value = 1
        else:
            value = 0
        self.brightness_contrast = value
        if scr.p1_conn:
            scr.p1_conn.send(['brightness_contrast', self.brightness_contrast])
        self.app.config.set('pose', 'brightness_contrast',
                                        self.brightness_contrast)
        self.app.config.write()
        print("brightness_contrast =", self.brightness_contrast)

    def on_save_in_json(self, instance, value):
        if value:
            value = 1
        else:
            value = 0
        scr = self.app.screen_manager.get_screen('Main')
        scr.save_in_json = value
        self.datas = []
        print("save_in_json =", value)

    def do_save(self):
        scr = self.app.screen_manager.get_screen('Main')
        dt_now = datetime.now()
        dt = dt_now.strftime("%Y_%m_%d_%H_%M")
        fichier = f"./records/json/cap_{dt}.json"
        print(scr.datas)
        with open(fichier, "w") as fd:
            fd.write(json.dumps(scr.datas))
        print(f"Enregistrement du json: cap_{dt}.json")

# Variable globale qui définit les écrans
# L'écran de configuration est toujours créé par défaut
# Il suffit de créer un bouton d'accès
# Les class appelées (MainScreen, ...) sont placées avant
SCREENS = { 0: (MainScreen, 'Main'),
            1: (Reglage, 'Reglage')}


class GE_CaptureApp(App):
    """Construction de l'application. Exécuté par if __name__ == '__main__':,
    app est le parent de cette classe dans kv
    """

    def build(self):
        """Exécuté après build_config, construit les écrans"""

        # Création des écrans
        self.screen_manager = ScreenManager()
        for i in range(len(SCREENS)):
            # Pour chaque écran, équivaut à
            # self.screen_manager.add_widget(MainScreen(name="Main"))
            self.screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))

        return self.screen_manager

    def build_config(self, config):
        """Excécuté en premier (ou après __init__()).
        Si le fichier *.ini n'existe pas,
                il est créé avec ces valeurs par défaut.
        Il s'appelle comme le kv mais en ini
        Si il manque seulement des lignes, il ne fait rien !
        [camera]
        width_input = 1280
        height_input = 720

        [pose]
        brightness = -0.14
        contrast = 0.06
        brightness_contrast = 0
        threshold = 0.71
        profondeur_mini = 830
        profondeur_maxi = 4900
        largeur_maxi = 500
        brightness_contrast = 0

        [move]
        threshold = 0.21

        [osc]
        ip = 127.0.0.1
        port = 8000
        """

        print("Création du fichier *.ini si il n'existe pas")

        config.setdefaults( 'camera',
                                        {   'width_input': 1280,
                                            'height_input': 720})

        config.setdefaults( 'pose',
                                        {   'brightness': 0,
                                            'contrast': 0,
                                            'brightness_contrast': 0,
                                            'threshold': 0.71,
                                            'profondeur_mini': 830,
                                            'profondeur_maxi': 4900,
                                            'largeur_maxi': 500,
                                            'pile_size': 30,
                                            'lissage': 11})

        config.setdefaults( 'move',
                                        {   'threshold': 0.21})

        config.setdefaults( 'osc',
                                        {   'ip': '127.0.0.1',
                                            'port': 8000})


        print("self.config peut maintenant être appelé")

    def build_settings(self, settings):
        """Construit l'interface de l'écran Options, pour GE_Capture seul,
        Les réglages Kivy sont par défaut.
        Cette méthode est appelée par app.open_settings() dans .kv,
        donc si Options est cliqué !
        """

        print("Construction de l'écran Options")

        data = """[ {"type": "title", "title": "Capture"},

                        {   "type": "string",
                            "title": "IP",
                            "desc": "IP où envoyer",
                            "section": "osc", "key": "ip"},

                        {   "type": "numeric",
                            "title": "Port",
                            "desc": "Port où envoyer",
                            "section": "osc", "key": "port"}

                    ]"""

        # self.config est le config de build_config
        settings.add_json_panel('GE_Capture', self.config, data=data)

    def go_mainscreen(self):
        """Retour au menu principal depuis les autres écrans."""
        self.screen_manager.current = ("Main")

    def do_quit(self):
        print("Je quitte proprement dans Kivy ...")
        scr = self.screen_manager.get_screen('Main')

        scr.p1_conn.send(['quit', 1])
        scr.p3_conn.send(['quit', 1])
        sleep(2)

        print("scr.kivy_receive_loop = 0")
        scr.kivy_receive_loop = 0

        scr.p1.terminate()
        scr.p3.terminate()
        sleep(3)
        print("Tous les process sont terminés")

        # Kivy
        print("Quit final")
        GE_CaptureApp.get_running_app().stop()


if __name__ == '__main__':
    """L'application s'appelle GE_Capture
    d'où
    la class
        GE_CaptureApp()
    les fichiers:
        ge_capture.kv
        ge_capture.ini
    """

    GE_CaptureApp().run()
