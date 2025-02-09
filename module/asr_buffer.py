class ASRBuffer:
    def __init__(self, max_size=10):
        self.buffer = []
        self.max_size = max_size

    def add(self, data):
        if len(self.buffer) >= self.max_size:
            self.buffer.pop(0)
        self.buffer.append(data)

    def clear_before(self, index):
        self.buffer = self.buffer[index:]

    def get_content(self) -> str:
        return "".join(self.buffer)