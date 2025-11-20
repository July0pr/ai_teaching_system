import base64
import io
import fitz
from PIL import Image
from openai import OpenAI
from langchain_core.documents import Document


client = OpenAI(
    # 输入转发API Key
    api_key="sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP",
    base_url="https://api.chatanywhere.tech/v1"
)


def encode_image(pdf_path, page_number: int):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_number - 1)  # input is one-indexed
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def generate_image_summary(pdf_path):
    """ 使用 GPT-4o 生成图片摘要 """
    base64_image = encode_image(pdf_path, 1)
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


def return_document_pdf(pdf_file_paths):
    documents = []
    for file_path in pdf_file_paths:
        if file_path.endswith((".pdf")):
            summary = generate_image_summary(file_path)
            print(f"摘要 ({file_path}): {summary}")

            # 存入 LangChain Document
            doc = Document(page_content=summary, metadata={"image_path": file_path})
            documents.append(doc)
    return documents
