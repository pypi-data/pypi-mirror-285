from django.contrib import admin

from simple_media_manager.infrastructure.models import Image


class ImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Image)
