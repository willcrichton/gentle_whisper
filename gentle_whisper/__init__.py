import json
import subprocess as sp
import sys
import tempfile
from pathlib import Path

import docker
import whisper
from intervaltree import IntervalTree

GENTLE_INTERIOR_PORT = 8765
GENTLE_EXTERIOR_PORT = 8765


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Transcriber:
    def __init__(self):
        eprint("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        client = docker.from_env()

        eprint("Starting Gentle container...")
        ports = {f"{GENTLE_INTERIOR_PORT}/tcp": GENTLE_EXTERIOR_PORT}
        self.gentle_container = client.containers.run(
            "lowerquality/gentle", detach=True, ports=ports
        )

    def __del__(self):
        eprint("Killing Gentle container...")
        self.gentle_container.kill()

    def run_whisper(self, path):
        eprint("Running Whisper...")
        return self.whisper_model.transcribe(path)

    def run_gentle(self, path, text):
        eprint("Running Gentle...")
        with tempfile.NamedTemporaryFile() as f:
            f.write(text.encode())
            f.flush()

            cmd = f'curl -s -F "audio=@{path}" -F "transcript=@{f.name}" "http://localhost:{GENTLE_EXTERIOR_PORT}/transcriptions?async=false"'
            gentle_raw_output = sp.check_output(cmd, shell=True).decode("utf-8")
            gentle_output = json.loads(gentle_raw_output)
            return gentle_output

    def to_itree(self, text, aligned):
        cur_time = 0
        cur_idx = 0

        segments = IntervalTree()
        for entry in aligned:
            word = entry["word"]
            word_time_start = entry["start"]
            word_time_end = entry["end"]
            word_idx_start = text[cur_idx:].find(word) + cur_idx
            word_idx_end = word_idx_start + len(word)

            if abs(cur_time - word_time_start) > 0.001:
                segments[cur_time:word_time_start] = text[cur_idx:word_idx_start]

            segments[word_time_start:word_time_end] = text[word_idx_start:word_idx_end]

            cur_idx = word_idx_end
            cur_time = word_time_end

        return segments

    def transcribe(self, path: any):
        path = Path(path).resolve()
        if not path.exists():
            raise Exception(f"Path does not exist: {path}")
        path = str(path)

        whisper_output = self.run_whisper(path)
        text = whisper_output["text"]

        gentle_output = self.run_gentle(path, text)
        aligned = gentle_output["words"]

        return self.to_itree(text, aligned)


def transcribe(path):
    return Transcriber().transcribe(path)


def main():
    if len(sys.argv) == 1:
        raise Exception("You must provide a path to the video or audio to transcribe.")

    transcription = transcribe(sys.argv[1])
    intervals = [
        {"start": intvl.begin, "end": intvl.end, "text": intvl.data}
        for intvl in sorted(transcription)
    ]
    print(json.dumps(intervals, indent=4))


if __name__ == "__main__":
    main()
