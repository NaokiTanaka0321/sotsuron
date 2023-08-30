import librosa
import librosa.display
import numpy as np
import math
import soundfile as sf
import glob
import os

"""
param = 
[[気導音のdB減り始め, 気導音のdB減り終わり], 0
[耳骨導音のdB減り始め, 耳骨導音のdB減り終わり], 1
[喉骨導音のdB減り始め, 喉骨導音のdB減り終わり], 2
気導音→体内音の重み, 3
耳導音→体内音の重み, 4
喉骨導音→体内音の重み, 5
体内音→自己聴取音の重み, 6
気導音→自己聴取音の重み] 7

f_border = [0→31, 1→44, 2→63, 3→88, 4→125, 5→180, 6→250, 7→355, 8→500, 9→710, 10→1000, 11→1400, 12→2000, 13→2800, 14→4000, 15→5600, 16→8000, 17→11300, 18→16000, 19→22000]
"""

#音量を正規化する関数
def normalize(data):
    max_data = max(data)
    for i in range(len(data)):
        data[i] = (data[i]/max_data) *0.5
    return data

def rm_allsounds():
    for name in glob.glob('air_filtered.wav'):
        os.remove(name)
    for name in glob.glob('ear_filtered.wav'):
        os.remove(name)
    for name in glob.glob('throat_filtered.wav'):
        os.remove(name)
    for name in glob.glob('body.wav'):
        os.remove(name)

