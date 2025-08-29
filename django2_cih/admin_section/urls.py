from django.urls import path
from .import views


urlpatterns=[
    path('',views.login,name='login'),
    path('header',views.header,name='header'),
    path('index',views.index,name='index'),
    path('deletecat/<int:id>/',views.deletecat,name='deletecat'),
    path('updatecat/<int:id>/',views.updatecat,name='updatecat'),
    path('deletequiz/<int:id>/',views.deletequiz,name='deletequiz'),

    path('check-category-exists/', views.check_category_exists, name='check_category_exists'),
    path('newcategory',views.newcategory,name='newcategory'),
    path('newquiz',views.newquiz,name='newquiz'),
    path('newviewquiz',views.newviewquiz,name='newviewquiz'),
    path('newupdatequiz/<int:id>/',views.newupdatequiz,name='newupdatequiz'),

    path('check_email', views.check_email, name='check_email'),
    path('viewregister',views.viewregister,name='viewregister'),
    path('deleteuser/<int:id>/',views.deleteuser,name='deleteuser'),
    path('updateuser/<int:id>/',views.updateuser,name='updateuser'),
    path('register_users',views.register_users,name='register_users'),
   
    path('profile',views.profile,name='profile'),
    path('adminlogout',views.adminlogout,name='adminlogout'),

    path('schedule_exam',views.schedule_exam, name='schedule_exam'),
    path('questions_page',views.submit_selected_questions, name='questions_page'),
    path('attempted_quiz/<int:user_id>/', views.attempted_quiz, name='attempted_quiz'),
    path('attempted_result/<int:attempt_id>/', views.attempted_result, name='attempted_result'),
    path('aptitude_details/<int:attempt_id>/', views.aptitude_details, name='aptitude_details'),

    path('permission',views.permissions,name='permission'),
    path('deletepermit/<int:id>/',views.deletepermit,name='deletepermit'),
    path('updatepermit/<int:id>/',views.updatepermit,name='updatepermit'),

    path('roles',views.roles,name='roles'),
    path('view_roles',views.view_roles,name='view_roles'),
    path('delete_role/<int:role_id>/', views.delete_role, name='delete_role'),
    path('update_role/<int:role_id>/', views.update_role, name='update_role'),
    
    path('super_check_email', views.super_check_email, name='super_check_email'),
    path('superusers',views.superusers,name='superusers'),
    path('view_superusers',views.view_superusers,name='view_superusers'),
    path('update_superusers/<int:id>',views.update_superusers,name='update_superusers'),
    path('delete_superusers/<int:id>',views.delete_superuser,name='delete_superusers'),
    path('organisations',views.organisations,name='organisations'),
    path('update_organisations/<int:id>',views.update_organisations,name='update_organisations'),
    path('delete_organisations/<int:id>',views.delete_organisations,name='delete_organisations'),

    path('verify_quiz/', views.verify_quiz, name='verify_quiz'),
    path('verify_question/<int:question_id>/', views.verify_question, name='verify_question'),
    path('verify_update/<int:id>',views.verify_update,name='verify_update'),
    path('verify_delete/<int:id>',views.verify_delete,name='verify_delete'),

    path('subcategories',views.subcategories,name='subcategories'),
    path('view_subcategory',views.view_subcategory,name='view_subcategory'),
    path('update_subcat/<int:id>',views.update_subcat,name='update_subcat'),
    path('delete_subcat/<int:id>',views.delete_subcat,name='delete_subcat'),

    path('viewlog/<int:question_id>/', views.viewlog, name='viewlog'),
    path('get_subcategories/', views.get_subcategories, name='get_subcategories'),
    path('get_subcategories_by_category/', views.get_subcategories_by_category, name='get_subcategories_by_category'),
    
    path('create_exam', views.create_exam, name='create_exam'),
    path('create_questions/<int:exam_id>/', views.create_questions, name='create_questions'),
    
    # path('exam_invite/<int:exam_id>/', views.exam_invite, name='exam_invite'),
    
    path('view_exams',views.view_exams,name='view_exams'),
    path('delete_exam/<int:id>',views.delete_exam,name='delete_exam'), 
    path('see_exam_questions/<int:exam_id>/', views.see_exam_questions, name='see_exam_questions'),

    path('view_applied_exams', views.view_applied_exams, name='view_applied_exams'),
    path('already_scheduled', views.already_scheduled, name='already_scheduled'),
    path('delete_application/<int:id>',views.delete_application,name='delete_application'),

    path('assign_exam/<int:application_id>/', views.assignexam, name='assign_exam'),

    path('my_questions',views.my_questions,name='my_questions'),

    path('exam_time_slot',views.exam_time_slot,name='exam_time_slot')
    
]