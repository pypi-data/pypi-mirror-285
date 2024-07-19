"""
Main module to run the availability checker for the "revolucionesMotor" column

rules:
    - if presionAceiteMotor is 0, the bus is turned off. Do nothing
    - if presionAceiteMotor <> 0 and revolucionesMotor == 0 is an error
    - if tipoBusEnDB is Buseton (T) revolucionesMotor must be between 650 and 2800 otherwise is an error
    - if tipoBusEnDB is Padron (P) revolucionesMotor must be between 550 and 2300 otherwise is an error
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data

# pylint: disable=too-few-public-methods
class EngineRMPAvailabilityChecker:
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
    def _validate_engine_rpm(
            motor_rpm: float,
            oil_pressure: float,
            type_bus: str
    ) -> bool:
        """
        Method to validate the engine RPM

        Parameters:
            motor_rpm (float): The engine RPM
            oil_pressure (float): The engine oil pressure
            type_bus (str): The type of bus in the DB

        Returns:
            bool: True if the engine RPM is valid, False otherwise
        """
        if oil_pressure == 0:
            # The bus is turned off
            return True
        if oil_pressure != 0 and motor_rpm == 0:
            return False

        if oil_pressure != 0 and motor_rpm != 0:
            if type_bus == "T":
                return 650 <= motor_rpm <= 2800
            if type_bus == "P":
                return 550 <= motor_rpm <= 2300

        return False

    def _mark_invalid_records(self) -> pd.DataFrame:
        """
        Method to mark the invalid records in the data

        ***
        A record only can be invalid when the vehicle is running,
        if the vehicle is turned off, the record is valid

        A record is invalid if presionAceiteMotor <> 0 and revolucionesMotor == 0 
        or revolucionesMotor is out of the range
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results
        """
        # Validate if the required columns are in the data
        required_columns = [
            "idVehiculo", 
            "fechaHoraLecturaDato",
            "tipoBusEnDB",
            "revolucionesMotor",
            "presionAceiteMotor"
        ]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            message = f"Columns {required_columns} not found in the data to get the availability for revolucionesMotor"
            raise ValueError(message)

        # Initialize the column revolucionesMotorFailures with 0
        self.data["revolucionesMotorFailures|"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")
            vehicle_data["revolucionesMotor"] = vehicle_data["revolucionesMotor"].fillna(0)
            vehicle_data["presionAceiteMotor"] = vehicle_data["presionAceiteMotor"].fillna(0)
            vehicle_data["tipoBusEnDB"] = vehicle_data["tipoBusEnDB"].str.upper().fillna('')

            invalid_revolutions = ~vehicle_data.apply(
                lambda x: self._validate_engine_rpm(
                    x["revolucionesMotor"],
                    x["presionAceiteMotor"],
                    x["tipoBusEnDB"]
                ), axis=1
            )

            self.data.loc[vehicle_data.index, "revolucionesMotorFailures"] = invalid_revolutions.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the revolucionesMotor

        Returns:
            dict: The availability data and the data for the global availability
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "revolucionesMotorFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "revolucionesMotor"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "revolucionesMotorFailures"]]
        }

        return response
