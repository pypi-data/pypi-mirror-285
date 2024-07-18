"""
Module to define the common classes and methods for the availability checker
"""

import pandas as pd


class CommonCalcsForAvailability:
    """
    This class contains the common methods to calculate the availability of the variables
    this commons methods are:
        - One to calculate the consecutive failures or errors in the data for each vehicle
        - Process the data to perform the availability calculation mtbf, mttr, availability
    """

    def __init__(self, data: pd.DataFrame, fails_column: str):
        """
        Constructor for the common calculations

        Parameters:
            data (pd.DataFrame): The data to process. 
            The data must have the fails_column to check the consecutive failures or errors
            fails_column (str): The column to check the consecutive failures
        """
        self.data = data
        self.fails_column = fails_column

    @staticmethod
    def _get_total_readings(data: pd.DataFrame, column_fails: str) -> pd.DataFrame:
        """
        Get the total of readings for each vehicle

        Parameters:
            data (pd.DataFrame): The data to process
            column_fails (str): The column to check the consecutive failures

        Returns:
            pd.DataFrame: The DataFrame with the total of readings for each vehicle

        """
        total_readings = data.groupby("idVehiculo").size().reset_index()
        total_readings.columns = ["idVehiculo", "total_de_tramas"]
        total_readings[f"tiempo_disponible_{column_fails}"] = total_readings["total_de_tramas"] / 60
        return total_readings

    @staticmethod
    def _calculate_consecutive_failures(data: pd.DataFrame, column_fails: str) -> pd.DataFrame:
        """
        Method to calculate the consecutive failures in the data for each vehicle

        Parameters:
            data (pd.DataFrame): The data to process
            column_fails (str): The column to check the consecutive failures

        Returns:
            pd.DataFrame: The DataFrame with the consecutive failures for each vehicle

        """
        data.sort_values(by=["idVehiculo", "fechaHoraLecturaDato"], inplace=True)

        # Identify changes in the 'failure' state or vehicle ID to find consecutive failures
        data["change"] = data[column_fails].ne(data[column_fails].shift()) | data["idVehiculo"].ne(
            data["idVehiculo"].shift()
        )

        # Group these changes by vehicle and count the number of true blocks per vehicle
        data["block"] = data["change"].cumsum()

        # Filter the blocks with failures
        failed_blocks = data[data[column_fails] == 1]

        # Group by vehicle_id and count distinct blocks
        result = failed_blocks.groupby("idVehiculo")["block"].nunique().reset_index()

        # Rename the column for clarity
        result.rename(columns={"block": "cantidad_paradas"}, inplace=True)

        # Get the total of true values in the 'failure' column for each vehicle and merge with result
        total_failures = data.groupby("idVehiculo")[column_fails].sum().reset_index()
        result = result.merge(total_failures, on="idVehiculo", how="left")

        result[f"tiempo_paradas_{column_fails}"] = result[column_fails] / 60
        return result

    def calculate_availability(self) -> pd.DataFrame:
        """
        Calculate the availability for the given data
        """
        # Total of readings for each vehicle
        total_readings = self._get_total_readings(self.data, self.fails_column)
        total_failures = self._calculate_consecutive_failures(self.data, self.fails_column)

        # Merge the data
        result = total_readings.merge(total_failures, on="idVehiculo", how="left")

        result["tiempo_disponible"] = (
            result[f"tiempo_disponible_{self.fails_column}"] - result[f"tiempo_paradas_{self.fails_column}"])

        result["mtbf"] = result["tiempo_disponible"] / result["cantidad_paradas"]
        result["mttr"] = result[f"tiempo_paradas_{self.fails_column}"] / result["cantidad_paradas"]
        result["availability"] = round((result["mtbf"] / (result["mtbf"] + result["mttr"])) * 100, 2)

        result.fillna({"cantidad_paradas": 0}, inplace=True)
        result.fillna({"total_tramas_en_falla": 0}, inplace=True)
        result.fillna({f"tiempo_paradas_{self.fails_column}": 0}, inplace=True)
        result.fillna({"mtbf": 0}, inplace=True)
        result.fillna({"mttr": 0}, inplace=True)
        result.fillna({"availability": 100}, inplace=True)
        result.fillna({f"{self.fails_column}": 0}, inplace=True)
        result.fillna({"tiempo_disponible": 0}, inplace=True)

        result.rename(
            columns={
                f"tiempo_paradas_{self.fails_column}": "tiempo_paradas",
                f"{self.fails_column}": "total_tramas_en_falla",
            },
            inplace=True,
        )

        result.drop(columns=[f"tiempo_disponible_{self.fails_column}"],inplace=True)

        return result
