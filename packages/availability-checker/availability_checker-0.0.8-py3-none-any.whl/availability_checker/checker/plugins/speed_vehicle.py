"""
Main module to run the availability checker for the "velocidadVehiculo"

rules:
    - The velocidadVehiculo must be between 0 and 90 km/h
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data


# pylint: disable=too-few-public-methods
class SpeedVehicleAvailabilityChecker:
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
        A record is invalid if the velocidadVehiculo is greater than 90 km/h
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results
        """
        # validate if the required columns are in the data
        required_columns = ["idVehiculo", "fechaHoraLecturaDato", "tipoBusEnDB", "tipoFreno"]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            message = f"Columns {required_columns} not found in the data to get the availability for velocidadVehiculo"
            raise ValueError(message)

        # Initialize the column velocidadVehiculoFailures with 0
        self.data["velocidadVehiculoFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")
            vehicle_data["velocidadVehiculo"] = vehicle_data["velocidadVehiculo"].fillna(-1)

            # Check if the velocidadVehiculo is greater than 90 km/h and different from -1
            invalid_speed = (vehicle_data["velocidadVehiculo"] > 90) | (vehicle_data["velocidadVehiculo"] == -1)
            self.data.loc[vehicle_data.index, "velocidadVehiculoFailures"] = invalid_speed.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the velocidadVehiculo
        
        Returns:
            dict: The availability data and the data for the global availability
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "velocidadVehiculoFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "velocidadVehiculo"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "velocidadVehiculoFailures"]]
        }

        return response
