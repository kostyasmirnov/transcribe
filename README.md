# Транскрипция аудио/видео

Скрипт для автоматической транскрипции аудио и видео файлов с поддержкой разделения по спикерам.

Использует [faster-whisper](https://github.com/SYSTRAN/faster-whisper) для транскрипции и [pyannote.audio](https://github.com/pyannote/pyannote-audio) для диаризации (определения спикеров).

---

## Требования

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/) (установить через `brew install ffmpeg`)
- Hugging Face токен — нужен только для режима `--diarize`

### Установка зависимостей

```bash
python3 -m venv ~/transcribe-env
source ~/transcribe-env/bin/activate
pip install faster-whisper pyannote.audio torchaudio
```

### Hugging Face токен (для диаризации)

1. Зарегистрируйтесь на [huggingface.co](https://huggingface.co) и получите токен в [настройках](https://huggingface.co/settings/tokens)
2. Примите условия использования моделей:
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
3. Добавьте токен в переменную окружения:

```bash
export HF_TOKEN=hf_ваш_токен_здесь
```

Чтобы не вводить каждый раз, добавьте строку выше в `~/.zshrc` или `~/.bashrc`.

---

## Использование

### Базовая команда

```bash
~/transcribe-env/bin/python ~/transcribe/transcribe.py /путь/к/файлу
```

> Если в пути есть пробелы — берите путь в кавычки.

---

## Примеры

**Простая транскрипция:**
```bash
~/transcribe-env/bin/python ~/transcribe/transcribe.py ~/Downloads/video.mp4
```

**С разделением по спикерам:**
```bash
~/transcribe-env/bin/python ~/transcribe/transcribe.py ~/Downloads/video.mp4 --diarize
```

**Сохранить результат в файл:**
```bash
~/transcribe-env/bin/python ~/transcribe/transcribe.py ~/Downloads/video.mp4 --diarize -o ~/Desktop/результат.txt
```

**Указать язык (быстрее, точнее):**
```bash
~/transcribe-env/bin/python ~/transcribe/transcribe.py ~/Downloads/video.mp4 -l ru
```

**Полный пример:**
```bash
~/transcribe-env/bin/python ~/transcribe/transcribe.py ~/Downloads/интервью.aac --diarize -l ru -m medium -o ~/Desktop/интервью.txt
```

**Файл с пробелами в имени:**
```bash
~/transcribe-env/bin/python ~/transcribe/transcribe.py "/Users/pocket/Movies/2026-03-12 16-29-21.mov" --diarize -o ~/Desktop/результат.txt -l ru
```

---

## Параметры

| Флаг | Описание |
|------|----------|
| `--diarize`, `-d` | Разделение по спикерам (требует HF_TOKEN) |
| `--language ru`, `-l ru` | Язык аудио (`ru`, `en` и т.д.). Если не указан — определяется автоматически |
| `--model small`, `-m small` | Модель Whisper: `tiny`, `base`, `small`, `medium`, `large-v3` (по умолчанию: `medium`) |
| `--output файл.txt`, `-o файл.txt` | Сохранить результат в файл |
| `--speakers 2`, `-s 2` | Указать количество спикеров заранее (повышает точность диаризации) |
| `--hf-token TOKEN` | Hugging Face токен (альтернатива переменной `HF_TOKEN`) |

---

## Модели

| Модель | Качество | Скорость |
|--------|----------|----------|
| `tiny` | низкое | очень быстро |
| `base` | удовлетворительное | быстро |
| `small` | среднее | быстро |
| `medium` | хорошее (по умолчанию) | средне |
| `large-v3` | лучшее | медленно |

---

## Поддерживаемые форматы

`mp3`, `mp4`, `m4a`, `aac`, `wav`, `flac`, `ogg`, `webm`, `mkv`, `mov`
