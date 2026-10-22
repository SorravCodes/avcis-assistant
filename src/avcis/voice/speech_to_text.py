"""Local microphone capture and Whisper speech recognition."""

from __future__ import annotations

import argparse
import sys
import tempfile
import wave
from pathlib import Path

import sounddevice as sd
from faster_whisper import WhisperModel


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "models"
AUDIO_DIR = PROJECT_ROOT / "runtime_data" / "audio"

SAMPLE_FORMAT_BYTES = 2  # 16-bit audio


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Transcribe microphone input using local Whisper."
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Recording duration in seconds (between 1 and 30; default: 5).",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices without recording.",
    )
    return parser


def transcribe_from_microphone(duration: float) -> tuple[str, str]:
    """Record a short clip and return its transcript and detected language."""
    if not 1.0 <= duration <= 30.0:
        raise ValueError("Recording duration must be between 1 and 30 seconds.")

    # Load the model before recording. The first run may download model files.
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading the local Whisper tiny model...")
    print("The first run may download model files; please wait.")

    model = WhisperModel(
        "tiny",
        device="cpu",
        compute_type="int8",
        download_root=str(MODEL_DIR),
    )

    input_device = sd.query_devices(kind="input")
    sample_rate = int(input_device["default_samplerate"])

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Microphone: {input_device['name']}")
    input(f"Press Enter to record for {duration:g} seconds...")

    print("Recording now. Speak clearly.")

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )
    sd.wait()

    audio_path: Path | None = None

    try:
        # Use a temporary WAV file; delete it after transcription.
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            prefix="avcis_",
            dir=AUDIO_DIR,
            delete=False,
        ) as temporary_file:
            audio_path = Path(temporary_file.name)

        with wave.open(str(audio_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(SAMPLE_FORMAT_BYTES)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio.tobytes())

        segments, information = model.transcribe(
            str(audio_path),
            beam_size=1,
        )

        transcript = " ".join(
            segment.text.strip() for segment in segments
        ).strip()

        return transcript, information.language

    finally:
        if audio_path is not None:
            audio_path.unlink(missing_ok=True)


def main() -> int:
    """Run the speech-recognition command."""
    parser = build_parser()
    arguments = parser.parse_args()

    if not 1.0 <= arguments.duration <= 30.0:
        parser.error("--duration must be between 1 and 30 seconds.")

    if arguments.list_devices:
        try:
            print(sd.query_devices())
            return 0
        except Exception as exc:
            print(f"Could not list audio devices: {exc}", file=sys.stderr)
            return 1

    try:
        transcript, language = transcribe_from_microphone(
            arguments.duration
        )
        print(f"\nDetected language: {language}")
        print(f"Transcript: {transcript or '[No speech recognized]'}")
        return 0

    except KeyboardInterrupt:
        print("\nRecording cancelled.")
        return 130

    except Exception as exc:
        print(
            f"AVCIS speech recognition failed: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())