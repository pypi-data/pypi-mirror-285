import oss2
from typing import Union
from oss2.models import PartInfo
from requests import Response
from cobweb import log


class OssDB:

    def __init__(
            self,
            bucket_name,
            endpoint,
            access_key,
            secret_key,
            chunk_size=1024 ** 2,
            min_size=1024
    ):
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.auth = oss2.Auth(
            access_key_id=access_key,
            access_key_secret=secret_key
        )
        self.bucket = oss2.Bucket(
            auth=self.auth,
            endpoint=endpoint,
            bucket_name=bucket_name
        )
        self.chunk_size = chunk_size
        self.min_size = min_size

    @staticmethod
    def format_upload_len(length):
        if not length:
            raise ValueError("Length cannot be None or 0")

        units = ["KB", "MB", "GB", "TB"]
        for i in range(3):
            num = length / (1024 ** (i + 1))
            if num <= 1024:
                return f"{round(num, 2)} {units[i]}"

    def assemble(self, ready_data, part_data):
        upload_data = None
        ready_data = ready_data + part_data
        if len(ready_data) >= self.chunk_size:
            upload_data = ready_data[:self.chunk_size]
            ready_data = ready_data[self.chunk_size:]

        return ready_data, upload_data

    def iter_data(self, data):
        if isinstance(data, Response):
            for part_data in data.iter_content(self.chunk_size):
                yield part_data
        if isinstance(data, bytes):
            for i in range(0, len(data), self.chunk_size):
                yield data[i:i + self.chunk_size]

    def upload_split(
            self, oss_path: str,
            data: Union[bytes, Response],
            timeout: int = 300,
    ):
        parts = []
        status = False
        upload_id = None
        ready_data = b""
        upload_data_len = 0
        headers = {"Expires": str(timeout * 1000)}
        try:
            upload_id = self.bucket.init_multipart_upload(oss_path).upload_id
            for part_data in self.iter_data(data):
                upload_data_len += len(part_data)
                ready_data, upload_data = self.assemble(ready_data, part_data)
                if upload_data:
                    part_index = len(parts) + 1
                    upload_info = self.bucket.upload_part(
                        oss_path, upload_id, part_index, upload_data
                    )
                    parts.append(PartInfo(part_index, upload_info.etag))

            format_upload = self.format_upload_len(upload_data_len)

            if parts and ready_data:
                part_index = len(parts) + 1
                upload_info = self.bucket.upload_part(
                    oss_path, upload_id, part_index, ready_data
                )
                parts.append(PartInfo(part_index, upload_info.etag))
                self.bucket.complete_multipart_upload(
                    oss_path, upload_id, parts
                )
                log.info(
                    f"split upload, file path: {oss_path}"
                    f", file size: {format_upload}"
                )

            elif len(ready_data) > self.min_size:
                self.bucket.put_object(oss_path, ready_data, headers)
                log.info(
                    f"upload file, file path: {oss_path}"
                    f", file size: {format_upload}"
                )

            # else:
            #     log.info(
            #         f"file size smaller than min size! "
            #         f"file size: {format_upload}"
            #     )
            status = True
        except ValueError as e:
            pass
            # log.exception(str(e))
        except oss2.exceptions.RequestError as e:
            self.bucket = oss2.Bucket(
                auth=self.auth,
                endpoint=self.endpoint,
                bucket_name=self.bucket_name
            )
            log.exception("oss timeout! " + str(e))
        except Exception as e:
            self.bucket.abort_multipart_upload(oss_path, upload_id, headers)
            log.exception("upload file exception: " + str(e))

        return status

