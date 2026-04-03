#!/usr/bin/env python3
"""
Транскрипция аудио/видео с разделением по спикерам.
Использует faster-whisper (транскрипция) + pyannote.audio (диаризация).
"""

import argparse
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=RuntimeWarning, module="faster_whisper")

from faster_whisper import WhisperModel


def transcribe_simple(audio_path: str, model_size: str = "medium", language: str = None):
    """Транскрипция без разделения по спикерам."""
    print(f"Загрузка модели '{model_size}'...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"Транскрибирую: {audio_path}")
    segments, info = model.transcribe(audio_path, language=language, beam_size=5)

    print(f"Язык: {info.language} (вероятность: {info.language_probability:.2f})")
    print("-" * 60)

    results = []
    for segment in segments:
        line = f"[{_fmt_time(segment.start)} -> {_fmt_time(segment.end)}] {segment.text.strip()}"
        print(line)
        results.append({"start": segment.start, "end": segment.end, "text": segment.text.strip()})

    return results, info


def transcribe_with_diarization(
    audio_path: str,
    model_size: str = "medium",
    language: str = None,
    hf_token: str = None,
    num_speakers: int = None,
):
    """Транскрипция с разделением по спикерам."""
    from pyannote.audio import Pipeline

    token = hf_token or os.environ.get("HF_TOKEN")
    if not token:
        print("ОШИБКА: Для диаризации нужен Hugging Face токен.")
        print("Установите переменную HF_TOKEN или передайте --hf-token.")
        print("Получить токен: https://huggingface.co/settings/tokens")
        print()
        print("Также нужно принять условия моделей:")
        print("  https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("  https://huggingface.co/pyannote/segmentation-3.0")
        sys.exit(1)

    # 1. Транскрипция
    print(f"Загрузка whisper модели '{model_size}'...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"Транскрибирую: {audio_path}")
    segments_raw, info = model.transcribe(audio_path, language=language, beam_size=5)
    segments_list = list(segments_raw)

    print(f"Язык: {info.language} (вероятность: {info.language_probability:.2f})")

    # 2. Диаризация
    print("Загрузка модели диаризации...")
    os.environ["HF_TOKEN"] = token
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")

    print("Загрузка аудио для диаризации...")
    import subprocess
    import tempfile
    import torchaudio

    # Конвертируем в WAV через ffmpeg (soundfile не поддерживает все форматы)
    tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_wav.close()
    subprocess.run(
        ["ffmpeg", "-y", "-i", audio_path, "-ac", "1", "-ar", "16000", tmp_wav.name],
        capture_output=True,
    )
    waveform, sample_rate = torchaudio.load(tmp_wav.name)
    os.unlink(tmp_wav.name)

    print("Определяю спикеров...")
    diarization_params = {}
    if num_speakers:
        diarization_params["num_speakers"] = num_speakers
    audio_input = {"waveform": waveform, "sample_rate": sample_rate}
    result = pipeline(audio_input, **diarization_params)
    # pyannote 4.x возвращает DiarizeOutput, извлекаем Annotation
    diarization = getattr(result, "speaker_diarization", result)

    # 3. Совмещение результатов
    print("-" * 60)

    for segment in segments_list:
        speaker = _get_speaker(diarization, segment.start, segment.end)
        line = f"[{_fmt_time(segment.start)} -> {_fmt_time(segment.end)}] {speaker}: {segment.text.strip()}"
        print(line)


def _get_speaker(diarization, seg_start: float, seg_end: float) -> str:
    """Определяет спикера для данного сегмента по максимальному перекрытию."""
    best_speaker = "Неизвестный"
    best_overlap = 0.0

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        overlap_start = max(turn.start, seg_start)
        overlap_end = min(turn.end, seg_end)
        overlap = max(0.0, overlap_end - overlap_start)

        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = speaker

    return best_speaker


def _fmt_time(seconds: float) -> str:
    """Форматирует секунды в MM:SS."""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def save_to_file(output_path: str, content: str):
    """Сохраняет результат в файл."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nРезультат сохранён: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Транскрипция аудио/видео с разделением по спикерам"
    )
    parser.add_argument("audio", help="Путь к аудио/видео файлу")
    parser.add_argument(
        "--model", "-m",
        default="medium",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Размер модели Whisper (по умолчанию: medium)",
    )
    parser.add_argument(
        "--language", "-l",
        default=None,
        help="Язык аудио (ru, en, и т.д.). Если не указан — определяется автоматически",
    )
    parser.add_argument(
        "--diarize", "-d",
        action="store_true",
        help="Включить разделение по спикерам (требует HF_TOKEN)",
    )
    parser.add_argument(
        "--hf-token",
        default=None,
        help="Hugging Face токен (или установите HF_TOKEN)",
    )
    parser.add_argument(
        "--speakers", "-s",
        type=int,
        default=None,
        help="Количество спикеров (если известно заранее)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Сохранить результат в файл",
    )

    args = parser.parse_args()

    if not Path(args.audio).exists():
        print(f"Файл не найден: {args.audio}")
        sys.exit(1)

    # Перенаправляем вывод если нужно сохранить в файл
    original_stdout = sys.stdout
    output_lines = []

    if args.output:
        class Tee:
            def __init__(self):
                self.lines = []
            def write(self, text):
                original_stdout.write(text)
                self.lines.append(text)
            def flush(self):
                original_stdout.flush()

        tee = Tee()
        sys.stdout = tee

    if args.diarize:
        transcribe_with_diarization(
            args.audio,
            model_size=args.model,
            language=args.language,
            hf_token=args.hf_token,
            num_speakers=args.speakers,
        )
    else:
        transcribe_simple(
            args.audio,
            model_size=args.model,
            language=args.language,
        )

    if args.output:
        sys.stdout = original_stdout
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("".join(tee.lines))
        print(f"\nРезультат сохранён: {args.output}")


if __name__ == "__main__":
    main()
