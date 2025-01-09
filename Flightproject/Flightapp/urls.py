from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.Front_Explore, name='Front_Explore'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('front', views.front, name='front'),
    path('result', views.result, name='result'),
    path('personalInfo/<int:flight_id>', views.personalInfo, name='personalInfo'),
    path('personalInfo/', views.personalInfo, name='personalInfo'),
    path('explore', views.explore, name='explore'),    
    path('promos', views.promos, name='promos'),
    path('adminpromos', views.adminpromos, name='adminpromos'),
    path('adminpromos2/<int:flight_id>/', views.adminpromos2, name='adminpromos2'),
    path('gatekeep', views.gatekeep, name='gatekeep'),
    path('search-flights/', views.search_flights, name='search_flights'),
    path('admin1', views.admin1, name='admin1'),
    path('admin2', views.admin2, name='admin2'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:encoded_email>/<str:token>/', views.reset_password, name='reset_password'),
    path('api/provinces-cities/', views.get_provinces_and_cities, name='provinces-cities'), 
    path('flighthistory', views.flighthistory, name='flighthistory'),
    path('user_prof', views.user_prof, name='user_prof'),
    path('generate_pdf_view/', views.generate_pdf_view, name='generate_pdf_view'),
    path('force-password-change/', views.force_password_change, name='force_password_change'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)