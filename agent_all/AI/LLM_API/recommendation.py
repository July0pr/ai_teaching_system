from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Recommendation, User, Resource, ClassStudent, CourseBaseInfo, ClassResource, AssignmentSubmission
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from AI.LLM_API.llm import safe_call_llm
from AI.LLM_API.PPT_to_PDF import trans
from AI.LLM_API.vedio import return_document
from AI.LLM_API.PDF import return_document_pdf
from AI.LLM_API.picture import return_document_picture
from AI.LLM_API.prompt_recommendation import RECOMMENDATION_PROMPT

os.environ['OPENAI_API_BASE'] = 'https://api.chatanywhere.tech/v1'
os.environ['OPENAI_API_KEY'] = 'sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP'

# 数据库连接字符串
DATABASE_URL = r"sqlite:///D:/项目与竞赛/深度学习与人工智能/agent_all/data/db.db"

# 创建 SQLAlchemy 引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 创建 Session 类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def analyze_student_submissions(assignments_submissions):
    if not assignments_submissions:
        return None, None  # 如果没有提交记录，则返回 None

    # 计算最近一次提交时间
    latest_submission_time = max([submission.submission_date for submission in assignments_submissions])

    # 计算平均分数
    avg_grade = sum(
        [submission.grade for submission in assignments_submissions if submission.grade is not None]
    ) / len(assignments_submissions)

    return latest_submission_time, avg_grade


def find_relevant_document(llm_response, documents):
    # 使用 OpenAI 进行 embedding
    embeddings = OpenAIEmbeddings(openai_api_key='sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP')

    vectorstore = FAISS.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 1})

    result = retriever.invoke(llm_response)

    return result


def find_relevant_video(llm_response, video_file_paths):
    dd = return_document(video_file_paths)
    # 使用 OpenAI 进行 embedding
    embeddings = OpenAIEmbeddings(openai_api_key='sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP')
    vectorstore = FAISS.from_documents(dd, embeddings)
    vectorstore.save_local("VIDEO_RAG")
    retriever = FAISS.load_local("VIDEO_RAG", OpenAIEmbeddings(),
                                 allow_dangerous_deserialization=True).as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 1,
                       "score_threshold": 0.7})
    result = retriever.invoke(llm_response)
    return result


def find_relevant_ppt(llm_response, pdf_file_paths):
    dd = return_document_pdf(pdf_file_paths)
    # 使用 OpenAI 进行 embedding
    embeddings = OpenAIEmbeddings(openai_api_key='sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP')
    vectorstore = FAISS.from_documents(dd, embeddings)
    vectorstore.save_local("PPT_RAG")
    print("向量数据库已创建并保存")
    retriever = FAISS.load_local("PPT_RAG", OpenAIEmbeddings(),
                                 allow_dangerous_deserialization=True).as_retriever(search_type="similarity",
                                                                                    search_kwargs={"k": 1})
    result = retriever.invoke(llm_response)
    return result


def find_relevant_picture(llm_response, picture_file_paths):
    dd = return_document_picture(picture_file_paths)
    embeddings = OpenAIEmbeddings(openai_api_key='sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP')
    vectorstore = FAISS.from_documents(dd, embeddings)
    vectorstore.save_local("PICTURE_RAG")
    print("向量数据库已创建并保存")
    retriever = FAISS.load_local("PICTURE_RAG", OpenAIEmbeddings(),
                                 allow_dangerous_deserialization=True).as_retriever(search_type="similarity",
                                                                                    search_kwargs={"k": 1})
    result = retriever.invoke(llm_response)
    return result


def process_resources(resource_type, db: Session, llm_response):
    if resource_type == '教案':
        # 获取所有 resource_type 为 '教案' 的资源及其 file_path
        txt_resources = db.query(Resource).filter(Resource.resource_type == '教案').all()
        documents = []
        for resource in txt_resources:
            file_path = resource.file_path
            if os.path.exists(file_path) and file_path.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                documents.extend(loader.load())

        print('number of documents in resource list:', len(documents))
        path_mapping = None
        # 调用 find_relevant_document 函数获取最相关的文档
        result = find_relevant_document(llm_response, documents)
        print(result)

    elif resource_type == '视频':
        # 获取所有 resource_type 为 'video' 的资源及其 file_path
        video_resources = db.query(Resource).filter(Resource.resource_type == '视频').all()
        video_file_paths = []

        for resource in video_resources:
            file_path = resource.file_path
            if os.path.exists(file_path) and file_path.lower().endswith((".mp4", ".avi", ".mov")):  # 常见的视频格式
                video_file_paths.append(file_path)

        print('number of video resources:', len(video_file_paths))
        path_mapping = None
        result = find_relevant_video(llm_response, video_file_paths)
        print(result)

    elif resource_type == 'PPT':
        # 获取所有 resource_type 为 'PPT' 的资源及其 file_path
        ppt_resources = db.query(Resource).filter(Resource.resource_type == 'PPT').all()
        ppt_file_paths = []

        for resource in ppt_resources:
            file_path = resource.file_path
            # 检查文件是否是常见的PPT格式
            if file_path.lower().endswith((".ppt", ".pptx")):
                ppt_file_paths.append(file_path)

        print('number of PPT resources:', len(ppt_file_paths))
        pdf_file_paths, path_mapping = trans(ppt_file_paths)
        result = find_relevant_ppt(llm_response, pdf_file_paths)
        print(result)

    elif resource_type == '图片':
        # 获取所有 resource_type 为 '图片' 的资源及其 file_path
        image_resources = db.query(Resource).filter(Resource.resource_type == '图片').all()
        image_file_paths = []

        for resource in image_resources:
            file_path = resource.file_path
            if os.path.exists(file_path) and file_path.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                image_file_paths.append(file_path)

        print('number of image resources:', len(image_file_paths))
        path_mapping = None
        result = find_relevant_picture(llm_response, image_file_paths)
        print(result)

    else:
        print("未知的资源类型")
        result = None
        path_mapping = None

    print('\n')
    return result, path_mapping


