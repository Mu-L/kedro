# Copyright 2021 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
# or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.
"""Databricks specific DataSets"""
import functools
from typing import Any, Dict

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, DataFrameWriter

from kedro.extras.datasets.spark import SparkDataSet
from kedro.io.core import Version


class DeltaTableDataset(SparkDataSet):
    """
    Schema validation: https://docs.databricks.com/delta/delta-batch.html#schema-validation-1
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        filepath: str,
        delta_options: Dict[str, Any] = None,
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
        version: Version = None,
        credentials: Dict[str, Any] = None,
    ) -> None:
        super().__init__(
            filepath=filepath,
            file_format="delta",
            load_args=load_args,
            save_args=save_args,
            version=version,
            credentials=credentials,
        )
        self._delta_options = delta_options
        self._update_options = save_args.pop(
            "insert_options"
        )  # TBD - maybe better solution?
        self._insert_options = save_args.pop(
            "update_options"
        )  # TBD - maybe better solution?
        self._upsert_columns = save_args.pop(
            "upsert_columns"
        )  # TBD - maybe better solution?

    def _add_options(self, df: DataFrame) -> DataFrameWriter:
        # DeltaTable specific opts, such as `schemaValidation`
        if self._delta_options:
            df_writer = df.write
            return functools.reduce(
                lambda dfw, opt: df_writer.option(opt, self._delta_options[opt]),
                self._delta_options,
                df_writer,
            )
        return df.write

    def _load(self):
        load_path = self._fs_prefix + str(self._get_load_path())
        return DeltaTable.forPath(self._get_spark(), load_path)

    def _overwrite(self, df: DataFrame):
        save_path = self._fs_prefix + str(self._get_save_path())
        self._add_options(df).format(self._file_format).mode("overwrite").save(
            save_path
        )

    def _append(self, df: DataFrame):
        save_path = self._fs_prefix + str(self._get_save_path())
        self._add_options(df).format(self._file_format).mode("append").save(save_path)

    def _update(self, df: DeltaTable):
        # this should be define and retrievable from conf
        df.update(self._update_options["foo"], self._update_options["bar"])

    def _upsert(self, df: DeltaTable, other: DeltaTable):
        # how to handle `other`?
        df.alias("a").merge(
            other.alias("b"), f"a.{self._upsert_columns} = b.{self._upsert_columns}"
        ).whenMatchedUpdate(set=self._update_options).whenNotMatchedInsert(
            values=self._insert_options
        ).execute()

    def _delete(self, df: DeltaTable):
        df.delete("delete predicate here")

    def _save(self, df: DataFrame):
        # this needs a strat pattern to resolve the methods above
        # also - remove super call
        super()._save(data=df)
