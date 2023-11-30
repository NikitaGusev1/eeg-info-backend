import json
import sys
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
from scipy.ndimage import grey_erosion, grey_dilation

def detect_eeg_peaks(signals):
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
        occo_result = average_occo(signal, distance)
        filtered_signal = signal - occo_result
        return filtered_signal

    total_peaks = 0

    for signal_data in signals:
        if "signal" not in signal_data or "samplingFrequency" not in signal_data:
            raise ValueError("Missing required fields in signal data")

        signal = signal_data["signal"]
        sampling_frequency = signal_data["samplingFrequency"]

        # Apply the filter to the original EEG signal
        filtered_signal = apply_filter(signal, distance=len(signal)//10, sampling_frequency=sampling_frequency)

        # Calculate the threshold
        threshold = 8 * np.median(np.abs(filtered_signal[find_peaks(filtered_signal)[0]]))

        # Count the peaks above the threshold with width and prominence criteria
        detected_peaks_indices, _ = find_peaks(filtered_signal, height=threshold, width=40, prominence=260)

        total_peaks += len(detected_peaks_indices)

    result = {
        "total_peaks": total_peaks,
    }

    return result

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())

        if "signals" not in input_data:
            raise ValueError("Missing required fields in input data")

        signals = input_data["signals"]

        result = detect_eeg_peaks(signals)

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
