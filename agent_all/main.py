from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from models import User, Role, Base, Resource, ResourceKeyword, AIResource, Class, ClassStudent, ClassResource, LessonPlan, Assignment, Exercise, AssignmentExercise, AssignmentSubmission, Recommendation, CourseBaseInfo, CourseResource, LessonPreparation, ExerciseStudent, ShareResource
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uuid
import shutil
from fastapi.responses import FileResponse
#from AI.LLM_API.llm import safe_call_llm
from localServerLLMCall import safe_call_llm
from AI.LLM_API.picture_llm import *
from AI.LLM_API.video_llm import *
from AI.LLM_API.ppt_llm import *
from AI.LLM_API.recommendation import recommend_resources_students
import datetime
os.environ['OPENAI_API_BASE'] = 'https://api.chatanywhere.tech/v1'
os.environ['OPENAI_API_KEY'] = 'sk-Y3fu4oyrlebG3PxY2xwVhoQZFBs8env2btCNwnJE1ghwjxEP'
if not os.path.exists('data'):
    os.makedirs('data')
DATABASE_URL = "sqlite:///./data/db.db"

# 创建数据库引擎和会话
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 定义用户创建请求的数据模型
class UserCreate(BaseModel):
    username: str
    password: str
    role: str

# 定义用户更新请求的数据模型
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

# 定义用户响应的数据模型
class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    status: str  # 新增状态字段
    created_at: datetime.datetime
    updated_at: datetime.datetime

# 定义资源创建请求的数据模型
class ResourceCreate(BaseModel):
    resource_name: str
    resource_type: str
    file_path: str

# 定义资源更新请求的数据模型
class ResourceUpdate(BaseModel):
    resource_name: Optional[str] = None
    resource_type: Optional[str] = None
    file_path: Optional[str] = None

# 定义资源响应的数据模型
class ResourceResponse(BaseModel):
    id: int
    resource_name: str
    resource_type: str
    file_path: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

# 定义 AI 生成资源创建请求的数据模型
class AIResourceCreate(BaseModel):
    resource_name: str
    resource_type: str
    file_path: str
    user_id: int

# 定义 AI 生成资源更新请求的数据模型
class AIResourceUpdate(BaseModel):
    resource_name: Optional[str] = None
    resource_type: Optional[str] = None
    file_path: Optional[str] = None
    user_id: Optional[int] = None

# 定义班级创建请求的数据模型
class ClassCreate(BaseModel):
    class_name: str
    teacher_id: int
    subjects: Optional[str] = None  # 新增教授科目字段，设为可选

# 定义班级更新请求的数据模型
class ClassUpdate(BaseModel):
    class_name: Optional[str] = None
    teacher_id: Optional[int] = None
    subjects: Optional[str] = None  # 新增教授科目字段

# 定义班级响应的数据模型
class ClassResponse(BaseModel):
    id: int
    class_name: str
    teacher_id: int
    subjects: Optional[str] = None  # 新增教授科目字段
    created_at: datetime.datetime
    updated_at: datetime.datetime

# 定义添加学生到班级的请求数据模型
class ClassStudentCreate(BaseModel):
    class_id: int
    student_id: int

# 定义班级资源创建请求的数据模型
class ClassResourceCreate(BaseModel):
    class_id: int
    resource_type: str
    resource_name: str
    file_path: str
    uploaded_by: int

# 定义班级资源更新请求的数据模型
class ClassResourceUpdate(BaseModel):
    class_id: Optional[int] = None
    resource_type: Optional[str] = None
    resource_name: Optional[str] = None
    file_path: Optional[str] = None
    uploaded_by: Optional[int] = None

# 定义班级资源响应的数据模型
class ClassResourceResponse(BaseModel):
    id: int
    class_id: int
    resource_type: str
    resource_name: str
    file_path: str
    uploaded_by: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

# 定义教案创建请求的数据模型
class LessonPlanCreate(BaseModel):
    teacher_id: int
    class_id: int
    title: str
    description: str
    file_path: str

# 定义教案更新请求的数据模型
class LessonPlanUpdate(BaseModel):
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None

# 定义教案响应的数据模型
class LessonPlanResponse(BaseModel):
    id: int
    teacher_id: int
    class_id: int
    title: str
    description: str
    file_path: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

# 作业模块的数据模型
class AssignmentCreate(BaseModel):
    class_id: int
    title: str
    description: str
    due_date: datetime.datetime

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime.datetime] = None

class AssignmentResponse(BaseModel):
    id: int
    class_id: int
    title: str
    description: str
    due_date: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime

# 习题模块的数据模型
class ExerciseCreate(BaseModel):
    user_id: int
    type: str  # '单选', '多选', '填空', '判断', '简答'
    title: str
    content: str
    options: Optional[str] = None  # JSON字符串，可为空
    answers: str

class ExerciseUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    options: Optional[str] = None
    answers: Optional[str] = None

class ExerciseResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    content: str
    options: Optional[str] = None
    answers: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

# 作业-习题关联的数据模型
class AssignmentExerciseCreate(BaseModel):
    assignment_id: int
    exercise_id: int

# 作业提交的数据模型
class AssignmentSubmissionCreate(BaseModel):
    assignment_id: int
    student_id: int
    answers: str  # JSON字符串

class AssignmentSubmissionUpdate(BaseModel):
    answers: Optional[str] = None
    grade: Optional[float] = None
    feedback: Optional[str] = None

class AssignmentSubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    submission_date: datetime.datetime
    answers: str
    grade: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

# 学习资源推荐的数据模型
class RecommendationCreate(BaseModel):
    student_id: int
    resource_id: int
    priority: Optional[int] = 0
    reason: Optional[str] = None

class RecommendationUpdate(BaseModel):
    priority: Optional[int] = None
    reason: Optional[str] = None
    is_viewed: Optional[int] = None

class RecommendationResponse(BaseModel):
    id: int
    student_id: int
    resource_id: int
    priority: int
    reason: Optional[str] = None
    recommended_at: datetime.datetime
    is_viewed: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

# 定义登录请求的数据模型
class LoginRequest(BaseModel):
    username: str
    password: str

# 定义登录响应的数据模型
class LoginResponse(BaseModel):
    id: int
    username: str
    role: str
    token: str  # 实际项目中应该使用JWT token

# 定义课程基础信息请求的数据模型
class CourseBaseInfoCreate(BaseModel):
    name: str
    theme: str
    objective: str
    target_class: int  # 修改为整数类型，表示班级ID
    duration: str
    teacher_id: int
    features: dict
    special_requirements: List[str]

# 定义课程基础信息响应的数据模型
class CourseBaseInfoResponse(BaseModel):
    id: int
    name: str
    theme: str
    objective: str
    target_class: str
    duration: str
    teacher_id: int
    features: dict
    special_requirements: List[str]
    created_at: datetime.datetime

# 定义生成教案请求的数据模型
class GenerateLessonPlanRequest(BaseModel):
    course_id: int
    suggestions: Optional[str] = None

# 定义生成教案响应的数据模型
class GenerateLessonPlanResponse(BaseModel):
    content: str

# 定义保存教案请求的数据模型
class SaveLessonPlanRequest(BaseModel):
    course_id: int
    content: str

# 定义生成习题请求的数据模型
class GenerateExercisesRequest(BaseModel):
    course_id: int
    types: dict  # {"choice": 2, "judgment": 3, ...}
    difficulty: int  # 1-5
    selected_ids: Optional[List[int]] = None  # 要重新生成的题目ID列表
    suggestions: Optional[str] = None  # 修改建议

# 定义习题响应的数据模型
class ExerciseItem(BaseModel):
    id: Optional[int] = None
    type: str
    title: str
    content: str
    options: Optional[str] = None
    answers: str

# 定义生成习题响应的数据模型
class GenerateExercisesResponse(BaseModel):
    exercises: List[ExerciseItem]

# 定义保存习题请求的数据模型
class SaveExercisesRequest(BaseModel):
    course_id: int
    exercises: List[ExerciseItem]

# 资源推荐响应模型
class ResourceRecommendResponse(BaseModel):
    courseware: List[dict]
    video: List[dict]
    image: List[dict]

# 保存选中资源的请求模型
class SaveResourcesRequest(BaseModel):
    course_id: int
    selected_resources: dict

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# 更新初始化程序，在应用启动时执行
@app.on_event("startup")
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        
        # 检查是否已经有数据
        if db.query(User).first() is None:
            # 创建默认用户
            default_users = [
                User(username="admin", password="admin123", role="admin"),
                User(username="teacher1", password="teacher123", role="teacher"),
                User(username="student1", password="student123", role="student")
            ]
            db.add_all(default_users)
            db.commit()

            # 创建默认班级
            default_classes = [
                Class(
                    class_name="软件2202班",
                    teacher_id=2,  # teacher1的ID
                    subjects="数据结构"
                ),
                Class(
                    class_name="软件2203班",
                    teacher_id=2,
                    subjects="数据结构"
                ),
                Class(
                    class_name="集成2307班",
                    teacher_id=2,
                    subjects="C语言、嵌入式"
                )
            ]
            db.add_all(default_classes)
            db.commit()

        # 检查并创建文件夹
        folders = ['PPT', '视频', '图片']
        for folder in folders:
            folder_path = os.path.join('data', folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        # 检查是否存在角色
        if not db.query(Role).first():
            # 创建默认角色
            roles = [
                Role(role_name='teacher', permissions='{}'),
                Role(role_name='student', permissions='{}'),
                Role(role_name='admin', permissions='{}')
            ]
            db.add_all(roles)
            db.commit()

        # 检查是否存在管理员用户
        if not db.query(User).filter(User.username == 'admin').first():
            admin_user = User(username='admin', password='admin', role='admin')
            teacher_user = User(username='teacher', password='teacher', role='teacher')
            student_user = User(username='student', password='student', role='student')
            db.add(admin_user)
            db.add(teacher_user)
            db.add(student_user)
            db.commit()

        # 检查是否存在资源
        if not db.query(Resource).first():
            # 创建默认资源
            default_resources = [
                Resource(resource_name='test1.pptx', resource_type='PPT', file_path='data/PPT/test1.pptx', user_id=2),
                Resource(resource_name='test2.pptx', resource_type='PPT', file_path='data/PPT/test2.pptx', user_id=2),
                Resource(resource_name='test1.mp4', resource_type='视频', file_path='data/视频/test1.mp4', user_id=2),
                Resource(resource_name='test2.mp4', resource_type='视频', file_path='data/视频/test2.mp4', user_id=2),
                Resource(resource_name='test1.jpg', resource_type='图片', file_path='data/图片/test1.jpg', user_id=2),
                Resource(resource_name='test2.jpg', resource_type='图片', file_path='data/图片/test2.jpg', user_id=2),
                Resource(resource_name='test1.pptx', resource_type='PPT', file_path='data/PPT/test1.pptx', user_id=3),
                Resource(resource_name='test2.mp4', resource_type='视频', file_path='data/视频/test2.mp4', user_id=3),
                Resource(resource_name='test1.jpg', resource_type='图片', file_path='data/图片/test1.jpg', user_id=3),
            ]
            db.add_all(default_resources)
            db.commit()

            # 创建默认关键字
            default_keywords = [
                (default_resources[0].id, 'PPT'),
                (default_resources[1].id, 'PPT'),
                (default_resources[2].id, '视频'),
                (default_resources[3].id, '视频'),
                (default_resources[4].id, '图片'),
                (default_resources[5].id, '图片')
            ]
            for resource_id, keyword in default_keywords:
                resource_keyword = ResourceKeyword(resource_id=resource_id, keyword=keyword)
                db.add(resource_keyword)
            db.commit()
            
        if not db.query(Recommendation).first():
            default_recommendations = [
                Recommendation(student_id=3, resource_id=7, priority=1, reason='推荐理由1'),
                Recommendation(student_id=3, resource_id=8, priority=2, reason='推荐理由2'),
                Recommendation(student_id=3, resource_id=9, priority=3, reason='推荐理由3')
            ]
            db.add_all(default_recommendations)
            db.commit()
            
        # 检查是否存在班级
        if not db.query(Class).first():
            # 创建默认班级
            default_classes = [
                Class(class_name='示例班级', teacher_id=2)  # 使用teacher用户ID
            ]
            db.add_all(default_classes)
            db.commit()

        # 检查是否存在班级学生
        if not db.query(ClassStudent).first():
            # 创建默认班级学生
            default_class_students = [
                ClassStudent(class_id=1, student_id=3)  # 使用student用户
            ]
            db.add_all(default_class_students)
            db.commit()

        # 创建示例文件
        example_files = [
            ('data/PPT/test1.pptx', b'Example PPT content 1'),
            ('data/PPT/test2.pptx', b'Example PPT content 2'),
            ('data/视频/test1.mp4', b'Example video_llm.py content 1'),
            ('data/视频/test2.mp4', b'Example video_llm.py content 2'),
            ('data/图片/test1.jpg', b'Example image content 1'),
            ('data/图片/test2.jpg', b'Example image content 2')
        ]

        for file_path, content in example_files:
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(content)

        db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"初始化数据库失败: {str(e)}")

