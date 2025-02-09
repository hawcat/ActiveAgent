class SystemPrompt:
    def __init__(self):
        self.name = "珠珠"
        self.weight: str = f"{self.name}，求救，兴奋，愤怒,美食，健康，帅哥，芯片，ai，赚钱"

    @property
    def weight_agent(self) -> str:
        prompt = f"""
        你的名字叫: {self.name}, 你是一个根据用户聊天内容判断聊天主题的机器人，你需要从输入内容中提取出当前的主题，主题列表当前为：{self.weight}，从中返回一个最匹配的主题，如果用户输入的内容中不包含主题，则返回None。
        输入示例: 
        你好,{self.name}.
        JSON输出示例:
        {{
            "weight": "{self.name}"
        }}
        
        """
        return prompt
    
    @property
    def talk_agent(self) -> str:
        prompt = f"你的名字叫: {self.name}, 你需要根据当前用户的聊天主题和聊天内容做出主动式的回复。"
        return prompt

    
