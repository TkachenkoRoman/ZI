#!/usr/bin/env python
import pyaudio
from wave import struct as wave_struct
from numpy import blackman
from numpy.fft import rfft
from numpy import array
import numpy
import sys, time, os
import curses


CHUNK = 2000 # Chunk of audio input to consider
RATE = 44100 # Recording rate
WINDOW = blackman(CHUNK) # Using blackman window. For more information see
SAMPLE_SIZE = 8
                # Number of data points to average over. This is used for 2 things
                # 1. Reducing noise between subsequent string strokes
                # 2. We don't output too many values which might confuse the user



try: # Windows?
    import msvcrt
    def kbfunc():
        return ord(msvcrt.getch()) if msvcrt.kbhit() else 0
except: # Unix/Mac
    import select
    def kbfunc():
        inp, out, err = select.select([sys.stdin], [], [], 0.001) # 0.1 second delay
        return sys.stdin.readline() if sys.stdin in inp else 0

class Decoder:

    term_width = 80 # Stores the character width of the terminal

    def __init__(self):
        self.term_width = int(168)
        self.freq_list = []

    def _open_audio(self):
        """ Opens the audio device for listening """
        audio = pyaudio.PyAudio()
        stream = None
        while True: # Fix for Mac OS
            stream = audio.open(format = pyaudio.paInt16,
                                channels = 1,
                                rate = RATE,
                                input = True,
                                output = False, # TODO
                                frames_per_buffer = CHUNK)
            try:
                # On Mac OS, the first call to stream.read usually fails
                data = stream.read(CHUNK)
                break
            except:
                stream.close()
        self.audio = audio
        self.stream = stream



    def _loop(self):
        """ This loop runs until the user hits the Enter key """
        last_n = [0] * SAMPLE_SIZE # Stores the values of the last N frequencies.
                                   # This list is used as an array
        curpos = 0   # Stores the index to the array where we will store our next value
        last_avg = 1 # Stores the average of the last N set of samples.
                     # This value will be compared to the current average to detect
                     # the change in note
        # play stream and find the frequency of each chunk

        while True:
            perfect_cnt = 0
            data = self.stream.read(CHUNK)
            # unpack the data and times by the hamming window
            indata = array(wave_struct.unpack("%dh"%(len(data)/2), data))*WINDOW

            # Take the fft and square each value
            fftData=abs(rfft(indata))**2
            # find the maximum
            which = fftData[1:].argmax() + 1
            # use quadratic interpolation around the max
            thefreq = 0
            if which != len(fftData)-1:
                y0, y1, y2 = numpy.log(fftData[which-1:which+2:])
                x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
                # find the frequency and output it
                thefreq = (which+x1)*RATE/CHUNK
            else:
                thefreq = which*RATE/CHUNK
            # Store this freq in an array
            last_n[curpos] = int(thefreq)
            curpos += 1
            if curpos == SAMPLE_SIZE:
                curpos = 0
            this_avg = sum(last_n) / SAMPLE_SIZE # Compute the average
            print(thefreq)
            self.freq_list.append(thefreq)




    def _close_audio(self):
        """ Call this function at the end """
        self.stream.close()
        self.audio.terminate()

    def decode(self):
        self._open_audio()
        self._loop()
        self._close_audio()




if __name__ == '__main__':
    u = Decoder()
    u.decode()
