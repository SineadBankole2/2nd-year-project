from django.urls import path
from .views import askQ, listQ, answerQ, unanswered_questions


app_name = 'questions'  

urlpatterns = [
    path('ask/', askQ, name='ask_q'),
    path('', listQ, name='list'),  
    path('answer/<int:question_id>/', answerQ, name='answer_q'),
    path('admin/unanswered/', unanswered_questions, name='unanswered_admin'),
]
