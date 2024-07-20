from io import BytesIO

from PIL import Image as PillowImage
from django.core.files import File as DjangoFile
from django.db import models, transaction

from ..models.file import File


class Image(File):
    original = models.ImageField(upload_to='media/images/originals', null=True, verbose_name='original size')
    thumbnail = models.ImageField(upload_to='media/images/thumbnails', null=True, verbose_name='thumbnail size')
    compact = models.ImageField(upload_to='media/images/compacts', null=True, verbose_name='compact size')

    def delete_files(self):
        self.original.delete()
        self.thumbnail.delete()
        self.compact.delete()

    def delete(self, using=None, keep_parents=False):
        with transaction.atomic():
            self.delete_files()
            super(Image, self).delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        if not self.name:
            return self.original.name
        return self.name

    class Meta:
        ordering = ('-created_at',)
