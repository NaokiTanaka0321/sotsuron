import librosa
import librosa.display
import numpy as np
import math
import soundfile as sf
import glob
import os

#音量を正規化する関数
def normalize(data):
    max_data = max(data)
    for i in range(len(data)):
        data[i] = (data[i]/max_data) *0.5
    return data

#GA(遺伝的アルゴリズム)を用いて次の音を生成する関数
def sound_for_GA(children, f_border, n, air_voice_path, ear_voice_path, throat_voice_path):
    #音声データの読み取り  
    data_air, samplerate = sf.read(air_voice_path)
    data_air = normalize(data_air)
    data_ear, samplerate = sf.read(ear_voice_path)
    data_ear = normalize(data_ear)
    data_throat, samplerate = sf.read(throat_voice_path)
    data_throat = normalize(data_throat)

    for num in range(len(children)):

        #フィルター
        air_dB_start = children[num][0][0]
        air_dB_end = children[num][0][1]
        ear_dB_start = children[num][1][0]
        ear_dB_end = children[num][1][1]
        throat_dB_start = children[num][2][0]
        throat_dB_end = children[num][2][1]

        #体内音を作る上での重み
        air_to_body_weight = children[num][3]
        ear_to_body_weight = children[num][4]
        throat_to_body_weight = children[num][5]

        #自己聴取音を作る上での重み
        body_to_myvoice_weight = children[num][6]
        air_to_myvoice_weight = children[num][7]


        #STFT
        Fs = 2048
        ol = 410
        fft_num = Fs//2 + 1

        X_air = librosa.stft(data_air, n_fft=Fs, win_length=Fs, hop_length=ol, window="hann")
        #フィルターの処理
        air_dB_start_fq = f_border[air_dB_start]
        air_dB_end_fq = f_border[air_dB_end]
        for i in range(0, fft_num):
            freq = (i/fft_num)*samplerate/2
            if freq > air_dB_end_fq:
                dB = -48
                for j in range(len(X_air[0])):
                    X_air[i][j] *= math.pow(10, dB/20)
            elif freq > air_dB_start_fq:
                dB = (math.log(freq/air_dB_start_fq)/math.log(air_dB_end_fq/air_dB_start_fq))*-48
                for j in range(len(X_air[0])):
                    X_air[i][j] *= math.pow(10, dB/20)
            
        X_ear = librosa.stft(data_ear, n_fft=Fs, win_length=Fs, hop_length=ol, window="hann")
        #フィルターの処理
        ear_dB_start_fq = f_border[ear_dB_start]
        ear_dB_end_fq = f_border[ear_dB_end]
        for i in range(0, fft_num):
            freq = (i/fft_num)*samplerate/2
            if freq > ear_dB_end_fq:
                dB = -48
                for j in range(len(X_ear[0])):
                    X_ear[i][j] *= math.pow(10, dB/20)
            elif freq > ear_dB_start_fq:
                dB = (math.log(freq/ear_dB_start_fq)/math.log(ear_dB_end_fq/ear_dB_start_fq))*-48
                for j in range(len(X_ear[0])):
                    X_ear[i][j] *= math.pow(10, dB/20)
            

        X_throat = librosa.stft(data_throat, n_fft=Fs, win_length=Fs, hop_length=ol, window="hann")
        #フィルターの処理
        throat_dB_start_fq = f_border[throat_dB_start]
        throat_dB_end_fq = f_border[throat_dB_end]
        for i in range(0, fft_num):
            freq = (i/fft_num)*samplerate/2
            if freq > throat_dB_end_fq:
                dB = -48
                for j in range(len(X_throat[0])):
                    X_throat[i][j] *= math.pow(10, dB/20)
            elif freq > throat_dB_start_fq:
                dB = (math.log(freq/throat_dB_start_fq)/math.log(throat_dB_end_fq/throat_dB_start_fq))*-48
                for j in range(len(X_throat[0])):
                    X_throat[i][j] *= math.pow(10, dB/20)
                    
        #ISTFTで音声復元
        data_air_2 = librosa.istft(X_air, win_length=Fs, hop_length=ol, window="hann")
        data_air_2 = normalize(data_air_2)
        sf.write("air_filtered"+str(num+1)+".wav", data_air_2, samplerate)
        data_ear_2 = librosa.istft(X_ear, win_length=Fs, hop_length=ol, window="hann")
        data_ear_2 = normalize(data_ear_2)
        sf.write("ear_filtered"+str(num+1)+".wav", data_ear_2, samplerate)
        data_throat_2 = librosa.istft(X_throat, win_length=Fs, hop_length=ol, window="hann")
        data_throat_2 = normalize(data_throat_2)
        sf.write("throat_filtered"+str(num+1)+".wav", data_throat_2, samplerate)

        #体内音への重み付け
        data_2_num = min(len(data_air_2), len(data_ear_2), len(data_throat_2))
        data_body = [0] * data_2_num

        air_amp = pow(10, 0.5*math.log2(air_to_body_weight))
        ear_amp = pow(10, 0.5*math.log2(ear_to_body_weight))
        throat_amp = pow(10, 0.5*math.log2(throat_to_body_weight))

        for i in range(data_2_num):
            data_body[i] = data_air_2[i]*air_amp+data_ear_2[i]*ear_amp+data_throat_2[i]*throat_amp
        data_body = np.array(data_body)
        data_body = normalize(data_body)
        sf.write("body"+str(num+1)+".wav", data_body, samplerate)

