from django.urls import include, path

from simple_media_manager.presentation.apis.v2.image import DeleteImageByIdApi, GetImageByIdApi, SearchImagesApi, \
    UpdateImageApi, \
    UploadImagesApi

app_name = 'v2'
urlpatterns = [
    path('image/', include([
        path('<int:pk>/delete', DeleteImageByIdApi.as_view(), name='delete_image_by_id'),
        path('<int:pk>', GetImageByIdApi.as_view(), name='get_image'),
        path('<int:pk>/update', UpdateImageApi.as_view(), name='upload_image_v2'),
        path('upload', UploadImagesApi.as_view(), name='upload_image_v2'),
        path('search', SearchImagesApi.as_view(), name='search_images'),
    ]))
]
