from module.system_prompt import SystemPrompt
from module.messages_manager import Messages
from openai import AsyncOpenAI, OpenAI
import json
from logger import hLogger
logger = hLogger()
logger = logger.get_logger()
a_client = AsyncOpenAI(
    base_url="https://api.deepseek.com", api_key="sk-2a72bc0a50f64e1eb29fdb05e23fc078"
)
client = OpenAI(
    base_url="https://api.deepseek.com", api_key="sk-2a72bc0a50f64e1eb29fdb05e23fc078"
)
class LLM:
    def __init__(self):
        
        pass

    def communicate_with_llm(self, messages_type:Messages, user_content):
        messages_type.add_message("user", user_content)
        messages = messages_type.get_messages()
        response = client.chat.completions.create(
            model="deepseek-chat", messages=messages, 
            response_format={
            'type': 'json_object'
            }
        )

        try:
            result = json.loads(response.choices[0].message.content)

        except Exception as e:
            result = {}
            logger.info(f"Failed to parse response: {response.choices[0].message.content}")
            logger.error(f"Failed to parse response: {e}")

        messages_type.clear_messages()

        return result

    async def communicate_with_llm_stream(self, messages_type:Messages, user_content):
        messages_type.add_message("user", user_content)
        messages = messages_type.get_messages()
        chunks = await a_client.chat.completions.create(
            model="deepseek-chat", stream=True, messages=messages, temperature=1.3
        )
        response = ""

        async for chunk in chunks:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content

        messages_type.add_message("assistant", response)