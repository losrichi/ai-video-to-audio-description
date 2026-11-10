"""Offline speech synthesis with eSpeak or pyttsx3, no external cloud service."""
from pathlib import Path
import shutil
import subprocess


class SpeechSynthesisError(RuntimeError):
    pass


def synthesize(text: str, target: str | Path, language: str = "en", rate: int = 145) -> Path:
    if not text.strip():
        raise SpeechSynthesisError("Cannot synthesize an empty narration")
    if language not in ("en", "fr"):
        raise ValueError("language must be en or fr")
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    engine = shutil.which("espeak-ng") or shutil.which("espeak")
    if engine:
        # Using separate argv avoids shell command injection; UTF-8 text is passed via stdin.
        result = subprocess.run([engine, "-v", language, "-s", str(rate), "-w", str(target), "--stdin"],
                                input=text, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise SpeechSynthesisError(f"eSpeak failed: {result.stderr.strip()}")
    else:
        try:
            import pyttsx3
            synthesizer = pyttsx3.init()
            synthesizer.setProperty("rate", rate)
            voices = synthesizer.getProperty("voices")
            for voice in voices:
                languages = str(getattr(voice, "languages", "")).lower()
                if language in languages:
                    synthesizer.setProperty("voice", voice.id)
                    break
            synthesizer.save_to_file(text, str(target))
            synthesizer.runAndWait()
            synthesizer.stop()
        except Exception as exc:
            raise SpeechSynthesisError(
                "No working local TTS engine. Install eSpeak (Linux) or pyttsx3, "
                "or rerun with --no-audio."
            ) from exc
    if not target.exists() or target.stat().st_size < 100:
        raise SpeechSynthesisError(f"The speech engine did not produce a valid WAV: {target}")
    return target
