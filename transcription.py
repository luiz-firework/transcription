import queue
import sys
import time

from google.cloud import speech

from audio_capture import AudioCapture

STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = 100  # 100ms


def get_current_time() -> int:
    """Return Current Time in MS."""
    return int(round(time.time() * 1000))


class Transcription:
    """Controls the audio capture and transcription process."""

    def __init__(self):
        self.transcription_buffer = queue.Queue()
        self._audio_stream = None
        self.closed = True

    def __enter__(self):
        self.closed = False
        self.start_time = get_current_time()
        return self

    def __exit__(self, type, value, traceback):
        """Closes the transcription stream and releases resources."""
        self.closed = True

    def transcription_generator(
        self, language_code="en-US", streaming_limit=STREAMING_LIMIT
    ):
        """opens audio stream and serves responses through a generator.

        Returns:            A generator that yields speech_api responses.
        """

        # starts bidirectional streaming from microphone input to speech API
        client = speech.SpeechClient()

        # configures general seeting for recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code=language_code,
            max_alternatives=1,
            enable_automatic_punctuation=True,
            model="latest_long",
        )

        # configures streaming settings for recognition
        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=False
        )

        # instantiate the audio input stream. The input must be in 16-bit mono format
        audio_capture = AudioCapture(SAMPLE_RATE, CHUNK_SIZE)

        # opens the audio stream and starts recording
        with audio_capture as stream:
            stream.audio_input = []
            audio_generator = stream.generator()

            # creates the requests generator that iterates through the audio chunks and sends them to the speech API
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            # sends the requests generator to the speech API and returns a responses generator
            responses = client.streaming_recognize(streaming_config, requests)

            while not stream.closed:
                if get_current_time() - self.start_time > streaming_limit:
                    stream.closed = True
                    self.closed = True
                    break

                for response in responses:
                    if not response.results:
                        continue

                    result = response.results[0]

                    if not result.alternatives:
                        continue

                    transcript = result.alternatives[0].transcript

                    current_time = get_current_time()

                    yield transcript, current_time


def main():
    print("\033[0;32m", "Transcription started, speak!\n\n Say 'exit' to stop the transcription.\n")
    with Transcription() as stream:
        for transcript, transcript_time in stream.transcription_generator():
            readable_time = time.strftime("%x %X")
            print("\033[0;33m", str(readable_time) + " - " + transcript + "\n")
            if "exit" in transcript.strip().lower():
                stream.closed = True
                break

if __name__ == "__main__":
    main()
