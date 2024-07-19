"""
Main module to run the availability checker for the "tipoFreno" column

rules:
    - The tipoFreno must be 1 if tipoBusEnDB is Buseton (T)
    and 2 if tipoBusEnDB is Padron (P)
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data


class BrakeTypeAvailabilityChecker:
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

    @staticmethod
    def validate_brake_type(type_bus_in_db: str, brake_type: int) -> bool:
        """
        Method to validate the tipoFreno

        Parameters:
            typeBusInDB (str): The type of bus in the DB
            brake_type (int): The brake type
        
        Returns:
            bool: True if the tipoFreno is valid, False otherwise
        """
        if type_bus_in_db == "T" and brake_type == 1:
            return True
        if type_bus_in_db == "P" and brake_type == 2:
            return True
        return False

    def _mark_invalida_records(self) -> pd.DataFrame:
        """
        Method to mark the invalid records in the data

        ***
        A record is invalid if the tipoFreno is different from the expected value
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results
        """
        # validate if the required columns are in the data
        required_columns = ["idVehiculo", "fechaHoraLecturaDato", "tipoBusEnDB", "tipoFreno"]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            raise ValueError(f"Columns {required_columns} not found in the data to get the availability for tipoFreno")

        # Initialize tipoFrenoFailures column to store the fails in data
        self.data["tipoFrenoFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")
            vehicle_data["tipoBusEnDB"] = vehicle_data["tipoBusEnDB"].str.upper().fillna('')
            vehicle_data["tipoFreno"] = vehicle_data["tipoFreno"].fillna(0)

            # Check if the tipoFreno is different from the expected value
            invalid_brake_types = ~vehicle_data.apply(
                lambda x: self.validate_brake_type(x["tipoBusEnDB"], x["tipoFreno"]), axis=1
            )
            self.data.loc[vehicle_data.index, "tipoFrenoFailures"] = invalid_brake_types.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the tipoFreno

        Returns:
            dict: The availability data for the tipoFreno
        """
        self.data = self._mark_invalida_records()
        common_calcs = CommonCalcsForAvailability(self.data, "tipoFrenoFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "tipoFreno"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "tipoFrenoFailures"]]
        }

        return response
