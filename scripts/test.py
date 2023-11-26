import json
import numpy as np
import subprocess

def generate_random_signal(length):
    return np.random.rand(length).tolist()

if __name__ == "__main__":
    try:
        # Generate random signal
        random_signal = generate_random_signal(308480)

        # Create input dictionary
        input_data = {
            "signal": random_signal,
            "samplingFrequency": 256  # Adjust the sampling frequency as needed
        }

        # Convert the dictionary to a JSON-formatted string
        input_json = json.dumps(input_data)

        # Run the EEG peak detection script as a separate process
        script_path = "find_peaks.py"  # Update with your script filename

        process = subprocess.Popen(["python3", script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=input_json)

        if process.returncode == 0:
            print("Script executed successfully.")
            print("Output:")
            print(stdout)
        else:
            print(f"Error executing the script. Exit code: {process.returncode}")
            print("Error output:")
            print(stderr)

    except Exception as e:
        print(json.dumps({"error": str(e)}))
