"""
Python module that loads YAML config to Dagster Asset Checks from YAML
"""
from enum import Enum
from typing import Generator, List

import polars as pl
from dagster import (
    AssetCheckResult,
    AssetChecksDefinition,
    AssetExecutionContext,
    asset_check,
)
from jinja2 import Template
from jsonschema.exceptions import ValidationError

from core_library.utilities.data_utils import key_values_in_lod
from core_library.utilities.file_utils import (
    get_files_directory,
    json_read_file,
    yaml_read_file,
    yaml_validate_schema,
)
from core_library.utilities.misc_utils import setup_console_logger

mds_logger = setup_console_logger()


class Engines(Enum):
    """
    Engines we have defined for Asset Checks
    """

    polars = "polars"


class PolarsAssetChecks:
    """
    Asset checks for polars
    Each check should return the 'illegal' records
    """

    def main_handler(self, test_name: str, column: str) -> str:
        """
        Function that handles what Data Asset Check to call

        :param test_name: test name to run
        :type test_name: str
        :param column: column to run the test on
        :type column: str
        :raises Exception: If check is not implemented
        :return: code to execute
        :rtype: str
        """
        if test_name == "not_null":
            return self.not_null(column=column)
        elif test_name == "unique":
            return self.unique(column=column)
        else:
            raise Exception(f"Asset Check {test_name} is not configured")

    def not_null(self, column: str) -> str:
        """
        Polars Data Test for not_null columns

        :param column: column to check
        :type column: str
        :return: Failed records
        :rtype: str
        """
        template = Template("df.filter(pl.col('{{ column }}').is_null())")
        generated_code = template.render(column=column)
        return generated_code

    def unique(self, column: str) -> str:
        """
        Polars Data Test for unique columns

        :param column: column to check
        :type column: str
        :return: Failed records
        :rtype: str
        """
        template = Template("df.filter(pl.col('{{ column }}').is_duplicated())")
        generated_code = template.render(column=column)
        return generated_code


def load_yaml_asset_check_files(
    directory: str = "mds_dagster/asset_checks"
) -> Generator[List, None, None]:
    """
    Load all the YAML Asset Check files into a Generator of lists

    :param directory: directory to load yaml files from, defaults to "mds_dagster/asset_checks"
    :type directory: str, optional
    :yield: List data from YAML file of tests
    :rtype: Generator
    """
    files = get_files_directory(directory=directory, file_extension=".yaml")
    for file in files:
        asset_check_def = yaml_read_file(file_path=file)
        # Validate the schema
        try:
            asset_check_schema = json_read_file(
                "mds_dagster/asset_checks/asset_checks_schema.json"
            )
            yaml_validate_schema(asset_check_def, asset_check_schema)
        except ValidationError:
            mds_logger.error(f"File: {file} failed yaml asset_check_schema validation")
            continue

        # Validate the engine value
        engines = key_values_in_lod(
            asset_check_def.get("data_tests"), select_key="engine"
        )
        for engine in engines:
            assert hasattr(
                Engines, engine
            ), f"Asset Check Factory Error - File {file} has invalid engine."

        # TODO: We need to validate all of the test_names that they are valid test names

        data = asset_check_def.get("data_tests")
        assert isinstance(data, List)

        yield data


def create_dagster_asset_check_name(
    asset_name: str, check_name: str, column_name: str
) -> str:
    """
    Create the Dagster Asset Check Name. What dagster registers the asset check as

    :param asset_name: asset name to run the check on
    :type asset_name: str
    :param check_name: the check to run
    :type check_name: str
    :param column_name: the columnn to run the check on
    :type column_name: str
    :return: asset check name
    :rtype: str
    """

    check_name = "asset_check__" + asset_name + "_" + check_name + "_" + column_name

    return check_name


def create_dagster_check(
    asset_name: str, check_name: str, column_name: str, engine_name: str
) -> AssetChecksDefinition:
    """
    Function that creates the dagster asset check
    :param asset_name: asset name to run the check on
    :type asset_name: str
    :param check_name: the check to run
    :type check_name: str
    :param column_name: the columnn to run the check on
    :type column_name: str
    :param engine_name: the engine to use
    :type engine_name: str
    :raises Exception: If engine is not configured
    :return: Dagster Asset Check
    :rtype: AssetChecksDefinition
    """
    polars_asset_checks = PolarsAssetChecks()
    asset_check_name = create_dagster_asset_check_name(
        asset_name, check_name, column_name
    )

    @asset_check(
        name=asset_check_name,
        asset=asset_name,
        required_resource_keys={
            "strava_api_resource",
            "polars_parquet_io_manager_strava_ingest",
        },
    )
    def _check(context: AssetExecutionContext) -> AssetCheckResult:
        """
        Helper function for registering and executing the check

        :param context: Dagster context
        :type context: AssetExecutionContext
        :raises Exception: Exception if engine is not configured
        :return: Dagster Asset Check Result
        :rtype: AssetCheckResult
        """
        if engine_name == "polars":
            # TODO: This is not currently very flexible as it is assuming a base directory
            # And it is tied to the Strava Ingest
            base_directory = (
                context.resources.polars_parquet_io_manager_strava_ingest.base_dir
            )

            mds_logger.info(f"Setting Directory for parquet - {base_directory}")
            df = pl.read_parquet(source=f"{base_directory}/{asset_name}.parquet")  # noqa: F841
            code_to_run = polars_asset_checks.main_handler(
                test_name=check_name, column=column_name
            )

            result_df = eval(code_to_run)
            assert isinstance(result_df, pl.DataFrame)

            return AssetCheckResult(passed=len(result_df) == 0)
        else:
            raise Exception(f"Asset Check Engine {engine_name} is not configured")

    return _check


def dagster_load_all_checks() -> List[AssetChecksDefinition]:
    """
    Function that loads all the Dagster Asset Checks into a list

    :return: Dagster Asset Checks
    :rtype: List[AssetChecksDefinition]
    """
    check_results = []
    checks = load_yaml_asset_check_files()
    # Parse the asset check dictionary
    for assets in checks:
        for asset in assets:
            asset_name = asset["asset"]
            engine_name = asset["engine"]
            for test in asset.get("tests"):
                test_name = test.get("name")
                for column in test.get("columns"):
                    result = create_dagster_check(
                        asset_name=asset_name,
                        check_name=test_name,
                        column_name=column,
                        engine_name=engine_name,
                    )
                    check_results.append(result)
    return check_results
