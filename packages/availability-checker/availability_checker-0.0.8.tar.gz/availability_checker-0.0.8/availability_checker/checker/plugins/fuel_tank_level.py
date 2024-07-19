"""
Main module to run the availability checker for the "nivelTanqueCombustible" column

rules:
    - if kilometrosOdometro and temperaturaMotor are equal to 0, the bus is turned off do nothing
    - if kilometrosOdometro <> 0 and temperaturaMotor <> 0 and nivelTanqueCombustible == 0 is an error
    - nivelTanqueCombustible must be between 0 and 100 otherwise is an error
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data


# pylint: disable=too-few-public-methods
class FuelTankLevelAvailabilityChecker:
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
        A record only can be invalid when the vehicle is running,
        if the vehicle is turned off, the record is valid

        A record is invalid if:
            - nivelTanqueCombustible must be between 0 and 100
            - kilometrosOdometro and temperaturaMotor are <> 0 and nivelTanqueCombustible is 0
        """
        # Validate if the required columns are in the data
        required_columns = [
            "idVehiculo",
            "fechaHoraLecturaDato",
            "kilometrosOdometro",
            "nivelTanqueCombustible",
            "temperaturaMotor"
        ]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            message = f"Columns {required_columns} not found in the data to get the availability for fuel tank level"
            raise ValueError(message)

        # Initialize the column fuelTankLevelFailures with 0
        self.data["nivelTanqueCombustibleFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")

            vehicle_data["nivelTanqueCombustible"] = vehicle_data["nivelTanqueCombustible"].fillna(0)
            vehicle_data["kilometrosOdometro"] = vehicle_data["kilometrosOdometro"].fillna(0)
            vehicle_data["temperaturaMotor"] = vehicle_data["temperaturaMotor"].fillna(0)

            # pylint: disable=line-too-long
            invalid_fuel_tank = (
                (vehicle_data["nivelTanqueCombustible"] < 0) |
                (vehicle_data["nivelTanqueCombustible"] > 100) |
                ((vehicle_data["kilometrosOdometro"] != 0) & (vehicle_data["temperaturaMotor"] != 0) & (vehicle_data["nivelTanqueCombustible"] == 0))
            )

            self.data.loc[vehicle_data.index, "nivelTanqueCombustibleFailures"] = invalid_fuel_tank.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the fuel tank level

        Returns:
            dict: The availability data for the fuel tank level
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "nivelTanqueCombustibleFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "nivelTanqueCombustible"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "nivelTanqueCombustibleFailures"]]
        }

        return response
        