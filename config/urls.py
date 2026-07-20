from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

admin.site.site_header = "Administration boutique"
admin.site.site_title = "Admin boutique"
admin.site.index_title = "Gestion du site de vente"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("core.urls")),
    path("", include("catalog.urls")),
    path("", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
