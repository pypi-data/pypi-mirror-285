"""
Main module to run the availability checker for the "tecnologíaMotor" columns

rules:
    - The tecnologiaMotor must be 1 if tipoBusEnDB is Buseton (T) 
    and 2 if tipoBusEnDB is Padron (P)

"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data


class EngineTechnologyAvailabilityChecker:
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
    def validate_tech_motor(type_bus_in_db: str, tech_motor: int) -> bool:
        """
        Method to validate the tecnologiaMotor

        Parameters:
            typeBusInDB (str): The type of bus in the DB
            tech_motor (int): The technology of the motor

        Returns:
            bool: True if the tecnologiaMotor is valid, False otherwise
        """
        if type_bus_in_db == "T" and tech_motor == 1:
            return True
        if type_bus_in_db == "P" and tech_motor == 2:
            return True
        return False


    def _mark_invalid_records(self) -> pd.DataFrame:
        """
        Method to marck the invalid records in the data

        ***
        A record is invalid if the tecnologiaMotor is different from the expected value
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results
        """
        # validate if the required columns are in the data
        required_columns = ["idVehiculo", "fechaHoraLecturaDato", "tipoBusEnDB", "tecnologiaMotor"]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            message = f"Columns {required_columns} not found in the data to get the availability for tecnologiaMotor"
            raise ValueError(message)

        # Initialize tecnologiaMotorFailures column to store the fails in data
        self.data["tecnologiaMotorFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")
            vehicle_data["tipoBusEnDB"] = vehicle_data["tipoBusEnDB"].str.upper().fillna('')
            vehicle_data["tecnologiaMotor"] = vehicle_data["tecnologiaMotor"].fillna(0)

            # Check if the tecnologiaMotor is different from the expected value
            invalid_tech_motor = ~vehicle_data.apply(
                lambda x: self.validate_tech_motor(x["tipoBusEnDB"], x["tecnologiaMotor"]), axis=1
            )
            self.data.loc[vehicle_data.index, "tecnologiaMotorFailures"] = invalid_tech_motor.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the tecnologiaMotor

        Returns:
            dict: The availability data for the tecnologiaMotor
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "tecnologiaMotorFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "tecnologiaMotor"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "tecnologiaMotorFailures"]]
        }

        return response
