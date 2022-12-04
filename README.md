# gentle_whisper: automatic transcription + fine-grained time-alignment

This repository provides a Python library that combines the [Whisper](https://github.com/openai/whisper) transcription model with the
[Gentle](https://github.com/lowerquality/gentle/) forced-aligner to produce automatic transcriptions of audio with fine-grained time alignment.

## Installation

Before using `gentle_whisper`, you must have installed:
* [ffmpeg](https://github.com/FFmpeg/FFmpeg) (for Whisper)
* [Docker](https://www.docker.com/) (for Gentle)

Note that as of 12/02/2022, the Gentle Docker image does NOT work on an M1 Macbook Pro with macOS. (I don't know why.) 
I have only verified that this library works on Ubuntu 16.04 with x86 architecture CPU, and I'm guessing it will work on any x86 system.

### From source

```
git clone https://github.com/willcrichton/gentle_whisper
cd gentle_whisper
pip install -e .
```

### From PyPI

Apparently PyPI doesn't allow packages to have "direct" dependencies on Github repositories. The Whisper library is not yet published to PyPI, so for now
this library will not be published to PyPI. You have to install it from source.

## Usage

You can call the top-level script to print out a JSON object of the transcription. You can pass either an audio or video file.

```
gentle-whisper my-audio.mp3
```

You can import the library and call it from Python:

```python
from gentle_whisper import transcribe

transcription = transcribe("my-audio.mp3")
```

If you intend to transcribe many videos, you should use the `Transcriber` class to only initialize the model and Docker container once:

```python
from gentle_whisper import Transcriber

transcriber = Transcriber()
transcriber.transcribe("my-audio.mp3")
transcriber.transcribe("my-video.mp4")
# etc.
```

The `transcribe` function returns an [`IntervalTree`](https://github.com/chaimleib/intervaltree/) that maps ranges of time to text in the transcript.
