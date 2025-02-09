import base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
class Messages:
    def __init__(self, system_prompt, max_size=10):
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": self.system_prompt}]
        # self.messages[0] = {"role": "system", "content": self.system_prompt}
        self.max_size = max_size

    def add_message(self, role, content, image=None):
        self.messages[0] = {"role": "system", "content": self.system_prompt}

        if len(self.messages) >= self.max_size:
            del self.messages[1:3]
        if image:
            content = [{"type": "text", "text": content}, {"type": "image_url", "image_url": {"url": encode_image(image)}}]
        else:
            content = content

        self.messages.append({"role": role, "content": content})

    def get_messages(self):
        return self.messages
    
    def clear_messages(self):
        self.messages = self.messages[1:]

    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt