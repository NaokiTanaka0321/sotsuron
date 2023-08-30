from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
import pathlib
import glob
import GA
import gen_sound

resource_add_path("font")
LabelBase.register(DEFAULT_FONT, "NotoSansJP-Black.otf")


n = 8 #1世代の個数
elite_num = 1 #エリート選択をする個数
roulette_num = 1 #ルーレット選択する個数
BLX_num = 2 #BLXする個数
random_num = 4 #ランダム生成する個数
alpha = 1.5 #BLXの際のパラメーター
f_border = [31, 44, 63, 88, 125, 180, 250, 355, 500, 710, 1000, 1400, 2000, 2800, 4000, 5600, 8000, 11300, 16000, 22000]


air_voice_path = '-' #気導音のファイルのパス
ear_voice_path = '-' #耳骨導音のファイルのパス
throat_voice_path = '-' #喉骨導音のファイルのパス
body_voice_path = '-' #体内音のファイルのパス
folder = '' #3つの音源が置いてあるフォルダ

children = []
best_param = [[5, 9], [7, 11], [5, 12], 0.4, 0.4, 0.2, 0.9, 0.1]

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

    def display(self):
         self.ids["select_sounds_display"].text = "体内音を生成中です。(20秒ほどかかります)"

    def generate(self):
        air_filename = self.ids["air_voice"].text
        ear_filename = self.ids["ear_voice"].text
        throat_filename = self.ids["throat_voice"].text
        if (air_filename != "-" and ear_filename != "-" and throat_filename != "-"):
            gen_sound.rm_othersounds()
            global children
            children = GA.ga([], [], 8, 0, 0, 0, 8, 1.5)
            gen_sound.sound_for_GA(children, f_border, n, air_voice_path, ear_voice_path, throat_voice_path)
            self.clear_widgets()
            window_next = SoundPlayer_body()
            self.add_widget(window_next)
    

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

#使い方
class Howtouse(BoxLayout):
    pass


#体内音の評価
class SoundPlayer_body(BoxLayout):
    text  = StringProperty()
    sound = SoundLoader.load('body1.wav')

    #おまじない
    def __init__(self, **kwargs):
        super(SoundPlayer_body, self).__init__(**kwargs)
        self.text = "体内音ができました。音を聞いてください。"

    #音を再生する関数
    def play_sound(self, num):
        #self.sound.volume = 0.5
        self.sound.play()


    #音を停止する関数
    def stop_sound(self, num):
        self.sound.stop()
            
    #5段階評価をする関数
    def evaluation(self, id_num, eval_num):
        if(self.text == "体内音ができました。音を聞いてください。" or self.text == "全ての音に対して評価してください。"):
            label_id = "body"+str(id_num)+"_view"
            self.ids[label_id].text = str(eval_num)


    #OKボタンが押されたときに評価を記録しておく関数
    def ok(self):
        evaluation_list_body = []
        for id_num in range(1,9):
            label_id = "body"+str(id_num)+"_view"
            txt = self.ids[label_id].text
            if txt != "-":
                evaluation_list_body.append(int(txt))
        if(len(evaluation_list_body) == 8 and (self.text == "体内音ができました。音を聞いてください。" or self.text == "全ての音に対して評価してください。")):
            self.text = "体内音を生成中です。(20秒ほどかかります)"
        return evaluation_list_body

    #OKボタンが押されたときに次の世代に進むか判定する関数
    def next_epoch(self, evaluation_list):
        if(self.text == "体内音を生成中です。(20秒ほどかかります)"):
            global children
            gen_sound.rm_othersounds()
            children = GA.ga(children, evaluation_list, n, elite_num, roulette_num, BLX_num, random_num, alpha)
            gen_sound.sound_for_GA(children, f_border, n, air_voice_path, ear_voice_path, throat_voice_path)
            self.text = "体内音ができました。音を聞いてください。"
            for id_num in range(1,9):
                label_id = "body"+str(id_num)+"_view"
                self.ids[label_id].text = "-"
        elif len(evaluation_list) != 8 and self.text == "体内音ができました。音を聞いてください。":
            self.text = "全ての音に対して評価してください。"

    #終了画面に切り替える関数
    def Actionchange_end(self):
        self.clear_widgets()
        window_end = End_body()
        self.add_widget(window_end)


#体内音終了画面
class End_body(BoxLayout):

    #おまじない
    def __init__(self, **kwargs):
        super(End_body, self).__init__(**kwargs)

    #選ばれた音がなにか表示する関数
    def display_num(self,num):
        self.ids["aaa"].text = "体内音"+str(num)

    def to_myvoice_text(self):
        txt = self.ids["aaa"].text
        if txt != "-":
            self.ids["label1"].text = "自己聴取音を生成中です。(10秒ほどかかります)"

    #選ばれた体内音を元に自己聴取音を生成する関数
    def to_myvoice(self):
        if self.ids["label1"].text == "自己聴取音を生成中です。(10秒ほどかかります)":
            global children
            global best_param
            global body_voice_path
            txt = self.ids["aaa"].text
            num = int(txt.replace("体内音", ""))
            best_param = children[num-1]
            body_voice_path = folder + "体内音.wav"
            gen_sound.make_best_sound_body(num, folder)
            gen_sound.rm_allsounds()
            gen_sound.myvoice(air_voice_path, body_voice_path)
            gen_sound.txt_information_body(children, num, f_border, folder)
            self.clear_widgets()
            window_main = SoundPlayer_myvoice()
            self.add_widget(window_main)

    #終了画面に切り替える関数
    def Actionchange_main(self):
        self.clear_widgets()
        window_main = SoundPlayer_body()
        self.add_widget(window_main)

            

#自己聴取音を選ぶ画面
class SoundPlayer_myvoice(BoxLayout):
    text  = StringProperty()
    sound = SoundLoader.load('myvoice1.wav')

    #おまじない
    def __init__(self, **kwargs):
        super(SoundPlayer_myvoice, self).__init__(**kwargs)
        self.text = "この中で自己聴取音に一番近い音を選んでください。"

    #音を再生する関数
    def play_sound(self):
        self.sound.play()

    #音を停止する関数
    def stop_sound(self):
        self.sound.stop()

    def display_num(self,num):
        self.ids["aaa"].text = "自己聴取音"+str(num)

    #選ばれた自己聴取音を元に他の音を消してアプリを終了する関数
    def app_end(self):
        txt = self.ids["aaa"].text
        if txt != "-":
            best_answer = int(txt.replace("自己聴取音", ""))
            gen_sound.make_best_sound(best_answer, folder)
            gen_sound.txt_information_best(best_param, best_answer, f_border, folder)
            gen_sound.rm_allsounds()
            exit()

#kvファイルとの同期づけ
class MyApp(App):

    #起動したらはじめに3つのマイクの録音音源を選ぶ画面を立ち上げる
    def build(self):
        return SelectSounds()

#アプリを起動
gen_sound.rm_allsounds()
MyApp().run()

