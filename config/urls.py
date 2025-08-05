from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Your API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@yourproject.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', lambda request: HttpResponse("🚀 서버 정상 작동 중입니다!")),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    #path('postss/', include('posts.urls')),
    #path('products/', include('products.urls')),
   # path('chat/', include('chat.urls')),
]
