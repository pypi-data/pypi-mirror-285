from __future__ import annotations

REGISTRY = {}
DATAFRAME_TYPES = []

try:
    from digitalhub_data.readers.objects.pandas import DataframeReaderPandas

    REGISTRY["pandas"] = DataframeReaderPandas
    REGISTRY["pandas.core.frame.DataFrame"] = DataframeReaderPandas
    DATAFRAME_TYPES.append("pandas.core.frame.DataFrame")

except ImportError:
    pass
