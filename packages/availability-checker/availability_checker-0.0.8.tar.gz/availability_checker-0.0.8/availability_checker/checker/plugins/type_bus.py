"""
Main module to run the availability checker

rules:
    - The bus must match with the allowed type of buses
    Buseton type must be T
    Padron type must be P
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data

# pylint: disable=too-few-public-methods
class TypeRouteAvailabilityChecker:
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
        A record is invalid if being padron type is not P or being buseton type is not T
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results
        
        Raises:
            ValueError: If the column tipoBus is not found in the data
        """
        # Validate if the required columns are in the data
        required_columns = ["tipoBus", "idVehiculo", "fechaHoraLecturaDato", "tipoBusEnDB"]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            raise ValueError(f"Columns {required_columns} not found in the data to get the availability for tipoBus")

        # Initialize tipoBusFailures column to store the fails in data
        self.data["tipoBusFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")
            vehicle_data["tipoBusEnDB"] = vehicle_data["tipoBusEnDB"].str.upper().fillna('')
            vehicle_data["tipoBus"] = vehicle_data["tipoBus"].str.upper().fillna('')

            # Check if the tipoBus is different from the tipoBusEnDB
            invalid_types_of_bus = vehicle_data["tipoBus"] != vehicle_data["tipoBusEnDB"]
            self.data.loc[vehicle_data.index, "tipoBusFailures"] = invalid_types_of_bus.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the tipoBus

        Returns:
            dict: The availability data for the tipoBus
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "tipoBusFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "tipoBus"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "tipoBusFailures"]]
        }

        return response
