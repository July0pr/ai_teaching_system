import requests
import json
import time

MODEL_NAME = "deepseek-r1:1.5b"

# token统计（如果不需要可以不更新）
total_prompt_tokens = 0
total_response_tokens = 0

def call_local_ollama(input_prompt, model=MODEL_NAME):
    """
    通过本地 Ollama Serve 调用模型
    """
    url = f"http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": input_prompt,
        "temperature": 0.7,
        "stream": False,
        "options": {
            "num_predict": 65535
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        res_json = response.json()
        # Ollama Serve 返回的文本字段通常是 'text'
        sys_response = res_json.get("response", "")
        # 模拟 token 统计，可根据实际返回改写
        prompt_token = len(input_prompt.split())
        response_token = len(sys_response.split())
        return sys_response, prompt_token, response_token
    else:
        raise ValueError(f"Ollama Serve error: {response.status_code} {response.text}")


def safe_call_llm(input_prompt, **kwargs) -> str:
    """
    改写后的 safe_call_llm：
    输入 input_prompt 返回模型生成的内容
    内部自动错误重试5次，5次错误抛异常
    """
    global MODEL_NAME
    global total_prompt_tokens
    global total_response_tokens

    for i in range(5):
        try:
            sys_response, prompt_token, response_token = call_local_ollama(input_prompt, model=MODEL_NAME)

            # 更新 token 统计
            total_prompt_tokens += prompt_token
            total_response_tokens += response_token

            print(f"\nsys_response:\n{sys_response}")
            print(f"\nprompt_token, response_token: {prompt_token}, {response_token}\n")

            return sys_response
        except Exception as ex:
            print(ex)
            print(f"Request {MODEL_NAME} failed. Try {i+1}/5. Sleep 20 secs.")
            time.sleep(20)

    raise ValueError('safe_call_llm error! Maximum retries exceeded.')
