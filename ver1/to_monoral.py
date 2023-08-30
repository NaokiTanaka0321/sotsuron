from pydub import AudioSegment
import sys

if __name__ == '__main__':
    args= sys.argv
    if len(args) != 3:
        print('python3 to_monoral.py before.wav after.wav')
    else:
        sound = AudioSegment.from_wav(args[1])
        sound = sound.set_channels(1)
        sound.export(args[2], format="wav")
