"""
Utilities for handling audio voices.

ref: https://thepythoncode.com/article/convert-text-to-speech-in-python
"""

import asyncio
import os
import random

from abc import ABC
from pathlib import Path

import edge_tts
import gtts
import speech_recognition as sr

from edge_tts import VoicesManager
from pydub import AudioSegment

from artbox.base import ArtBox


def convert_mp3_to_wav(input_path: str, output_path: str) -> None:
    """Convert from mp3 to wav."""
    sound = AudioSegment.from_mp3(input_path)
    sound.export(output_path, format="wav")


class Speech(ArtBox, ABC):
    """Set of methods for handing audio voices."""


class SpeechFromTextEngineBase(Speech):
    """Set of methods for handing audio voices."""

    def convert(self) -> None:
        """Convert text to audio speech."""
        ...


class SpeechFromText(Speech):
    """Speech class will run commands according to the selected engine."""

    engine: SpeechFromTextEngineBase

    def __init__(self, *args, **kwargs) -> None:
        """Initialize Speech class."""
        super().__init__(*args, **kwargs)
        engine = self.args.get("engine", "edge-tts")

        if engine == "edge-tts":
            self.engine: SpeechFromTextEngineBase = SpeechEngineMSEdgeTTS(
                *args, **kwargs
            )
        elif engine == "gtts":
            self.engine: SpeechFromTextEngineBase = SpeechEngineGTTS(
                *args, **kwargs
            )
        else:
            raise Exception(f"Engine {engine} not found.")

    def convert(self) -> None:
        """Convert text to audio speech."""
        return self.engine.convert()


class SpeechEngineGTTS(SpeechFromTextEngineBase):
    """Google-Text-To-Speech engine."""

    def convert(self) -> None:
        """Convert text to audio speech."""
        title: str = self.args.get("title", "")
        input_path: str = self.args.get("input-path", "")
        lang: str = self.args.get("lang", "en")

        if not title:
            raise Exception("Argument `title` not given")

        if not input_path:
            raise Exception("Argument `input_path` not given")

        with open(input_path, "r") as f:
            text = f.read()

        tts = gtts.gTTS(text, lang=lang, slow=False)
        tts.save(str(self.output_path))


class SpeechEngineMSEdgeTTS(SpeechFromTextEngineBase):
    """Microsoft Edge Text-To-Speech engine."""

    async def async_convert(self) -> None:
        """Convert text to audio speech in async mode."""
        title: str = self.args.get("title", "")
        input_path: str = self.args.get("input-path", "")
        lang: str = self.args.get("lang", "en")
        rate = self.args.get("rate", "+0%")
        volume = self.args.get("volume", "+0%")
        pitch = self.args.get("pitch", "+0Hz")

        if not title:
            raise Exception("Argument `title` not given")

        if not input_path:
            raise Exception("Argument `input_path` not given")

        with open(input_path, "r") as f:
            text = f.read()

        params = {"Locale": lang} if "-" in lang else {"Language": lang}
        voices = await VoicesManager.create()
        voice_options = voices.find(Gender="Female", **params)

        communicate = edge_tts.Communicate(
            text=text,
            voice=random.choice(voice_options)["Name"],
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
        with open(self.output_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    print(f"WordBoundary: {chunk}")

    def convert(self) -> None:
        """Convert text to audio speech."""
        loop = asyncio.get_event_loop_policy().get_event_loop()
        try:
            loop.run_until_complete(self.async_convert())
        finally:
            loop.close()


class SpeechToText(Speech):
    """Speech to Text class."""

    def convert(self) -> None:
        """Recognize speech from MP# using various engines options."""
        file_path: str = str(self.input_path)

        if file_path.endswith("mp3"):
            self.convert_from_mp3()
            return

        if file_path.endswith("wav"):
            self.convert_from_wav()
            return

        raise Exception(
            "The file format is not valid. Valid types are mp3 and wav."
        )

    def convert_from_mp3(self) -> None:
        """Recognize speech from MP# using various engines options."""
        file_path: Path = self.input_path

        # Convert MP3 to WAV
        wav_path = str(file_path).replace(".mp3", ".wav")
        convert_mp3_to_wav(str(file_path), wav_path)

        self.input_path = Path(wav_path)
        self.convert_from_wav()

        # Cleanup: Remove the WAV file
        os.remove(wav_path)

    def convert_from_wav(self) -> None:
        """Recognize speech from WAVE using various engines options."""
        wav_path: str = str(self.input_path)
        output_path: str = str(self.output_path)
        language: str = self.args.get("lang", "en-US")
        engine: str = self.args.get("engine", "google")

        # Initialize recognizer
        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            kwargs = {"audio_data": audio_data, "language": language}
            try:
                if engine == "google":
                    text = recognizer.recognize_google(**kwargs)
                elif engine == "google_cloud":
                    text = recognizer.recognize_google_cloud(**kwargs)
                elif engine == "wit":
                    text = recognizer.recognize_wit(**kwargs)
                elif engine == "azure":
                    text = recognizer.recognize_azure(**kwargs)
                elif engine == "houndify":
                    text = recognizer.recognize_houndify(**kwargs)
                elif engine == "ibm":
                    text = recognizer.recognize_ibm(**kwargs)
                elif engine == "vosk":
                    text = recognizer.recognize_vosk(**kwargs)
                elif engine == "whisper":
                    text = recognizer.recognize_whisper(**kwargs)
                elif engine == "whisper-api":
                    text = recognizer.recognize_whisper_api(
                        kwargs.get("audio_data")
                    )
                else:
                    raise Exception(f"Engine '{engine}' is not supported.")
            except sr.UnknownValueError:
                raise Exception(
                    f"{engine.title()} could not understand the audio"
                )
            except sr.RequestError as e:
                raise Exception(
                    f"Could not request results from {engine.title()}; {e}"
                )

        with open(output_path, "w") as f:
            f.write(text)
