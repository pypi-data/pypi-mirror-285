from simple_media_manager.domain.repository.video import VideoWriteRepository


class DjangoImageWriteRepository(VideoWriteRepository):
    def save(self, file: bytes, name: str):
        pass

    def bulk_save(self, files: list):
        pass

    def delete(self, pk: int):
        pass
