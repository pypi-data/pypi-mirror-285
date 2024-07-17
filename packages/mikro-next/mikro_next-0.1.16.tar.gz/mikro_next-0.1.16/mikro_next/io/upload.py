from typing import TYPE_CHECKING
from mikro_next.scalars import ArrayLike, ParquetLike, FileLike
import asyncio
import s3fs
from aiobotocore.session import get_session
import botocore
from concurrent.futures import ThreadPoolExecutor
from .errors import PermissionsError, UploadError


if TYPE_CHECKING:
    from mikro_next.api.schema import CredentialsFragment
    from mikro_next.datalayer import DataLayer


def _store_xarray_input(
    xarray: ArrayLike,
    credentials: "CredentialsFragment",
    endpoint_url: "DataLayer",
) -> str:
    """Stores an xarray in the DataLayer"""

    filesystem = s3fs.S3FileSystem(
        secret=credentials.secret_key,
        key=credentials.access_key,
        client_kwargs={
            "endpoint_url": endpoint_url,
            "aws_session_token": credentials.session_token,
        },
    )

    # random_uuid = uuid.uuid4()
    # s3_path = f"zarr/{random_uuid}.zarr"
    dataset = xarray.value.to_dataset(name="data")
    dataset.attrs["fileversion"] = "v1"

    s3_path = f"{credentials.bucket}/{credentials.key}"

    try:
        store = filesystem.get_mapper(s3_path)
        dataset.to_zarr(store=store, consolidated=True, compute=True)
        return credentials.store
    except Exception as e:
        raise UploadError(f"Error while uploading to {s3_path}") from e


def _store_parquet_input(
    parquet_input: ParquetLike,
    credentials: "CredentialsFragment",
    endpoint_url: str,
) -> str:
    """Stores an xarray in the DataLayer"""
    import pyarrow.parquet as pq
    from pyarrow import Table
    filesystem = s3fs.S3FileSystem(
        secret=credentials.secret_key,
        key=credentials.access_key,
        client_kwargs={
            "endpoint_url": endpoint_url,
            "aws_session_token": credentials.session_token,
        },
    )

    table: Table = Table.from_pandas(parquet_input.value)

    try:
        s3_path = f"s3://{credentials.bucket}/{credentials.key}"
        pq.write_table(table, s3_path, filesystem=filesystem)
        return credentials.store
    except Exception as e:
        raise UploadError(f"Error while uploading to {s3_path}") from e


async def aupload_bigfile(
    file: FileLike,
    credentials: "CredentialsFragment",
    datalayer: "DataLayer",
    executor: ThreadPoolExecutor = None,
) -> str:
    """Store a DataFrame in the DataLayer"""
    session = get_session()

    endpoint_url = await datalayer.get_endpoint_url()

    async with session.create_client(
        "s3",
        region_name="us-west-2",
        endpoint_url=endpoint_url,
        aws_secret_access_key=credentials.secret_key,
        aws_access_key_id=credentials.access_key,
        aws_session_token=credentials.session_token,
    ) as client:
        try:
            await client.put_object(
                Bucket=credentials.bucket, Key=credentials.key, Body=file.value
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "InvalidAccessKeyId":
                return PermissionsError(
                    "Access Key is invalid, trying to get new credentials"
                )

            raise e

    return credentials.store


async def aupload_xarray(
    array: ArrayLike,
    credentials: "CredentialsFragment",
    datalayer: "DataLayer",
    executor: ThreadPoolExecutor,
) -> str:
    """Store a DataFrame in the DataLayer"""
    co_future = executor.submit(
        _store_xarray_input, array, credentials, await datalayer.get_endpoint_url()
    )
    return await asyncio.wrap_future(co_future)


async def aupload_parquet(
    parquet: ParquetLike,
    credentials: "CredentialsFragment",
    datalayer: "DataLayer",
    executor: ThreadPoolExecutor,
) -> str:
    """Store a DataFrame in the DataLayer"""
    co_future = executor.submit(
        _store_parquet_input, parquet, credentials, await datalayer.get_endpoint_url()
    )
    return await asyncio.wrap_future(co_future)
