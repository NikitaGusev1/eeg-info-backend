import json
import sys
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import grey_erosion, grey_dilation

def detect_eeg_peaks(signals, start_minute, duration_minutes=1, morphological_distance_samples=1280):
    # Function to trim the signal based on start minute and duration
    def trim_signal(signal, sampling_frequency, start_minute, duration_minutes):
        start_index = int(start_minute * 60 * sampling_frequency)
        end_index = int((start_minute + duration_minutes) * 60 * sampling_frequency)
        return signal[start_index:end_index]

    # Function for opening operation
    def opening_operation(signal, distance):
        erosion_result = grey_erosion(signal, size=distance)
        dilation_result = grey_dilation(erosion_result, size=distance)
        return dilation_result

    # Function for closing operation
    def closing_operation(signal, distance):
        dilation_result = grey_dilation(signal, size=distance)
        erosion_result = grey_erosion(dilation_result, size=distance)
        return erosion_result

    # Function for average OC/CO operation
    def average_occo(signal, distance):
        opening_result = opening_operation(signal, distance)
        closing_result = closing_operation(signal, distance)
        occo_result = (opening_result + closing_result) / 2
        return occo_result

    # Function to apply the filter and calculate the threshold
    def apply_filter(signal, morphological_distance_samples, sampling_frequency):
        occo_result = average_occo(signal, distance=morphological_distance_samples)
        filtered_signal = np.abs(signal) - np.abs(occo_result)

        # Calculate the threshold based on the formula described in the passage
        median_background_activity = np.median(filtered_signal)
        threshold = 2.0 * median_background_activity

        return filtered_signal, threshold

    total_peaks_per_minute = []

    for signal_data in signals:
        if "signal" not in signal_data or "samplingFrequency" not in signal_data:
            raise ValueError("Missing required fields in signal data")

        signal = signal_data["signal"]
        sampling_frequency = signal_data["samplingFrequency"]

        trimmed_signal = trim_signal(signal, sampling_frequency, start_minute, duration_minutes)
        filtered_signal, threshold = apply_filter(trimmed_signal, morphological_distance_samples, sampling_frequency)

        # Count the peaks above the threshold with width and prominence criteria
        detected_peaks_indices, _ = find_peaks(filtered_signal, height=threshold, width=5, prominence=30)

        total_peaks_per_minute.append({
            "minute": start_minute,
            "total_peaks": len(detected_peaks_indices)
        })

        # Update start_minute for the next iteration
        start_minute += duration_minutes

    result = {
        "total_peaks_per_minute": total_peaks_per_minute,
    }

    return result

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())

        if "signals" not in input_data:
            raise ValueError("Missing required fields in input data")

        signals = input_data["signals"]
        start_minute = input_data.get("start_minute", 1)
        duration_minutes = input_data.get("duration_minutes", 1)

        # Set the fixed number of samples for morphological distance
        morphological_distance_samples = 1280

        result = detect_eeg_peaks(signals, start_minute=start_minute, duration_minutes=duration_minutes, morphological_distance_samples=morphological_distance_samples)

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
