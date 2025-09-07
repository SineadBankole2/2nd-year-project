from django.urls import path
from . import views
from .views import stock_management, add_product, delete_product, filter_list, product_detail, stock_search, update_stock
from questions.views import answerQ

app_name = 'store'

urlpatterns = [
    path('store/men/', views.mens_view, name='mens_view'),
    path('store/<str:main_category>/', views.category_view, name='category_view'),
    path('products/', views.all_products_view, name='all_products'),
    path('admin/stock/', stock_management, name='stock_management'), 
    path('admin/stock/add/', add_product, name='add_product'),
    path('admin/stock/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('filter/', filter_list, name='filter_list'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('admin/stock/search/', views.stock_search, name='stocksearch'),
    path('admin/stock/update/', views.update_stock, name='update_stock'),
    path('answer/<int:question_id>/', answerQ, name='answer_q'),
    path('admin/analysis/', views.analytics_dashboard, name='admin_analytics'),
    
]
