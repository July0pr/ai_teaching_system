import requests
import datetime
from AI.complex_use_llm import *
client = ZhipuAI(api_key="2fc9599650f9426f8c01d4a7a7cbcea5.O7YGnKF7CLC0g87M")  # 请填写您自己的APIKey
def picture_llm(prompt):
    response = client.images.generations(
        model="cogview-4-250304",  # 填写需要调用的模型编码
        prompt=prompt,
    )
    result=response.data[0].url
    picture = requests.get(result)
    timestamp = str(datetime.datetime.now().timestamp())

    with open(f'D:/项目与竞赛/深度学习与人工智能/agent_all/data/图片/{timestamp}.png', 'wb') as f:
        f.write(picture.content)
    return f'D:/项目与竞赛/深度学习与人工智能/agent_all/data/图片/{timestamp}.png'

if __name__=='__main__':
    store_picture(picture_llm('生成一个牛'))