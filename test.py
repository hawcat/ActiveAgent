import asyncio

import aiohttp


# 模拟流式 ASR 的生成器
async def asr_stream():
    # 实际应用中，这里应该是实时从麦克风或者 ASR 服务获取文本片段
    # 此处只是模拟返回的片段
    for chunk in ["你好", "，我叫", "小明", "。", "请问", "你是谁", "？"]:
        await asyncio.sleep(0.5)  # 模拟网络或处理延时
        yield chunk


# 调用大模型 API 的函数
async def send_to_large_model(prompt):
    # 请替换为你实际使用的大模型 API 地址和参数
    url = "https://api.example.com/large-model"
    payload = {"prompt": prompt, "max_tokens": 100}
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY",  # 替换为实际 API Key
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result.get("response", "")
            else:
                print("调用大模型失败，状态码：", resp.status)
                return ""


# 主程序：处理 ASR 流并与大模型交互
async def main():
    buffer = ""
    async for chunk in asr_stream():
        print("ASR 返回片段:", chunk)
        buffer += chunk

        # 检查是否已经构成一个完整的输入（这里以句号、问号或感叹号作为结束符）
        if buffer.endswith("。") or buffer.endswith("？") or buffer.endswith("！"):
            prompt = buffer.strip()
            print("\n完整输入：", prompt)
            response = await send_to_large_model(prompt)
            print("大模型响应：", response, "\n")
            buffer = ""  # 清空缓冲区，为下一个输入做准备

    # 若结束时缓冲区内仍有残余内容，也可以发送出去
    if buffer:
        prompt = buffer.strip()
        print("\n剩余输入：", prompt)
        response = await send_to_large_model(prompt)
        print("大模型响应：", response)


if __name__ == "__main__":
    asyncio.run(main())
