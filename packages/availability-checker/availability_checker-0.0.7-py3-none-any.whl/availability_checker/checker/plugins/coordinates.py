"""
Main module to run the availability checker for the "coordenadas" column

rules:
    - The coordenadas must be in the allowed coordinates
    Coordinates must be different than 0,0

"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data

# pylint: disable=too-few-public-methods
class CoordinatesAvailabilityChecker:
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
        A record is invalid if the coordenadas is 0,0
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results

        Raises:
            ValueError: If the column coordenadas is not found in the data
        """

        # Validate if the required columns are in the data
        required_columns = ["latitud", "longitud", "idVehiculo", "fechaHoraLecturaDato" ]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            raise ValueError(f"Columns {required_columns} not found in the data to get the availability for coords")

        self.data["coordenadasFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")

            # Check if the coordenadas is 0,0
            invalid_coords = (vehicle_data["latitud"] == 0) & (vehicle_data["longitud"] == 0)
            self.data.loc[vehicle_data.index, "coordenadasFailures"] = invalid_coords.astype(int)

        return self.data

    def get_availability(self) -> pd.DataFrame:
        """
        Method to get the availability for the coords

        Returns:
            dict: The availability data for the coords
        """
        self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "coordenadasFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "coordenadas"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "coordenadasFailures"]]
        }

        return response
