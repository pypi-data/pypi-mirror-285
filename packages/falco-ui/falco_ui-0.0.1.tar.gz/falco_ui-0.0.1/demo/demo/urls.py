from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("falco_ui.favicons.urls")),
    path("admin/", admin.site.urls),
]
