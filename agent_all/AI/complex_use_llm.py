from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from AI.const import *
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from AI.LLM_API.llm import client
import io
import fitz
from PIL import Image
from win32com.client import gencache
import os
from zhipuai import ZhipuAI
from typing import List, Union
import base64
from pathlib import Path
os.environ['OPENAI_API_BASE'] = 'https://api.chatanywhere.tech/v1'
os.environ['OPENAI_API_KEY'] = 'sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP'


class exercise(BaseModel):
    content: str = Field(description="习题内容，包含问题或题目描述")
    options: Union[List[str], None] = Field(description="习题选项。如果是选择题（单选或多选），请按格式提供选项列表，若无选项则None。对于单选题，选项不包括A、B、C、D等前缀；例如：['美丽', '丑陋', '帅气', '还行']")
    answer: str = Field(description="习题答案。对于选择题，填写选项对应的字母（A、B、C、D等）；对于判断题，填写'是'或'否'；对于填空题和简答题，填写正确答案。")



# ai输入应为 exercise_type（练习题类型） difficulty（难度）name（课程名称） theme（课程主题） objective（教学目标）
def generate_exercise_initial(exercise_type,difficulty,name,theme,objective):
    parser = JsonOutputParser(pydantic_object=exercise)
    prompt = PromptTemplate(
        template=initial_generate_Exercise,
        input_variables=["exercise_type","difficulty","course_name","course_theme","course_objective"],
        partial_variables={"format_instructions": parser.get_format_instructions()})
    chain = prompt | client | parser
    json = chain.invoke({"exercise_type":exercise_type,"difficulty":difficulty,"course_name":name,"course_theme":theme,"course_objective":objective})
    return json



# ai输入应为 request.suggestions（修改建议），exercise_type（练习题类型） request.difficulty（难度）course.name（课程名称） course.theme（课程主题） course.objective（教学目标）
def generate_exercise_continous_all(suggestions,exercise_type,difficulty,name,theme,objective):
    parser = JsonOutputParser(pydantic_object=exercise)
    prompt = PromptTemplate(
        template=continous_all_generate_Exercise,
        input_variables=["suggestions","exercise_type","difficulty","course_name","course_theme","course_objective"],
        partial_variables={"format_instructions": parser.get_format_instructions()})
    chain = prompt | client | parser
    json = chain.invoke({"suggestions":suggestions,"exercise_type":exercise_type,"difficulty":difficulty,"course_name":name,"course_theme":theme,"course_objective":objective})
    return json


# ai输入应为 request.suggestions（修改建议），ex.content（当前题目内容），ex.answers（当前题目答案），exercise_type（练习题类型） request.difficulty（难度）course.name（课程名称） course.theme（课程主题） course.objective（教学目标）
def generate_exercise_continous_part(suggestions, content,answers,exercise_type,difficulty,name,theme,objective):
    parser = JsonOutputParser(pydantic_object=exercise)
    prompt = PromptTemplate(
        template=continous_part_generate_Exercise,
        input_variables=["suggestions","content","answers","exercise_type","difficulty","course_name","course_theme","course_objective"],
        partial_variables={"format_instructions": parser.get_format_instructions()})
    chain = prompt | client | parser
    json = chain.invoke({"suggestions":suggestions,"content":content,"answers":answers,"exercise_type":exercise_type,"difficulty":difficulty,"course_name":name,"course_theme":theme,"course_objective":objective})
    return json


