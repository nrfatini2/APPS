from django.urls import path
from django.contrib.auth.views import LoginView
from .import views

urlpatterns = [
    # Utility URLs
    path('', views.index, name="home"),
    path('about/', views.about, name='about'),
    
    # User Authentication URLs
    path('register/', views.register,name="register"),
    path('login', LoginView.as_view(template_name="main/login.html"),name="login"),
    path('logout', views.logout_view, name='logout'),
    path('edit-profile/<id>',views.edit_profile,name='edit-profile'),
    
    # User Management URLs
    path('read-user',views.read_user,name='read-user'),
    path('create-user',views.create_user,name='create-user'),
    path('update-user/<id>',views.update_user,name='update-user'),
    path('delete-user/<id>',views.delete_user,name='delete-user'),
    
    # Production Plan Management URLs
    path('get-plan-list', views.get_plan_list, name='get-plan-list'),
    path('input_plan_variables/<plan_ID>', views.input_plan_variables, name='input_plan_variables'),
    path('delete_plan/<plan_ID>', views.delete_plan, name='delete_plan'),
    path('initiate_plan_optimize/<plan_ID>', views.initiate_plan_optimize, name='initiate_plan_optimize'),
    path('initiate_sensitivity_analysis/<plan_ID>', views.initiate_sensitivity_analysis, name='initiate_sensitivity_analysis'),
    path('generate_report/<plan_ID>', views.generate_report,name='generate_report'),
]