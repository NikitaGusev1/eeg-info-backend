import json
import sys
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import grey_erosion, grey_dilation

def detect_eeg_peaks(signals, duration_minutes=1):
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
    def apply_filter(signal, distance, sampling_frequency):
        occo_result = average_occo(signal, distance)
        filtered_signal = signal - occo_result
        # Calculate the threshold based on the formula
        threshold = 8 * np.median(np.abs(filtered_signal[find_peaks(filtered_signal)[0]]))
        return filtered_signal, threshold

    results = []

    for signal_data in signals:
        if "signal" not in signal_data or "samplingFrequency" not in signal_data:
            raise ValueError("Missing required fields in signal data")

        signal = signal_data["signal"]
        sampling_frequency = signal_data["samplingFrequency"]

        # Calculate the number of minutes in the signal
        total_minutes = int(len(signal) / (60 * sampling_frequency))

        # Iterate over each minute
        for minute in range(total_minutes):
            # Trim the signal for the current minute
            trimmed_signal = trim_signal(signal, sampling_frequency, minute, duration_minutes)

            # Apply the filter and calculate the threshold
            filtered_signal, threshold = apply_filter(trimmed_signal, distance=len(trimmed_signal)//10, sampling_frequency=sampling_frequency)

            # Count the peaks above the threshold with width and prominence criteria
            detected_peaks_indices, _ = find_peaks(filtered_signal, height=threshold, width=3, prominence=237)

            # Append the result for the current minute
            results.append({
                "minute": minute + 1,  # Adding 1 to make minutes 1-indexed
                "peaks_count": len(detected_peaks_indices)
            })

    return results

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())

        if "signals" not in input_data:
            raise ValueError("Missing required fields in input data")

        signals = input_data["signals"]
        duration_minutes = input_data.get("duration_minutes", 1)

        result = detect_eeg_peaks(signals, duration_minutes=duration_minutes)

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