#体内音のパラメーターを元に重みを少しずつ変えて自己聴取音を作る関数
def myvoice(air_voice_path, body_voice_path):

    #音声データの読み取り  
    data_air, samplerate = sf.read(air_voice_path)
    data_air = normalize(data_air)
    data_body, samplerate = sf.read(body_voice_path)
    data_body = normalize(data_body)

    data_num = min(len(data_air), len(data_body))

    for myvoice_num in range(6):
        body_to_myvoice_weight = myvoice_num/5
        air_to_myvoice_weight = 1-body_to_myvoice_weight
        body_amp = 0
        air_amp = 0

        if (body_to_myvoice_weight == 0):
            air_amp = 1
        elif (body_to_myvoice_weight == 1):
            body_amp = 1
        else:
            body_amp = pow(10, 0.5*math.log2(body_to_myvoice_weight))
            air_amp = pow(10, 0.5*math.log2(air_to_myvoice_weight))
        #自己聴取音への重み付け
        data_myvoice = [0] * data_num
        for i in range(data_num):
            data_myvoice[i] = data_body[i]*body_amp+data_air[i]*air_amp
        data_myvoice = np.array(data_myvoice)
        data_myvoice = normalize(data_myvoice)
        sf.write("myvoice"+str(myvoice_num+1)+".wav", data_myvoice, samplerate)


#全ての音を消す関数
def rm_allsounds():
    for name in glob.glob('air_filtered?.wav'):
        os.remove(name)
    for name in glob.glob('ear_filtered?.wav'):
        os.remove(name)
    for name in glob.glob('throat_filtered?.wav'):
        os.remove(name)
    for name in glob.glob('body_filtered?.wav'):
        os.remove(name)
    for name in glob.glob('body?.wav'):
        os.remove(name)
    for name in glob.glob('myvoice?.wav'):
        os.remove(name)
    for name in glob.glob('complete_myvoice.wav'):
        os.remove(name)

#complete_myvoice以外全ての音を消す関数
def rm_othersounds():
    for name in glob.glob('air_filtered?.wav'):
        os.remove(name)
    for name in glob.glob('ear_filtered?.wav'):
        os.remove(name)
    for name in glob.glob('throat_filtered?.wav'):
        os.remove(name)
    for name in glob.glob('body_filtered?.wav'):
        os.remove(name)
    for name in glob.glob('body?.wav'):
        os.remove(name)
    for name in glob.glob('myvoice?.wav'):
        os.remove(name)


#体内音.wavを保存する関数
def make_best_sound_body(best_answer, folder):
    path2 = 'body'+str(best_answer)+'.wav'
    data2, samplerate = sf.read(path2)
    sf.write(folder+"体内音.wav", data2, samplerate)

#自己聴取音.wavを保存する関数
def make_best_sound(best_answer, folder):
    path1 = 'myvoice'+str(best_answer)+'.wav'
    data1, samplerate = sf.read(path1)
    sf.write(folder+"自己聴取音.wav", data1, samplerate)
    
def dB(border_num, dB_start_num, dB_end_num):
    reduce_speed = dB_end_num-dB_start_num
    reduce_item = border_num-dB_start_num
    return str(format(-48*reduce_item/reduce_speed, '.1f'))+"dB\n"