# 数据库会话依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 登录接口
@app.post("/login/", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.username == login_data.username,
        User.password == login_data.password  # 实际项目中应该使用加密密码
    ).first()
    
    if db_user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查用户状态，禁用用户不允许登录
    if db_user.status == '已禁用':
        raise HTTPException(status_code=403, detail="该用户已被禁用，请联系管理员")
    
    # 这里应该生成JWT token，这里简单返回一个模拟token
    token = f"mock_token_{db_user.id}_{db_user.role}"
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "role": db_user.role,
        "token": token
    }

# 创建用户接口
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 验证角色是否有效
    if user.role not in ['teacher', 'student', 'admin']:
        raise HTTPException(status_code=400, detail="无效的用户角色")
    
    # 创建新用户
    db_user = User(
        username=user.username,
        password=user.password,  # 实际项目中应该对密码进行加密
        role=user.role,
        status="正常"  # 默认状态为激活
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="创建用户失败")

# 获取用户信息接口
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# 更新用户信息接口
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username is not None:
        db_user.username = user.username
    if user.password is not None:
        db_user.password = user.password
    if user.role is not None:
        db_user.role = user.role
    db.commit()
    db.refresh(db_user)
    return db_user

# 删除用户接口
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 删除用户
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}

# 创建资源接口
@app.post("/resources/", response_model=ResourceResponse)
async def create_resource(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传资源文件并保存到数据库
    """
    try:
        # 获取文件扩展名
        file_ext = file.filename.split('.')[-1].lower()
        
        # 获取资源类型
        resource_type = get_resource_type(file_ext)
        if not resource_type:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
            
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        
        # 根据资源类型确定保存目录
        save_dir = f"data/{resource_type}"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 保存文件
        file_path = os.path.join(save_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 获取当前用户ID
        current_user_id = get_current_user_id()
            
        # 创建资源记录
        resource = Resource(
            resource_name=file.filename,
            resource_type=resource_type,
            file_path=file_path,
            user_id=current_user_id
        )
        db.add(resource)
        db.flush()  # 获取resource.id
        
        # 提取关键词（这里简单地使用文件名作为关键词）
        keywords = file.filename.split('.')[0].split('_')
        for keyword in keywords:
            if keyword.strip():
                resource_keyword = ResourceKeyword(
                    resource_id=resource.id,
                    keyword=keyword.strip()
                )
                db.add(resource_keyword)
        
        db.commit()
        return resource
        
    except Exception as e:
        db.rollback()
        # 如果文件已保存，删除文件
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

def get_resource_type(file_ext: str) -> str:
    """
    根据文件扩展名判断资源类型
    """
    type_mapping = {
        'pdf': '教材',
        'doc': '教案',
        'docx': '教案',
        'ppt': 'PPT',
        'pptx': 'PPT',
        'jpg': '图片',
        'jpeg': '图片',
        'png': '图片',
        'gif': '图片',
        'mp4': '视频',
        'avi': '视频',
        'mov': '视频',
        'xlsx': '习题',
        'xls': '习题'
    }
    return type_mapping.get(file_ext.lower())


def get_current_user_id():
    """获取当前用户ID"""
    # 这里应该从token中获取用户ID
    # 临时返回一个固定值
    return 1


# 获取资源信息接口
@app.get("/resources/{resource_id}", response_model=ResourceResponse)
def read_resource(resource_id: int, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return db_resource


# 更新资源信息接口
@app.put("/resources/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: int, resource: ResourceUpdate, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    if resource.resource_name is not None:
        db_resource.resource_name = resource.resource_name
    if resource.resource_type is not None:
        db_resource.resource_type = resource.resource_type
    if resource.file_path is not None:
        db_resource.file_path = resource.file_path
    db.commit()
    db.refresh(db_resource)
    return db_resource


# 删除资源接口
@app.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    # 检查资源是否存在
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # 删除与资源相关的关键字
    db_keywords = db.query(ResourceKeyword).filter(ResourceKeyword.resource_id == resource_id).all()
    for keyword in db_keywords:
        db.delete(keyword)
    db.commit()
    
    # 删除资源
    db.delete(db_resource)
    db.commit()
    return {"detail": "Resource deleted"}


# 添加关键字接口
@app.post("/resources/{resource_id}/keywords/")
def add_keyword(resource_id: int, keyword: str, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    resource_keyword = ResourceKeyword(resource_id=resource_id, keyword=keyword)
    db.add(resource_keyword)
    db.commit()
    return {"detail": "Keyword added"}


# 通过关键字查找资源接口
@app.get("/resources/keywords/{keyword}")
def get_resources_by_keyword(keyword: str, db: Session = Depends(get_db)):
    db_keywords = db.query(ResourceKeyword).filter(ResourceKeyword.keyword == keyword).all()
    resource_ids = [rk.resource_id for rk in db_keywords]
    resources = db.query(Resource).filter(Resource.id.in_(resource_ids)).all()
    return resources

# 创建 AI 生成资源接口
@app.post("/ai_resources/", response_model=ResourceResponse)
def create_ai_resource(ai_resource: AIResourceCreate, db: Session = Depends(get_db)):
    db_ai_resource = AIResource(
        resource_name=ai_resource.resource_name,
        resource_type=ai_resource.resource_type,
        file_path=ai_resource.file_path,
        user_id=ai_resource.user_id
    )
    db.add(db_ai_resource)
    db.commit()
    db.refresh(db_ai_resource)
    return db_ai_resource

# 通过 user_id 获取 AI 生成资源信息接口
@app.get("/ai_resources/user/{user_id}", response_model=List[ResourceResponse])
def read_ai_resources_by_user(user_id: int, db: Session = Depends(get_db)):
    db_ai_resources = db.query(AIResource).filter(AIResource.user_id == user_id).all()
    if not db_ai_resources:
        raise HTTPException(status_code=404, detail="No AI Resources found for this user")
    return db_ai_resources

# 通过 ID 获取 AI 生成资源信息接口
@app.get("/ai_resources/{resource_id}", response_model=ResourceResponse)
def read_ai_resource(resource_id: int, db: Session = Depends(get_db)):
    db_ai_resource = db.query(AIResource).filter(AIResource.id == resource_id).first()
    if db_ai_resource is None:
        raise HTTPException(status_code=404, detail="AI Resource not found")
    return db_ai_resource

# 更新 AI 生成资源信息接口
@app.put("/ai_resources/{resource_id}", response_model=ResourceResponse)
def update_ai_resource(resource_id: int, ai_resource: AIResourceUpdate, db: Session = Depends(get_db)):
    db_ai_resource = db.query(AIResource).filter(AIResource.id == resource_id).first()
    if db_ai_resource is None:
        raise HTTPException(status_code=404, detail="AI Resource not found")
    if ai_resource.resource_name is not None:
        db_ai_resource.resource_name = ai_resource.resource_name
    if ai_resource.resource_type is not None:
        db_ai_resource.resource_type = ai_resource.resource_type
    if ai_resource.file_path is not None:
        db_ai_resource.file_path = ai_resource.file_path
    if ai_resource.user_id is not None:
        db_ai_resource.user_id = ai_resource.user_id
    db.commit()
    db.refresh(db_ai_resource)
    return db_ai_resource

# 删除 AI 生成资源接口
@app.delete("/ai_resources/{resource_id}")
def delete_ai_resource(resource_id: int, db: Session = Depends(get_db)):
    db_ai_resource = db.query(AIResource).filter(AIResource.id == resource_id).first()
    if db_ai_resource is None:
        raise HTTPException(status_code=404, detail="AI Resource not found")
    db.delete(db_ai_resource)
    db.commit()
    return {"detail": "AI Resource deleted"}

# 复制 AI 生成资源到资源接口
@app.post("/ai_resources/{resource_id}/copy_to_resources/")
def copy_ai_resource_to_resources(resource_id: int, db: Session = Depends(get_db)):
    db_ai_resource = db.query(AIResource).filter(AIResource.id == resource_id).first()
    if db_ai_resource is None:
        raise HTTPException(status_code=404, detail="AI Resource not found")
    new_resource = Resource(
        resource_name=db_ai_resource.resource_name,
        resource_type=db_ai_resource.resource_type,
        file_path=db_ai_resource.file_path
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource

# 创建班级接口
@app.post("/classes/", response_model=ClassResponse)
def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    db_class = Class(
        class_name=class_data.class_name,
        teacher_id=class_data.teacher_id,
        subjects=class_data.subjects
    )
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

# 获取班级信息接口
@app.get("/classes/{class_id}", response_model=ClassResponse)
def read_class(class_id: int, db: Session = Depends(get_db)):
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

# 更新班级信息接口
@app.put("/classes/{class_id}", response_model=ClassResponse)
def update_class(class_id: int, class_data: ClassUpdate, db: Session = Depends(get_db)):
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    if class_data.class_name is not None:
        db_class.class_name = class_data.class_name
    if class_data.teacher_id is not None:
        db_class.teacher_id = class_data.teacher_id
    if class_data.subjects is not None:
        db_class.subjects = class_data.subjects
    db.commit()
    db.refresh(db_class)
    return db_class

# 删除班级接口
@app.delete("/classes/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(db_class)
    db.commit()
    return {"detail": "Class deleted"}

# 添加学生到班级接口
@app.post("/classes/students/", response_model=dict)
def add_student_to_class(class_student: ClassStudentCreate, db: Session = Depends(get_db)):
    db_class_student = ClassStudent(
        class_id=class_student.class_id,
        student_id=class_student.student_id
    )
    db.add(db_class_student)
    db.commit()
    return {"detail": "Student added to class"}

# 查询班级里的学生接口
@app.get("/classes/{class_id}/students")
def get_students_in_class(class_id: int, db: Session = Depends(get_db)):
    students = db.query(ClassStudent).filter(ClassStudent.class_id == class_id).all()
    student_ids = [student.student_id for student in students]
    db_students = db.query(User).filter(User.id.in_(student_ids)).all()
    return db_students

# 删除学生接口
@app.delete("/classes/{class_id}/students/{student_id}")
def delete_student_from_class(class_id: int, student_id: int, db: Session = Depends(get_db)):
    db_class_student = db.query(ClassStudent).filter(ClassStudent.class_id == class_id, ClassStudent.student_id == student_id).first()
    if db_class_student is None:
        raise HTTPException(status_code=404, detail="Student not found in class")
    db.delete(db_class_student)
    db.commit()
    return {"detail": "Student removed from class"}

# 上传班级资源接口
@app.post("/classes/resources/", response_model=dict)
def upload_class_resource(class_resource: ClassResourceCreate, db: Session = Depends(get_db)):
    db_class_resource = ClassResource(
        class_id=class_resource.class_id,
        resource_type=class_resource.resource_type,
        resource_name=class_resource.resource_name,
        file_path=class_resource.file_path,
        uploaded_by=class_resource.uploaded_by
    )
    db.add(db_class_resource)
    db.commit()
    return {"detail": "Class resource uploaded"}

# 获取班级资源接口
@app.get("/classes/{class_id}/resources", response_model=List[ClassResourceResponse])
def get_class_resources(class_id: int, db: Session = Depends(get_db)):
    db_resources = db.query(ClassResource).filter(ClassResource.class_id == class_id).all()
    return db_resources

# 更新班级资源接口
@app.put("/classes/resources/{resource_id}", response_model=dict)
def update_class_resource(resource_id: int, class_resource: ClassResourceUpdate, db: Session = Depends(get_db)):
    db_class_resource = db.query(ClassResource).filter(ClassResource.id == resource_id).first()
    if db_class_resource is None:
        raise HTTPException(status_code=404, detail="Class resource not found")
    if class_resource.class_id is not None:
        db_class_resource.class_id = class_resource.class_id
    if class_resource.resource_type is not None:
        db_class_resource.resource_type = class_resource.resource_type
    if class_resource.resource_name is not None:
        db_class_resource.resource_name = class_resource.resource_name
    if class_resource.file_path is not None:
        db_class_resource.file_path = class_resource.file_path
    if class_resource.uploaded_by is not None:
        db_class_resource.uploaded_by = class_resource.uploaded_by
    db.commit()
    return {"detail": "Class resource updated"}

# 删除班级资源接口
@app.delete("/classes/resources/{resource_id}")
def delete_class_resource(resource_id: int, db: Session = Depends(get_db)):
    db_class_resource = db.query(ClassResource).filter(ClassResource.id == resource_id).first()
    if db_class_resource is None:
        raise HTTPException(status_code=404, detail="Class resource not found")
    db.delete(db_class_resource)
    db.commit()
    return {"detail": "Class resource deleted"}

# 创建教案接口
@app.post("/lesson_plans/", response_model=LessonPlanResponse)
def create_lesson_plan(lesson_plan: LessonPlanCreate, db: Session = Depends(get_db)):
    # 检查教师是否存在
    teacher = db.query(User).filter(User.id == lesson_plan.teacher_id, User.role == 'teacher').first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # 检查班级是否存在
    class_obj = db.query(Class).filter(Class.id == lesson_plan.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # 创建教案
    db_lesson_plan = LessonPlan(
        teacher_id=lesson_plan.teacher_id,
        class_id=lesson_plan.class_id,
        title=lesson_plan.title,
        description=lesson_plan.description,
        file_path=lesson_plan.file_path
    )
    db.add(db_lesson_plan)
    db.commit()
    db.refresh(db_lesson_plan)
    return db_lesson_plan

# 获取教案信息接口
@app.get("/lesson_plans/{lesson_plan_id}", response_model=LessonPlanResponse)
def read_lesson_plan(lesson_plan_id: int, db: Session = Depends(get_db)):
    db_lesson_plan = db.query(LessonPlan).filter(LessonPlan.id == lesson_plan_id).first()
    if db_lesson_plan is None:
        raise HTTPException(status_code=404, detail="Lesson plan not found")
    return db_lesson_plan

# 获取教师的所有教案接口
@app.get("/teachers/{teacher_id}/lesson_plans", response_model=List[LessonPlanResponse])
def read_teacher_lesson_plans(teacher_id: int, db: Session = Depends(get_db)):
    # 检查教师是否存在
    teacher = db.query(User).filter(User.id == teacher_id, User.role == 'teacher').first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # 获取教师的所有教案
    db_lesson_plans = db.query(LessonPlan).filter(LessonPlan.teacher_id == teacher_id).all()
    return db_lesson_plans

# 获取班级的所有教案接口
@app.get("/classes/{class_id}/lesson_plans", response_model=List[LessonPlanResponse])
def read_class_lesson_plans(class_id: int, db: Session = Depends(get_db)):
    # 检查班级是否存在
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # 获取班级的所有教案
    db_lesson_plans = db.query(LessonPlan).filter(LessonPlan.class_id == class_id).all()
    return db_lesson_plans

# 更新教案信息接口
@app.put("/lesson_plans/{lesson_plan_id}", response_model=LessonPlanResponse)
def update_lesson_plan(lesson_plan_id: int, lesson_plan: LessonPlanUpdate, db: Session = Depends(get_db)):
    db_lesson_plan = db.query(LessonPlan).filter(LessonPlan.id == lesson_plan_id).first()
    if db_lesson_plan is None:
        raise HTTPException(status_code=404, detail="Lesson plan not found")
    
    # 更新教案信息
    if lesson_plan.teacher_id is not None:
        # 检查教师是否存在
        teacher = db.query(User).filter(User.id == lesson_plan.teacher_id, User.role == 'teacher').first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        db_lesson_plan.teacher_id = lesson_plan.teacher_id
    
    if lesson_plan.class_id is not None:
        # 检查班级是否存在
        class_obj = db.query(Class).filter(Class.id == lesson_plan.class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        db_lesson_plan.class_id = lesson_plan.class_id
    
    if lesson_plan.title is not None:
        db_lesson_plan.title = lesson_plan.title
    
    if lesson_plan.description is not None:
        db_lesson_plan.description = lesson_plan.description
    
    if lesson_plan.file_path is not None:
        db_lesson_plan.file_path = lesson_plan.file_path
    
    db.commit()
    db.refresh(db_lesson_plan)
    return db_lesson_plan

# 删除教案接口
@app.delete("/lesson_plans/{lesson_plan_id}")
def delete_lesson_plan(lesson_plan_id: int, db: Session = Depends(get_db)):
    db_lesson_plan = db.query(LessonPlan).filter(LessonPlan.id == lesson_plan_id).first()
    if db_lesson_plan is None:
        raise HTTPException(status_code=404, detail="Lesson plan not found")
    db.delete(db_lesson_plan)
    db.commit()
    return {"detail": "Lesson plan deleted"}

# 创建作业接口
@app.post("/assignments/", response_model=AssignmentResponse)
def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):
    # 检查班级是否存在
    class_obj = db.query(Class).filter(Class.id == assignment.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # 创建作业
    db_assignment = Assignment(
        class_id=assignment.class_id,
        title=assignment.title,
        description=assignment.description,
        due_date=assignment.due_date
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

# 获取作业信息接口
@app.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
def read_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if db_assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return db_assignment

# 获取班级的所有作业接口
@app.get("/classes/{class_id}/assignments", response_model=List[AssignmentResponse])
def read_class_assignments(class_id: int, db: Session = Depends(get_db)):
    # 检查班级是否存在
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # 获取班级的所有作业
    db_assignments = db.query(Assignment).filter(Assignment.class_id == class_id).all()
    return db_assignments

# 更新作业信息接口
@app.put("/assignments/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(assignment_id: int, assignment: AssignmentUpdate, db: Session = Depends(get_db)):
    db_assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if db_assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # 更新作业信息
    if assignment.title is not None:
        db_assignment.title = assignment.title
    if assignment.description is not None:
        db_assignment.description = assignment.description
    if assignment.due_date is not None:
        db_assignment.due_date = assignment.due_date
    
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

# 删除作业接口
@app.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if db_assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # 删除作业相关的习题关联
    db.query(AssignmentExercise).filter(AssignmentExercise.assignment_id == assignment_id).delete()
    
    # 删除作业相关的提交记录
    db.query(AssignmentSubmission).filter(AssignmentSubmission.assignment_id == assignment_id).delete()
    
    # 删除作业
    db.delete(db_assignment)
    db.commit()
    return {"detail": "Assignment deleted"}

# 创建习题接口
@app.post("/exercises/", response_model=ExerciseResponse)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    # 检查用户是否存在
    user = db.query(User).filter(User.id == exercise.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 创建习题
    db_exercise = Exercise(
        user_id=exercise.user_id,
        type=exercise.type,
        title=exercise.title,
        content=exercise.content,
        options=exercise.options,
        answers=exercise.answers
    )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

# 获取习题信息接口
@app.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_exercise

# 获取用户创建的所有习题接口
@app.get("/users/{user_id}/exercises", response_model=List[ExerciseResponse])
def read_user_exercises(user_id: int, db: Session = Depends(get_db)):
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 获取用户创建的所有习题
    db_exercises = db.query(Exercise).filter(Exercise.user_id == user_id).all()
    return db_exercises

# 更新习题信息接口
@app.put("/exercises/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(exercise_id: int, exercise: ExerciseUpdate, db: Session = Depends(get_db)):
    db_exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # 更新习题信息
    if exercise.type is not None:
        db_exercise.type = exercise.type
    if exercise.title is not None:
        db_exercise.title = exercise.title
    if exercise.content is not None:
        db_exercise.content = exercise.content
    if exercise.options is not None:
        db_exercise.options = exercise.options
    if exercise.answers is not None:
        db_exercise.answers = exercise.answers
    
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

# 删除习题接口
@app.delete("/exercises/{exercise_id}")
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # 删除习题相关的作业关联
    db.query(AssignmentExercise).filter(AssignmentExercise.exercise_id == exercise_id).delete()
    
    # 删除习题
    db.delete(db_exercise)
    db.commit()
    return {"detail": "Exercise deleted"}

# 添加习题到作业接口
@app.post("/assignments/exercises/", response_model=dict)
def add_exercise_to_assignment(assignment_exercise: AssignmentExerciseCreate, db: Session = Depends(get_db)):
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_exercise.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # 检查习题是否存在
    exercise = db.query(Exercise).filter(Exercise.id == assignment_exercise.exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # 检查是否已经添加过
    existing = db.query(AssignmentExercise).filter(
        AssignmentExercise.assignment_id == assignment_exercise.assignment_id,
        AssignmentExercise.exercise_id == assignment_exercise.exercise_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Exercise already added to assignment")
    
    # 添加习题到作业
    db_assignment_exercise = AssignmentExercise(
        assignment_id=assignment_exercise.assignment_id,
        exercise_id=assignment_exercise.exercise_id
    )
    db.add(db_assignment_exercise)
    db.commit()
    return {"detail": "Exercise added to assignment"}

# 获取作业的所有习题接口
@app.get("/assignments/{assignment_id}/exercises", response_model=List[ExerciseResponse])
def read_assignment_exercises(assignment_id: int, db: Session = Depends(get_db)):
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # 获取作业的所有习题
    exercise_ids = db.query(AssignmentExercise.exercise_id).filter(
        AssignmentExercise.assignment_id == assignment_id
    ).all()
    exercise_ids = [id[0] for id in exercise_ids]
    
    exercises = db.query(Exercise).filter(Exercise.id.in_(exercise_ids)).all()
    return exercises

# 从作业中移除习题接口
@app.delete("/assignments/{assignment_id}/exercises/{exercise_id}")
def remove_exercise_from_assignment(assignment_id: int, exercise_id: int, db: Session = Depends(get_db)):
    # 检查关联是否存在
    assignment_exercise = db.query(AssignmentExercise).filter(
        AssignmentExercise.assignment_id == assignment_id,
        AssignmentExercise.exercise_id == exercise_id
    ).first()
    if not assignment_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found in assignment")
    
    # 移除习题
    db.delete(assignment_exercise)
    db.commit()
    return {"detail": "Exercise removed from assignment"}

# 提交作业接口
@app.post("/assignments/submissions/", response_model=AssignmentSubmissionResponse)
def submit_assignment(submission: AssignmentSubmissionCreate, db: Session = Depends(get_db)):
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # 检查学生是否存在
    student = db.query(User).filter(User.id == submission.student_id, User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # 检查是否已经提交过
    existing = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == submission.assignment_id,
        AssignmentSubmission.student_id == submission.student_id
    ).first()
    
    if existing:
        # 更新已有提交
        existing.answers = submission.answers
        existing.submission_date = datetime.datetime.now()  # 使用本地时间
        db.commit()
        db.refresh(existing)
        return existing
    
    # 创建新提交
    db_submission = AssignmentSubmission(
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        answers=submission.answers
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

# 获取作业提交信息接口
@app.get("/assignments/submissions/{submission_id}", response_model=AssignmentSubmissionResponse)
def read_submission(submission_id: int, db: Session = Depends(get_db)):
    db_submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return db_submission

# 获取作业的所有提交接口
@app.get("/assignments/{assignment_id}/submissions", response_model=List[AssignmentSubmissionResponse])
def read_assignment_submissions(assignment_id: int, db: Session = Depends(get_db)):
    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # 获取作业的所有提交
    db_submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id
    ).all()
    return db_submissions

# 获取学生的所有提交接口
@app.get("/students/{student_id}/submissions", response_model=List[AssignmentSubmissionResponse])
def read_student_submissions(student_id: int, db: Session = Depends(get_db)):
    # 检查学生是否存在
    student = db.query(User).filter(User.id == student_id, User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # 获取学生的所有提交
    db_submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.student_id == student_id
    ).all()
    return db_submissions

# 评分作业提交接口
@app.put("/assignments/submissions/{submission_id}", response_model=AssignmentSubmissionResponse)
def grade_submission(submission_id: int, submission: AssignmentSubmissionUpdate, db: Session = Depends(get_db)):
    db_submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # 更新提交信息
    if submission.answers is not None:
        db_submission.answers = submission.answers
    if submission.grade is not None:
        db_submission.grade = submission.grade
    if submission.feedback is not None:
        db_submission.feedback = submission.feedback
    
    db.commit()
    db.refresh(db_submission)
    return db_submission

# 删除作业提交接口
@app.delete("/assignments/submissions/{submission_id}")
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    db_submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # 删除提交
    db.delete(db_submission)
    db.commit()
    return {"detail": "Submission deleted"}

# 创建学习资源推荐接口
@app.post("/recommendations/", response_model=RecommendationResponse)
def create_recommendation(recommendation: RecommendationCreate, db: Session = Depends(get_db)):
    # 检查学生是否存在
    student = db.query(User).filter(User.id == recommendation.student_id, User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # 检查资源是否存在
    resource = db.query(Resource).filter(Resource.id == recommendation.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # 检查是否已经推荐过
    existing = db.query(Recommendation).filter(
        Recommendation.student_id == recommendation.student_id,
        Recommendation.resource_id == recommendation.resource_id
    ).first()
    
    if existing:
        # 更新已有推荐
        if recommendation.priority is not None:
            existing.priority = recommendation.priority
        if recommendation.reason is not None:
            existing.reason = recommendation.reason
        existing.recommended_at = datetime.datetime.now()  # 使用本地时间
        existing.is_viewed = 0  # 重置为未查看
        db.commit()
        db.refresh(existing)
        return existing
    
    # 创建新推荐
    db_recommendation = Recommendation(
        student_id=recommendation.student_id,
        resource_id=recommendation.resource_id,
        priority=recommendation.priority,
        reason=recommendation.reason
    )
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

# 获取推荐信息接口
@app.get("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
def read_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    db_recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if db_recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return db_recommendation

# 获取学生的所有推荐接口
@app.get("/students/{student_id}/recommendations", response_model=List[RecommendationResponse])
def read_student_recommendations(student_id: int, db: Session = Depends(get_db)):
    # 检查学生是否存在
    student = db.query(User).filter(User.id == student_id, User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 调用 recommend_resources 生成新的推荐
    recommend_resources_students(db=db, student_id=student_id)
    # 提交事务以确保新推荐被保存
    db.commit()
    
    # 获取学生的所有推荐，按优先级降序排列
    db_recommendations = db.query(Recommendation).filter(
        Recommendation.student_id == student_id
    ).order_by(Recommendation.priority.desc()).all()
    return db_recommendations

# 更新推荐信息接口
@app.put("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
def update_recommendation(recommendation_id: int, recommendation: RecommendationUpdate, db: Session = Depends(get_db)):
    db_recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if db_recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # 更新推荐信息
    if recommendation.priority is not None:
        db_recommendation.priority = recommendation.priority
    if recommendation.reason is not None:
        db_recommendation.reason = recommendation.reason
    if recommendation.is_viewed is not None:
        db_recommendation.is_viewed = recommendation.is_viewed
    
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

# 标记推荐为已查看接口
@app.put("/recommendations/{recommendation_id}/view", response_model=RecommendationResponse)
def mark_recommendation_viewed(recommendation_id: int, db: Session = Depends(get_db)):
    db_recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if db_recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # 标记为已查看
    db_recommendation.is_viewed = 1
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

# 删除推荐接口
@app.delete("/recommendations/{recommendation_id}")
def delete_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    db_recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if db_recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # 删除推荐
    db.delete(db_recommendation)
    db.commit()
    return {"detail": "Recommendation deleted"}

# 批量创建推荐接口
@app.post("/recommendations/batch", response_model=dict)
def create_recommendations_batch(recommendations: List[RecommendationCreate], db: Session = Depends(get_db)):
    created_count = 0
    updated_count = 0
    
    for rec in recommendations:
        # 检查学生是否存在
        student = db.query(User).filter(User.id == rec.student_id, User.role == 'student').first()
        if not student:
            continue
        
        # 检查资源是否存在
        resource = db.query(Resource).filter(Resource.id == rec.resource_id).first()
        if not resource:
            continue
        
        # 检查是否已经推荐过
        existing = db.query(Recommendation).filter(
            Recommendation.student_id == rec.student_id,
            Recommendation.resource_id == rec.resource_id
        ).first()
        
        if existing:
            # 更新已有推荐
            if rec.priority is not None:
                existing.priority = rec.priority
            if rec.reason is not None:
                existing.reason = rec.reason
            existing.recommended_at = datetime.datetime.now()  # 使用本地时间
            existing.is_viewed = 0  # 重置为未查看
            updated_count += 1
        else:
            # 创建新推荐
            db_recommendation = Recommendation(
                student_id=rec.student_id,
                resource_id=rec.resource_id,
                priority=rec.priority,
                reason=rec.reason
            )
            db.add(db_recommendation)
            created_count += 1
    
    db.commit()
    return {"detail": f"Created {created_count} recommendations, updated {updated_count} recommendations"}

# 创建课程基础信息接口
@app.post("/course/base-info/", response_model=CourseBaseInfoResponse)
def create_course_base_info(course_info: CourseBaseInfoCreate, db: Session = Depends(get_db)):
    try:
        # 验证教师是否存在
        teacher = db.query(User).filter(
            User.id == course_info.teacher_id,
            User.role == 'teacher'
        ).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="教师不存在")

        # 创建课程基础信息记录
        db_course_info = CourseBaseInfo(
            name=course_info.name,
            theme=course_info.theme,
            objective=course_info.objective,
            target_class=course_info.target_class,
            duration=course_info.duration,
            teacher_id=course_info.teacher_id,
            features=course_info.features,
            special_requirements=course_info.special_requirements
        )
        
        # 保存到数据库
        db.add(db_course_info)
        db.commit()
        db.refresh(db_course_info)
        
        return db_course_info
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建课程基础信息失败: {str(e)}")

# 获取教师的所有课程基础信息接口
@app.get("/course/base-info/teacher/{teacher_id}", response_model=List[CourseBaseInfoResponse])
def get_teacher_course_base_info(teacher_id: int, db: Session = Depends(get_db)):
    try:
        # 验证教师是否存在
        teacher = db.query(User).filter(
            User.id == teacher_id,
            User.role == 'teacher'
        ).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="教师不存在")
            
        # 获取该教师的所有课程基础信息
        course_info_list = db.query(CourseBaseInfo).filter(
            CourseBaseInfo.teacher_id == teacher_id
        ).all()
        
        return course_info_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取课程基础信息失败: {str(e)}")

# 获取单个课程基础信息接口
@app.get("/course/base-info/{course_id}", response_model=CourseBaseInfoResponse)
def get_course_base_info(course_id: int, db: Session = Depends(get_db)):
    try:
        course_info = db.query(CourseBaseInfo).filter(
            CourseBaseInfo.id == course_id
        ).first()
        
        if not course_info:
            raise HTTPException(status_code=404, detail="课程基础信息不存在")
            
        return course_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取课程基础信息失败: {str(e)}")

# 更新课程基础信息接口
@app.put("/course/base-info/{course_id}", response_model=CourseBaseInfoResponse)
def update_course_base_info(course_id: int, course_info: CourseBaseInfoCreate, db: Session = Depends(get_db)):
    try:
        # 获取现有课程信息
        db_course_info = db.query(CourseBaseInfo).filter(
            CourseBaseInfo.id == course_id
        ).first()
        
        if not db_course_info:
            raise HTTPException(status_code=404, detail="课程基础信息不存在")
            
        # 更新信息
        for key, value in course_info.dict().items():
            setattr(db_course_info, key, value)
            
        db.commit()
        db.refresh(db_course_info)
        return db_course_info
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新课程基础信息失败: {str(e)}")

# 删除课程基础信息接口
@app.delete("/course/base-info/{course_id}")
def delete_course_base_info(course_id: int, db: Session = Depends(get_db)):
    try:
        # 获取课程信息
        db_course_info = db.query(CourseBaseInfo).filter(
            CourseBaseInfo.id == course_id
        ).first()
        
        if not db_course_info:
            raise HTTPException(status_code=404, detail="课程基础信息不存在")
            
        # 删除课程信息
        db.delete(db_course_info)
        db.commit()
        return {"detail": "课程基础信息已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除课程基础信息失败: {str(e)}")

# 生成教案接口
@app.post("/lesson-plans/generate/", response_model=GenerateLessonPlanResponse)
def generate_lesson_plan(request: GenerateLessonPlanRequest, db: Session = Depends(get_db)):
    try:
        # 获取课程基础信息
        course_info = db.query(CourseBaseInfo).filter(
            CourseBaseInfo.id == request.course_id
        ).first()
        if not course_info:
            raise HTTPException(status_code=404, detail="课程基础信息不存在")
        # AI生成教案服务
        #AI需要输入为 course_info.name（课程名称） course_info.theme（课程主题） course_info.objective（教学目标）course_info.duration（课时长度） request.suggestions（修改意见）
        mock_content = f"""
# {course_info.name}教案
                
## 基本信息
- 课程主题：{course_info.theme}
- 教学目标：{course_info.objective}
- 目标班级：{course_info.target_class}
- 课时长度：{course_info.duration}
                
## 教学内容

"""
        # 如果有修改建议，添加相应的内容
        if request.suggestions:
            #一定要保存教案才能使用!!!
            lesson_plan = db.query(LessonPlan).filter(
                LessonPlan.teacher_id == course_info.teacher_id,
                LessonPlan.course_id == course_info.id
            ).first()
            #也可以注释掉但是大模型就不知道原来教案了
            if not lesson_plan:
                raise HTTPException(status_code=404, detail="原始教案未保存")
            if not lesson_plan.file_path:
                raise HTTPException(status_code=404, detail="原始教案未上传")
            with open(lesson_plan.file_path, "r", encoding="utf-8") as file:
                lesson_content = file.read()
            prompt=continous_generate_Teachingplan.format(suggestions=request.suggestions,old_teachingplan=lesson_content or " ")
            response=safe_call_llm(prompt)
            print(response)
            mock_content += f"""
- 已采纳修改建议：{request.suggestions}
根据修改建议调整后的内容：

"""
            mock_content+=response
        else:
            prompt=initial_generate_Teachingplan.format(name=course_info.name,theme=course_info.theme,objective=course_info.objective,duration=course_info.duration)
            print(prompt)
            response=safe_call_llm(prompt)
            print(response)
            mock_content += response
        
        return {"content": mock_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成教案失败: {str(e)}")

# 保存教案内容接口
@app.post("/lesson-plans/save/", response_model=LessonPlanResponse)
def save_lesson_plan(request: SaveLessonPlanRequest, db: Session = Depends(get_db)):
    try:
        # 检查课程是否存在
        course = db.query(CourseBaseInfo).filter(CourseBaseInfo.id == request.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 生成文件名（使用课程名称）
        filename = f"{course.name}.txt"
        
        # 确保目录存在
        if not os.path.exists('data/教案'):
            os.makedirs('data/教案')
            
        # 保存文件
        file_path = os.path.join('data/教案', filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(request.content)

        # 检查是否已存在该教师和课程的教案
        lesson_plan = db.query(LessonPlan).filter(
            LessonPlan.teacher_id == course.teacher_id,
            LessonPlan.course_id == course.id
        ).first()

        if lesson_plan:
            # 更新现有教案
            lesson_plan.title = course.name
            lesson_plan.description = request.content[:200]  # 使用前200个字符作为描述
            lesson_plan.file_path = file_path
            lesson_plan.updated_at = datetime.datetime.now()  # 使用本地时间
        else:
            # 创建新教案
            lesson_plan = LessonPlan(
                teacher_id=course.teacher_id,
                class_id=course.target_class,
                course_id=course.id,  # 设置课程ID
                title=course.name,
                description=request.content[:200],  # 使用前200个字符作为描述
                file_path=file_path
            )
            db.add(lesson_plan)

        db.commit()
        db.refresh(lesson_plan)
        return lesson_plan

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 获取教师的所有班级接口
@app.get("/teachers/{teacher_id}/classes", response_model=List[ClassResponse])
def get_teacher_classes(teacher_id: int, db: Session = Depends(get_db)):
    try:
        # 验证教师是否存在
        teacher = db.query(User).filter(
            User.id == teacher_id,
            User.role == 'teacher'
        ).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="教师不存在")
            
        # 获取该教师的所有班级
        classes = db.query(Class).filter(
            Class.teacher_id == teacher_id
        ).all()
        
        return classes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取教师班级失败: {str(e)}")

# 生成习题接口
@app.post("/exercises/generate/", response_model=GenerateExercisesResponse)
def generate_exercises(request: GenerateExercisesRequest, db: Session = Depends(get_db)):
    try:
        # 检查课程是否存在
        course = db.query(CourseBaseInfo).filter(CourseBaseInfo.id == request.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 如果提供了要重新生成的题目ID列表，则只重新生成这些题目
        if request.selected_ids and len(request.selected_ids) > 0:
            # 获取原有题目信息
            existing_exercises = db.query(Exercise).filter(
                Exercise.id.in_(request.selected_ids)
            ).all()
            
            if not existing_exercises:
                # 如果没有找到任何题目，生成新题目而不是报错
                existing_exercises = []
        else:
            existing_exercises = []

        # 生成题目
        exercises = []
        type_map = {
            'choice': '单选',
            'multiple': '多选',
            'judgment': '判断',
            'blank': '填空',
            'short': '简答'
        }
        
        # 如果是重新生成已有题目
        if existing_exercises:
            for ex in existing_exercises:
                options = None
                if ex.type in ['单选', '多选']:
                    options = json.dumps(["选项A", "选项B", "选项C", "选项D"])
                elif ex.type == '判断':
                    options = json.dumps(["正确", "错误"])
                #ai输入应为 request.suggestions（修改建议），ex.content（当前题目内容），ex.answers（当前题目答案），exercise_type（练习题类型） request.difficulty（难度）course.name（课程名称） course.theme（课程主题） course.objective（教学目标）
                response=generate_exercise_continous_part(request.suggestions, ex.content, ex.answers, ex.type,request.difficulty, course.name, course.theme, course.objective)
                try:
                    ee = exercise(**response)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"生成JSON格式错误：{str(e)}")
                print(ee)
                exercises.append(ExerciseItem(
                    id=ex.id,
                    type=ex.type,
                    title=f"重新生成的{ex.type}（难度：{request.difficulty}）",
                    content=ee.content,
                    options=ee.options,
                    answers=ee.answer
                ))
        # 生成新题目
        else:
            for type_key, count in request.types.items():
                if count and count > 0 and type_key in type_map:
                    for i in range(int(count)):
                        exercise_type = type_map[type_key]
                        options = None
                        if exercise_type in ['单选', '多选']:
                            options = json.dumps(["选项A", "选项B", "选项C", "选项D"])
                        elif exercise_type == '判断':
                            options = json.dumps(["正确", "错误"])
                        # ai输入应为 request.suggestions（修改建议）,exercise_type（练习题类型） request.difficulty（难度）course.name（课程名称） course.theme（课程主题） course.objective（教学目标）
                        if request.suggestions:
                            response=generate_exercise_continous_all(request.suggestions,exercise_type, request.difficulty, course.name, course.theme, course.objective)
                        else:
                        # ai输入应为 exercise_type（练习题类型） request.difficulty（难度）course.name（课程名称） course.theme（课程主题） course.objective（教学目标）
                            response=generate_exercise_initial(exercise_type,request.difficulty,course.name,course.theme,course.objective)

                        try:
                            ee = exercise(**response)
                        except Exception as e:
                            raise HTTPException(status_code=500, detail=f"生成JSON格式错误：{str(e)}")
                        print(ee)
                        exercises.append(ExerciseItem(
                            type=exercise_type,
                            title=f"新生成的{exercise_type}（难度：{request.difficulty}）",
                            content=ee.content,
                            options=json.dumps(ee.options),
                            answers=ee.answer
                        ))

        return GenerateExercisesResponse(exercises=exercises)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成题目失败：{str(e)}")


# 保存习题接口
@app.post("/exercises/save/", response_model=List[ExerciseResponse])
def save_exercises(request: SaveExercisesRequest, db: Session = Depends(get_db)):
    try:
        # 检查课程是否存在
        course = db.query(CourseBaseInfo).filter(CourseBaseInfo.id == request.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        saved_exercises = []
        for exercise_item in request.exercises:
            # 如果题目已存在，更新它
            if exercise_item.id:
                exercise = db.query(Exercise).filter(Exercise.id == exercise_item.id).first()
                if exercise:
                    exercise.type = exercise_item.type
                    exercise.title = exercise_item.title
                    exercise.content = exercise_item.content
                    exercise.options = exercise_item.options
                    exercise.answers = exercise_item.answers
                    exercise.updated_at = datetime.datetime.now()  # 使用本地时间
                else:
                    # 如果指定的ID不存在，创建新题目
                    exercise = Exercise(
                        course_id=request.course_id,
                        user_id=course.teacher_id,
                        **exercise_item.dict(exclude={'id'})
                    )
                    db.add(exercise)
            else:
                # 创建新题目
                exercise = Exercise(
                    course_id=request.course_id,
                    user_id=course.teacher_id,
                    **exercise_item.dict(exclude={'id'})
                )
                db.add(exercise)

            db.commit()
            db.refresh(exercise)
            saved_exercises.append(exercise)

        return saved_exercises
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 资源推荐接口
@app.get("/resources/recommend/{course_id}", response_model=ResourceRecommendResponse)
def recommend_resources(course_id: int, db: Session = Depends(get_db)):
    try:

        # 检查课程是否存在
        course = db.query(CourseBaseInfo).filter(CourseBaseInfo.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        # 获取所有资源
        resources = db.query(Resource).all()

        # AI生成视频 储存在本地的向量库
        prompt = video_generate_prompt.format(name=course.name, theme=course.theme, objective=course.objective)
        print(prompt)
        video_path = video_llm(prompt)
        print("开始存储")
        store_video(video_path)
        print("存储完成")
        # 创建AI生成视频记录
        ai_video_resource = AIResource(
            resource_name=f"{course.name}_视频",
            resource_type="视频",
            file_path=video_path
        )
        db.add(ai_video_resource)
        db.flush()  # 获取新资源的ID

        # AI生成ppt,储存在本地的向量库
        prompt = ppt_generate_prompt.format(name=course.name, theme=course.theme, objective=course.objective)
        ppt_path = ppt_llm(prompt)
        store_ppt(ppt_path, prompt)
        similiary_prompt = prompt
        # 创建AI生成PPT记录
        ai_ppt_resource = AIResource(
            resource_name=f"{course.name}_PPT",
            resource_type="PPT",
            file_path=ppt_path
        )
        db.add(ai_ppt_resource)
        db.flush()  # 获取新资源的ID
        # AI生成图片 储存在本地的向量库
        prompt = picture_generate_prompt.format(name=course.name, theme=course.theme, objective=course.objective)
        picture_path = picture_llm(prompt)
        store_picture(picture_path)
        # 创建AI生成图片记录
        ai_picture_resource = AIResource(
            resource_name=f"{course.name}_图片",
            resource_type="图片",
            file_path=picture_path
        )
        db.add(ai_picture_resource)
        db.flush()  # 获取新资源的ID
        db.commit()

        ai_resources = db.query(AIResource).all()

        # 初始化返回数据
        courseware_list = []
        video_list = []
        image_list = []

        # 处理常规资源
        for resource in resources:
            print(resource.resource_type)
            # 与问题进行检索获得匹配的分数
            if resource.resource_type == '图片':
                matchRate = get_Rate_picture(resource.file_path,course.name,course.theme,course.objective)
            if resource.resource_type == 'PPT':
                matchRate = get_Rate_ppt(resource.file_path,course.name,course.theme,course.objective,"无关")
            if resource.resource_type == '视频':
                matchRate = get_Rate_video(resource.file_path,course.name,course.theme,course.objective)

            resource_data = {
                "id": resource.id,
                "name": resource.resource_name,
                "path": resource.file_path,
                "matchRate": matchRate,
                "is_ai_generated": False
            }

            if resource.resource_type == 'PPT':
                courseware_list.append(resource_data)
            elif resource.resource_type == '视频':
                video_list.append(resource_data)
            elif resource.resource_type == '图片':
                image_list.append(resource_data)

        # 处理AI生成的资源
        for resource in ai_resources:
            print(resource.resource_type)

            # 计算匹配度
            if resource.resource_type == '图片':
                print('图片')
                matchRate = get_Rate_picture(resource.file_path, course.name, course.theme, course.objective)
            elif resource.resource_type == 'PPT':
                print('PPT')
                matchRate = get_Rate_ppt(resource.file_path, course.name, course.theme, course.objective, '哈哈哈')
            elif resource.resource_type == '视频':
                print('视频')
                matchRate = get_Rate_video(resource.file_path, course.name, course.theme, course.objective)

            resource_data = {
                "id": 100000 + resource.id,  # 统一编号，避免 ai_ 前缀
                "name": resource.resource_name,
                "path": resource.file_path,
                "matchRate": matchRate,
                "is_ai_generated": True
            }

            # 根据类型分类存储
            if resource.resource_type == 'PPT':
                print("?PPT")
                courseware_list.append(resource_data)
            elif resource.resource_type == '视频':
                print("?视频")
                video_list.append(resource_data)
            elif resource.resource_type == '图片':
                print("?图片")
                image_list.append(resource_data)

        print('start 3 list')
        # 取前三个推荐资源
        top_courseware = sorted(courseware_list, key=lambda x: x["matchRate"], reverse=True)[:3]
        top_video = sorted(video_list, key=lambda x: x["matchRate"], reverse=True)[:3]
        top_image = sorted(image_list, key=lambda x: x["matchRate"], reverse=True)[:3]
        print('finish 3 list')

        # **仅存入前三条推荐资源中的 AI 资源**
        recommended_ai_resources = [
            res for res in (top_courseware + top_video + top_image) if res["is_ai_generated"]
        ]

        print('finish ai list')

        # 插入 AI 资源到 resources 表
        for res in recommended_ai_resources:
            new_resource = Resource(
                id=res["id"],  # 这里使用 AI 资源编号
                resource_name=res["name"],
                resource_type="PPT" if res in top_courseware else
                "视频" if res in top_video else
                "图片",
                file_path=res["path"]
            )
            db.add(new_resource)
        print('finish insert')
        db.commit()  # 提交事务，存入 AI 资源
        print('finish commit')
        # 返回推荐资源（前 3 个，保留匹配度）
        return {
            "courseware": [{**res, "matchRate": round(res["matchRate"], 3)} for res in top_courseware],
            "video": [{**res, "matchRate": round(res["matchRate"], 3)} for res in top_video],
            "image": [{**res, "matchRate": round(res["matchRate"], 3)} for res in top_image]
        }

        # # 处理AI生成的资源
        # for resource in ai_resources:
        #     # 获取检索分数
        #     # 与问题进行检索获得匹配的分数
        #     print(resource.resource_type)
        #     if resource.resource_type == '图片':
        #         print('图片')
        #         matchRate = get_Rate_picture(resource.file_path,course.name,course.theme,course.objective)
        #     if resource.resource_type == 'PPT':
        #         print('PPT')
        #         matchRate = get_Rate_ppt(resource.file_path,course.name,course.theme,course.objective,'哈哈哈')
        #     if resource.resource_type == '视频':
        #         print('视频')
        #         matchRate = get_Rate_video(resource.file_path,course.name,course.theme,course.objective)
        #     print(1)
        #     resource_data = {
        #         "id": f"ai_{resource.id}",  # 添加ai_前缀以区分
        #         "name": resource.resource_name,
        #         "path": resource.file_path,
        #         "matchRate": matchRate,
        #         "is_ai_generated": True
        #     }
        #     print(resource_data)
        #     print(resource.resource_type)
        #     if resource.resource_type == 'PPT':
        #         print("?PPT")
        #         courseware_list.append(resource_data)
        #     elif resource.resource_type == '视频':
        #         print("?视频")
        #         video_list.append(resource_data)
        #     elif resource.resource_type == '图片':
        #         print("?图片")
        #         image_list.append(resource_data)
        #     print(resource)
        # # return {
        # #     # "courseware": courseware_list,
        # #     # "video": video_list,
        # #     # "image": image_list
        # #     "courseware": sorted(courseware_list, key=lambda x: x["matchRate"], reverse=True)[:3],  # 取前三个PPT
        # #     "video": sorted(video_list, key=lambda x: x["matchRate"], reverse=True)[:3],  # 取前三个视频
        # #     "image": sorted(image_list, key=lambda x: x["matchRate"], reverse=True)[:3]  # 取前三个图片
        # # }
        # return {
        #     "courseware": [
        #         {**res, "matchRate": round(res["matchRate"], 3)}
        #         for res in sorted(courseware_list, key=lambda x: x["matchRate"], reverse=True)[:3]
        #     ],
        #     "video": [
        #         {**res, "matchRate": round(res["matchRate"], 3)}
        #         for res in sorted(video_list, key=lambda x: x["matchRate"], reverse=True)[:3]
        #     ],
        #     "image": [
        #         {**res, "matchRate": round(res["matchRate"], 3)}
        #         for res in sorted(image_list, key=lambda x: x["matchRate"], reverse=True)[:3]
        #     ]
        # }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/resources/save/")
def save_selected_resources(request: SaveResourcesRequest, db: Session = Depends(get_db)):
    try:
        # 检查课程是否存在
        course = db.query(CourseBaseInfo).filter(CourseBaseInfo.id == request.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 更新所有资源的选中状态
        for resource_type, resource_ids in request.selected_resources.items():
            # 先将该课程所有该类型的资源标记为未选中
            db.query(CourseResource).filter(
                CourseResource.course_id == request.course_id,
                CourseResource.resource_type == resource_type.upper()
            ).update({"is_selected": 0})
            
            if not resource_ids:
                continue

            # 分离普通资源ID和AI生成资源ID
            normal_ids = []
            ai_resource_ids = []
            
            for rid in resource_ids:
                if isinstance(rid, str) and rid.startswith('ai_'):
                    ai_resource_ids.append(int(rid[3:]))  # 移除'ai_'前缀
                else:
                    normal_ids.append(int(rid))

            # 处理普通资源
            if normal_ids:
                # 获取选中的资源信息
                resources = db.query(Resource).filter(Resource.id.in_(normal_ids)).all()
                for resource in resources:
                    # 检查是否已存在对应的CourseResource记录
                    course_resource = db.query(CourseResource).filter(
                        CourseResource.course_id == request.course_id,
                        CourseResource.resource_type == resource.resource_type,
                        CourseResource.resource_name == resource.resource_name
                    ).first()
                    
                    if course_resource:
                        # 如果存在，更新选中状态
                        course_resource.is_selected = 1
                    else:
                        # 如果不存在，创建新记录
                        course_resource = CourseResource(
                            course_id=request.course_id,
                            resource_type=resource.resource_type,
                            resource_name=resource.resource_name,
                            file_path=resource.file_path,
                            is_selected=1
                        )
                        db.add(course_resource)

            # 处理AI生成的资源
            if ai_resource_ids:
                for ai_rid in ai_resource_ids:
                    ai_resource = db.query(AIResource).filter(AIResource.id == ai_rid).first()
                    if ai_resource:
                        # 将文件从临时目录移动到正式目录
                        if ai_resource.file_path.startswith('backend/data/temp/'):
                            new_path = ai_resource.file_path.replace('backend/data/temp/', 'data/')
                            os.makedirs(os.path.dirname(new_path), exist_ok=True)
                            if os.path.exists(ai_resource.file_path):
                                os.rename(ai_resource.file_path, new_path)
                                
                            # 创建新的Resource记录
                            new_resource = Resource(
                                resource_name=ai_resource.resource_name,
                                resource_type=ai_resource.resource_type,
                                file_path=new_path
                            )
                            db.add(new_resource)
                            db.flush()  # 获取新资源的ID
                            
                            # 创建CourseResource记录
                            course_resource = CourseResource(
                                course_id=request.course_id,
                                resource_type=ai_resource.resource_type,
                                resource_name=ai_resource.resource_name,
                                file_path=new_path,
                                is_selected=1
                            )
                            db.add(course_resource)
                            
                            # 删除AI资源记录
                            db.delete(ai_resource)

        db.commit()
        return {"message": "资源保存成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


class CompleteLessonPreparationRequest(BaseModel):
    course_id: int
    teacher_id: int
    lesson_plan_id: int
    selected_resources: dict
    exercises: Optional[dict] = None


@app.post("/lesson-preparation/complete/", response_model=dict)
def complete_lesson_preparation(request: CompleteLessonPreparationRequest, db: Session = Depends(get_db)):
    try:
        # 1. 验证课程是否存在
        course = db.query(CourseBaseInfo).filter(CourseBaseInfo.id == request.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 2. 验证教师是否存在
        teacher = db.query(User).filter(User.id == request.teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="教师不存在")

        # 3. 验证教案是否存在
        lesson_plan = db.query(LessonPlan).filter(LessonPlan.id == request.lesson_plan_id).first()
        if not lesson_plan:
            raise HTTPException(status_code=404, detail="教案不存在")

        # 4. 创建备课记录
        # 格式化习题数据
        exercises_data = None
        if request.exercises and 'selected_ids' in request.exercises:
            exercises = db.query(Exercise).filter(
                Exercise.id.in_(request.exercises['selected_ids'])
            ).all()
            if exercises:
                exercises_data = [{
                    'id': exercise.id,
                    'type': exercise.type,
                    'title': exercise.title,
                    'content': exercise.content,
                    'options': exercise.options,
                    'answers': exercise.answers
                } for exercise in exercises]

        preparation = LessonPreparation(
            course_id=request.course_id,
            teacher_id=request.teacher_id,
            lesson_plan_id=request.lesson_plan_id,
            selected_resources=request.selected_resources,
            exercises=exercises_data,  # 保存格式化后的习题数据
            preparation_date=datetime.datetime.now()  # 使用本地时间
        )
        db.add(preparation)
        
        # 5. 清理未被选中的AI生成资源
        # 获取所有选中的AI资源ID
        selected_ai_resources = []
        for resource_type, resources in request.selected_resources.items():
            for resource_id in resources:
                if isinstance(resource_id, str) and resource_id.startswith('ai_'):
                    selected_ai_resources.append(int(resource_id[3:]))
        
        # 删除未被选中的AI资源
        if selected_ai_resources:  # 只有当有选中的AI资源时才执行删除
            db.query(AIResource).filter(
                AIResource.user_id == request.teacher_id,  # 确保只删除该教师的资源
                ~AIResource.id.in_(selected_ai_resources)
            ).delete(synchronize_session=False)
        
        # 6. 清理未被选中的习题（如果有）
        if request.exercises and 'selected_ids' in request.exercises:
            selected_exercises = request.exercises['selected_ids']
            if selected_exercises:  # 只有当有选中的习题时才执行删除
                db.query(Exercise).filter(
                    Exercise.user_id == request.teacher_id,  # 确保只删除该教师的习题
                    Exercise.course_id == request.course_id,
                    ~Exercise.id.in_(selected_exercises)
                ).delete(synchronize_session=False)
        
        db.commit()
        return {"message": "备课完成，数据已保存", "preparation_id": preparation.id}
        
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lesson-preparation/history/{teacher_id}", response_model=List[dict])
def get_lesson_preparation_history(teacher_id: int, db: Session = Depends(get_db)):
    try:
        preparations = db.query(LessonPreparation).filter(
            LessonPreparation.teacher_id == teacher_id
        ).order_by(LessonPreparation.preparation_date.desc()).all()
        
        result = []
        for prep in preparations:
            # 获取课程信息
            course = db.query(CourseBaseInfo).filter(
                CourseBaseInfo.id == prep.course_id
            ).first()
            
            # 获取教案信息
            lesson_plan = db.query(LessonPlan).filter(
                LessonPlan.id == prep.lesson_plan_id
            ).first()
            
            # 获取班级信息
            class_name = None
            if course and course.target_class:
                class_obj = db.query(Class).filter(Class.id == course.target_class).first()
                if class_obj:
                    class_name = class_obj.class_name
            
            result.append({
                "id": prep.id,
                "course_name": course.name if course else None,
                "target_class": class_name,  # 使用班级名称替代ID
                "duration": course.duration if course else None,
                "preparation_date": prep.preparation_date,
                "lesson_plan_title": lesson_plan.title if lesson_plan else None,
                "selected_resources": prep.selected_resources,
                "exercises": prep.exercises
            })
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lesson-plans/content/{lesson_plan_title}")
def get_lesson_plan_content(lesson_plan_title: str, db: Session = Depends(get_db)):
    # 从数据库中获取教案记录
    lesson_plan = db.query(LessonPlan).filter(LessonPlan.title == lesson_plan_title).first()
    if not lesson_plan:
        raise HTTPException(status_code=404, detail="教案不存在")

    try:
        # 读取教案文件内容
        with open(lesson_plan.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取教案内容失败: {str(e)}")

# 更新教案内容的请求模型
class LessonPlanUpdateRequest(BaseModel):
    lesson_plan_id: int
    title: str
    content: str
    course_id: int

class ExerciseRequest(BaseModel):
    id: Optional[int] = None
    type: str
    title: str
    content: str
    options: Optional[str] = None
    answers: str

class ExerciseUpdateRequest(BaseModel):
    course_id: int
    exercises: List[ExerciseRequest]
    lesson_plan_id: int

# 创建作业的请求模型
class AssignmentCreateRequest(BaseModel):
    class_id: int
    title: str
    description: str
    due_date: datetime.datetime
    exercises: List[int]
    teacher_id: int
    course_id: int

# 更新教案内容接口
@app.put("/lesson-plans/update", response_model=LessonPlanResponse)
def update_lesson_plan_content(request: LessonPlanUpdateRequest, db: Session = Depends(get_db)):
    try:
        # 检查教案是否存在
        lesson_plan = db.query(LessonPlan).filter(LessonPlan.id == request.lesson_plan_id).first()
        if not lesson_plan:
            raise HTTPException(status_code=404, detail="教案不存在")

        # 更新教案内容
        lesson_plan.title = request.title
        lesson_plan.description = request.content[:200]  # 使用内容前200字符作为描述
        
        # 确保目录存在
        if not os.path.exists('data/教案'):
            os.makedirs('data/教案')
            
        # 保存文件
        file_path = os.path.join('data/教案', f"{request.title}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(request.content)
            
        lesson_plan.file_path = file_path
        lesson_plan.updated_at = datetime.datetime.now()  # 使用本地时间

        # 更新备课记录中的教案内容
        preparation = db.query(LessonPreparation).filter(
            LessonPreparation.lesson_plan_id == request.lesson_plan_id
        ).first()
        if preparation:
            preparation.updated_at = datetime.datetime.now()  # 使用本地时间
        
        db.commit()
        db.refresh(lesson_plan)
        return lesson_plan
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 更新习题内容接口
@app.put("/exercises/update", response_model=List[ExerciseResponse])
def update_exercises(request: ExerciseUpdateRequest, db: Session = Depends(get_db)):
    try:
        # 检查课程是否存在
        course = db.query(CourseBaseInfo).filter(CourseBaseInfo.id == request.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 检查教案是否存在
        lesson_plan = db.query(LessonPlan).filter(LessonPlan.id == request.lesson_plan_id).first()
        if not lesson_plan:
            raise HTTPException(status_code=404, detail="教案不存在")

        # 获取备课记录
        preparation = db.query(LessonPreparation).filter(
            LessonPreparation.lesson_plan_id == request.lesson_plan_id
        ).first()
        if not preparation:
            raise HTTPException(status_code=404, detail="备课记录不存在")

        updated_exercises = []
        existing_exercise_ids = set()  # 用于跟踪现有习题ID

        for exercise_data in request.exercises:
            if exercise_data.id:
                existing_exercise_ids.add(exercise_data.id)
                # 更新现有习题
                exercise = db.query(Exercise).filter(Exercise.id == exercise_data.id).first()
                if exercise:
                    # 覆盖保存现有习题
                    exercise.type = exercise_data.type
                    exercise.title = exercise_data.title
                    exercise.content = exercise_data.content
                    exercise.options = exercise_data.options
                    exercise.answers = exercise_data.answers
                    exercise.updated_at = datetime.datetime.now()  # 使用本地时间
                else:
                    # 如果指定ID的习题不存在，创建新习题
                    exercise = Exercise(
                        course_id=request.course_id,
                        user_id=lesson_plan.teacher_id,
                        type=exercise_data.type,
                        title=exercise_data.title,
                        content=exercise_data.content,
                        options=exercise_data.options,
                        answers=exercise_data.answers
                    )
                    db.add(exercise)
            else:
                # 创建新习题
                exercise = Exercise(
                    course_id=request.course_id,
                    user_id=lesson_plan.teacher_id,
                    type=exercise_data.type,
                    title=exercise_data.title,
                    content=exercise_data.content,
                    options=exercise_data.options,
                    answers=exercise_data.answers
                )
                db.add(exercise)
            
            db.flush()  # 刷新数据库会话，获取新创建习题的ID
            updated_exercises.append(exercise)

        # 更新备课记录中的习题列表
        exercises_data = [{
            'id': ex.id,
            'type': ex.type,
            'title': ex.title,
            'content': ex.content,
            'options': ex.options,
            'answers': ex.answers
        } for ex in updated_exercises]
        
        preparation.exercises = exercises_data
        preparation.updated_at = datetime.datetime.now()  # 使用本地时间

        db.commit()
        return updated_exercises

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 创建作业接口
@app.post("/assignments/create", response_model=AssignmentResponse)
def create_assignment(request: AssignmentCreateRequest, db: Session = Depends(get_db)):
    try:
        # 检查班级是否存在
        class_obj = db.query(Class).filter(Class.id == request.class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="班级不存在")

        # 检查教师是否存在
        teacher = db.query(User).filter(User.id == request.teacher_id, User.role == 'teacher').first()
        if not teacher:
            raise HTTPException(status_code=404, detail="教师不存在")

        # 检查课程是否存在
        course = db.query(CourseBaseInfo).filter(CourseBaseInfo.id == request.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")

        # 检查习题是否存在
        exercises = db.query(Exercise).filter(Exercise.id.in_(request.exercises)).all()
        if len(exercises) != len(request.exercises):
            raise HTTPException(status_code=404, detail="部分习题不存在")

        # 创建作业
        assignment = Assignment(
            class_id=request.class_id,
            title=request.title,
            description=request.description,
            due_date=request.due_date
        )
        db.add(assignment)
        db.flush()  # 获取作业ID

        # 关联习题
        for exercise_id in request.exercises:
            assignment_exercise = AssignmentExercise(
                assignment_id=assignment.id,
                exercise_id=exercise_id
            )
            db.add(assignment_exercise)

        db.commit()
        db.refresh(assignment)
        return assignment

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class LessonPreparationUpdateRequest(BaseModel):
    preparation_id: int
    course_id: int
    teacher_id: int
    lesson_plan_id: int
    selected_resources: dict
    exercises: dict

@app.put("/lesson-preparation/update/", response_model=dict)
def update_lesson_preparation(request: LessonPreparationUpdateRequest, db: Session = Depends(get_db)):
    try:
        # 查找现有的备课记录
        preparation = db.query(LessonPreparation).filter(
            LessonPreparation.id == request.preparation_id,
            LessonPreparation.teacher_id == request.teacher_id
        ).first()
        
        if not preparation:
            raise HTTPException(status_code=404, detail="备课记录不存在")
        
        # 获取课程信息
        course = db.query(CourseBaseInfo).filter(CourseBaseInfo.id == request.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
            
        # 获取教案信息
        lesson_plan = db.query(LessonPlan).filter(LessonPlan.id == request.lesson_plan_id).first()
        if not lesson_plan:
            raise HTTPException(status_code=404, detail="教案不存在")
        
        # 获取习题详细信息
        exercise_ids = request.exercises.get('selected_ids', []) if isinstance(request.exercises, dict) else []
        exercises = db.query(Exercise).filter(Exercise.id.in_(exercise_ids)).all()
        
        # 构建习题数据
        exercises_data = [{
            'id': ex.id,
            'type': ex.type,
            'title': ex.title,
            'content': ex.content,
            'options': ex.options,
            'answers': ex.answers
        } for ex in exercises]
        
        # 更新记录
        preparation.course_id = request.course_id
        preparation.lesson_plan_id = request.lesson_plan_id
        preparation.selected_resources = request.selected_resources
        preparation.exercises = exercises_data
        preparation.updated_at = datetime.datetime.now()
        
        db.commit()
        return {
            "message": "更新成功", 
            "preparation_id": preparation.id,
            "course_name": lesson_plan.title,  # 使用教案标题作为课程名称
            "exercises": exercises_data
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 批量删除备课记录的请求模型
class BatchDeletePreparationsRequest(BaseModel):
    preparation_ids: List[int]

@app.delete("/lesson-preparation/batch-delete/")
def batch_delete_preparations(request: BatchDeletePreparationsRequest, db: Session = Depends(get_db)):
    try:
        # 删除指定的备课记录
        deleted_count = db.query(LessonPreparation).filter(
            LessonPreparation.id.in_(request.preparation_ids)
        ).delete(synchronize_session=False)
        
        db.commit()
        return {"message": f"成功删除{deleted_count}条记录"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resources/user/{user_id}", response_model=List[ResourceResponse])
def get_user_resources(
    user_id: int, 
    search_query: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取用户的资源列表，支持搜索和筛选
    - search_query: 搜索关键词，会匹配资源名称和关键词
    - resource_type: 资源类型筛选，可选值：'全部', '教材', '教案', '习题', '图片', '视频', 'PPT'
    """
    try:
        # 构建基础查询
        query = db.query(Resource).filter(Resource.user_id == user_id)
        
        # 添加搜索条件
        if search_query:
            # 从资源名称中搜索
            name_matches = query.filter(Resource.resource_name.ilike(f"%{search_query}%"))
            
            # 从关键词中搜索
            keyword_matches = db.query(Resource).join(ResourceKeyword).filter(
                Resource.user_id == user_id,
                ResourceKeyword.keyword.ilike(f"%{search_query}%")
            )
            
            # 合并两个查询结果
            query = name_matches.union(keyword_matches)
        
        # 添加类型筛选
        if resource_type and resource_type != '全部':
            query = query.filter(Resource.resource_type == resource_type)
        
        # 按创建时间降序排序
        resources = query.order_by(Resource.created_at.desc()).all()
        
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 新增获取用户列表API，支持按角色过滤
@app.get("/users/", response_model=List[UserResponse])
def get_users(role: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.all()

# 切换用户状态API（禁用/启用）
@app.put("/users/{user_id}/toggle-status", response_model=UserResponse)
def toggle_user_status(user_id: int, db: Session = Depends(get_db)):
    """
    切换用户状态，禁用/启用用户
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 切换状态
    user.status = '已禁用' if user.status == '正常' else '正常'
    db.commit()
    db.refresh(user)
    return user

# 添加重置密码请求模型
class ResetPasswordRequest(BaseModel):
    user_id: int
    new_password: Optional[str] = None  # 如果不提供，则使用默认密码

# 添加重置密码API
@app.post("/users/{user_id}/reset-password", response_model=UserResponse)
def reset_user_password(user_id: int, request: ResetPasswordRequest = None, db: Session = Depends(get_db)):
    """
    重置用户密码
    如果提供了新密码，则使用提供的密码；否则使用默认密码"123456"
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 设置新密码（实际项目中应该加密）
    default_password = "123456"
    new_password = request.new_password if request and request.new_password else default_password
    
    user.password = new_password
    db.commit()
    db.refresh(user)
    
    return user

@app.get("/students/{student_id}/classes", response_model=List[ClassResponse])
def get_student_classes(student_id: int, db: Session = Depends(get_db)):
    # 检查学生是否存在
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 获取学生所在的班级
    class_students = db.query(ClassStudent).filter(ClassStudent.student_id == student_id).all()
    class_ids = [cs.class_id for cs in class_students]
    classes = db.query(Class).filter(Class.id.in_(class_ids)).all()
    
    return classes

@app.delete("/students/{student_id}/classes/{class_id}")
def student_leave_class(student_id: int, class_id: int, db: Session = Depends(get_db)):
    # 检查学生是否存在
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 检查班级是否存在
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在")

    # 检查学生是否在班级中
    class_student = db.query(ClassStudent).filter(
        ClassStudent.student_id == student_id,
        ClassStudent.class_id == class_id
    ).first()
    if not class_student:
        raise HTTPException(status_code=404, detail="学生不在该班级中")

    # 删除班级学生关系
    db.delete(class_student)
    db.commit()

    return {"message": "成功退出班级"}

@app.get("/students/{student_id}/assignments/{assignment_id}/status")
def get_student_assignment_status(student_id: int, assignment_id: int, db: Session = Depends(get_db)):
    # 检查学生是否存在
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 检查作业是否存在
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")

    # 获取学生的作业提交情况
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.student_id == student_id,
        AssignmentSubmission.assignment_id == assignment_id
    ).first()

    return {
        "submitted": bool(submission),
        "submission_date": submission.submission_date if submission else None,
        "grade": submission.grade if submission else None,
        "feedback": submission.feedback if submission else None
    }

@app.get("/students/{student_id}/performance")
def get_student_performance(student_id: int, db: Session = Depends(get_db)):
    # 检查学生是否存在
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 获取学生所有的作业提交
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.student_id == student_id
    ).all()

    # 计算平均分
    grades = [s.grade for s in submissions if s.grade is not None]
    avg_grade = sum(grades) / len(grades) if grades else 0

    # 获取班级内排名
    class_students = db.query(ClassStudent).filter(
        ClassStudent.student_id == student_id
    ).first()
    
    if class_students:
        class_id = class_students.class_id
        all_students = db.query(ClassStudent).filter(
            ClassStudent.class_id == class_id
        ).all()
        
        student_grades = []
        for student in all_students:
            student_submissions = db.query(AssignmentSubmission).filter(
                AssignmentSubmission.student_id == student.student_id
            ).all()
            student_grades.append({
                "student_id": student.student_id,
                "avg_grade": sum([s.grade for s in student_submissions if s.grade is not None]) / 
                            len([s for s in student_submissions if s.grade is not None])
                if any(s.grade is not None for s in student_submissions) else 0
            })
        
        # 计算排名
        student_grades.sort(key=lambda x: x["avg_grade"], reverse=True)
        rank = next(i for i, item in enumerate(student_grades, 1) if item["student_id"] == student_id)
        total_students = len(student_grades)
    else:
        rank = 0
        total_students = 0

    return {
        "rank": f"{rank}/{total_students}" if total_students > 0 else "暂无排名",
        "mastery_rate": round(avg_grade, 2),
        "prediction": "优秀" if avg_grade >= 90 else "良好" if avg_grade >= 80 else "中等" if avg_grade >= 70 else "及格" if avg_grade >= 60 else "需要努力",
        "evaluation": get_evaluation(avg_grade),
        "suggestion": get_suggestion(avg_grade)
    }

