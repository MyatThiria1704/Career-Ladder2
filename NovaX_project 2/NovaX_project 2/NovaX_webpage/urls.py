from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('quiz_hub/', views.quiz_hub, name='quiz_hub'),
    
    path('aptitude_test/', views.aptitude_test_Q, name='aptitude_test_Q'),
    path('aptitude_result/', views.aptitude_test_R, name='aptitude_test_R'),
    path('educational_test/', views.educational_test_Q, name='educational_test_Q'),
    path('educational_major_selection/', views.educational_major_selection, name='educational_major_selection'),
    path('educational_major_selection/educational_test_CSE/', views.educational_test_CSE_Q, name='educational_test_CSE_Q'),
    path('educational_test_CSE_result/', views.educational_test_CSE_result, name='educational_test_CSE_result'),
    path('combined_test/', views.combined_test_Q, name='combined_test_Q'),
    path('api/save-survey/', views.save_survey, name='save_survey'), 
      
     # AI Counseling URLs
    path('predict-career/', views.predict_career, name='predict_career'),
    path('career-counseling/', views.career_counseling, name='career_counseling'),
    path('start-counseling/', views.start_counseling, name='start_counseling'),
    path('process-answer/', views.process_counseling_answer, name='process_answer'),
    path('download-report/', views.download_career_report, name='download_report'),
    path('conversation-history/', views.get_conversation_history, name='conversation_history'),

    path('architecture_path/', views.architecture_path, name='architecture_path'),
    path('institution_detail/', views.institution_detail, name='institution_detail'),
    path('private_colleges/', views.private_colleges, name='private_colleges'),
    path('private-colleges/<int:pk>/', views.private_college_detail, name='private_college_detail'),
    path('public_universities/', views.public_universities, name='public_universities'),
    path('public-universities/<int:pk>/', views.public_university_detail, name='public_university_detail'),
]
