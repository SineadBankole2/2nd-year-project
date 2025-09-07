from django.urls import path
from .views import ReviewsView, SubmitReviewView, delete_review
from . import views

urlpatterns = [
    path('', ReviewsView.as_view(), name='reviews'),  
    path('submit/', SubmitReviewView.as_view(), name='submit_review'),
    path('delete/<int:review_id>/', delete_review, name='delete_review'),
    path('like-test/', views.like_test, name='like_test'),
    path('like-test-action/<int:review_id>/', views.test_like_review, name='test_like_review'),
    path('like-review/<int:review_id>/', views.like_review, name='like_review'),

]
