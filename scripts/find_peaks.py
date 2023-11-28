import json
import sys
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
from scipy.ndimage import grey_erosion, grey_dilation

def detect_eeg_peaks(signal, sampling_frequency):
    # Define a function to design a bandpass filter
    def bandpass_filter(signal, sampling_frequency, lowcut, highcut, order=4):
        nyquist = 0.5 * sampling_frequency
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        filtered_signal = filtfilt(b, a, signal)
        return filtered_signal

    # Define a function for opening operation
    def opening_operation(signal, distance):
        erosion_result = grey_erosion(signal, size=distance)
        dilation_result = grey_dilation(erosion_result, size=distance)
        return dilation_result

    # Define a function for closing operation
    def closing_operation(signal, distance):
        dilation_result = grey_dilation(signal, size=distance)
        erosion_result = grey_erosion(dilation_result, size=distance)
        return erosion_result

    # Define a function for average OC/CO operation
    def average_occo(signal, distance):
        opening_result = opening_operation(signal, distance)
        closing_result = closing_operation(signal, distance)
        occo_result = (opening_result + closing_result) / 2
        return occo_result

    # Define a function to apply the filter
    def apply_filter(signal, distance, sampling_frequency):
        # Apply bandpass filter to focus on the 49-51 Hz frequency range
        filtered_signal = bandpass_filter(signal, sampling_frequency, 49, 51)
        occo_result = average_occo(filtered_signal, distance)
        filtered_signal = signal - occo_result
        return filtered_signal

    # Define a function to calculate the threshold
    def calculate_threshold(filtered_signal):
        extrema_amplitudes = np.abs(filtered_signal[find_peaks(filtered_signal)[0]])
        threshold = 8 * np.median(extrema_amplitudes)
        return threshold

    # Apply the filter to the original EEG signal
    filtered_signal = apply_filter(signal, distance=len(signal)//10, sampling_frequency=sampling_frequency)

    # Calculate the threshold
    threshold = calculate_threshold(filtered_signal)

    # Count the peaks above the threshold with width and prominence criteria
    detected_peaks_indices, _ = find_peaks(filtered_signal, height=threshold, width=40, prominence=237)

    detected_peaks_count = len(detected_peaks_indices)

    result = {
        "peaks_count": detected_peaks_count,
        # "peaks_array": detected_peaks_indices.tolist(),
    }

    return result

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())

        if "signal" not in input_data or "samplingFrequency" not in input_data:
            raise ValueError("Missing required fields in input data")

        signal = input_data["signal"]
        sampling_frequency = input_data["samplingFrequency"]

        result = detect_eeg_peaks(signal, sampling_frequency)

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
