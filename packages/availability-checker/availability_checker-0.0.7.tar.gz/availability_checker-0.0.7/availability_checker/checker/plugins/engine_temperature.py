"""
Main module to run the availability checker for the "temperaturaMotor" column

rules:
    - if kilometrosOdometro and nivelTanqueCombustible are equal to 0, the bus is turned off do nothing
    - if kilometrosOdometro <> 0 and nivelTanqueCombustible <> 0, 
    temperatureMotor must be greater than 0 and less than 99
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import (
    validate_if_required_columns_are_in_data,
)


# pylint: disable=too-few-public-methods
class EngineTemperatureAvailabilityChecker:
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
    def _validate_engine_temperature(
        kilometros_odometro: float,
        nivel_tanque_combustible: float,
        temperatura_motor: float,
    ) -> bool:
        """
        Method to validate the engine temperature

        Parameters:
            kilometrosOdometro (float): The odometer value
            nivelTanqueCombustible (float): The fuel tank level
            temperaturaMotor (float): The engine temperature

        Returns:
            bool: True if the engine temperature is valid, False otherwise
        """

        if kilometros_odometro == 0 and nivel_tanque_combustible == 0:
            # The bus is turned off
            return True
        if kilometros_odometro != 0 and nivel_tanque_combustible != 0:
            return 0 < temperatura_motor < 99
        return False

    def _mark_invalid_records(self) -> pd.DataFrame:
        """
        Method to mark the invalid records in the data

        ***
        A record is not valid when the vehicle is running,
        the engine temperature is equal to 0 or higher than 99

        The vehicle is considered running when the odometer and fuel tank are different from 0
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results
        """
        # Validate if the required columns are in the data
        required_columns = [
            "idVehiculo",
            "fechaHoraLecturaDato",
            "kilometrosOdometro",
            "nivelTanqueCombustible",
            "temperaturaMotor",
        ]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            message = f"Columns {required_columns} not found in the data to get the availability for temperaturaMotor"
            raise ValueError(message)

        # Initialize the column temperaturaMotorFailures with 0
        self.data["temperaturaMotorFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")

            vehicle_data["temperaturaMotor"] = vehicle_data["temperaturaMotor"].fillna(0)
            vehicle_data["kilometrosOdometro"] = vehicle_data["kilometrosOdometro"].fillna(0)
            vehicle_data["nivelTanqueCombustible"] = vehicle_data["nivelTanqueCombustible"].fillna(0)

            invalid_engine_temperature = ~vehicle_data.apply(
                lambda x: self._validate_engine_temperature(
                    x["kilometrosOdometro"],
                    x["nivelTanqueCombustible"],
                    x["temperaturaMotor"],
                ), axis=1
            )
            self.data.loc[vehicle_data.index, "temperaturaMotorFailures"] = invalid_engine_temperature.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the temperaturaMotor

        Returns:
            dict: The availability data and the data for the global availability
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "temperaturaMotorFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "temperaturaMotor"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "temperaturaMotorFailures"]]
        }

        return response
