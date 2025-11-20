import requests
import time
import datetime
from zhipuai import ZhipuAI
from AI.complex_use_llm import *
api_key = "2fc9599650f9426f8c01d4a7a7cbcea5.O7YGnKF7CLC0g87M"
client = ZhipuAI(api_key=api_key)


def video_llm(prompt):
    response = client.videos.generations(
        model="cogvideox-2",
        prompt=prompt,
        quality="speed",  # 输出模式，"quality"为质量优先，"speed"为速度优先
        with_audio=True,
        size="1920x1080",  # 视频分辨率，支持最高4K（如: "3840x2160"）
        fps=30,  # 帧率，可选为30或60
    )
    result = client.videos.retrieve_videos_result(
        id=response.id
    )
    cot=0
    while(result.task_status!='SUCCESS'):
        cot+=1
        print(cot)
        if(cot>60):
             raise ValueError('太慢了')
        time.sleep(5)
        result = client.videos.retrieve_videos_result(
            id=response.id
    )
    video = requests.get(result.video_result[0].url)
    timestamp = str(datetime.datetime.now().timestamp())
    #需要改路径
    with open(f'D:/项目与竞赛/深度学习与人工智能/agent_all/data/视频/{timestamp}.mp4', 'wb') as f:
        f.write(video.content)
    return f'D:/项目与竞赛/深度学习与人工智能/agent_all/data/视频/{timestamp}.mp4'


if __name__ == '__main__':
    store_video(video_llm('生成一条狗'))
