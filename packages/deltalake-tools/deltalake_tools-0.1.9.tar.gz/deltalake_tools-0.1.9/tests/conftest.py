import logging
import tempfile

import pandas as pd
import pytest
from deltalake import write_deltalake

from deltalake_tools.models.models import (S3ClientDetails, S3KeyPairWrite,
                                           S3Scheme, VirtualAddressingStyle,)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def s3key_pair_write() -> S3KeyPairWrite:
    return S3KeyPairWrite(
        access_key_id="test-access-key",
        secret_access_key="test-secret-access",
    )


@pytest.fixture(scope="session")
def s3_details(s3key_pair_write) -> S3ClientDetails:
    return S3ClientDetails(
        endpoint_host="localhost",
        region="us-east-1",
        virtual_addressing_style=VirtualAddressingStyle.Path,
        port=5002,
        bucket="my-test-bucket",
        hmac_keys=s3key_pair_write,
        scheme=S3Scheme.Http,
        allow_unsafe_https=True,
    )


@pytest.fixture(scope="session")
def tmp_path():
    tmp_path = tempfile.TemporaryDirectory()
    yield tmp_path.name


@pytest.fixture(scope="session")
def delta_table_path(tmp_path):
    delta_table_path = f"{tmp_path}/delta-table"

    data = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})

    write_deltalake(delta_table_path, data, mode="overwrite")

    yield delta_table_path


@pytest.fixture(scope="session")
def cli_delta_table_path(tmp_path):
    delta_table_path = f"{tmp_path}/delta-table_cli"

    data = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})

    write_deltalake(delta_table_path, data, mode="overwrite")

    yield delta_table_path


# @pytest.fixture(scope="session")
# def delta_table_with_data(tmp_path):
#     # Create a temporary directory for the Delta table
#     delta_table_path = (f"{tmp_path.name}/delta-table")

#     # Initialize the Delta table with some mock data
#     for i in range(10):
#         data = pd.DataFrame({
#             "id": [i+2, i+3],
#             "name": [f"{str(i)}_name", f"{str(i)}_other_name"]
#         })

#         write_deltalake(delta_table_path,
#                         data,
#                         mode="append"
#                     )
#     # Write the data to the Delta table
#     # write_deltalake(delta_table_path, data)

#     yield delta_table_path

# @pytest.fixture(scope="session")
# def s3_delta_table_path(s3_bucket, s3_details):
#     delta_table_path = f"s3://{s3_bucket}/cli-delta-table"

#     storage_options_result = s3_details.to_s3_config()
#     assert storage_options_result.is_ok()

#     storage_options = storage_options_result.unwrap()
#     # logger.error(f"{storage_options=}")

#     for i in range(10):
#         data = pd.DataFrame({
#             "id": [i+2, i+3],
#             "name": [f"{str(i)}_name", f"{str(i)}_other_name"]
#         })

#         write_deltalake(delta_table_path,
#                         data,
#                         mode="overwrite",
#                         storage_options=storage_options
#                     )

#     write_deltalake(delta_table_path, data, mode="append", storage_options=storage_options)

#     assert delta_table_path
#     dt = DeltaTable(delta_table_path, storage_options=storage_options)

#     assert dt.version() == 10

#     yield delta_table_path