#パラメーターの情報をtxtファイルに出力をする関数
def txt_information_body(children, children_num, f_border, folder):
    f = open(folder+'result_体内音.txt', 'w')
    child = children[children_num-1]
    f.write("体内音のパラメーター\n\n")
    f.write("気導音　のフィルターのdB下がりはじめ："+str(f_border[child[0][0]])+"Hz\n")
    f.write("気導音　のフィルターのdB下がりおわり："+str(f_border[child[0][1]])+"Hz\n")
    f.write("耳骨導音のフィルターのdB下がりはじめ："+str(f_border[child[1][0]])+"Hz\n")
    f.write("耳骨導音のフィルターのdB下がりおわり："+str(f_border[child[1][1]])+"Hz\n")
    f.write("喉骨導音のフィルターのdB下がりはじめ："+str(f_border[child[2][0]])+"Hz\n")
    f.write("喉骨導音のフィルターのdB下がりおわり："+str(f_border[child[2][1]])+"Hz\n\n")
    f.write("気導音　→体内音の重み："+format(child[3], '.2f')+"\n")
    f.write("耳骨導音→体内音の重み："+format(child[4], '.2f')+"\n")
    f.write("喉骨導音→体内音の重み："+format(child[5], '.2f')+"\n\n")

    f.write("気導音のdBの変化\n")
    f.write("~"+str(f_border[child[0][0]])+"Hz：0dB\n")
    for border_num in range(child[0][0]+1, child[0][1]):
        f.write(str(f_border[border_num])+"Hz："+dB(border_num, child[0][0], child[0][1]))
    f.write(str(f_border[child[0][1]])+"Hz~：-48dB\n\n")

    f.write("耳骨導音のdBの変化\n")
    f.write("~"+str(f_border[child[1][0]])+"Hz：0dB\n")
    for border_num in range(child[1][0]+1, child[1][1]):
        f.write(str(f_border[border_num])+"Hz："+dB(border_num, child[1][0], child[1][1]))
    f.write(str(f_border[child[1][1]])+"Hz~：-48dB\n\n")

    f.write("喉骨導音のdBの変化\n")
    f.write("~"+str(f_border[child[2][0]])+"Hz：0dB\n")
    for border_num in range(child[2][0]+1, child[2][1]):
        f.write(str(f_border[border_num])+"Hz："+dB(border_num, child[2][0], child[2][1]))
    f.write(str(f_border[child[2][1]])+"Hz~：-48dB\n\n")


#パラメーターの情報をtxtファイルに出力をする関数
def txt_information_best(best_param, best_answer, f_border, folder):
    weight = (best_answer-1)/5
    f = open(folder+'result_自己聴取音.txt', 'w')
    f.write("自己聴取音のパラメーター\n\n")
    f.write("気導音　のフィルターのdB下がりはじめ："+str(f_border[best_param[0][0]])+"Hz\n")
    f.write("気導音　のフィルターのdB下がりおわり："+str(f_border[best_param[0][1]])+"Hz\n")
    f.write("耳骨導音のフィルターのdB下がりはじめ："+str(f_border[best_param[1][0]])+"Hz\n")
    f.write("耳骨導音のフィルターのdB下がりおわり："+str(f_border[best_param[1][1]])+"Hz\n")
    f.write("喉骨導音のフィルターのdB下がりはじめ："+str(f_border[best_param[2][0]])+"Hz\n")
    f.write("喉骨導音のフィルターのdB下がりおわり："+str(f_border[best_param[2][1]])+"Hz\n\n")

    f.write("気導音　→体内音の重み："+format(best_param[3], '.2f')+"\n")
    f.write("耳骨導音→体内音の重み："+format(best_param[4], '.2f')+"\n")
    f.write("喉骨導音→体内音の重み："+format(best_param[5], '.2f')+"\n\n")

    f.write("体内音→自己聴取音の重み："+str(weight)+"\n")
    f.write("気導音→自己聴取音の重み："+str(1-weight)+"\n\n")

    f.write("気導音のdBの変化\n")
    f.write("~"+str(f_border[best_param[0][0]])+"Hz：0dB\n")
    for border_num in range(best_param[0][0]+1, best_param[0][1]):
        f.write(str(f_border[border_num])+"Hz："+dB(border_num, best_param[0][0], best_param[0][1]))
    f.write(str(f_border[best_param[0][1]])+"Hz~：-48dB\n\n")

    f.write("耳骨導音のdBの変化\n")
    f.write("~"+str(f_border[best_param[1][0]])+"Hz：0dB\n")
    for border_num in range(best_param[1][0]+1, best_param[1][1]):
        f.write(str(f_border[border_num])+"Hz："+dB(border_num, best_param[1][0], best_param[1][1]))
    f.write(str(f_border[best_param[1][1]])+"Hz~：-48dB\n\n")

    f.write("喉骨導音のdBの変化\n")
    f.write("~"+str(f_border[best_param[2][0]])+"Hz：0dB\n")
    for border_num in range(best_param[2][0]+1, best_param[2][1]):
        f.write(str(f_border[border_num])+"Hz："+dB(border_num, best_param[2][0], best_param[2][1]))
    f.write(str(f_border[best_param[2][1]])+"Hz~：-48dB\n\n")
