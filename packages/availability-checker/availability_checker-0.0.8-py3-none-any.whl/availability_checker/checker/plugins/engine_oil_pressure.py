"""
Main module to run the availability checker for the "presionAceiteMotor" column

rules:
    - if revolucionesMotor is 0, the bus is turned off do nothing
    - if revolucionesMotor <> 0 and presionAceiteMotor == 0 is an error
    - if tipoBusEnDB is Buseton (T) presionAceiteMotor must be between 150000 and 600000 otherwise is an error
    - if tipoBusEnDB is Padron (P) presionAceiteMotor must be between 150000 and 500000 otherwise is an error
"""
import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data


# pylint: disable=too-few-public-methods
class EngineOilPressureAvailabilityChecker:
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
    def _validate_engine_oil_pressure(
        revoluciones_motor: float,
        presion_aceite_motor: float,
        tipo_bus_in_db: str,
    ) -> bool:
        """
        Method to validate the engine oil pressure

        Parameters:
            revolucionesMotor (float): The engine revolutions
            presionAceiteMotor (float): The engine oil pressure
            tipoBusInDB (str): The type of bus in the DB

        Returns:
            bool: True if the engine oil pressure is valid, False otherwise
        """
        if revoluciones_motor == 0:
            # The bus is turned off
            return True
        if revoluciones_motor != 0 and presion_aceite_motor == 0:
            return False

        if revoluciones_motor != 0 and presion_aceite_motor != 0:
            if tipo_bus_in_db == "T":
                return 150000 <= presion_aceite_motor <= 600000
            if tipo_bus_in_db == "P":
                return 150000 <= presion_aceite_motor <= 500000

        return False


    def _mark_invalid_records(self) -> pd.DataFrame:
        """
        Method to mark the invalid records in the data

        ***
        A record only can be invalid when the vehicle is running,
        if the vehicle is turned off, the record is valid

        A record is invalid if the presionAceiteMotor is different from the expected value
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
            message = f"Columns {required_columns} not found in the data to get the availability for presionAceiteMotor"
            raise ValueError(message)

        # Initialize the column presionAceiteMotorFailures with 0
        self.data["presionAceiteMotorFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by="fechaHoraLecturaDato")

            vehicle_data["presionAceiteMotor"] = vehicle_data["presionAceiteMotor"].fillna(0)
            vehicle_data["revolucionesMotor"] = vehicle_data["revolucionesMotor"].fillna(0)
            vehicle_data["tipoBusEnDB"] = vehicle_data["tipoBusEnDB"].str.upper().fillna('')

            invalid_oil_pressure = ~vehicle_data.apply(
                lambda x: self._validate_engine_oil_pressure(
                    x["revolucionesMotor"],
                    x["presionAceiteMotor"],
                    x["tipoBusEnDB"]
                ), axis=1
            )
            self.data.loc[vehicle_data.index, "presionAceiteMotorFailures"] = invalid_oil_pressure.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to get the availability for the presionAceiteMotor

        Returns:
            dict: The availability data and the data for the global availability
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "presionAceiteMotorFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "presionAceiteMotor"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "presionAceiteMotorFailures"]]
        }

        return response