def get_evaluation(avg_grade: float) -> str:
    if avg_grade >= 90:
        return "学习态度认真，知识掌握扎实，有较强的自主学习能力"
    elif avg_grade >= 80:
        return "学习态度良好，知识掌握较好，具有一定的自主学习能力"
    elif avg_grade >= 70:
        return "学习态度尚可，基础知识掌握一般，需要加强自主学习"
    elif avg_grade >= 60:
        return "学习态度需要改进，基础知识有待巩固，需要加强学习"
    else:
        return "学习态度有待提高，基础知识薄弱，需要认真复习并及时改进"

def get_suggestion(avg_grade: float) -> str:
    if avg_grade >= 90:
        return "建议尝试更具挑战性的学习任务，培养创新思维"
    elif avg_grade >= 80:
        return "建议巩固薄弱环节，提高学习效率，争取更好成绩"
    elif avg_grade >= 70:
        return "建议加强基础知识学习，培养良好的学习习惯"
    elif avg_grade >= 60:
        return "建议制定详细的学习计划，及时复习，查漏补缺"
    else:
        return "建议及时与老师沟通，制定补救计划，打好基础"

# 获取未提交作业的学生列表
@app.get("/assignments/{assignment_id}/unsubmitted")
def get_unsubmitted_students(assignment_id: int, db: Session = Depends(get_db)):
    try:
        # 获取作业信息
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="作业不存在")

        # 获取班级所有学生
        class_students = db.query(ClassStudent).filter(
            ClassStudent.class_id == assignment.class_id
        ).all()
        student_ids = [cs.student_id for cs in class_students]

        # 获取已提交作业的学生
        submitted_students = db.query(AssignmentSubmission.student_id).filter(
            AssignmentSubmission.assignment_id == assignment_id
        ).all()
        submitted_ids = [s.student_id for s in submitted_students]

        # 找出未提交的学生
        unsubmitted_ids = [sid for sid in student_ids if sid not in submitted_ids]

        # 获取未提交学生的信息
        unsubmitted_students = db.query(User).filter(
            User.id.in_(unsubmitted_ids),
            User.role == 'student'
        ).all()

        # 返回学生信息
        return [{"id": student.id, "name": student.username} for student in unsubmitted_students]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 下载资源接口
