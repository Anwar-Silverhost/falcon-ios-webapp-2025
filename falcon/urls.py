from django.contrib import admin
from django.urls import path, include, re_path
from app import views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout', views.admin_logout, name='admin_logout'),
    path('web/', views.web,name="web"),
    path('web/',include('falcon_admin.urls')),

    #API SERVICE
    path('api/', include('api.urls')),


    path('privacy-policy', views.privacy_policy, name='privacy_policy'),
    path('support', views.support, name='support'),
    
    
        
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)