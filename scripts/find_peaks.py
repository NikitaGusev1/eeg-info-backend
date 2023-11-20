import json
import numpy as np
from scipy.ndimage import grey_erosion, grey_dilation
from scipy.signal import find_peaks

def detect_peaks(eeg_signal, open_size=5, close_size=5, threshold=3.0):
    def grey_opening(signal):
        eroded_signal = grey_erosion(signal, size=(open_size,))
        opened_signal = grey_dilation(eroded_signal, size=(open_size,))
        return opened_signal

    def grey_closing(signal):
        dilated_signal = grey_dilation(signal, size=(close_size,))
        closed_signal = grey_erosion(dilated_signal, size=(close_size,))
        return closed_signal

    def close_opening(signal):
        closed_signal = grey_closing(signal)
        opened_closed_signal = grey_opening(closed_signal)
        return opened_closed_signal

    def open_closing(signal):
        opened_signal = grey_opening(signal)
        closed_opened_signal = grey_closing(opened_signal)
        return closed_opened_signal

    def average_of_operators(signal, operator1, operator2):
        result1 = operator1(signal)
        result2 = operator2(signal)
        averaged_signal = (result1 + result2) / 2.0
        return averaged_signal

    filtered_signal = average_of_operators(eeg_signal, close_opening, open_closing)
    peaks, _ = find_peaks(filtered_signal, height=threshold)
    peaks_list = peaks.tolist()

    return peaks_list

if __name__ == "__main__":
    signal = json.loads(input())
    result = detect_peaks(signal)
    print(json.dumps(result))