@app.get("/resources/{resource_id}/download")
def download_resource(resource_id: int, db: Session = Depends(get_db)):
    # 查询资源
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # 检查文件是否存在
    if not os.path.exists(db_resource.file_path):
        raise HTTPException(status_code=404, detail="Resource file not found")
    
    # 获取文件名和扩展名
    file_name = os.path.basename(db_resource.file_path)
    file_ext = file_name.split('.')[-1] if '.' in file_name else ""
    
    # 设置响应头，指定内容类型和附件名称
    headers = {
        "Content-Disposition": f"attachment; filename={db_resource.resource_name}"
    }
    
    # 返回文件响应
    return FileResponse(
        path=db_resource.file_path,
        filename=db_resource.resource_name,
        headers=headers
    )

# 预览资源接口
@app.get("/resources/{resource_id}/preview")
def preview_resource(resource_id: int, db: Session = Depends(get_db)):
    # 查询资源
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # 检查文件是否存在
    if not os.path.exists(db_resource.file_path):
        raise HTTPException(status_code=404, detail="Resource file not found")
    
    # 获取文件扩展名
    file_ext = db_resource.file_path.split('.')[-1] if '.' in db_resource.file_path else ""
    
    # 根据资源类型设置适当的内容类型
    content_type = None
    if db_resource.resource_type == 'PPT':
        content_type = "application/vnd.ms-powerpoint"
    elif db_resource.resource_type == '图片':
        if file_ext.lower() in ['jpg', 'jpeg']:
            content_type = "image/jpeg"
        elif file_ext.lower() == 'png':
            content_type = "image/png"
        elif file_ext.lower() == 'gif':
            content_type = "image/gif"
    elif db_resource.resource_type == '视频':
        if file_ext.lower() == 'mp4':
            content_type = "video_llm.py/mp4"
        elif file_ext.lower() == 'avi':
            content_type = "video_llm.py/x-msvideo"
        elif file_ext.lower() == 'mov':
            content_type = "video_llm.py/quicktime"
    elif db_resource.resource_type == '教材':
        content_type = "application/pdf"
    elif db_resource.resource_type in ['教案', '习题']:
        if file_ext.lower() in ['doc', 'docx']:
            content_type = "application/msword"
        elif file_ext.lower() in ['xls', 'xlsx']:
            content_type = "application/vnd.ms-excel"
            
    # 如果无法确定内容类型，则默认为二进制流
    if content_type is None:
        content_type = "application/octet-stream"
    
    # 返回文件响应
    return FileResponse(
        path=db_resource.file_path,
        media_type=content_type
    )