def get_matched_resource(recommend_resource_type, result, path_mapping, db: Session):
    if recommend_resource_type == '教案':
        # 教案资源直接从metadata['source']获取
        matched_file_path = result[0].metadata['source']
    elif recommend_resource_type == '视频':
        # 视频资源从metadata['image_path']获取
        matched_file_path = result[0].metadata['video_path']
    elif recommend_resource_type == 'PPT':
        # PPT资源从metadata['image_path']获取并映射回原始PPT文件路径
        matched_file_path = result[0].metadata['image_path']
        matched_file_path = path_mapping.get(matched_file_path, "No matching original PPT found")
    elif recommend_resource_type == '图片':
        # 图片资源从metadata['image_path']获取
        matched_file_path = result[0].metadata['image_path']
    else:
        print("未知的资源类型")
        return None

    # 根据匹配到的文件路径查找对应的资源
    matched_resource = db.query(Resource).filter(Resource.file_path == matched_file_path).first()
    return matched_resource


def recommend_resources_students(db: Session, student_id: int):
    # 获取学生已注册的课程
    students_classes = db.query(ClassStudent).filter(ClassStudent.student_id == student_id).all()
    student_classes_ids = [cls.class_id for cls in students_classes]

    recommendations = []

    # 获取并分析学生提交作业的数据
    assignments_submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.student_id == student_id
    ).all()

    # 调用 analyze_student_submissions 函数来分析提交数据
    latest_submission_time, avg_grade = analyze_student_submissions(assignments_submissions)

    if latest_submission_time and avg_grade is not None:
        prompt = RECOMMENDATION_PROMPT.format(subject="数学", latest_submission_time=latest_submission_time,
                                              avg_grade=avg_grade)
        llm_response = safe_call_llm(prompt)
    else:
        llm_response = "没有足够的提交记录来生成个性化建议。"
        print(llm_response)

    # 定义推荐资源类型的列表
    resource_types = ['视频', 'PPT', '教案', '图片']

    # 清空当前学生的已有推荐
    db.query(Recommendation).filter(Recommendation.student_id == student_id).delete()
    db.commit()

    # 计算起始优先级值，可以基于现有推荐的数量
    existing_recommendations_count = db.query(Recommendation).filter(
        Recommendation.student_id == student_id
    ).count()
    priority_start = existing_recommendations_count + 1

    # 对每种资源类型进行处理
    for recommend_resource_type in resource_types:
        result, path_mapping = process_resources(recommend_resource_type, db, llm_response)

        # 根据大语言模型的响应内容找到对应的资源 ID 并添加推荐
        if result:
            matched_resource = get_matched_resource(recommend_resource_type, result, path_mapping, db)

            if matched_resource:
                existing_recommendation = db.query(Recommendation).filter(
                    Recommendation.student_id == student_id,
                    Recommendation.resource_id == matched_resource.id
                ).first()

                if not existing_recommendation:
                    new_recommendation = Recommendation(
                        student_id=student_id,
                        resource_id=matched_resource.id,
                        priority=priority_start,  # 使用计算出的起始优先级
                        reason=f"推荐学习资料\n大语言模型建议: {llm_response}",  # 将大语言模型的建议加入原因
                        recommended_at=datetime.now(),
                        is_viewed=0  # 默认为未查看
                    )
                    recommendations.append(new_recommendation)
                    priority_start += 1  # 每次添加后递增优先级

    if recommendations:
        db.add_all(recommendations)
        db.commit()
        print(f"{len(recommendations)} 条推荐资源已添加")


# 测试推荐资源函数
def test_recommend_resources(db: Session):
    student_id = 3  # 学生ID

    # 调用函数
    recommend_resources_students(db, student_id)

    # 检查推荐是否已成功添加到 Recommendation 表中
    recommendations = db.query(Recommendation).filter(Recommendation.student_id == student_id).all()

    # 输出结果以进行检查
    for recommendation in recommendations:
        print(f"Student {recommendation.student_id} has been recommended resource {recommendation.resource_id} with priority {recommendation.priority}")


# 运行测试
if __name__ == "__main__":
    db = next(get_db())
    test_recommend_resources(db)
