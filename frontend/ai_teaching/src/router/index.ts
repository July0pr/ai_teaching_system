import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/teacher/workbench'
    },
    /*{
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue')
    },*/
    // 教师端路由
    {
      path: '/teacher',
      name: 'teacher',
      component: () => import('../views/teacher/TeacherLayout.vue'),
      meta: { requiresAuth: true, role: 'teacher' },
      children: [
        {
          path: 'workbench',
          name: 'teacherWorkbench',
          component: () => import('../views/teacher/workbench/WorkbenchIndex.vue')
        },
        {
          path: 'workbench/step1',
          name: 'workbenchStep1',
          component: () => import('../views/teacher/workbench/Step1View.vue')
        },
        {
          path: 'workbench/step2',
          name: 'workbenchStep2',
          component: () => import('../views/teacher/workbench/Step2View.vue')
        },
        {
          path: 'workbench/step3',
          name: 'workbenchStep3',
          component: () => import('../views/teacher/workbench/Step3View.vue')
        },
        {
          path: 'workbench/step4',
          name: 'workbenchStep4',
          component: () => import('../views/teacher/workbench/Step4View.vue')
        },
        {
          path: 'resources',
          name: 'teacherResources',
          component: () => import('../views/teacher/resources/ResourcesIndex.vue')
        },
        {
          path: 'resources/history',
          name: 'teacherResourcesHistory',
          component: () => import('../views/teacher/resources/HistoryView.vue')
        },
        {
          path: 'resources/personal',
          name: 'teacherResourcesPersonal',
          component: () => import('../views/teacher/resources/PersonalView.vue')
        },
        {
          path: 'classes',
          name: 'teacherClasses',
          component: () => import('../views/teacher/classes/ClassesIndex.vue')
        },
        {
          path: 'classes/:id',
          name: 'teacherClassDetail',
          component: () => import('../views/teacher/classes/ClassDetailView.vue')
        },
        {
          path: 'assignments/:id/submissions',
          name: 'teacherAssignmentSubmissions',
          component: () => import('../views/teacher/assignments/AssignmentSubmissions.vue')
        },
        {
          path: 'assignments/:assignmentId/submissions/:submissionId/review',
          name: 'teacherAssignmentReview',
          component: () => import('../views/teacher/assignments/AssignmentReview.vue')
        }
      ]
    }
    // 学生端路由
/*    {
      path: '/student',
      name: 'student',
      component: () => import('../views/student/StudentLayout.vue'),
      meta: { requiresAuth: true, role: 'student' },
      children: [
        {
          path: 'recommend',
          name: 'studentRecommend',
          component: () => import('../views/student/recommend/RecommendIndex.vue')
        },
        {
          path: 'recommend/resources',
          name: 'studentResources',
          component: () => import('../views/student/recommend/ResourcesView.vue')
        },
        {
          path: 'recommend/exercises',
          name: 'studentExercises',
          component: () => import('../views/student/recommend/ExercisesView.vue')
        },
        {
          path: 'resources/history',
          name: 'studentResourcesHistory',
          component: () => import('../views/student/resources/HistoryView.vue')
        },
        {
          path: 'exercises/practice/:id',
          name: 'studentExercisePractice',
          component: () => import('../views/student/exercises/PracticeView.vue')
        },
        {
          path: 'classes',
          name: 'studentClasses',
          component: () => import('../views/student/classes/ClassesIndex.vue')
        },
        {
          path: 'classes/:id',
          name: 'studentClassDetail',
          component: () => import('../views/student/classes/ClassDetailView.vue')
        },
        {
          path: 'assignments/:id',
          name: 'StudentAssignmentDetail',
          component: () => import('@/views/student/assignments/AssignmentDetail.vue')
        }
      ]
    },
    // 管理员端路由
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        {
          path: '',
          redirect: '/admin/users'
        },
        {
          path: 'users',
          name: 'UserManagement',
          component: () => import('../views/admin/UserManagementView.vue'),//报错不用管，不影响运行，stupid bird，回回找不到文件
          meta: {
            title: '用户管理',
            requiresAuth: true,
            requiresAdmin: true
          }
        },
        {
          path: 'resources',
          name: 'ResourceManagement',
          component: () => import('../views/admin/ResourceManagementView.vue'),
          meta: {
            title: '资源管理',
            requiresAuth: true,
            requiresAdmin: true
          }
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: () => import('../views/NotFoundView.vue')
    }*/
  ]
})


// 路由守卫
/*
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const role = to.matched.find(record => record.meta.role)?.meta.role
  
  // 模拟检查用户是否已登录和角色
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  const userRole = localStorage.getItem('userRole')
  
  if (requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (requiresAuth && role && role !== userRole) {
    next('/login') // 或者可以跳转到无权限页面
  } else {
    next()
  }
})*/


export default router