def encode_image(image_path):
    """ 将图片转换为 base64 编码 """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def pptToPDF(ppt_path):
    if not os.path.isfile(ppt_path):
        print(f"错误: 找不到 PPT 文件 -> {ppt_path}")
        return None

    # 获取文件名（不带扩展名）和 PPT 所在目录
    ppt_dir = os.path.dirname(ppt_path)  # 获取 PPT 所在目录
    ppt_filename = os.path.basename(ppt_path).rsplit('.', 1)[0]  # 提取文件名（去掉后缀）

    # 生成 PDF 存储目录
    pdf_dir = os.path.join(os.path.dirname(ppt_dir), "pdf")
    os.makedirs(pdf_dir, exist_ok=True)  # 如果目录不存在，则创建

    # 生成 PDF 文件路径
    pdf_path = os.path.join(pdf_dir, ppt_filename + ".pdf")

    # 如果目标 PDF 文件已存在，跳过转换
    if os.path.isfile(pdf_path):
        print(f"{pdf_path} 已存在，跳过转换")
        return pdf_path
    print("调用ppt")
    import win32com.client
    win32com.client.gencache.EnsureDispatch('PowerPoint.Application')
    # 启动 PowerPoint 应用
    p = gencache.EnsureDispatch("PowerPoint.Application")
    print("成功")
    try:
        # 打开 PPT 文件（ReadOnly=False, Untitled=False, WithWindow=False）
        ppt = p.Presentations.Open(ppt_path, False, False, False)
        try:
        # 将 PPT 导出为 PDF（2 代表 PDF 格式）
            ppt.ExportAsFixedFormat(pdf_path, 2, PrintRange=None)
        except Exception as e:
            print(e)

        # 关闭 PPT 文件
        ppt.Close()
    except Exception as e:
        print(f"文件 {os.path.basename(ppt_path)} 转换失败，错误: {e}")
        return None
    finally:
        p.Quit()  # 关闭 PowerPoint 应用

    return pdf_path


def encode_pdf(pdf_path, page_number: int):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_number - 1)  # input is one-indexed
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def generate_ppt_summary(ppt_path):
    print(1)
    pdf_path = pptToPDF(ppt_path)
    """ 使用 GPT-4o 生成ppt摘要 """
    base64_image = encode_pdf(pdf_path, 2)

    client = OpenAI(
        # 输入转发API Key
        api_key="sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP",
        base_url="https://api.chatanywhere.tech/v1"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "生成ppt摘要"},
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
    # 返回的类型是字符串

    return response.choices[0].message.content


def generate_image_summary(image_path):
    """ 使用 GPT-4o 生成图片摘要 """
    base64_image = encode_image(image_path)
    client = OpenAI(
        # 输入转发API Key
        api_key="sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP",
        base_url="https://api.chatanywhere.tech/v1"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "生成图片摘要"},
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
    # 返回的类型是字符串

    return response.choices[0].message.content


