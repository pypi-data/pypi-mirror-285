"""
Main Module to run the full availability checker

rules:
    if one of the variable fails, the record is invalid
"""

import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability

# pylint: disable=too-few-public-methods
class GlobalAvailabilityChecker:
    """
    Enty point for the availability checker
    """

    def __init__(self, dataframes: list[pd.DataFrame]):
        """
        Constructor for the availability checker

        Parameters:
            data (pd.DataFrame): The data to check (Complete data)
        """
        # Join the dataframes to have all the data in one
        self.data = dataframes[0]
        for df in dataframes[1:]:
            self.data = pd.merge(
                self.data,
                df,
                on=["idVehiculo", "fechaHoraLecturaDato"],
                how="outer",
                validate="many_to_many",
            )

    def _mark_invalid_records(self) -> pd.DataFrame:
        """
        Method to mark the invalid records in the data

        ***
        A record is invalid if one of the variables are 1
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results
        """
        # Get the unique idVehiculo and create the globalFailures to store the fails in data
        self.data["globalFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")

            # Check if one of the variables is 1
            columns_to_check = vehicle_data.columns.tolist()
            columns_to_check.remove("idVehiculo")
            columns_to_check.remove("fechaHoraLecturaDato")

            invalid_records = vehicle_data[columns_to_check].sum(axis=1) > 0

            self.data.loc[vehicle_data.index, "globalFailures"] = invalid_records.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the global variables

        Returns:
            dict: The availability data for the global variables
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "globalFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "global"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "globalFailures"]]
        }

        return response
