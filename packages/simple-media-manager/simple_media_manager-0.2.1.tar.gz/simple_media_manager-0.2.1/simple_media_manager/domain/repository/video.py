from abc import ABC, abstractmethod

from . import AbstractRepository


class VideoReadRepository(AbstractRepository):

    @abstractmethod
    def get(self, pk: int):
        ...

    @abstractmethod
    def find(self, name: str):
        ...

    @abstractmethod
    def all(self):
        ...


class VideoWriteRepository(AbstractRepository):
    @abstractmethod
    def save(self, file: bytes, name: str):
        ...

    @abstractmethod
    def bulk_save(self, files: list):
        ...

    @abstractmethod
    def delete(self, pk: int):
        ...


class VideoRepository(VideoReadRepository, VideoWriteRepository, ABC):
    ...


class CompoundVideoRepository(VideoRepository):
    def __init__(self, read_repository: VideoReadRepository, write_repository: VideoWriteRepository):
        self.read_repository = read_repository
        self.write_repository = write_repository

    def get(self, pk: int):
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
