from django.urls import path
from .import views

urlpatterns=[
     path('',views.ulogin,name='/'),
     # path('register',views.register,name='register'),
     # path('uindex',views.u_index,name='u_index'),
     path('questionare',views.questionare,name='questionare'),
     path('results/<int:score>/',views.results, name='results'),
     # path('logout',views.logout,name='logout'),
     path('logout',views.logout_view, name='logout'),


     path('newregister',views.newregister,name='newregister'),
     path('check_email', views.check_email, name='check_email'),
     path('exam',views.exam,name='exam'),
     path('aptitude_test',views.aptitude_test,name='aptitude_test'),
     path('user_profile',views.user_profile,name='user_profile'),
     path('see_test_results/<int:user_id>/', views.see_test_results, name='see_test_results'),
     path('results_details/<int:attempt_id>/', views.results_details, name='results_details'),
     path('assessment_details/<int:attempt_id>/', views.assessment_details, name='assessment_details'),

     path('home',views.home,name='home'),
     path('navbar',views.navbar,name='navbar'),
     path('test',views.test,name='test'),
     
     # path('exam_invite/<int:exam_id>/', views.exam_invite, name='exam_invite'),
     path('exam_invite/<str:encoded_exam_id>/', views.exam_invite, name='exam_invite'),
     path('assigned_exam/<int:exam_id>/', views.assigned_exam, name='assigned_exam'),
     path('exam_not_yet_started/<str:set_date>/<str:set_time>/', views.exam_not_yet_started, name='exam_not_yet_started'),
    
    
     path('exam_already_ended/<str:set_date>/<str:set_time>/<str:allowed_time>/', views.exam_already_ended, name='exam_already_ended'),
     # path('assigned_exam_results/<int:score>/',views.assigned_exam_results, name='assigned_exam_results'),
     path('exam_not_scheduled/', views.exam_not_scheduled, name='exam_not_scheduled'),

     path('assessment', views.assessment, name='assessment'),
     path('assigned_exam_results/<int:attempt_id>/', views.assigned_exam_results, name='assigned_exam_results'),

     path('planned_exam', views.planned_exam, name='planned_exam'),
]