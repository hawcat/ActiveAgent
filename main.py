import base64
import json
import asyncio
import websocket

from logger import hLogger
from module.asr_buffer import ASRBuffer
from module.system_prompt import SystemPrompt
from module.messages_manager import Messages
from module.llm import LLM
from module.recorder import BackgroundRecorder

llm = LLM()
logger = hLogger.get_logger()
asr_buffer = ASRBuffer(max_size=5)
system_prompt = SystemPrompt()
weight_messagaes_manager = Messages(system_prompt=system_prompt.weight_agent, max_size=10)
talk_messages_manager = Messages(system_prompt=system_prompt.talk_agent, max_size=10)
recorder = BackgroundRecorder()
ws = websocket.WebSocket()

try:
    ws.connect("ws://localhost:9910/ws/transcribe?sample_rate=44100")
    # ws.connect("wss://core.max.mcpanl.cn/ws/speech_to_text")
    logger.info("WebSocket connection established.")
except Exception as e:
    logger.error(f"Failed to connect to WebSocket: {e}")


async def process_llm_communication(asr_buffer:ASRBuffer, weight_messagaes_manager:Messages, talk_messages_manager:Messages, llm:LLM):
    result = llm.communicate_with_llm(weight_messagaes_manager, asr_buffer.get_content())
    logger.info(f"Weight：{result}")

    if result["weight"] and result["weight"] != "None":
        question = "用户当前聊天内容主题是：" + result["weight"] + "，聊天内容是：" + asr_buffer.get_content() + "，请根据聊天内容主题，回答用户问题。"
        result_it = llm.communicate_with_llm_stream(talk_messages_manager, question)
        async for chunk in result_it:
            logger.info(f"主动返回：{chunk}")

        asr_buffer.clear_before(len(asr_buffer.buffer) - 1)

def communicate_with_asr(audio_data):
    b64_audio_data = base64.b64encode(audio_data).decode("utf-8")
    ws.send(b64_audio_data)
    data = ws.recv()
    return data

async def main():
    recorder.start_recording()
    n = 0
    
    try:
        while True:
            n += 1
            indata = recorder.get_audio_data()
            if indata is None:
                continue
            data = communicate_with_asr(indata)
            retdata = json.loads(data)
            
            if retdata["code"] == 0:
                logger.info(f"Current ASR：{data['data']}")
                asr_buffer.add(data["data"])
                logger.info(f"ASR Streaming Buffer：{asr_buffer.get_content()}")
                
            if n % 5 == 0:
                await process_llm_communication(asr_buffer, weight_messagaes_manager, talk_messages_manager, llm)
                n = 0

    except KeyboardInterrupt:
        recorder.stop_recording()
        print("Recording stopped.")

if __name__ == "__main__":
    asyncio.run(main())
    
