import json
import sys
import numpy as np
from scipy.ndimage import grey_erosion, grey_dilation
from scipy.signal import find_peaks

def detect_peaks(eeg_signal, sampling_frequency, duration_minutes=1, open_size=5, close_size=5):
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

    def calculate_threshold(signal):
        # Find the indices of extrema (peaks and troughs)
        diff_signal = np.diff(signal)
        extrema_up = np.where(diff_signal > 0)[0] + 1  # Add 1 to get the correct index for peaks
        extrema_down = np.where(diff_signal < 0)[0] + 1  # Add 1 to get the correct index for troughs
        extrema = np.concatenate((extrema_up, extrema_down))

        # Ensure extrema indices are within the valid range
        extrema = extrema[(extrema > 0) & (extrema < len(signal) - 1)]

        # Calculate the threshold as 8 times the median of the absolute values of the extrema
        threshold = 8 * np.median(np.abs(signal[extrema]))

        return threshold

    # Ensure that eeg_signal is a one-dimensional NumPy array
    eeg_signal = np.asarray(eeg_signal).ravel()

    # Calculate the number of samples corresponding to the specified duration
    window_samples = int(duration_minutes * 60 * sampling_frequency)

    # Trim the signal to the specified duration
    eeg_signal = eeg_signal[:window_samples]

    # Calculate the threshold based on the formula
    threshold = calculate_threshold(eeg_signal)

    # Apply the opening and closing operators
    filtered_signal = average_of_operators(eeg_signal, close_opening, open_closing)

    # Find peaks using the calculated threshold
    peaks, _ = find_peaks(filtered_signal, height=threshold)
    peaks_count = len(peaks)

    result = {
        "peaks_count": peaks_count,
        "threshold_used": float(threshold),
    }

    return result

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())

        # Check for required fields
        if "signal" not in input_data or "samplingFrequency" not in input_data:
            raise ValueError("Missing required fields in input data")

        signal = input_data["signal"]
        sampling_frequency = input_data["samplingFrequency"]

        result = detect_peaks(signal, sampling_frequency)

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