def store_picture(picture_path):
    summary = generate_image_summary(picture_path)
    doc = Document(page_content=summary, metadata={"picture_path": picture_path})
    doc = [doc]
    embeddings = OpenAIEmbeddings()
    if not os.path.exists('D:/项目与竞赛/深度学习与人工智能/agent_all/data/PICTURE_RAG'):
        path = 'D:/项目与竞赛/深度学习与人工智能/agent_all/data/PICTURE_RAG'
        os.makedirs(path, exist_ok=True)
        vectorstore = FAISS.from_documents(doc, embeddings)
        vectorstore.save_local('D:/项目与竞赛/深度学习与人工智能/agent_all/data/PICTURE_RAG')
    else:
        temp_work_path_picture = Path(r"D:/项目与竞赛/深度学习与人工智能/agent_all/data/PICTURE_RAG")
        os.chdir(temp_work_path_picture)
        vectorstore = FAISS.load_local(".", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        vectorstore.add_documents(doc)
        vectorstore.save_local(".")
    return vectorstore


def store_ppt(ppt_path, prompt):
    # summary=generate_ppt_summary(ppt_path) 更改这里
    summary = prompt
    doc = Document(page_content=summary, metadata={"ppt_path": ppt_path,"ppt_prompt":prompt})
    doc = [doc]
    embeddings = OpenAIEmbeddings()
    if not os.path.exists('D:/项目与竞赛/深度学习与人工智能/agent_all/data/PPT_RAG'):
        path = 'D:/项目与竞赛/深度学习与人工智能/agent_all/data/PPT_RAG'
        os.makedirs(path, exist_ok=True)
        vectorstore = FAISS.from_documents(doc, embeddings)
        vectorstore.save_local('D:/项目与竞赛/深度学习与人工智能/agent_all/data/PPT_RAG')
    else:
        temp_work_path_ppt = Path(r"D:/项目与竞赛/深度学习与人工智能/agent_all/data/PPT_RAG")
        os.chdir(temp_work_path_ppt)
        vectorstore = FAISS.load_local(".", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        vectorstore.add_documents(doc)
        vectorstore.save_local(".")
    return vectorstore


def generate_video_summary(video_path):
    with open(video_path, 'rb') as video_file:
        video_base = base64.b64encode(video_file.read()).decode('utf-8')
    client = ZhipuAI(api_key="2fc9599650f9426f8c01d4a7a7cbcea5.O7YGnKF7CLC0g87M")
    print("开始")
    print('this')
    try:
        response = client.chat.completions.create(
            model="glm-4v-plus-0111",  # 填写需要调用的模型名称
            messages=[
            {
                "role": "user",
                "content": [
                {
                    "type": "video_url",
                    "video_url": {
                        "url": video_base
                    }
                },
                {
                    "type": "text",
                    "text": '''提供图像摘要'''
                }
                ]
            }
            ]
        )
    except Exception as e:
        print(e)
    print("成功")
    return response.choices[0].message.content


def store_video(video_path):
    print(video_path)
    summary = generate_video_summary(video_path)
    doc = Document(page_content=summary, metadata={"video_path": video_path})
    doc = [doc]
    embeddings = OpenAIEmbeddings()
    print("start")
    if not os.path.exists(r'D:/项目与竞赛/深度学习与人工智能/agent_all/data/VIDEO_RAG'):
        print(1)
        path = r'D:/项目与竞赛/深度学习与人工智能/agent_all/data/VIDEO_RAG'
        print(1)
        os.makedirs(path, exist_ok=True)
        print(1)
        vectorstore = FAISS.from_documents(doc, embeddings)
        print(1)
        vectorstore.save_local(r'D:/项目与竞赛/深度学习与人工智能/agent_all/data/VIDEO_RAG')
        print(1)
    else:
        temp_work_path_video = Path(r"D:/项目与竞赛/深度学习与人工智能/agent_all/data/VIDEO_RAG")
        os.chdir(temp_work_path_video)
        vectorstore = FAISS.load_local(".", OpenAIEmbeddings(),
                                       allow_dangerous_deserialization=True)
        vectorstore.add_documents(doc)
        vectorstore.save_local(".")
    return vectorstore


def get_Rate_picture(file_path, name, theme, objective):
    print("图片summary")
    summary = generate_image_summary(file_path)
    sentence2 = picture_research_prompt.format(course_name=name, course_theme=theme, course_objective=objective)
    embeddings = OpenAIEmbeddings()
    # 生成向量
    vector1 = embeddings.embed_query(summary)
    vector2 = embeddings.embed_query(sentence2)

    # 计算余弦相似度
    similarity = cosine_similarity([vector1], [vector2])[0][0]
    print("成功返回")
    return similarity


def get_Rate_ppt(file_path, name, theme, objective, prompt):
    summary = prompt
    sentence2 = ppt_research_prompt.format(course_name=name, course_theme=theme, course_objective=objective)
    embeddings = OpenAIEmbeddings()
    # 生成向量
    vector1 = embeddings.embed_query(summary)
    vector2 = embeddings.embed_query(sentence2)

    # 计算余弦相似度
    similarity = cosine_similarity([vector1], [vector2])[0][0]
    return similarity


def get_Rate_video(file_path, name, theme, objective):
    summary = generate_video_summary(file_path)
    sentence2 = video_research_prompt.format(course_name=name, course_theme=theme, course_objective=objective)
    embeddings = OpenAIEmbeddings()
    # 生成向量
    vector1 = embeddings.embed_query(summary)
    vector2 = embeddings.embed_query(sentence2)

    # 计算余弦相似度
    similarity = cosine_similarity([vector1], [vector2])[0][0]
    return similarity


if __name__ == '__main__':
    store_video(r"D:/项目与竞赛/深度学习与人工智能/agent_all/data/视频/1742905045.041184.mp4")
