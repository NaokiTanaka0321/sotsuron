import os
import subprocess
import sys
import glob
import librosa
import numpy as np
from nnmnkwii.metrics import melcd
import pyworld
import pysptk as sptk
from dtw import dtw
import soundfile as sf

args=sys.argv
if len(args) != 3:
    print("python3 mcd.py [input wavfile1] [input wavfile2]")
    sys.exit()

else:
    sr = 16000
    wav1, _ = librosa.load(sys.argv[1], sr=sr, mono=True)
    wav2, _ = librosa.load(sys.argv[2], sr=sr, mono=True)
    wav1 = librosa.effects.remix(wav1, intervals=librosa.effects.split(wav1))
    wav2 = librosa.effects.remix(wav2, intervals=librosa.effects.split(wav2))
    wav1 = wav1.astype(np.float64)
    f0_1, timeaxis_1 = pyworld.harvest(wav1, sr)
    sp1 = pyworld.cheaptrick(wav1, f0_1, timeaxis_1, sr)    
    wav2 = wav2.astype(np.float64)
    f0_2, timeaxis_2 = pyworld.harvest(wav2, sr)
    sp2 = pyworld.cheaptrick(wav2, f0_2, timeaxis_2, sr)
    # mel-cepstrum
    mgc1 = sptk.sp2mc(sp1, 24, 0.42)
    mgc2 = sptk.sp2mc(sp2, 24, 0.42)
    print("mel-cep")
    # dtw
    dist, cost, acc_cost, path = dtw(mgc1, mgc2, dist=lambda x, y: np.linalg.norm(x[1:]-y[1:]))
    dtw_mgc1 = mgc1[path[0]]
    dtw_mgc2 = mgc2[path[1]]
    print("dtw")

    # mcd
    result = melcd(dtw_mgc1, dtw_mgc2)
    print("result")
    print(result)
