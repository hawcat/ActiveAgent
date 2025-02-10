class ASRBuffer:
    def __init__(self, max_size=10):
        self.buffer = []
        self.max_size = max_size

    def add(self, data):
        if len(self.buffer) >= self.max_size:
            self.buffer.pop(0)
        self.buffer.append(data)

    def clear(self):
        self.buffer.clear()

    def get_content(self) -> str:
        return "".join(self.buffer)

    async def get_content_stream(self):
        async for chunk in self.buffer:
            yield chunk
