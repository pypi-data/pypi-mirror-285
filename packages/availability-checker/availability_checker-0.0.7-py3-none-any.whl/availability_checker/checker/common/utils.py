"""
Common utils functions to be used in the library
"""
import pandas as pd

def validate_if_required_columns_are_in_data(data: pd.DataFrame, required_columns: list[str]) -> bool:
    """
    This metod validates if the required columns are in the data
    """
    if not all(column in data.columns for column in required_columns ):
        return False

    return True
