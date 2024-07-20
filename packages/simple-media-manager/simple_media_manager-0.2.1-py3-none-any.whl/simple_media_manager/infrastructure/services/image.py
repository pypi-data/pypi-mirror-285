from io import BytesIO

from PIL import Image as PillowImage, ImageOps
from django.core.files import File
from django.core.files.uploadedfile import TemporaryUploadedFile

from simple_media_manager.domain.entities.constants import MINIMUM_HHEIGHT, MINIMUM_HWIDTH, MINIMUM_VHEIGHT, MINIMUM_VWIDTH
from simple_media_manager.domain.entities.enums import ImageSizeOrientation


class ImageProcessingService:

    @classmethod
    def _is_image_resizable(cls, min_width: int, min_height: int, image_width: int, image_height: int) -> bool:
        if image_width > min_width or image_height > min_height:
            return True
        return False

    @classmethod
    def _get_new_size(cls, width: int, height: int, resize_percent: int) -> tuple[int, int]:
        new_size = (
            int(width - width * (resize_percent / 100)),
            int(height - height * (resize_percent / 100))
        )
        return new_size

    @classmethod
    def _get_image_orientation(cls, image: PillowImage):
        if image.width < image.height:
            return ImageSizeOrientation.VERTICAL
        elif image.width > image.height:
            return ImageSizeOrientation.HORIZONTAL
        elif image.width == image.height:
            return ImageSizeOrientation.SQUARE

    @classmethod
    def resize_image(cls, image_file: TemporaryUploadedFile, resize_percent: int) -> File:
        image = PillowImage.open(image_file)
        img_format = image.format
        image = ImageOps.exif_transpose(image)
        should_be_resized = False
        match cls._get_image_orientation(image=image):
            case ImageSizeOrientation.VERTICAL:
                should_be_resized = cls._is_image_resizable(MINIMUM_VWIDTH,
                                                            MINIMUM_VHEIGHT,
                                                            image_width=image.width,
                                                            image_height=image.height)
            case ImageSizeOrientation.HORIZONTAL:
                should_be_resized = cls._is_image_resizable(MINIMUM_HWIDTH,
                                                            MINIMUM_HHEIGHT,
                                                            image_width=image.width,
                                                            image_height=image.height)
            case ImageSizeOrientation.SQUARE:
                should_be_resized = cls._is_image_resizable(MINIMUM_VWIDTH,
                                                            MINIMUM_VWIDTH,
                                                            image_width=image.width,
                                                            image_height=image.height)
            case _:
                raise Exception("Orientation is not recognizable")

        if should_be_resized:
            new_size = cls._get_new_size(image.width, image.height, resize_percent=resize_percent)
            image = image.resize(new_size, resample=4)

        image_io = BytesIO()
        image.save(image_io, format=img_format, quality=60, optimize=True)
        django_image = File(image_io, name=image_file.name)
        return django_image
