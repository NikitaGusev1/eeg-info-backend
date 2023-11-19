import json
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
from scipy.ndimage import grey_erosion, grey_dilation

def detect_peaks_morphological(eeg_data, threshold=0.5, window_size=11):
    # Apply a bandpass filter to the EEG signal
    filtered_eeg = bandpass_filter(eeg_data)

    # Apply closing operation to smooth the signal from above
    smoothed_signal = closing_operation(filtered_eeg, window_size)

    # Apply erosion to further shape the signal
    eroded_signal = erosion_operation(smoothed_signal, window_size)

    # Apply dilation to enhance peaks
    dilated_signal = dilation_operation(eroded_signal, window_size)

    # Find peaks in the enhanced signal
    peaks, _ = find_peaks(dilated_signal, height=threshold)

    return peaks.tolist()

def bandpass_filter(eeg_data, lowcut=0.5, highcut=50.0, fs=1000.0, order=4):
    # Design a bandpass filter
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')

    # Apply the bandpass filter using filtfilt for zero-phase filtering
    filtered_data = filtfilt(b, a, eeg_data)

    return filtered_data

def closing_operation(signal, window_size):
    # Apply closing operation to smooth the signal from above
    struct_element = np.ones(window_size)
    smoothed_signal = filtfilt(struct_element, 1, signal)

    return smoothed_signal

def erosion_operation(signal, window_size):
    # Apply erosion operation to shape the signal
    eroded_signal = grey_erosion(signal, size=window_size)

    return eroded_signal

def dilation_operation(signal, window_size):
    # Apply dilation operation to enhance peaks
    dilated_signal = grey_dilation(signal, size=window_size)

    return dilated_signal

if __name__ == "__main__":
    # Read input from Node.js
    input_data = json.loads(input())

    # Process EEG data and detect peaks
    result = detect_peaks_morphological(input_data)

    # Send the result back to Node.js
    print(json.dumps(result))
