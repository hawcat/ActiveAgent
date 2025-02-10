import sys
import time

sys.path.append("./")
from openai import AsyncOpenAI, OpenAI

from logger import hLogger
from module.messages_manager import Messages
from module.system_prompt import SystemPrompt, WeightFormat

logger = hLogger.get_logger()
a_client = AsyncOpenAI(base_url="https://api.deepseek.com", api_key="")
client = OpenAI(
    base_url="https://aihubmix.com/v1",
    api_key="",
)


class LLM:
    def __init__(self):
        pass

    def communicate_with_llm_with_format(self, messages_type: Messages, user_content):
        start_time = time.time()
        messages_type.add_message("user", user_content)
        messages = messages_type.get_messages()
        response = client.beta.chat.completions.parse(
            model="o3-mini",
            messages=messages,
            response_format=WeightFormat,
        )
        result = response.choices[0].message.parsed
        messages_type.clear_messages()

        end_time = time.time()
        logger.info(f"大模型响应时间：{end_time - start_time}秒")

        return result

    async def communicate_with_llm_stream(self, messages_type: Messages, user_content):
        start_time = time.time()
        messages_type.add_message("user", user_content)
        messages = messages_type.get_messages()
        chunks = await a_client.chat.completions.create(
            model="deepseek-chat", stream=True, messages=messages, temperature=1.3
        )
        response = ""

        async for chunk in chunks:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
                end_time = time.time()
                yield chunk.choices[0].delta.content

        logger.info(f"大模型流式响应时间：{end_time - start_time}秒")

        messages_type.add_message("assistant", response)


if __name__ == "__main__":
    llm = LLM()

    system_prompt = SystemPrompt()
    weight_messagaes_manager = Messages(
        system_prompt=system_prompt.weight_agent, max_size=10
    )
    result = llm.communicate_with_llm_with_format(
        Messages(system_prompt=system_prompt.weight_agent),
        "今天下厨，做个什么",
    )
    print(result)
    print(result.weight)
