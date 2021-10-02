from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url
from django.contrib.auth.views import LoginView,LogoutView
from .views import home,signup_view,login_request,change_password
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    #url(r'login$',  LoginView.as_view(template_name = 'login.html'),name='login'),
    url(r'login$',  login_request, name='login_request'),
    url(r'logout$', LogoutView.as_view(),name='logout'),
    url(r'signup$', signup_view, name='signup'),
    url(r'^password/$', change_password, name='change_password'),
    url(r'^birds/', include('website.urls')),
    url(r'', home,name='home'),

]
#+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