def conversion(f_border, folder, air_voice_path, ear_voice_path, throat_voice_path, body_params, myvoice_params):
    
    #音声データの読み取り
    data_air, samplerate = sf.read(air_voice_path)
    data_air = normalize(data_air)
    data_ear, samplerate = sf.read(ear_voice_path)
    data_ear = normalize(data_ear)
    data_throat, samplerate = sf.read(throat_voice_path)
    data_throat = normalize(data_throat)


    #体内音のパラメーターの取得
    #f_body = open(folder+body_params)
    f_body = open(body_params)
    body_info = f_body.readlines()
    hz_num = body_info[2].rfind('：')
    air_dB_start = f_border.index(int(body_info[2][hz_num+1:-3]))
    air_dB_end = f_border.index(int(body_info[3][hz_num+1:-3]))
    ear_dB_start = f_border.index(int(body_info[4][hz_num+1:-3]))
    ear_dB_end = f_border.index(int(body_info[5][hz_num+1:-3]))
    throat_dB_start = f_border.index(int(body_info[6][hz_num+1:-3]))
    throat_dB_end = f_border.index(int(body_info[7][hz_num+1:-3]))

    weight1_num = body_info[9].rfind('：')
    #体内音を作る上での重み
    air_to_body_weight = float(body_info[9][weight1_num+1:])
    ear_to_body_weight = float(body_info[10][weight1_num+1:])
    throat_to_body_weight = float(body_info[11][weight1_num+1:])

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
    sf.write("air_filtered.wav", data_air_2, samplerate)
    data_ear_2 = librosa.istft(X_ear, win_length=Fs, hop_length=ol, window="hann")
    data_ear_2 = normalize(data_ear_2)
    sf.write("ear_filtered.wav", data_ear_2, samplerate)
    data_throat_2 = librosa.istft(X_throat, win_length=Fs, hop_length=ol, window="hann")
    data_throat_2 = normalize(data_throat_2)
    sf.write("throat_filtered.wav", data_throat_2, samplerate)

    #体内音への重み付け
    data_2_num = min(len(data_air_2), len(data_ear_2), len(data_throat_2))
    data_body = [0] * data_2_num
    air_amp = 0
    ear_amp = 0
    throat_amp = 0
    if air_to_body_weight >= 0.01:
        air_amp = pow(10, 0.5*math.log2(air_to_body_weight))
    if ear_to_body_weight >= 0.01:
        ear_amp = pow(10, 0.5*math.log2(ear_to_body_weight))
    if throat_to_body_weight >= 0.01:
        throat_amp = pow(10, 0.5*math.log2(throat_to_body_weight))
    for i in range(data_2_num):
        data_body[i] = data_air_2[i]*air_amp+data_ear_2[i]*ear_amp+data_throat_2[i]*throat_amp
    data_body = np.array(data_body)
    data_body = normalize(data_body)
    sf.write(folder+"体内音.wav", data_body, samplerate)
    rm_allsounds()


    f_body.close()

    #体内音のパラメーターの取得
    #f_myvoice = open(folder+myvoice_params)
    f_myvoice = open(myvoice_params)
    myvoice_info = f_myvoice.readlines()
    hz_num = myvoice_info[2].rfind('：')
    air_dB_start = f_border.index(int(myvoice_info[2][hz_num+1:-3]))
    air_dB_end = f_border.index(int(myvoice_info[3][hz_num+1:-3]))
    ear_dB_start = f_border.index(int(myvoice_info[4][hz_num+1:-3]))
    ear_dB_end = f_border.index(int(myvoice_info[5][hz_num+1:-3]))
    throat_dB_start = f_border.index(int(myvoice_info[6][hz_num+1:-3]))
    throat_dB_end = f_border.index(int(myvoice_info[7][hz_num+1:-3]))

    weight1_num = myvoice_info[9].rfind('：')
    #体内音を作る上での重み
    air_to_body_weight = float(myvoice_info[9][weight1_num+1:])
    ear_to_body_weight = float(myvoice_info[10][weight1_num+1:])
    throat_to_body_weight = float(myvoice_info[11][weight1_num+1:])

    weight2_num = myvoice_info[13].rfind('：')
    #自己聴取音を作る上での重み
    body_to_myvoice_weight = float(myvoice_info[13][weight2_num+1:])
    air_to_myvoice_weight = float(myvoice_info[14][weight2_num+1:])
    

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
    sf.write("air_filtered.wav", data_air_2, samplerate)
    data_ear_2 = librosa.istft(X_ear, win_length=Fs, hop_length=ol, window="hann")
    data_ear_2 = normalize(data_ear_2)
    sf.write("ear_filtered.wav", data_ear_2, samplerate)
    data_throat_2 = librosa.istft(X_throat, win_length=Fs, hop_length=ol, window="hann")
    data_throat_2 = normalize(data_throat_2)
    sf.write("throat_filtered.wav", data_throat_2, samplerate)

    #体内音への重み付け
    data_2_num = min(len(data_air_2), len(data_ear_2), len(data_throat_2))
    data_body = [0] * data_2_num
    air_amp = 0
    ear_amp = 0
    throat_amp = 0
    if air_to_body_weight >= 0.01:
        air_amp = pow(10, 0.5*math.log2(air_to_body_weight))
    if ear_to_body_weight >= 0.01:
        ear_amp = pow(10, 0.5*math.log2(ear_to_body_weight))
    if throat_to_body_weight >= 0.01:
        throat_amp = pow(10, 0.5*math.log2(throat_to_body_weight))
    for i in range(data_2_num):
        data_body[i] = data_air_2[i]*air_amp+data_ear_2[i]*ear_amp+data_throat_2[i]*throat_amp
    data_body = np.array(data_body)
    data_body = normalize(data_body)
    sf.write("body.wav", data_body, samplerate)

    #自己聴取音への重み付け
    data_myvoice = [0] * data_2_num
    body_amp = 0
    airbefore_amp = 0
    if body_to_myvoice_weight >= 0.01:
        body_amp = pow(10, 0.5*math.log2(body_to_myvoice_weight))
    if air_to_myvoice_weight >= 0.01:
        airbefore_amp = pow(10, 0.5*math.log2(air_to_myvoice_weight))
    for i in range(data_2_num):
        data_myvoice[i] = data_body[i]*body_amp+data_air[i]*airbefore_amp
    data_myvoice = np.array(data_myvoice)
    data_myvoice = normalize(data_myvoice)
    sf.write(folder+"自己聴取音.wav", data_myvoice, samplerate)
    rm_allsounds()

    f_myvoice.close()
