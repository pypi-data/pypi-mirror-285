"""
Main Module to run the availability checker

rules:
    - The idRoute must be in the allowed routes

"""

import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data
from availability_checker.checker.plugins.plugins_config import PLUGINS_CONFIGURATION_BY_COMPANY

# pylint: disable=too-few-public-methods
class IDRouteAvailabilityChecker:
    """
    Entry point for the availability checker
    """

    def __init__(self, data: pd.DataFrame, company_code: str):
        """
        Constructor for the availability checker

        Parameters:
            data (pd.DataFrame): The data to check (Complete data)
            company_code (str): The company code

        Raises:
            ValueError: If the columns to check are invalid or if the company code is not found
        """
        self.data = data
        self.configs = PLUGINS_CONFIGURATION_BY_COMPANY.get(company_code, {}).get("idRuta", {})

        if not self.configs:
            raise ValueError(f"Company code {company_code} not found in the configurations for idRuta")

    def _mark_invalid_records(self) -> pd.DataFrame:
        """
        Method to mark the invalid records in the data

        ***
        A record is invalid if the idRuta is not in the allowed routes
        ***

        Returns:
            pd.DataFrame: The DataFrame with the availability check results

        Raises:
            ValueError: If the column idRuta is not found in the data
        """
        # Validate if the required columns are in the data
        required_columns = ["idRuta", "idVehiculo", "fechaHoraLecturaDato"]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            raise ValueError(f"Columns {required_columns} not found in the data to get the availability for idRuta")

        # Get the unique idVehiculo and create the idRutaFailures to store the fails in data
        self.data["idRutaFailures"] = 0
        unique_vehicles = self.data["idVehiculo"].unique()

        for vehicle in unique_vehicles:
            # Filter the data by vehicle and sort by fechaHoraLecturaDato
            vehicle_data = self.data[self.data["idVehiculo"] == vehicle].sort_values(by=["fechaHoraLecturaDato"])
            vehicle_data["idRuta"] = vehicle_data["idRuta"].astype(str)

            # If the route is not in the allowed routes, put 1 in the idRutaCheck
            invalid_routes = ~vehicle_data["idRuta"].isin(self.configs["allowed_routes"])
            self.data.loc[vehicle_data.index, "idRutaFailures"] = invalid_routes.astype(int)

        return self.data

    def get_availability(self) -> dict:
        """
        Method to check the availability of the idRuta variable

        Returns:
            dict: The availability data for the idRuta

        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "idRutaFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "idRuta"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "idRutaFailures"]]
        }

        return response
