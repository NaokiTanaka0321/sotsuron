from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
import pathlib
import glob
import convert_sound


resource_add_path("font")
LabelBase.register(DEFAULT_FONT, "NotoSansJP-Black.otf")

air_voice_path = '-' #気導音のファイルのパス
ear_voice_path = '-' #耳骨導音のファイルのパス
throat_voice_path = '-' #喉骨導音のファイルのパス
folder = '' #3つの音源が置いてあるフォルダ
f_border = [31, 44, 63, 88, 125, 180, 250, 355, 500, 710, 1000, 1400, 2000, 2800, 4000, 5600, 8000, 11300, 16000, 22000]

body_params = '-' #体内音のパラメーターが格納されているパス
myvoice_params = '-' #自己聴取音のパラメーターが格納されているパス

#録音を選択する画面
class SelectSounds(BoxLayout):
    air = StringProperty()
    ear = StringProperty()
    throat = StringProperty()

    #おまじない
    def __init__(self, **kwargs):
        super(SelectSounds, self).__init__(**kwargs)
        self.air = air_voice_path
        self.ear = ear_voice_path
        self.throat = throat_voice_path

    def filechoose_air(self):
        self.clear_widgets()
        window_next = Filechooser_Air()
        self.add_widget(window_next)

    def filechoose_ear(self):
        self.clear_widgets()
        window_next = Filechooser_Ear()
        self.add_widget(window_next)

    def filechoose_throat(self):
        self.clear_widgets()
        window_next = Filechooser_Throat()
        self.add_widget(window_next)

    def to_params(self):
        air_filename = self.ids["air_voice"].text
        ear_filename = self.ids["ear_voice"].text
        throat_filename = self.ids["throat_voice"].text
        if (air_filename != "-" and ear_filename != "-" and throat_filename != "-"):
            self.clear_widgets()
            window_next = SelectParams()
            self.add_widget(window_next)

    #アクションバーでメインに移る
    

#音を選択する画面
class Filechooser_Air(GridLayout):
    #おまじない
    def __init__(self, **kwargs):
        super(Filechooser_Air, self).__init__(**kwargs)


    def selected(self, filename):
        try:
            wavfile_path = filename[0]
            current_path = str(pathlib.Path.cwd())
            relative_path = wavfile_path.replace(current_path+'/', '')
            global air_voice_path
            air_voice_path = relative_path
            global folder
            if "/" in air_voice_path:
                slash_num = air_voice_path.rfind('/')
                folder = air_voice_path[:slash_num+1]


            self.clear_widgets()
            window_next = SelectSounds()
            self.add_widget(window_next)
        except:
            pass

#音を選択する画面
class Filechooser_Ear(GridLayout):
    #おまじない
    def __init__(self, **kwargs):
        super(Filechooser_Ear, self).__init__(**kwargs)


    def selected(self, filename):
        try:
            wavfile_path = filename[0]
            current_path = str(pathlib.Path.cwd())
            relative_path = wavfile_path.replace(current_path+'/', '')
            global ear_voice_path
            ear_voice_path = relative_path

            self.clear_widgets()
            window_next = SelectSounds()
            self.add_widget(window_next)
        except:
            pass

#音を選択する画面
class Filechooser_Throat(GridLayout):
    #おまじない
    def __init__(self, **kwargs):
        super(Filechooser_Throat, self).__init__(**kwargs)


    def selected(self, filename):
        try:
            wavfile_path = filename[0]
            current_path = str(pathlib.Path.cwd())
            relative_path = wavfile_path.replace(current_path+'/', '')
            global throat_voice_path
            throat_voice_path = relative_path

            self.clear_widgets()
            window_next = SelectSounds()
            self.add_widget(window_next)
        except:
            pass

class SelectParams(BoxLayout):
    body = StringProperty()
    myvoice = StringProperty()
    #おまじない
    def __init__(self, **kwargs):
        super(SelectParams, self).__init__(**kwargs)
        self.body = body_params
        self.myvoice = myvoice_params

    def filechoose_body(self):
        self.clear_widgets()
        window_next = Filechooser_body()
        self.add_widget(window_next)

    def filechoose_myvoice(self):
        self.clear_widgets()
        window_next = Filechooser_myvoice()
        self.add_widget(window_next)

    def display(self):
         self.ids["select_params_display"].text = "体内音と自己聴取音を生成中です。"

    def conversion(self):
        if (self.body != "-" and self.myvoice != "-"):
            convert_sound.conversion(f_border, folder, air_voice_path, ear_voice_path, throat_voice_path, body_params, myvoice_params)
            exit()

    
#音を選択する画面
class Filechooser_body(GridLayout):
    #おまじない
    def __init__(self, **kwargs):
        super(Filechooser_body, self).__init__(**kwargs)


    def selected(self, filename):
        try:
            txtfile_path = filename[0]
            current_path = str(pathlib.Path.cwd())
            relative_path = txtfile_path.replace(current_path+'/', '')
            global body_params
            body_params = relative_path
            self.clear_widgets()
            window_next = SelectParams()
            self.add_widget(window_next)
        except:
            pass

#音を選択する画面
class Filechooser_myvoice(GridLayout):
    #おまじない
    def __init__(self, **kwargs):
        super(Filechooser_myvoice, self).__init__(**kwargs)


    def selected(self, filename):
        try:
            txtfile_path = filename[0]
            current_path = str(pathlib.Path.cwd())
            relative_path = txtfile_path.replace(current_path+'/', '')
            global myvoice_params
            myvoice_params = relative_path
            self.clear_widgets()
            window_next = SelectParams()
            self.add_widget(window_next)
        except:
            pass

#kvファイルとの同期づけ
class ConversionApp(App):

    #起動したらはじめに3つのマイクの録音音源を選ぶ画面を立ち上げる
    def build(self):
        return SelectSounds()

#アプリを起動
ConversionApp().run()
