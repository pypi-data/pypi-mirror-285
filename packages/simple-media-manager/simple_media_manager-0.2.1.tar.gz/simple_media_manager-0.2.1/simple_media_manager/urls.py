from django.urls import include, path

from simple_media_manager.presentation.apis.v1.image import DeleteImageByIdApi, GetImageByIdApi, GetImagesApi, UploadImageApi

urlpatterns = [

    # Image # TODO must be removed later on
    path("", include('simple_media_manager.presentation.apis.v1.urls', namespace='v1')),
    path("v2/", include('simple_media_manager.presentation.apis.v2.urls', namespace='v2')),

]
