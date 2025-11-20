import base64
import os
from openai import OpenAI
from langchain_core.documents import Document


client = OpenAI(
    # 输入转发API Key
    api_key="sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP",
    base_url="https://api.chatanywhere.tech/v1"
)


def encode_image(image_path):
    """ 将图片转换为 base64 编码 """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def generate_image_summary(image_path):
    """ 使用 GPT-4o 生成图片摘要 """
    base64_image = encode_image(image_path)
    prompt = """
    You are an assistant tasked with summarizing images for retrieval.
    These summaries will be embedded and used to retrieve the raw image.
    Give a concise summary of the image that is well optimized for retrieval.
    """
    # 发送带图片的消息
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpg;base64,{base64_image}"}
                    },
                ],
            }
        ],
        max_tokens=300,
        stream=False  # # 是否开启流式输出
    )
    return response.choices[0].message.content


def return_document_picture(picture_file_paths):
    documents = []

    for file_path in picture_file_paths:
        if file_path.endswith((".png", ".jpg", ".jpeg")):
            summary = generate_image_summary(file_path)
            print(f"摘要 ({file_path}): {summary}")

            # 存入 LangChain Document
            doc = Document(page_content=summary, metadata={"image_path": file_path})
            documents.append(doc)
    return documents


