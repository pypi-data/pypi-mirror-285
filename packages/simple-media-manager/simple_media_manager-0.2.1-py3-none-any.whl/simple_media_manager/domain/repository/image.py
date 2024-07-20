from abc import ABC, abstractmethod

from . import AbstractRepository
from ...infrastructure.models.image import Image


class ImageReadRepository(AbstractRepository):

    @abstractmethod
    def get(self, pk: int):
        ...

    @abstractmethod
    def find(self, name: str):
        ...

    @abstractmethod
    def all(self):
        ...


class ImageWriteRepository(AbstractRepository):
    @abstractmethod
    def save(self, file: bytes, name: str):
        ...

    @abstractmethod
    def bulk_save(self, files: list):
        ...

    @abstractmethod
    def delete(self, id: int):
        ...


class ImageRepository(ImageReadRepository, ImageWriteRepository, ABC):
    ...


class CompoundImageRepository(ImageRepository):
    def __init__(self, read_repository: ImageReadRepository, write_repository: ImageWriteRepository):
        self.read_repository = read_repository
        self.write_repository = write_repository

    def get(self, pk: int) -> Image:
        return self.read_repository.get(pk=pk)

    def find(self, name: str):
        return self.read_repository.find(name=name)

    def all(self):
        return self.read_repository.all()

    def save(self, file: bytes, name: str):
        return self.write_repository.save(file=file, name=name)

    def bulk_save(self, files: list):
        return self.write_repository.bulk_save(files=files)

    def delete(self, id: int):
        self.write_repository.delete(id=id)
