from uuid import UUID

from sempy.fabric._client._base_dataset_client import BaseDatasetClient
from sempy.fabric._environment import _get_onelake_endpoint
from sempy.fabric._token_provider import TokenProvider
from sempy.fabric._utils import SparkConfigTemporarily

from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from sempy.fabric._client import WorkspaceClient


class DatasetOneLakeImportClient(BaseDatasetClient):
    def __init__(
            self,
            workspace: Union[str, "WorkspaceClient"],
            dataset: Union[str, UUID],
            token_provider: Optional[TokenProvider] = None
    ):
        BaseDatasetClient.__init__(self, workspace, dataset, token_provider)

    def _get_pandas_table(self, table_name, num_rows, verbose):
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()

        workspace_id = self.resolver.workspace_id
        dataset_id = self.resolver.dataset_id

        host = _get_onelake_endpoint()

        url = f"abfss://{workspace_id}@{host}/{dataset_id}/Tables/{table_name}"

        # the Spark config is only relevant at toPandas(), but to be avoid any future mistakes, let's wrap the whole.
        with SparkConfigTemporarily(spark, "spark.sql.parquet.datetimeRebaseModeInRead", "CORRECTED"):
            df = spark.read.format("delta").load(url)

            if num_rows is not None:
                df = df.limit(num_rows)

            # PowerBI datasets frequently have old dates.
            return df.toPandas()
