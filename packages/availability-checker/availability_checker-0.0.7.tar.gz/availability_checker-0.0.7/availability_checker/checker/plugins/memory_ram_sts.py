"""
Main module to run the availability checker for the "memRamSts" column

rules:
    - the memRamSts must be != 0
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data


class MemoryRAMStsAvailabilityChecker:
    """
    Entry point for the availability checker
    """
    def __init__(self, data: pd.DataFrame):
        """
        Constructor for the availability checker

        Parameters:
            data (pd.DataFrame): The data to check (Complete data)
        """
        self.data = data

    def _mark_invalid_records(self) -> pd.DataFrame:
        """
        Method to mark the invalid records in the data

        ***
        A record is invalid if the memRamSts is 0
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results
        """

        # Validate if the required columns are in the data
        required_columns = [
            "idVehiculo",
            "fechaHoraLecturaDato",
            "memRamSts"
        ]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            message = f"Columns {required_columns} not found in the data to get the availability for memRamSts"
            raise ValueError(message)

        # Initialize the column memRamStsFailures with 0
        self.data["memRamStsFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")

            # Check if the memRamSts is 0
            invalid_memory = vehicle_data["memRamSts"] == 0

            self.data.loc[vehicle_data.index, "memRamStsFailures"] = invalid_memory.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the memRamSts

        Returns:
            dict: The availability data for the memRamSts
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "memRamStsFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "memRamSts"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "memRamStsFailures"]]
        }

        return response
