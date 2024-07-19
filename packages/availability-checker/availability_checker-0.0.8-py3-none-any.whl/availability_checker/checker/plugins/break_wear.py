import pandas as pd

from availability_checker.checker.common.common import CommonCalcsForAvailability
from availability_checker.checker.common.utils import validate_if_required_columns_are_in_data

class BrakeWearAvailabilityChecker:
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

    def _mark_invalid_records(self, threshold: int = 5) -> pd.DataFrame:
        """
        Get the total of fails in the variable "estadoDesgasteFrenos"

        - Given the variables "temperature" and "kilometerOdometer" if either
        is greater than zero then the variable "stateWearBrakes"
        must be greater than zero or it is considered a failure.

        - The mode of the variable "stateBrakeWear" should be calculated for each vehicle,
        and if the difference in absolute value between the variable "stateBrakeWear"
        and the mode is greater than 5 then it is considered a failure.

        - If both failures are met then it should be marked as a single failure.
        """
        # Validate if the required columns are in the data
        required_columns = [
            "idVehiculo",
            "fechaHoraLecturaDato",
            "estadoDesgasteFrenos",
            "temperaturaMotor",
            "kilometrosOdometro"
        ]
        if not validate_if_required_columns_are_in_data(self.data, required_columns):
            message = f"Columns {required_columns} not found to get the availability for estadoDesgasteFrenos"
            raise ValueError(message)

        dataset = self.data.sort_values(by=["idVehiculo", "fechaHoraLecturaDato"])
        mode = dataset.groupby("idVehiculo")["estadoDesgasteFrenos"].agg(
           lambda x: x[x > 0].mode().values[0] if not x[x > 0].empty else None
        )

        dataset = dataset.merge(mode, on="idVehiculo", suffixes=("", "_mode"))
        dataset["diff"] = (
            dataset["estadoDesgasteFrenos"] - dataset["estadoDesgasteFrenos_mode"]
        )

        dataset["abs_diff"] = dataset["diff"].abs()
        dataset["failure_by_variation"] = (dataset["abs_diff"] > threshold) & (
           (dataset["temperaturaMotor"] > 0) | (dataset["kilometrosOdometro"] > 0)
        )

        dataset["failure_by_consistency_data"] = (
            (dataset["temperaturaMotor"] > 0) | (dataset["kilometrosOdometro"] > 0)
        ) & (dataset["estadoDesgasteFrenos"] == 0)

        # Failure is True if any of the two conditions are met
        dataset["estadoDesgasteFrenosFailures"] = (
            dataset["failure_by_variation"] | dataset["failure_by_consistency_data"]
        )

        # Put estadoDesgasteFrenosFailures to 1 if its True
        dataset["estadoDesgasteFrenosFailures"] = dataset["estadoDesgasteFrenosFailures"].astype(int)

        return dataset

    def get_availability(self) -> dict:
        """
        Method to get the availability for the estadoDesgasteFrenos

        Returns:
            dict: The availability data and the data for the global availability
        """
        self.data = self._mark_invalid_records()
        common_calcs = CommonCalcsForAvailability(self.data, "estadoDesgasteFrenosFailures")
        availability_data: pd.DataFrame = common_calcs.calculate_availability()
        availability_data["variable"] = "estadoDesgasteFrenos"

        response = {
            "availability_data": availability_data,
            "data_for_global": self.data[["idVehiculo", "fechaHoraLecturaDato", "estadoDesgasteFrenosFailures"]]
        }

        return response
