from django.urls import path

from simple_media_manager.presentation.apis.v1.image import DeleteImageByIdApi, GetImageByIdApi, GetImagesApi, UploadImageApi

app_name = 'v1'

urlpatterns = [
    # path('upload-image', UploadImageApi.as_view(), name='upload_image'),
    path('get-images', GetImagesApi.as_view(), name='get_images'),
    path('get-image', GetImageByIdApi.as_view(), name='get_image_by_id'),
    path('delete-image', DeleteImageByIdApi.as_view(), name='delete_image_by_id'),
]
