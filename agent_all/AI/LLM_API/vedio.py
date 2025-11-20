import requests
from zhipuai import ZhipuAI
import base64
import os
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

api_key = "2fc9599650f9426f8c01d4a7a7cbcea5.O7YGnKF7CLC0g87M"


def image_to_summary(video_path):
    with open(video_path, 'rb') as video_file:
        video_base = base64.b64encode(video_file.read()).decode('utf-8')

    client = ZhipuAI(api_key=api_key) # 填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4v-plus-0111",  # 填写需要调用的模型名称
        messages=[
        {
            "role": "user",
            "content": [
            {
                "type": "video_url",
                "video_url": {
                    "url" : video_base
                }
            },
            {
                "type": "text",
                "text": '''你是一个助理，负责总结图像以便检索。
                    这些摘要将被嵌入并用于检索原始图像。
                    为检索提供一个简明的图像摘要'''
            }
            ]
        }
        ]
    )
    return response.choices[0].message.content


def return_document(video_file_paths):
    documents = []

    for file_path in video_file_paths:
        summary = image_to_summary(file_path)
        print(f"摘要 ({os.path.basename(file_path)}): {summary}")

        # 存入 LangChain Document
        doc = Document(page_content=summary, metadata={"video_path": file_path})
        documents.append(doc)

    return documents
