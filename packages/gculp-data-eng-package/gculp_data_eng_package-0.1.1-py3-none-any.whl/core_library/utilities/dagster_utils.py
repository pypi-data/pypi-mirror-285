"""
Dagster Utilities to help with dagster code
"""
from typing import Union

from dagster import AssetExecutionContext, AssetKey

from core_library.utilities.misc_utils import setup_console_logger

mds_logger = setup_console_logger()


def get_latest_asset_metadata_value(
    context: AssetExecutionContext, asset_name: str, metadata_key: str
) -> str:
    """
    Get the latest metadata result from an asset and the metadata key

    :param context: Dagster asset context
    :type context: AssetExecutionContext
    :param asset_name: The name of the asset
    :type asset_name: str
    :param metadata_key: The name of the metadata key
    :type metadata_key: str
    :return: the value of the metadata key
    :rtype: str
    """
    latest_materialization = context.instance.get_latest_materialization_event(
        AssetKey([asset_name])
    )
    # For typing
    assert latest_materialization is not None
    assert latest_materialization.asset_materialization is not None

    metadata_value = latest_materialization.asset_materialization.metadata[
        metadata_key
    ].text

    return str(metadata_value)


def get_high_watermark_value(
    context: AssetExecutionContext, asset_name: str
) -> Union[str, None]:
    """
    Function to get the metadata 'high_watermark

    :param context: Dagster context
    :type context: AssetExecutionContext
    :param asset_name: Dagster asset name
    :type asset_name: str
    :return: high_watermark value
    :rtype: Union[str, None]
    """
    mds_logger.info("Getting high_watermark from metadata")
    try:
        value = get_latest_asset_metadata_value(
            context, asset_name, metadata_key="high_watermark"
        )
        mds_logger.info(f"high_watermark value = {value}")
        return value
    except KeyError:
        mds_logger.warning("Unable to get high watermark")
        return None
