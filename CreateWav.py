import math
import wave
import struct
from interface import App
from Tkinter import *

freq0 = 600.0
freq1 = 800.0
freqBeginEnd = 400.0
data_size = 8000
fname = "WaveTest.wav"
frate = 11025.0  # framerate as a float
amp = 64000.0     # multiplier for amplitude

sine_list_x = []
def write_wav_data_element(freq):
    for x in range(data_size):
        sine_list_x.append(math.sin(2*math.pi*freq*(x/frate)))

def write_wav_data():
    wav_file = wave.open(fname, "w")
    nchannels = 1
    sampwidth = 2
    framerate = int(frate)
    nframes = data_size
    comptype = "NONE"
    compname = "not compressed"
    wav_file.setparams((nchannels, sampwidth, framerate, nframes,
    comptype, compname))
    f = open('workfile.txt', 'r')
    str = f.read()
    for i in str:
        k = ord(i)
        a = bin(k)
        for j in a:
            if j=='0':
                write_wav_data_element(freq0)
            if j=='1':
                write_wav_data_element(freq1)
    for s in sine_list_x:
    # write the audio frames to file
        wav_file.writeframes(struct.pack('h', int(s*amp/2)))
    wav_file.close()


write_wav_data()

root = Tk()
#root.geometry("320x240")
root.wm_maxsize(950, 950)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
app = App(root)
root.mainloop()
