import queue
from typing import Callable

import sounddevice as sd


class BackgroundRecorder:
    def __init__(
        self, rate=44100, channels=1, frames_per_buffer=1024, callback: Callable = None
    ):
        self.rate = rate
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.running = False
        self.audio_queue = queue.Queue()
        self.callback = callback

    def _callback(self, in_data, frames, time, status):
        if self.running:
            self.audio_queue.put(in_data)
            if self.callback:
                self.callback(in_data)

    def start_recording(self):
        if not self.running:
            self.running = True
            self.stream = sd.RawInputStream(
                samplerate=self.rate,
                device=1,
                channels=self.channels,
                blocksize=self.frames_per_buffer,
                callback=self._callback,
            )
            self.stream.start()
            # threading.Thread(target=self._process_audio, daemon=True).start()

    def _process_audio(self):
        while self.running:
            pass

    def get_audio_data(self):
        """获取最新的音频二进制数据"""
        if not self.audio_queue.empty():
            return self.audio_queue.get()
        return None

    def stop_recording(self):
        if self.running:
            self.running = False
            self.stream.stop()
            self.stream.close()
