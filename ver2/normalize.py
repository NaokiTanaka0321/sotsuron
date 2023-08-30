import soundfile as sf
import sys



#正規化
def normalize(wav_path):
    data, samplerate = sf.read(wav_path)
    max_data = max(data)
    for i in range(len(data)):
        data[i] = (data[i]/max_data) * 0.5
    sf.write(wav_path, data, samplerate)


args=sys.argv
if len(args) != 2:
    print("python3 normalize.py [input wavfile1]")
    sys.exit()

else:
    wav_path = args[1]
    normalize(wav_path)
