import json
import sys
import numpy as np
from scipy.ndimage import grey_erosion, grey_dilation
from scipy.signal import find_peaks, firwin, lfilter

def apply_structuring_element(signal, a, b):
    signal_array = np.array(signal)
    return a * signal_array**2 + b

def apply_fir_filter(signal, sampling_frequency, cutoff_frequency=30.0):
    nyquist = 0.5 * sampling_frequency
    num_taps = 101  # Adjust the number of taps as needed
    cutoff = cutoff_frequency / nyquist
    fir_coefficients = firwin(num_taps, cutoff, window='hamming')
    filtered_signal = lfilter(fir_coefficients, 1.0, signal)
    return filtered_signal

def calculate_threshold(signal):
    # Find the indices of extrema (peaks and troughs)
    diff_signal = np.diff(signal)
    extrema_up = np.where(diff_signal > 0)[0] + 1  # Add 1 to get the correct index for peaks
    extrema_down = np.where(diff_signal < 0)[0] + 1  # Add 1 to get the correct index for troughs
    extrema = np.concatenate((extrema_up, extrema_down))

    # Ensure extrema indices are within the valid range
    extrema = extrema[(extrema > 0) & (extrema < len(signal) - 1)]

    # Calculate the average value of the absolute extrema
    avg_extrema = np.mean(np.abs(signal[extrema]))

    # Calculate the threshold as 8 times the average of the absolute extrema
    threshold = 8 * avg_extrema

    return threshold

def detect_peaks(eeg_signal, sampling_frequency, duration_minutes=1, open_size=5, close_size=5):
    # Constants for structuring elements
    a1, b1 = 1.0, 1.0
    a2, b2 = 1.0, 1.0

    # Apply the structuring elements to the original signal
    g1_signal = apply_structuring_element(eeg_signal, a1, b1)
    g2_signal = apply_structuring_element(eeg_signal, a2, b2)

    # Apply FIR filter to the signals
    g1_signal_filtered = apply_fir_filter(g1_signal, sampling_frequency)
    g2_signal_filtered = apply_fir_filter(g2_signal, sampling_frequency)

    # Apply opening and closing operations to the filtered signals
    opened_g1_signal = grey_dilation(grey_erosion(g1_signal_filtered, size=(open_size,)), size=(open_size,))
    closed_g2_signal = grey_erosion(grey_dilation(g2_signal_filtered, size=(close_size,)), size=(close_size,))

    # Calculate the average of the two signals
    averaged_signal = (opened_g1_signal + closed_g2_signal) / 2.0

    # Find peaks using the calculated threshold
    peaks, _ = find_peaks(averaged_signal, height=calculate_threshold(averaged_signal))
    peaks_count = len(peaks)

    result = {
        "peaks_count": peaks_count,
        "debug_info": {}  # Add any additional debug information as needed
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
