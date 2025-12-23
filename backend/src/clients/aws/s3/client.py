from concurrent.futures import ThreadPoolExecutor
from logging import Logger
from pathlib import Path
from typing import Any, Literal, overload

import boto3
from mypy_boto3_s3 import S3Client as BotoS3Client
from mypy_boto3_s3.type_defs import DeleteTypeDef, ObjectIdentifierTypeDef
from src.config.aws import S3Bucket, aws_config
from src.logger import get_logger


class S3Client:
    def __init__(self, logger: Logger | None = None) -> None:
        self.logger = logger or get_logger("S3Client-logger")
        self.__client: BotoS3Client | None = None

    @property
    def _client(self) -> BotoS3Client:
        if not self.__client:
            self.__client = boto3.client(
                service_name="s3",
                aws_access_key_id=aws_config.access_key,
                aws_secret_access_key=aws_config.secret_access_key,
            )
        return self.__client

    def close(self) -> None:
        if not self.__client:
            return
        try:
            self.__client.close()
        except Exception:
            pass

    def upload_file(
        self,
        src_filepath: Path,
        bucket: S3Bucket,
        key_prefix: str,
        dst_filename: str | None = None,
    ) -> None:
        """
        Uploads a file to s3.
        If no dst_filename is provided, dst_filename will be same as the one as src_filepath.name
        """
        self._client.upload_file(
            Filename=str(src_filepath.resolve()),
            Bucket=bucket.value,
            Key=key_prefix + "/" + (dst_filename or src_filepath.name),
        )

    def upload_fileobj(
        self,
        file,
        bucket: S3Bucket,
        key_prefix: str,
        dst_filename: str,
    ) -> None:
        """
        Uploads a file object to s3
        `file` object needs to provide a .read() method
        """
        self._client.upload_fileobj(
            Fileobj=file, Bucket=bucket.value, Key=key_prefix + "/" + dst_filename
        )

    def upload_fileobjs(
        self,
        files: list,
        bucket: S3Bucket,
        key_prefix: str,
        dst_filenames: list[str],
    ) -> None:
        """
        Uploads file objects to s3
        `files` objects needs to provide a .read() method
        """
        if not len(files) == len(dst_filenames):
            raise Exception(
                f"Files len and dst_filenames are not equal: {len(files)=}, {len(dst_filenames)=}"
            )

        def one_upload_fileobj(file_filename: tuple[Any, str]) -> None:
            file, dst_filename = file_filename
            self.upload_fileobj(
                file=file,
                bucket=bucket,
                key_prefix=key_prefix,
                dst_filename=dst_filename,
            )

        with ThreadPoolExecutor(max_workers=20) as pool:
            list(
                pool.map(
                    one_upload_fileobj, [(f, df) for f, df in zip(files, dst_filenames)]
                )
            )

    def download_file(
        self,
        dst_folder: Path,
        s3_filename: str,
        bucket: S3Bucket,
        key_prefix: str,
        dst_filename: str | None = None,
    ) -> None:
        """
        Download a file to s3.
        If no dst_filename is provided, dst_filename will be same as the one as s3_filename
        """
        self._client.download_file(
            Bucket=bucket.value,
            Key=key_prefix + "/" + s3_filename,
            Filename=str(dst_folder / (dst_filename or s3_filename)),
        )

    @overload
    def presigned_url(
        self,
        bucket: S3Bucket,
        expires_in_s: int = 1800,
        client_method: Literal["get_object"] = "get_object",
        *,
        prefix: str,
        filename: str,
    ) -> str: ...

    @overload
    def presigned_url(
        self,
        bucket: S3Bucket,
        expires_in_s: int = 1800,
        client_method: Literal["get_object"] = "get_object",
        *,
        key: str,
    ) -> str: ...

    def presigned_url(
        self,
        bucket: S3Bucket,
        expires_in_s: int = 1800,
        client_method: Literal["get_object"] = "get_object",
        **kwargs,
    ) -> str:
        if "key" in kwargs:
            key = kwargs["key"]
        else:
            key = f"{kwargs["prefix"]}/{kwargs["filename"]}"
        return self._client.generate_presigned_url(
            ClientMethod=client_method,
            Params=dict(Bucket=bucket.value, Key=key),
            ExpiresIn=expires_in_s,
        )

    @overload
    def presigned_urls(
        self,
        bucket: S3Bucket,
        expires_in_s: int = 1800,
        client_method: Literal["get_object"] = "get_object",
        *,
        prefix: str,
        filenames: list[str],
    ) -> list[str]: ...

    @overload
    def presigned_urls(
        self,
        bucket: S3Bucket,
        expires_in_s: int = 1800,
        client_method: Literal["get_object"] = "get_object",
        *,
        keys: list[str],
    ) -> list[str]: ...

    def presigned_urls(
        self,
        bucket: S3Bucket,
        expires_in_s: int = 1800,
        client_method: Literal["get_object"] = "get_object",
        **kwargs,
    ) -> list[str]:
        if "keys" in kwargs:
            keys = kwargs["keys"]
        else:
            keys = [f"{kwargs["prefix"]}/{f}" for f in kwargs["filename"]]

        def one_presigned_url(key: str) -> str:
            return self.presigned_url(
                bucket=bucket,
                expires_in_s=expires_in_s,
                client_method=client_method,
                key=key,
            )

        with ThreadPoolExecutor(max_workers=20) as pool:
            return list(pool.map(one_presigned_url, keys))

    def delete_file(self, bucket: S3Bucket, key: str) -> None:
        self._client.delete_object(Bucket=bucket.value, Key=key)

    def delete_files(self, bucket: S3Bucket, keys: list[str]) -> None:
        for offset in range(0, len(keys), 1000):
            keys_chunk = keys[offset : offset + 1000]
            delete_type_def = DeleteTypeDef(
                Objects=[ObjectIdentifierTypeDef(Key=k) for k in keys_chunk]
            )
            self._client.delete_objects(Bucket=bucket.value, Delete=delete_type_def)
