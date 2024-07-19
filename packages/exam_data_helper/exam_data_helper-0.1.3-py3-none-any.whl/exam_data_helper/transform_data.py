import numpy as np
from scipy.io import wavfile
from typing import Tuple


def load_wav_file(file_path: str) -> Tuple[int, np.ndarray]:
    """
    Load a .wav file and return the sampling rate and data as a NumPy array.

    Args:
    - file_path (str): Path to the .wav file.

    Returns:
    - Tuple[int, np.ndarray]: Sampling rate and the audio data as a NumPy array.
    """
    try:
        sampling_rate, data = wavfile.read(file_path)
        return sampling_rate, data
    except Exception as e:
        raise ValueError(f"An error occurred while loading the .wav file: {e}")


# def load_wav_file_return_audio_buffer_and_sampling_rate(file_path: str) -> Tuple[bytes, int]:
#     """
#     Load a .wav file and return the audio data as a buffer and the sampling rate.

#     Args:
#     - file_path (str): Path to the .wav file.

#     Returns:
#     - Tuple[bytes, int]: Audio data as a buffer and the sampling rate.
#     """
#     try:
#         sampling_rate, data = wavfile.read(file_path)
#         audio_buffer = data.tobytes()
#         return audio_buffer, sampling_rate
#     except Exception as e:
#         raise ValueError(f"An error occurred while loading the .wav file: {e}")
