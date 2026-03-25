# Транскрипция аудио/видео

Скрипт для автоматической транскрипции аудио и видео файлов с поддержкой разделения по спикерам.

Использует [faster-whisper](https://github.com/SYSTRAN/faster-whisper) для транскрипции и [pyannote.audio](https://github.com/pyannote/pyannote-audio) для диаризации (определения спикеров).

---

## Установка

### 1. Установить ffmpeg

```bash
brew install ffmpeg
```

> Если `brew` не установлен: [brew.sh](https://brew.sh)

### 2. Скачать скрипт

```bash
cd ~
git clone https://github.com/kostyasmirnov/transcribe.git
```

Если папка `transcribe` уже существует:

```bash
rm -rf ~/transcribe
git clone https://github.com/kostyasmirnov/transcribe.git
```

### 3. Создать виртуальное окружение и установить зависимости

```bash
python3 -m venv ~/transcribe-env
~/transcribe-env/bin/pip install --upgrade pip
~/transcribe-env/bin/pip install faster-whisper "pyannote.audio>=3.1" torchaudio
```

> Обновление pip обязательно — старая версия может некорректно устанавливать пакеты.

### 4. Hugging Face токен (для диаризации `--diarize`)

1. Зарегистрируйтесь на [huggingface.co](https://huggingface.co) и получите токен в [настройках](https://huggingface.co/settings/tokens)
2. Примите условия использования моделей:
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
3. Добавьте токен в `~/.zshrc`:

```bash
echo 'export HF_TOKEN=hf_ваш_токен_здесь' >> ~/.zshrc
source ~/.zshrc
```

Проверить что токен подхватился:

```bash
echo $HF_TOKEN
```

---

## Использование

### Базовая команда

```bash
~/transcribe-env/bin/python ~/transcribe/transcribe.py /путь/к/файлу
```

> Если в пути есть пробелы — обязательно берите путь в кавычки.

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
~/transcribe-env/bin/python ~/transcribe/transcribe.py "/Users/имя/Movies/2026-03-12 16-29-21.mov" --diarize -o ~/Desktop/результат.txt -l ru
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

---

## Решение проблем

**`TypeError: from_pretrained() got an unexpected keyword argument 'token'`**

Устарела версия `pyannote.audio`. Обновить:
```bash
~/transcribe-env/bin/pip install --upgrade pyannote.audio
```

**`No such file or directory` для файла который существует**

Проверьте — нет ли пробела в конце пути. Путь к файлу обязательно в кавычках:
```bash
... "/путь/к/файлу.mov" ...
```

**`HF_TOKEN` не найден при диаризации**

```bash
echo $HF_TOKEN  # проверить
source ~/.zshrc  # перезагрузить переменные
```
