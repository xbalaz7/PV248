import sys
import wave
import struct
import numpy

def solve(file):  
    # Number of audio channels
    channels = file.getnchannels()    
    # Sampling frequency
    frame_rate = file.getframerate()
    # Number of frames
    frames_number = file.getnframes()
    # Read frames
    frames = file.readframes(frames_number)

    file.close()

    unpacked_frames = struct.unpack("%dh" % frames_number * channels, frames)
    
    del frames
    
    unpacked_frames = list(unpacked_frames)
    
    if channels == 2:
        mono = []
        for i in range(0, len(unpacked_frames), 2):
            tmp = (unpacked_frames[i] / 2) + (unpacked_frames[i + 1] / 2)
            mono.append(tmp)
        unpacked_frames = mono
    
    min_peak = sys.float_info.max 
    max_peak = sys.float_info.min 

    for i in range(0, len(unpacked_frames), frame_rate):
        window = unpacked_frames[i:i + frame_rate]
        
        if len(window) < frame_rate:
           break
        
        amplitudes = numpy.abs(numpy.fft.rfft(window))        
        average = numpy.average(amplitudes)
        
        peaks = numpy.argwhere(amplitudes >= 20* average)
        
        if len(peaks) > 0:                    
            if numpy.min(peaks) < min_peak: min_peak = numpy.min(peaks)               
            if numpy.max(peaks) > max_peak: max_peak = numpy.max(peaks)   

    if min_peak != sys.float_info.max  and max_peak != sys.float_info.min:
       print("low: " + str(min_peak) + ", high: " + str(max_peak))
    else:
       print("no peaks")

def main(argv):
    file = wave.open(sys.argv[1], 'r')    
    solve(file)

if __name__ == "__main__":
    main(sys.argv[1:])
