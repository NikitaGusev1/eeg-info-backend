import json
import sys
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
from scipy.ndimage import grey_erosion, grey_dilation

def detect_eeg_peaks(signals, start_minute=4, duration_minutes=1):
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

        # Calculate the start and end indices for the specified duration
        start_index = int(start_minute * 60 * sampling_frequency)
        end_index = start_index + int(duration_minutes * 60 * sampling_frequency)

        # Trim the signal to the specified duration
        trimmed_signal = signal[start_index:end_index]

        # Apply the filter to the trimmed EEG signal
        filtered_signal = apply_filter(trimmed_signal, distance=len(trimmed_signal)//10, sampling_frequency=sampling_frequency)

        # Calculate the threshold
        threshold = 8 * np.median(np.abs(filtered_signal[find_peaks(filtered_signal)[0]]))

        # Count the peaks above the threshold with width and prominence criteria
        detected_peaks_indices, _ = find_peaks(filtered_signal, height=threshold, width=5, prominence=249)

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
        start_minute = input_data.get("startMinute", 1)
        duration_minutes = input_data.get("durationMinutes", 1)

        result = detect_eeg_peaks(signals, start_minute, duration_minutes)

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
