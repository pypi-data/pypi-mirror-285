from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from simple_media_manager.domain.command.image import BulkUploadImageCommand, DeleteImageCommand, GetImageByIDCommand, \
    RetrieveImagesCommand
from simple_media_manager.infrastructure.common.pagination import LimitOffsetPagination, get_paginated_response
from simple_media_manager.infrastructure.dependency.registry import django_compound_image_repository as DjangoCompoundImageRepository
from simple_media_manager.presentation.apis.v2.serializers.image import BriefImageOutputSerializer, \
    ImageMultipleInputSerializer, \
    ImageOutputSerializer, SearchImageInputParameterSerializer


class UploadImagesApi(APIView):

    def __init__(self, **kwargs):
        super(UploadImagesApi, self).__init__(**kwargs)
        self.upload_image = BulkUploadImageCommand(repository=DjangoCompoundImageRepository)

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "images": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "binary", }}}}},
        responses=BriefImageOutputSerializer
    )
    def post(self, request):
        serializer = ImageMultipleInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = self.upload_image.handle(files=serializer.validated_data.get('images'))
            result = BriefImageOutputSerializer(instance, many=True, context={'request': request}).data
            return Response(result)
        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)


class UpdateImageApi(APIView):

    def __init__(self, **kwargs):
        super(UpdateImageApi, self).__init__(**kwargs)
        self.upload_image = BulkUploadImageCommand(repository=DjangoCompoundImageRepository)

    @extend_schema(
        request=ImageMultipleInputSerializer(many=True),
        responses=BriefImageOutputSerializer
    )
    def patch(self, request, pk: int):
        serializer = ImageMultipleInputSerializer(many=True, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = self.upload_image.handle(files=serializer.validated_data)
            result = BriefImageOutputSerializer(instance, many=True, context={'request': request}).data
            return Response(result)
        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)


class SearchImagesApi(APIView):

    def __init__(self, **kwargs):
        super(SearchImagesApi, self).__init__(**kwargs)
        self.retrieve_images = RetrieveImagesCommand(repository=DjangoCompoundImageRepository)

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    @extend_schema(
        parameters=[SearchImageInputParameterSerializer],
        responses=BriefImageOutputSerializer
    )
    def get(self, request):
        try:
            query = self.retrieve_images.handle()
            return get_paginated_response(
                pagination_class=self.Pagination,
                serializer_class=BriefImageOutputSerializer,
                queryset=query,
                request=request,
                view=self,
            )

        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)


class GetImageByIdApi(APIView):
    def __init__(self, **kwargs):
        super(GetImageByIdApi, self).__init__(**kwargs)
        self.get_image_by_id = GetImageByIDCommand(repository=DjangoCompoundImageRepository)

    @extend_schema(
        responses=ImageOutputSerializer
    )
    def get(self, request, pk):
        try:
            query = self.get_image_by_id.handle(image_id=pk)
            result = ImageOutputSerializer(query, context={"request": request}).data
            return Response(result)
        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)


class DeleteImageByIdApi(APIView):
    def __init__(self, **kwargs):
        super(DeleteImageByIdApi, self).__init__(**kwargs)
        self.delete_image_by_id = DeleteImageCommand(repository=DjangoCompoundImageRepository)

    def delete(self, request, pk):
        try:
            self.delete_image_by_id.handle(id=pk)
            return Response(f"Successfully deleted", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)
