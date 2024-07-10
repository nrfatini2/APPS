from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from .import views

urlpatterns = [
    # Utility URLs
    path('', views.index, name="home"),
    path('about', views.about, name='about'),
    path('feedback',views.feedback,name='feedback'),
    
    # User Authentication URLs
    path('signup/', views.signup,name="signup"),
    path('login/', LoginView.as_view(template_name="main/login.html"),name="login"),
    path('logout', views.logout_view, name='logout'),
    path('editprofile/<id>/',views.editprofile,name='editprofile'),
    
    # User Management URLs
    path('read',views.read_user,name='read'),
    path('create',views.create_user,name='create'),
    path('update/<id>/',views.update_user,name='update'),
    path('delete/<id>/',views.delete_user,name='delete'),
    
    # Production Plan Management URLs
    path('planList', views.planList, name='planList'),
    path('inputVariables/<plan_ID>/', views.inputVariables, name='inputVariables'),
    path('deletePlan/<plan_ID>', views.deletePlan, name='deletePlan'),
    path('initiateOptimize/<plan_ID>', views.initiateOptimize, name='initiateOptimize'),
    
    path('initiateSensitivity/<plan_ID>/', views.initiateSensitivity, name='initiateSensitivity'),
    
    path('download/<plan_ID>/', views.download,name='download'),
]
