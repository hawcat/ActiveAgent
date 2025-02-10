import asyncio
import base64
import json
import threading
import time

import websockets

from logger import hLogger
from module.asr_buffer import ASRBuffer
from module.llm import LLM
from module.messages_manager import Messages
from module.recorder import BackgroundRecorder
from module.system_prompt import SystemPrompt

llm = LLM()
logger = hLogger.get_logger()
asr_buffer = ASRBuffer(max_size=5)
system_prompt = SystemPrompt()
weight_messagaes_manager = Messages(
    system_prompt=system_prompt.weight_agent, max_size=10
)
talk_messages_manager = Messages(system_prompt=system_prompt.talk_agent, max_size=10)


uri = "ws://localhost:9910/ws/transcribe?sample_rate=44100"


class DataPool:
    def __init__(self):
        self.data = None

    def callback(self, indata):
        logger.info(f"Received data: {indata}")
        self.data = indata


data_pool = DataPool()
recorder = BackgroundRecorder(callback=data_pool.callback)


def call_llm(content):
    result = llm.communicate_with_llm_with_format(weight_messagaes_manager, content)
    return result


async def process_llm(queue):
    """异步处理 LLM 结果"""
    while True:
        weight, text = await queue.get()  # 阻塞直到有任务
        logger.info(f"LLM Request: {weight}, text is {text} when push.")
        if weight and weight.weight is not None and weight.weight != "None":
            async for response in call_llm_async(weight.weight, text):
                logger.info(f"Active LLM Response: {response}")
        queue.task_done()  # 标记任务完成


async def call_llm_async(weight, content):
    question = f"用户当前讨论的主题是：{weight}，当前交流的内容是： {content}"
    result = llm.communicate_with_llm_stream(talk_messages_manager, question)
    async for text in result:
        yield text


async def main():
    recorder.start_recording()
    asr_count = 1
    async with websockets.connect(uri) as ws:
        try:
            while True:
                if data_pool.data is None:
                    continue
                else:
                    indata = data_pool.data

                b64_audio_data = base64.b64encode(indata).decode("utf-8")
                send_content = b64_audio_data

                await ws.send(send_content)
                data = await ws.recv()
                retdata = json.loads(data)

                if retdata["code"] == 0:
                    asr_count += 1
                    logger.info(f"Current ASR：{retdata['data']}")

                # if asr_count % 8 == 0:
                #     copy_data = retdata["data"]
                #     weight = call_llm(copy_data)
                #     if weight and weight.weight is not None and weight.weight != "None":
                #         resp_it = call_llm_async(weight.weight, copy_data)
                #         async for resp in resp_it:
                #             logger.info(f"LLM Response: {resp}")

                #     asr_count = 1
                #     await ws.send("PARAMS:is_clear=1")  # 清除 ASR 缓存
                #     logger.info("Cleared ASR buffer.")

        except KeyboardInterrupt:
            recorder.stop_recording()
            print("Recording stopped.")


async def main_1():
    recorder.start_recording()
    last_request_time = asyncio.get_event_loop().time()
    queue = asyncio.Queue(maxsize=5)
    asyncio.create_task(process_llm(queue))
    async with websockets.connect(uri) as ws:
        try:
            while True:
                indata = await asyncio.to_thread(recorder.get_audio_data)
                if indata is None:
                    continue

                b64_audio_data = base64.b64encode(indata).decode("utf-8")
                send_content = b64_audio_data

                await ws.send(send_content)
                data = await ws.recv()
                retdata = json.loads(data)

                if retdata["code"] == 0:
                    logger.info(f"Current ASR：{retdata['data']}")

                # **检查是否达到 5 秒间隔**
                current_time = asyncio.get_running_loop().time()
                if current_time - last_request_time >= 5:
                    copy_data = retdata["data"]

                    async def fetch_llm():
                        weight = await asyncio.to_thread(call_llm, retdata["data"])
                        try:
                            await queue.put((weight, copy_data))
                        except asyncio.QueueFull:
                            logger.warning("LLM queue is full, dropping request.")

                    asyncio.create_task(fetch_llm())
                    last_request_time = current_time  # 更新请求时间
                    await ws.send("PARAMS:is_clear=1")  # 清除 ASR 缓存
                    logger.info("Cleared ASR buffer.")

        except KeyboardInterrupt:
            recorder.stop_recording()
            print("Recording stopped.")


if __name__ == "__main__":
    asyncio.run(main())
    # main()
