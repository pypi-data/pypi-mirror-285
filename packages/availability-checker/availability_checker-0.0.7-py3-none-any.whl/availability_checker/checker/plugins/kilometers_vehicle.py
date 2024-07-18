"""
Main module to run the availability checker for the "kilometrosVehiculo" column

rules:
    - if nivelTanqueCombustible and temperaturaMotor are equal to 0, the bus is turned off. Do nothing
    - if nivelTanqueCombustible <> 0 and temperaturaMotor <> 0 and kilometrosOdometro == 0 is an error
    - if the previous kilometers is greater than the current kilometers is an error
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data

# pylint: disable=too-few-public-methods
class KilometersOdometerAvailabilityChecker:
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
            - the previous kilometers is greater than the current kilometers
            - nivelTanqueCombustible and temperaturaMotor are equal to 0 and kilometrosOdometro is 0
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
            "temperaturaMotor"
        ]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            message = f"Columns {required_columns} not found in the data to get the availability for kilometers"
            raise ValueError(message)

        # Initialize the column kilometersFailures with 0
        self.data["kilometrosOdometroFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")

            vehicle_data["kilometrosOdometro"] = vehicle_data["kilometrosOdometro"].fillna(0)
            vehicle_data["nivelTanqueCombustible"] = vehicle_data["nivelTanqueCombustible"].fillna(0)
            vehicle_data["temperaturaMotor"] = vehicle_data["temperaturaMotor"].fillna(0)

            # Check if the previous kilometers is greater than the current kilometers
            # pylint: disable=line-too-long
            invalid_kilometers = (
                vehicle_data["kilometrosOdometro"].diff() < 0 |
                ((vehicle_data["nivelTanqueCombustible"] != 0) & (vehicle_data["temperaturaMotor"] != 0) & (vehicle_data["kilometrosOdometro"] == 0))
            )

            self.data.loc[vehicle_data.index, "kilometrosOdometroFailures"] = invalid_kilometers.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the kilometers

        Returns:
            dict: The availability data for the kilometers
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "kilometrosOdometroFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "kilometrosOdometro"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "kilometrosOdometroFailures"]]
        }

        return response