# 在适当的位置添加新的请求模型
class GenerateStudentExercisesRequest(BaseModel):
    student_id: int
    assignment_id: int
    types: dict  # {"choice": 2, "judgment": 3, ...}
    difficulty: int  # 1-5
    session_id: Optional[str] = None  # 会话ID


class SaveStudentExercisesRequest(BaseModel):
    student_id: int
    assignment_id: int
    exercises: List[dict]  # 练习题列表
    session_id: str  # 会话ID


# 在API路由部分添加新的接口
@app.post("/student/exercises/generate", response_model=List[dict])
def generate_student_exercises(request: GenerateStudentExercisesRequest, db: Session = Depends(get_db)):
    """生成基于已完成作业的练习题"""
    try:
        # 检查学生是否存在
        student = db.query(User).filter(User.id == request.student_id, User.role == "student").first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
            
        # 检查作业是否存在
        assignment = db.query(Assignment).filter(Assignment.id == request.assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="作业不存在")
            
        # 检查学生是否已提交该作业
        submission = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == request.assignment_id,
            AssignmentSubmission.student_id == request.student_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=400, detail="学生未提交该作业")
            
        # 获取该作业的所有题目作为参考
        assignment_exercises = db.query(Exercise).join(
            AssignmentExercise,
            Exercise.id == AssignmentExercise.exercise_id
        ).filter(
            AssignmentExercise.assignment_id == request.assignment_id
        ).all()
        
        # 根据学生选择的题型和数量生成练习题
        generated_exercises = []
        
        # 处理单选题和多选题
        if "choice" in request.types and request.types["choice"] > 0:
            for i in range(request.types["choice"]):
                # 简单示例：这里应该使用更复杂的AI算法生成题目
                generated_exercises.append({
                    "type": "单选",
                    "title": f"练习题 {len(generated_exercises) + 1}",
                    "content": f"这是一道基于你之前作业的单选题 {i+1}",
                    "options": json.dumps(["选项A", "选项B", "选项C", "选项D"]),  # 存储为JSON字符串
                    "answers": "A",
                    "difficulty": request.difficulty
                })
                
        # 处理判断题
        if "judgment" in request.types and request.types["judgment"] > 0:
            for i in range(request.types["judgment"]):
                generated_exercises.append({
                    "type": "判断",
                    "title": f"练习题 {len(generated_exercises) + 1}",
                    "content": f"这是一道基于你之前作业的判断题 {i+1}",
                    "options": None,
                    "answers": "正确" if i % 2 == 0 else "错误",
                    "difficulty": request.difficulty
                })
                
        # 处理填空题
        if "blank" in request.types and request.types["blank"] > 0:
            for i in range(request.types["blank"]):
                generated_exercises.append({
                    "type": "填空",
                    "title": f"练习题 {len(generated_exercises) + 1}",
                    "content": f"这是一道基于你之前作业的填空题 {i+1}: _____",
                    "options": None,
                    "answers": "参考答案",
                    "difficulty": request.difficulty
                })
                
        # 处理简答题
        if "short" in request.types and request.types["short"] > 0:
            for i in range(request.types["short"]):
                generated_exercises.append({
                    "type": "简答",
                    "title": f"练习题 {len(generated_exercises) + 1}",
                    "content": f"这是一道基于你之前作业的简答题 {i+1}",
                    "options": None,
                    "answers": "这是简答题的参考答案，实际应生成更有意义的内容。",
                    "difficulty": request.difficulty
                })
                
        return generated_exercises
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/student/exercises/save", response_model=dict)
def save_student_exercises(request: SaveStudentExercisesRequest, db: Session = Depends(get_db)):
    """保存学生的练习题记录"""
    try:
        # 检查学生是否存在
        student = db.query(User).filter(User.id == request.student_id, User.role == "student").first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
            
        # 检查作业是否存在
        assignment = db.query(Assignment).filter(Assignment.id == request.assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="作业不存在")
            
        # 检查是否已存在相同会话ID的记录
        existing_record = db.query(ExerciseStudent).filter(
            ExerciseStudent.student_id == request.student_id,
            ExerciseStudent.session_id == request.session_id
        ).first()
        
        # 获取当前最大序号
        max_sequence = db.query(func.max(ExerciseStudent.sequence_number)).filter(
            ExerciseStudent.student_id == request.student_id
        ).scalar() or 0
        
        if existing_record:
            # 更新现有记录
            existing_record.exercises = request.exercises
            existing_record.updated_at = datetime.datetime.now()
            db.commit()
            db.refresh(existing_record)
            return {
                "success": True,
                "message": "练习题已更新",
                "id": existing_record.id,
                "sequence_number": existing_record.sequence_number
            }
        else:
            # 创建新记录
            new_sequence = max_sequence + 1
            exercise_record = ExerciseStudent(
                student_id=request.student_id,
                assignment_id=request.assignment_id,
                exercises=request.exercises,
                session_id=request.session_id,
                sequence_number=new_sequence
            )
            db.add(exercise_record)
            db.commit()
            db.refresh(exercise_record)
            return {
                "success": True,
                "message": "练习题已保存",
                "id": exercise_record.id,
                "sequence_number": new_sequence
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/student/{student_id}/exercises/history", response_model=List[dict])
def get_student_exercises_history(student_id: int, db: Session = Depends(get_db)):
    """获取学生的练习题历史记录"""
    try:
        # 检查学生是否存在
        student = db.query(User).filter(User.id == student_id, User.role == "student").first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
            
        # 获取所有练习记录
        exercise_records = db.query(ExerciseStudent).filter(
            ExerciseStudent.student_id == student_id
        ).order_by(ExerciseStudent.sequence_number.desc()).all()
        
        results = []
        for record in exercise_records:
            # 获取作业信息
            assignment = db.query(Assignment).filter(Assignment.id == record.assignment_id).first()
            assignment_name = assignment.title if assignment else "未知作业"
            
            results.append({
                "id": record.id,
                "assignment_id": record.assignment_id,
                "assignment_name": assignment_name,
                "sequence_number": record.sequence_number,
                "exercise_count": len(record.exercises),
                "created_at": record.created_at,
                "updated_at": record.updated_at
            })
            
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/student/exercises/{record_id}", response_model=dict)
def get_student_exercise_detail(record_id: int, db: Session = Depends(get_db)):
    """获取学生练习题详细内容"""
    try:
        # 获取记录
        record = db.query(ExerciseStudent).filter(ExerciseStudent.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="练习记录不存在")
            
        # 获取作业信息
        assignment = db.query(Assignment).filter(Assignment.id == record.assignment_id).first()
        assignment_name = assignment.title if assignment else "未知作业"
        
        return {
            "id": record.id,
            "student_id": record.student_id,
            "assignment_id": record.assignment_id,
            "assignment_name": assignment_name,
            "sequence_number": record.sequence_number,
            "exercises": record.exercises,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 批量删除学生练习题记录的请求模型
class BatchDeleteExercisesRequest(BaseModel):
    record_ids: List[int]


@app.delete("/student/exercises/batch-delete")
def batch_delete_student_exercises(request: BatchDeleteExercisesRequest, db: Session = Depends(get_db)):
    """批量删除学生练习题记录"""
    try:
        # 删除指定的练习题记录
        deleted_count = db.query(ExerciseStudent).filter(
            ExerciseStudent.id.in_(request.record_ids)
        ).delete(synchronize_session=False)
        
        db.commit()
        return {"success": True, "message": f"成功删除{deleted_count}条记录"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/student/exercises/{record_id}")
def delete_student_exercise(record_id: int, db: Session = Depends(get_db)):
    """删除单个学生练习题记录"""
    try:
        # 查找记录
        record = db.query(ExerciseStudent).filter(ExerciseStudent.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="练习记录不存在")
        
        # 删除记录
        db.delete(record)
        db.commit()
        
        return {"success": True, "message": "练习记录已删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 添加共享资源API路由


@app.post("/share-resources/", response_model=dict)
async def create_share_resource(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传共享资源"""
    try:
        file_content = await file.read()
        
        # 获取文件名和扩展名
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 确定文件类型
        file_ext = os.path.splitext(filename)[1].lower()
        resource_type = get_resource_type(file_ext)
        
        # 生成安全的文件名
        secure_filename = f"{uuid.uuid4()}{file_ext}"
        
        # 根据资源类型创建目录
        resource_folder = os.path.join("static", "share_resources", resource_type.lower())
        os.makedirs(resource_folder, exist_ok=True)
        
        # 文件保存路径
        file_path = os.path.join(resource_folder, secure_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 获取当前用户ID
        user_id = get_current_user_id()
        
        # 创建共享资源记录
        share_resource = ShareResource(
            resource_name=filename,
            resource_type=resource_type,
            file_path=file_path,
            uploaded_by=user_id,
            status="待审核"
        )
        
        db.add(share_resource)
        db.commit()
        db.refresh(share_resource)
        
        return {
            "id": share_resource.id,
            "resource_name": share_resource.resource_name,
            "resource_type": share_resource.resource_type,
            "file_path": file_path,
            "message": "资源上传成功，等待审核"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传资源失败: {str(e)}")


@app.get("/share-resources/", response_model=List[dict])
def get_share_resources(
    search_query: Optional[str] = None,
    resource_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取共享资源列表"""
    query = db.query(ShareResource)
    
    # 根据参数过滤
    if search_query:
        query = query.filter(ShareResource.resource_name.contains(search_query))
    
    if resource_type:
        query = query.filter(ShareResource.resource_type == resource_type)
    
    if status:
        query = query.filter(ShareResource.status == status)
    
    resources = query.order_by(ShareResource.created_at.desc()).all()
    
    # 查询上传者信息
    result = []
    for resource in resources:
        user = db.query(User).filter(User.id == resource.uploaded_by).first()
        uploader_name = user.username if user else "未知用户"
        
        result.append({
            "id": resource.id,
            "resource_name": resource.resource_name,
            "resource_type": resource.resource_type,
            "file_path": resource.file_path,
            "status": resource.status,
            "uploader": uploader_name,
            "uploader_id": resource.uploaded_by,
            "created_at": resource.created_at
        })
    
    return result


@app.get("/share-resources/{resource_id}", response_model=dict)
def get_share_resource(resource_id: int, db: Session = Depends(get_db)):
    """获取单个共享资源详情"""
    resource = db.query(ShareResource).filter(ShareResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    user = db.query(User).filter(User.id == resource.uploaded_by).first()
    uploader_name = user.username if user else "未知用户"
    
    return {
        "id": resource.id,
        "resource_name": resource.resource_name,
        "resource_type": resource.resource_type,
        "file_path": resource.file_path,
        "status": resource.status,
        "uploader": uploader_name,
        "uploader_id": resource.uploaded_by,
        "created_at": resource.created_at
    }


@app.put("/share-resources/{resource_id}/approve", response_model=dict)
def approve_share_resource(resource_id: int, db: Session = Depends(get_db)):
    """审核通过共享资源"""
    resource = db.query(ShareResource).filter(ShareResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    resource.status = "已审核"
    db.commit()
    db.refresh(resource)
    
    return {
        "id": resource.id,
        "resource_name": resource.resource_name,
        "status": resource.status,
        "message": "资源审核通过"
    }


@app.delete("/share-resources/{resource_id}", response_model=dict)
def delete_share_resource(resource_id: int, db: Session = Depends(get_db)):
    """删除共享资源"""
    resource = db.query(ShareResource).filter(ShareResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    # 尝试删除文件
    try:
        if os.path.exists(resource.file_path):
            os.remove(resource.file_path)
    except Exception as e:
        print(f"删除文件失败: {str(e)}")
    
    # 删除数据库记录
    db.delete(resource)
    db.commit()
    
    return {"message": "资源删除成功"}
