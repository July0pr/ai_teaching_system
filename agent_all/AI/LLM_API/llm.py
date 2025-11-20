import os
import time
from langchain_openai import ChatOpenAI
os.environ['OPENAI_API_BASE']='https://api.chatanywhere.tech/v1'
os.environ['OPENAI_API_KEY']='sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP'
from langchain_openai import OpenAIEmbeddings
MAX_TRY = 5


MODEL_NAME = 'gpt-4o'

total_prompt_tokens = 0
total_response_tokens = 0

client = ChatOpenAI(name=MODEL_NAME,temperature=0.0)

def api_func(prompt: str):
    global MODEL_NAME
    print(f"\nUse OpenAI model: {MODEL_NAME}\n")
    global client
    response= client.invoke(prompt)

    text = response.content
    prompt_token = response.usage_metadata['input_tokens']
    response_token = response.usage_metadata['output_tokens']
    return text, prompt_token, response_token


def safe_call_llm(input_prompt, **kwargs) -> str:
    """
    函数功能描述：输入 input_prompt 返回模型生成的内容和使用token数量（内部自动错误重试5次，5次错误抛异常）
    """
    global MODEL_NAME
    global total_prompt_tokens
    global total_response_tokens

    for i in range(5):
        try:
            sys_response, prompt_token, response_token = api_func(input_prompt)
            print(f"\nsys_response: \n{sys_response}")
            print(f'\n prompt_token,response_token: {prompt_token} {response_token}\n')

            return sys_response
        except Exception as ex:
            print(ex)
            print(f'Request {MODEL_NAME} failed. try {i} times. Sleep 20 secs.')
            time.sleep(20)

    raise ValueError('safe_call_llm error!')


if __name__ == "__main__":
    res = safe_call_llm('我爸妈结婚为什么不邀请我？')
    print(res)
