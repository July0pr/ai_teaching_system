from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, String, Float, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

def local_now():
    return datetime.datetime.now()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(Enum('teacher', 'student', 'admin'))
    status = Column(Enum('正常', '已禁用'), default='正常')
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String)
    permissions = Column(String)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    resource_name = Column(String)
    resource_type = Column(Enum('教材', '教案', '习题', '图片', '视频', 'PPT'))
    file_path = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class ShareResource(Base):
    __tablename__ = "share_resources"
    id = Column(Integer, primary_key=True, index=True)
    resource_name = Column(String)
    resource_type = Column(Enum('教材', '教案', '习题', '图片', '视频', 'PPT'))
    file_path = Column(String)
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum('待审核', '已审核'), default='待审核')
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class ResourceKeyword(Base):
    __tablename__ = "resource_keywords"
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey('resources.id'))
    keyword = Column(String)
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class AIResource(Base):
    __tablename__ = "ai_resources"
    id = Column(Integer, primary_key=True, index=True)
    resource_name = Column(String)
    resource_type = Column(Enum('图片', '视频', 'PPT'))
    file_path = Column(String)
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)
    user_id = Column(Integer, ForeignKey('users.id'))

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    subjects = Column(String, nullable=True)
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class ClassStudent(Base):
    __tablename__ = "class_students"
    class_id = Column(Integer, ForeignKey('classes.id'), primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

class ClassResource(Base):
    __tablename__ = "class_resources"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey('classes.id'))
    resource_type = Column(Enum('教材', '教案', '习题', '图片', '视频', 'PPT'))
    resource_name = Column(String)
    file_path = Column(String)
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class LessonPlan(Base):
    __tablename__ = "lesson_plans"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    class_id = Column(Integer, ForeignKey('classes.id'))
    course_id = Column(Integer, ForeignKey('course_base_info.id'))
    title = Column(String)
    description = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey('classes.id'))
    title = Column(String)
    description = Column(String)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(Enum('单选', '多选', '填空', '判断', '简答'))
    title = Column(String)
    content = Column(String) 
    options = Column(String, nullable=True)
    answers = Column(String)
    course_id = Column(Integer, ForeignKey('course_base_info.id'))
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class AssignmentExercise(Base):
    __tablename__ = "assignments_exercises"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    exercise_id = Column(Integer, ForeignKey('exercises.id'))
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class AssignmentSubmission(Base):
    __tablename__ = "assignments_submissions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    student_id = Column(Integer, ForeignKey('users.id'))
    submission_date = Column(DateTime, default=local_now)
    answers = Column(String)
    grade = Column(Float, nullable=True)
    feedback = Column(String, nullable=True)
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    resource_id = Column(Integer, ForeignKey('resources.id'))
    priority = Column(Integer, default=0)
    reason = Column(String, nullable=True)
    recommended_at = Column(DateTime, default=local_now)
    is_viewed = Column(Integer, default=0)
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class CourseBaseInfo(Base):
    __tablename__ = "course_base_info"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    theme = Column(Text)
    objective = Column(Text)
    target_class = Column(String)
    duration = Column(String)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    features = Column(JSON)  # 存储功能开关状态
    special_requirements = Column(JSON)  # 存储特殊教学需求标签
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class CourseResource(Base):
    __tablename__ = "course_resources"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('course_base_info.id'))
    resource_type = Column(Enum('PPT', '视频', '图片'))
    resource_name = Column(String)
    file_path = Column(String)
    match_rate = Column(Float, default=95.0)  # 匹配度
    is_selected = Column(Integer, default=0)  # 是否被选中：0-未选中，1-已选中
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class LessonPreparation(Base):
    __tablename__ = "lesson_preparations"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('course_base_info.id'))
    teacher_id = Column(Integer, ForeignKey('users.id'))
    lesson_plan_id = Column(Integer, ForeignKey('lesson_plans.id'))
    selected_resources = Column(JSON)
    exercises = Column(JSON)
    preparation_date = Column(DateTime, default=local_now)
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)

class ExerciseStudent(Base):
    __tablename__ = "exercises_students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    assignment_id = Column(Integer, ForeignKey('assignments.id')) 
    exercises = Column(JSON)  # 存储练习题列表的JSON
    session_id = Column(String, index=True)  # 会话ID，用于相同会话的覆盖保存
    sequence_number = Column(Integer)  # 历史记录序号
    created_at = Column(DateTime, default=local_now)
    updated_at = Column(DateTime, default=local_now, onupdate=local_now)