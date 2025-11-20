import requests
import json
import datetime

BASE_URL = "http://127.0.0.1:8000"

# 测试创建用户
def test_create_user():
    response = requests.post(f"{BASE_URL}/users/", json={"username": "testuser", "password": "testpass", "role": "student"})
    print("Create User Response:", response.json())

# 测试获取用户信息
def test_read_user(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print("Read User Response:", response.json())

# 测试更新用户信息
def test_update_user(user_id):
    response = requests.put(f"{BASE_URL}/users/{user_id}", json={"username": "updateduser", "password": "updatedpass", "role": "teacher"})
    print("Update User Response:", response.json())

# 测试删除用户
def test_delete_user(user_id):
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    print("Delete User Response:", response.json())

# 测试创建资源
def test_create_resource():
    response = requests.post(f"{BASE_URL}/resources/", json={"resource_name": "示例教材2", "resource_type": "教材", "file_path": "data/教材/示例教材2"})
    print("Create Resource Response:", response.json())

# 测试获取资源信息
def test_read_resource(resource_id):
    response = requests.get(f"{BASE_URL}/resources/{resource_id}")
    print("Read Resource Response:", response.json())

# 测试更新资源信息
def test_update_resource(resource_id):
    response = requests.put(f"{BASE_URL}/resources/{resource_id}", json={"resource_name": "更新教材", "resource_type": "教材", "file_path": "data/教材/更新教材"})
    print("Update Resource Response:", response.json())

# 测试删除资源
def test_delete_resource(resource_id):
    response = requests.delete(f"{BASE_URL}/resources/{resource_id}")
    print("Delete Resource Response:", response.json())

# 测试添加关键字
def test_add_keyword(resource_id, keyword):
    response = requests.post(f"{BASE_URL}/resources/{resource_id}/keywords/?keyword={keyword}")
    print("Add Keyword Response:", response.json())

# 测试通过关键字查找资源
def test_get_resources_by_keyword(keyword):
    response = requests.get(f"{BASE_URL}/resources/keywords/{keyword}")
    print("Get Resources By Keyword Response:", response.json())

# 测试创建 AI 生成资源
def test_create_ai_resource():
    response = requests.post(f"{BASE_URL}/ai_resources/", json={
        "resource_name": "AI示例PPT",
        "resource_type": "PPT",
        "file_path": "data/AI/PPT/AI示例PPT",
        "user_id": 1,
        "description": "AI生成的示例PPT"
    })
    print("Create AI Resource Response:", response.json())

# 测试更新 AI 生成资源信息
def test_update_ai_resource(resource_id):
    response = requests.put(f"{BASE_URL}/ai_resources/{resource_id}", json={
        "resource_name": "更新的AI示例PPT",
        "resource_type": "PPT",
        "file_path": "data/AI/PPT/更新的AI示例PPT",
        "user_id": 1
    })
    print("Update AI Resource Response:", response.json())

# 测试删除 AI 生成资源
def test_delete_ai_resource(resource_id):
    response = requests.delete(f"{BASE_URL}/ai_resources/{resource_id}")
    print("Delete AI Resource Response:", response.json())

# 测试复制 AI 生成资源到资源
def test_copy_ai_resource_to_resources(resource_id):
    response = requests.post(f"{BASE_URL}/ai_resources/{resource_id}/copy_to_resources/")
    print("Copy AI Resource to Resources Response:", response.json())

# 测试通过 user_id 获取 AI 生成资源信息
def test_read_ai_resources_by_user(user_id):
    response = requests.get(f"{BASE_URL}/ai_resources/user/{user_id}")
    print("Read AI Resources By User Response:", response.json())

# 测试通过 ID 获取 AI 生成资源信息
def test_read_ai_resource(resource_id):
    response = requests.get(f"{BASE_URL}/ai_resources/{resource_id}")
    print("Read AI Resource Response:", response.json())

# 测试查询班级里的学生
def test_get_students_in_class(class_id):
    response = requests.get(f"{BASE_URL}/classes/{class_id}/students")
    print("Get Students In Class Response:", response.json())

# 测试删除班级
def test_delete_class(class_id):
    response = requests.delete(f"{BASE_URL}/classes/{class_id}")
    print("Delete Class Response:", response.json())

# 测试创建班级
def test_create_class():
    response = requests.post(f"{BASE_URL}/classes/", json={"class_name": "测试班级", "teacher_id": 1})
    print("Create Class Response:", response.json())

# 测试获取班级信息
def test_read_class(class_id):
    response = requests.get(f"{BASE_URL}/classes/{class_id}")
    print("Read Class Response:", response.json())

# 测试更新班级信息
def test_update_class(class_id):
    response = requests.put(f"{BASE_URL}/classes/{class_id}", json={"class_name": "更新班级名称", "teacher_id": 1})
    print("Update Class Response:", response.json())

# 测试添加学生到班级
def test_add_student_to_class(class_id, student_id):
    response = requests.post(f"{BASE_URL}/classes/students/", json={"class_id": class_id, "student_id": student_id})
    print("Add Student To Class Response:", response.json())

# 测试删除学生
def test_delete_student(class_id, student_id):
    response = requests.delete(f"{BASE_URL}/classes/{class_id}/students/{student_id}")
    print("Delete Student Response:", response.json())

# 测试上传班级资源
def test_upload_class_resource():
    response = requests.post(f"{BASE_URL}/classes/resources/", json={
        "class_id": 1,
        "resource_type": "习题",
        "resource_name": "班级习题",
        "file_path": "data/习题/班级习题",
        "uploaded_by": 1
    })
    print("Upload Class Resource Response:", response.json())

# 测试获取班级资源
def test_get_class_resources(class_id):
    response = requests.get(f"{BASE_URL}/classes/{class_id}/resources")
    print("Get Class Resources Response:", response.json())

# 测试更新班级资源
def test_update_class_resource(resource_id):
    response = requests.put(f"{BASE_URL}/classes/resources/{resource_id}", json={
        "class_id": 1,
        "resource_type": "习题",
        "resource_name": "更新的班级习题",
        "file_path": "data/习题/更新的班级习题",
        "uploaded_by": 1
    })
    print("Update Class Resource Response:", response.json())

# 测试删除班级资源
def test_delete_class_resource(resource_id):
    response = requests.delete(f"{BASE_URL}/classes/resources/{resource_id}")
    print("Delete Class Resource Response:", response.json())

# 测试创建教案
def test_create_lesson_plan():
    response = requests.post(f"{BASE_URL}/lesson_plans/", json={
        "teacher_id": 1,
        "class_id": 1,
        "title": "测试教案",
        "description": "这是一个测试教案的描述",
        "file_path": "data/教案/测试教案"
    })
    print("Create Lesson Plan Response:", response.json())
    return response.json()

# 测试获取教案信息
def test_read_lesson_plan(lesson_plan_id):
    response = requests.get(f"{BASE_URL}/lesson_plans/{lesson_plan_id}")
    print(f"Read Lesson Plan {lesson_plan_id} Response:", response.json())

# 测试获取教师的所有教案
def test_read_teacher_lesson_plans(teacher_id):
    response = requests.get(f"{BASE_URL}/teachers/{teacher_id}/lesson_plans")
    print(f"Read Teacher {teacher_id} Lesson Plans Response:", response.json())

# 测试获取班级的所有教案
def test_read_class_lesson_plans(class_id):
    response = requests.get(f"{BASE_URL}/classes/{class_id}/lesson_plans")
    print(f"Read Class {class_id} Lesson Plans Response:", response.json())

# 测试更新教案信息
def test_update_lesson_plan(lesson_plan_id):
    response = requests.put(f"{BASE_URL}/lesson_plans/{lesson_plan_id}", json={
        "title": "更新后的测试教案",
        "description": "这是更新后的测试教案描述"
    })
    print(f"Update Lesson Plan {lesson_plan_id} Response:", response.json())

# 测试删除教案
def test_delete_lesson_plan(lesson_plan_id):
    response = requests.delete(f"{BASE_URL}/lesson_plans/{lesson_plan_id}")
    print(f"Delete Lesson Plan {lesson_plan_id} Response:", response.json())

# 测试创建作业
def test_create_assignment():
    response = requests.post(f"{BASE_URL}/assignments/", json={
        "class_id": 1,
        "title": "测试作业",
        "description": "这是一个测试作业的描述",
        "due_date": (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat()
    })
    print("Create Assignment Response:", response.json())
    return response.json()

# 测试获取作业信息
def test_read_assignment(assignment_id):
    response = requests.get(f"{BASE_URL}/assignments/{assignment_id}")
    print(f"Read Assignment {assignment_id} Response:", response.json())

# 测试获取班级的所有作业
def test_read_class_assignments(class_id):
    response = requests.get(f"{BASE_URL}/classes/{class_id}/assignments")
    print(f"Read Class {class_id} Assignments Response:", response.json())

# 测试更新作业信息
def test_update_assignment(assignment_id):
    response = requests.put(f"{BASE_URL}/assignments/{assignment_id}", json={
        "title": "更新后的测试作业",
        "description": "这是更新后的测试作业描述",
        "due_date": (datetime.datetime.utcnow() + datetime.timedelta(days=10)).isoformat()
    })
    print(f"Update Assignment {assignment_id} Response:", response.json())

# 测试创建习题
def test_create_exercise():
    response = requests.post(f"{BASE_URL}/exercises/", json={
        "user_id": 1,
        "type": "单选",
        "title": "测试习题",
        "content": "这是一道测试单选题，请选择正确答案",
        "options": json.dumps(["选项A", "选项B", "选项C", "选项D"]),
        "answers": "A"
    })
    print("Create Exercise Response:", response.json())
    return response.json()

# 测试获取习题信息
def test_read_exercise(exercise_id):
    response = requests.get(f"{BASE_URL}/exercises/{exercise_id}")
    print(f"Read Exercise {exercise_id} Response:", response.json())

# 测试获取用户创建的所有习题
def test_read_user_exercises(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}/exercises")
    print(f"Read User {user_id} Exercises Response:", response.json())

# 测试更新习题信息
def test_update_exercise(exercise_id):
    response = requests.put(f"{BASE_URL}/exercises/{exercise_id}", json={
        "title": "更新后的测试习题",
        "content": "这是更新后的测试题目内容",
        "options": json.dumps(["新选项A", "新选项B", "新选项C", "新选项D"]),
        "answers": "B"
    })
    print(f"Update Exercise {exercise_id} Response:", response.json())

# 测试添加习题到作业
def test_add_exercise_to_assignment(assignment_id, exercise_id):
    response = requests.post(f"{BASE_URL}/assignments/exercises/", json={
        "assignment_id": assignment_id,
        "exercise_id": exercise_id
    })
    print("Add Exercise To Assignment Response:", response.json())

# 测试获取作业的所有习题
def test_read_assignment_exercises(assignment_id):
    response = requests.get(f"{BASE_URL}/assignments/{assignment_id}/exercises")
    print(f"Read Assignment {assignment_id} Exercises Response:", response.json())

# 测试提交作业
def test_submit_assignment(assignment_id, student_id):
    response = requests.post(f"{BASE_URL}/assignments/submissions/", json={
        "assignment_id": assignment_id,
        "student_id": student_id,
        "answers": json.dumps({"1": "A", "2": "B"})
    })
    print("Submit Assignment Response:", response.json())
    return response.json()

# 测试获取作业提交信息
def test_read_submission(submission_id):
    response = requests.get(f"{BASE_URL}/assignments/submissions/{submission_id}")
    print(f"Read Submission {submission_id} Response:", response.json())

# 测试获取作业的所有提交
def test_read_assignment_submissions(assignment_id):
    response = requests.get(f"{BASE_URL}/assignments/{assignment_id}/submissions")
    print(f"Read Assignment {assignment_id} Submissions Response:", response.json())

# 测试获取学生的所有提交
def test_read_student_submissions(student_id):
    response = requests.get(f"{BASE_URL}/students/{student_id}/submissions")
    print(f"Read Student {student_id} Submissions Response:", response.json())

# 测试评分作业提交
def test_grade_submission(submission_id):
    response = requests.put(f"{BASE_URL}/assignments/submissions/{submission_id}", json={
        "grade": 85.5,
        "feedback": "做得不错，但还有改进空间"
    })
    print(f"Grade Submission {submission_id} Response:", response.json())

# 测试从作业中移除习题
def test_remove_exercise_from_assignment(assignment_id, exercise_id):
    response = requests.delete(f"{BASE_URL}/assignments/{assignment_id}/exercises/{exercise_id}")
    print("Remove Exercise From Assignment Response:", response.json())

# 测试删除作业提交
def test_delete_submission(submission_id):
    response = requests.delete(f"{BASE_URL}/assignments/submissions/{submission_id}")
    print(f"Delete Submission {submission_id} Response:", response.json())

# 测试删除习题
def test_delete_exercise(exercise_id):
    response = requests.delete(f"{BASE_URL}/exercises/{exercise_id}")
    print(f"Delete Exercise {exercise_id} Response:", response.json())

# 测试删除作业
def test_delete_assignment(assignment_id):
    response = requests.delete(f"{BASE_URL}/assignments/{assignment_id}")
    print(f"Delete Assignment {assignment_id} Response:", response.json())

# 测试创建推荐
def test_create_recommendation():
    response = requests.post(f"{BASE_URL}/recommendations/", json={
        "student_id": 3,
        "resource_id": 1,
        "priority": 5,
        "reason": "根据您的学习情况，推荐这份教材"
    })
    print("Create Recommendation Response:", response.json())
    return response.json()

# 测试获取推荐信息
def test_read_recommendation(recommendation_id):
    response = requests.get(f"{BASE_URL}/recommendations/{recommendation_id}")
    print(f"Read Recommendation {recommendation_id} Response:", response.json())

# 测试获取学生的所有推荐
def test_read_student_recommendations(student_id):
    response = requests.get(f"{BASE_URL}/students/{student_id}/recommendations")
    print(f"Read Student {student_id} Recommendations Response:", response.json())

# 测试更新推荐信息
def test_update_recommendation(recommendation_id):
    response = requests.put(f"{BASE_URL}/recommendations/{recommendation_id}", json={
        "priority": 8,
        "reason": "更新后的推荐原因"
    })
    print(f"Update Recommendation {recommendation_id} Response:", response.json())

# 测试标记推荐为已查看
def test_mark_recommendation_viewed(recommendation_id):
    response = requests.put(f"{BASE_URL}/recommendations/{recommendation_id}/view")
    print(f"Mark Recommendation {recommendation_id} Viewed Response:", response.json())

# 测试删除推荐
def test_delete_recommendation(recommendation_id):
    response = requests.delete(f"{BASE_URL}/recommendations/{recommendation_id}")
    print(f"Delete Recommendation {recommendation_id} Response:", response.json())

# 测试批量创建推荐
def test_create_recommendations_batch():
    response = requests.post(f"{BASE_URL}/recommendations/batch", json=[
        {
            "student_id": 3,
            "resource_id": 2,
            "priority": 4,
            "reason": "批量推荐的教案"
        },
        {
            "student_id": 3,
            "resource_id": 3,
            "priority": 3,
            "reason": "批量推荐的习题"
        }
    ])
    print("Create Recommendations Batch Response:", response.json())

if __name__ == "__main__":
    print("开始测试")
     
    user_ids = [1, 2, 3]
    for user_id in user_ids:
        test_delete_user(user_id)
    test_create_user()
    # 创建一个教师用户，用于测试教案功能
    response = requests.post(f"{BASE_URL}/users/", json={"username": "teacheruser", "password": "teacherpass", "role": "teacher"})
    print("Create Teacher User Response:", response.json())
    # 创建一个学生用户，用于测试作业提交
    response = requests.post(f"{BASE_URL}/users/", json={"username": "studentuser", "password": "studentpass", "role": "student"})
    print("Create Student User Response:", response.json())
    test_read_user(1)
    test_update_user(1)
    test_read_user(1)
    
    resource_ids = [1, 2, 3, 4, 5, 6]
    for resource_id in resource_ids:
        test_delete_resource(resource_id)
    test_create_resource()
    test_add_keyword(1, "数学")
    test_read_resource(1)
    test_get_resources_by_keyword("教材")
    test_update_resource(1)
    test_add_keyword(1, "更新后的关键字")
    test_get_resources_by_keyword("更新后的关键字")
    
    test_create_ai_resource()
    test_read_ai_resources_by_user(1)
    test_read_ai_resource(1)
    test_update_ai_resource(1)
    test_copy_ai_resource_to_resources(1)
    test_delete_ai_resource(1)
    
    test_create_class()
    test_read_class(1)
    test_update_class(1)
    test_add_student_to_class(1, 3)  # 添加学生用户到班级
    test_get_students_in_class(1) 
    test_upload_class_resource()
    test_get_class_resources(1)
    test_update_class_resource(1)
    
    # 测试教案功能（放在删除班级之前）
    lesson_plan = test_create_lesson_plan()
    # 添加错误处理，检查返回结果是否包含id字段
    if "id" in lesson_plan:
        lesson_plan_id = lesson_plan["id"]
        test_read_lesson_plan(lesson_plan_id)
        test_read_teacher_lesson_plans(1)
        test_read_class_lesson_plans(1)
        test_update_lesson_plan(lesson_plan_id)
        test_read_lesson_plan(lesson_plan_id)
        test_delete_lesson_plan(lesson_plan_id)
    else:
        print("创建教案失败，跳过后续教案测试")
    
    # 测试作业与评估模块
    print("\n开始测试作业与评估模块")
    # 创建作业
    assignment = test_create_assignment()
    assignment_id = assignment["id"]
    test_read_assignment(assignment_id)
    test_read_class_assignments(1)
    test_update_assignment(assignment_id)
    
    # 创建习题
    exercise = test_create_exercise()
    exercise_id = exercise["id"]
    test_read_exercise(exercise_id)
    test_read_user_exercises(1)
    test_update_exercise(exercise_id)
    
    # 添加习题到作业
    test_add_exercise_to_assignment(assignment_id, exercise_id)
    test_read_assignment_exercises(assignment_id)
    
    # 提交作业
    submission = test_submit_assignment(assignment_id, 3)  # 使用学生用户提交
    submission_id = submission["id"]
    test_read_submission(submission_id)
    test_read_assignment_submissions(assignment_id)
    test_read_student_submissions(3)
    
    # 评分作业
    test_grade_submission(submission_id)
    test_read_submission(submission_id)
    
    # 测试学习资源推荐模块
    print("\n开始测试学习资源推荐模块")
    # 创建推荐
    recommendation = test_create_recommendation()
    recommendation_id = recommendation["id"]
    test_read_recommendation(recommendation_id)
    test_read_student_recommendations(3)
    test_update_recommendation(recommendation_id)
    test_mark_recommendation_viewed(recommendation_id)
    
    # 批量创建推荐
    test_create_recommendations_batch()
    test_read_student_recommendations(3)
    
    # 清理测试数据
    test_delete_recommendation(recommendation_id)
    
    # 清理作业与评估模块测试数据
    test_remove_exercise_from_assignment(assignment_id, exercise_id)
    test_delete_submission(submission_id)
    test_delete_exercise(exercise_id)
    test_delete_assignment(assignment_id)
    
    # 最后删除班级和学生
    test_delete_student(1, 3)
    test_delete_class(1) 