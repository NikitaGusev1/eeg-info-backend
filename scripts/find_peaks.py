import json
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import grey_erosion, grey_dilation

def detect_eeg_peaks(signal, sampling_frequency=256.0):
    # Define a function to generate parabola-shaped structuring elements
    def generate_parabola_structuring_elements(signal):
        # Calculate the widths of arcs
        widths, _ = find_peaks(signal, distance=10)  # Adjust distance as needed

        # Calculate heights of the structuring elements
        h1 = np.median(np.abs(signal))
        h2 = 2 * np.median(np.abs(signal))

        # Calculate widths of the structuring elements
        w1 = 0.5 * np.median(widths)
        w2 = 1.5 * np.median(widths)

        # Calculate parameters for the parabolas
        b1 = np.median(np.abs(signal))
        b2 = np.median(np.abs(signal))
        a1 = np.median(np.abs(signal)) / (0.5 * np.median(widths))
        a2 = np.median(np.abs(signal)) / (1.5 * np.median(widths))

        # Define the parabola-shaped structuring elements
        g1 = lambda t: a1 * t**2 + b1
        g2 = lambda t: a2 * t**2 + b2

        return g1, g2

    # Define a function for opening operation
    def opening_operation(signal, structuring_element):
        erosion_result = grey_erosion(signal, structure=np.array(structuring_element))
        dilation_result = grey_dilation(erosion_result, structure=np.array(structuring_element))
        return dilation_result

    # Define a function for closing operation
    def closing_operation(signal, structuring_element):
        dilation_result = grey_dilation(signal, structure=np.array(structuring_element))
        erosion_result = grey_erosion(dilation_result, structure=np.array(structuring_element))
        return erosion_result

    # Define a function for average OC/CO operation
    def average_occo(signal, structuring_element):
        opening_result = opening_operation(signal, structuring_element)
        closing_result = closing_operation(signal, structuring_element)
        occo_result = (opening_result + closing_result) / 2
        return occo_result

    # Define a function to apply the filter
    def apply_filter(signal, structuring_element):
        occo_result = average_occo(signal, structuring_element)
        filtered_signal = signal - occo_result
        return filtered_signal

    # Define a function to calculate the threshold
    def calculate_threshold(filtered_signal):
        extrema_amplitudes = np.abs(filtered_signal[find_peaks(filtered_signal)[0]])
        threshold = 8 * np.median(extrema_amplitudes)
        return threshold

    # Generate parabola-shaped structuring elements
    g1, g2 = generate_parabola_structuring_elements(signal)

    # Apply the filter to the original EEG signal
    filtered_signal = apply_filter(signal, g1)

    # Calculate the threshold
    threshold = calculate_threshold(filtered_signal)

    # Count the peaks above the threshold
    detected_peaks = len(find_peaks(filtered_signal, height=threshold)[0])

    result = {
        "peaks_count": detected_peaks,
        "debug_info": "Additional debug information if needed",
    }

    print(json.dumps(result))

if __name__ == "__main__":
    # Read input data from standard input
    input_data = json.loads(input())
    signal = input_data.get("signal", [])
    sampling_frequency = input_data.get("samplingFrequency", 256.0)  # Default to 256.0 if not provided

    # Call the function with the provided parameters
    detect_eeg_peaks(signal, sampling_frequency)
