"""
Main module to run the availability checker for the "aceleracionVehiculo"

rules:
    - The aceleration must be different from 0
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data


# pylint: disable=too-few-public-methods
class AccelerationVehicleAvailabilityChecker:
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
        A record is invalid if the aceleracionVehiculo is 0
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results
        """
        # validata if the required columns are in the data
        required_columns = ["idVehiculo", "fechaHoraLecturaDato", "aceleracionVehiculo"]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            message = f"Columns {required_columns} not found to get the availability for aceleracionVehiculo"
            raise ValueError(message)

        # Initialize the column aceleracionVehiculoFailures with 0
        self.data["aceleracionVehiculoFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")
            vehicle_data["aceleracionVehiculo"] = vehicle_data["aceleracionVehiculo"].fillna(0)

            # Check if the aceleracionVehiculo is 0
            invalid_acceleration = vehicle_data["aceleracionVehiculo"] == 0
            self.data.loc[vehicle_data.index, "aceleracionVehiculoFailures"] = invalid_acceleration.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the aceleracionVehiculo

        Returns:
            dict: The availability data for the aceleracionVehiculo
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "aceleracionVehiculoFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "aceleracionVehiculo"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "aceleracionVehiculoFailures"]]
        }

        return response
        