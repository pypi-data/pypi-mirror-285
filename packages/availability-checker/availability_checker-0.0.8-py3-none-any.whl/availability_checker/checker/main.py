"""
Main Module to run the availability checker
This library is intended to calculate the availability for the next set of variables:
- idRuta
- tipobus
- coordenadas
- tecnologiaMotor
- tipoFreno
- velocidadVehiculo
- AceleracionVehiculo
- temperaturaMotor
- presionAceiteMotor
- revolucionesMotor
- DesgasteFrenos
- kilometrosOdometro
- nivelTanqueCombustible
- temperaturaSts
- memRamSts

This variables are extracted from the P60 trams for ITS - Transmilenio
Melius ID - 2024
"""
import gc
import time

import pandas as pd

from availability_checker.checker.config import AvailablePluginsColsToCheck
from availability_checker.checker.plugins.id_route import IDRouteAvailabilityChecker
from availability_checker.checker.plugins.type_bus import TypeRouteAvailabilityChecker
from availability_checker.checker.plugins.coordinates import CoordinatesAvailabilityChecker
from availability_checker.checker.plugins.engine_technology import EngineTechnologyAvailabilityChecker
from availability_checker.checker.plugins.type_brake import BrakeTypeAvailabilityChecker
from availability_checker.checker.plugins.speed_vehicle import SpeedVehicleAvailabilityChecker
from availability_checker.checker.plugins.acceleration_vehicle import AccelerationVehicleAvailabilityChecker
from availability_checker.checker.plugins.engine_temperature import EngineTemperatureAvailabilityChecker
from availability_checker.checker.plugins.engine_oil_pressure import EngineOilPressureAvailabilityChecker
from availability_checker.checker.plugins.engine_rpm import EngineRMPAvailabilityChecker
from availability_checker.checker.plugins.kilometers_vehicle import KilometersOdometerAvailabilityChecker
from availability_checker.checker.plugins.fuel_tank_level import FuelTankLevelAvailabilityChecker
from availability_checker.checker.plugins.sts_temperature import STSTemperatureAvailabilityChecker
from availability_checker.checker.plugins.memory_ram_sts import MemoryRAMStsAvailabilityChecker
from availability_checker.checker.plugins.break_wear import BrakeWearAvailabilityChecker
from availability_checker.checker.plugins.global_calculation import GlobalAvailabilityChecker

# pylint: disable=too-few-public-methods
class Checker:
    """
    Entry point for the availability checker
    """

    def __init__(self, data: pd.DataFrame, columns_to_check: list[str], company: str):
        """
        Constructor for the availability checker

        Parameters:
            data (pd.DataFrame): The data to check (Complete data)
            columns_to_check (list[str]): The columns to check
            company (str): The company code

        Raises:
            ValueError: If the columns to check are invalid

        Returns:
            Class instance
        """
        self.df = data
        self.company = company

        available_plugins = [item.value for item in AvailablePluginsColsToCheck]

        # Validate witch columns are valid to check
        invalid_vars_to_calc = [
            column for column in columns_to_check if column not in available_plugins
        ]
        if invalid_vars_to_calc:
            raise ValueError(
                f"Invalid columns to check: {invalid_vars_to_calc}. Please check the available columns to check"
            )

        self.columns_to_check = columns_to_check

    def get_availability(self) -> pd.DataFrame:
        """
        Method to check the availability of the variables
        """
        initial_data = self.df.sort_values(by=["idVehiculo", "fechaHoraLecturaDato"])

        complete_calculation = []
        global_data = []

        # pylint: disable=line-too-long
        checker_plugins = {
            AvailablePluginsColsToCheck.ID_RUTA.value: lambda: IDRouteAvailabilityChecker(initial_data, self.company).get_availability(),
            AvailablePluginsColsToCheck.TIPO_BUS.value: lambda: TypeRouteAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.COORDENADAS.value: lambda: CoordinatesAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.TECNOLOGIA_MOTOR.value: lambda: EngineTechnologyAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.TIPO_FRENOS.value: lambda: BrakeTypeAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.VELOCIDAD_VEHICULO.value: lambda: SpeedVehicleAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.ACELERACION_VEHICULO.value: lambda: AccelerationVehicleAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.TEMPERATURA_MOTOR.value: lambda: EngineTemperatureAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.PRESION_ACEITE_MOTOR.value: lambda: EngineOilPressureAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.REVOLUCIONES_MOTOR.value: lambda: EngineRMPAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.KILOMETROS_ODOMETRO.value: lambda: KilometersOdometerAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.NIVEL_TANQUE_COMBUSTIBLE.value: lambda: FuelTankLevelAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.TEMPERATURA_STS.value: lambda: STSTemperatureAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.MEM_RAM_STS.value: lambda: MemoryRAMStsAvailabilityChecker(initial_data).get_availability(),
            AvailablePluginsColsToCheck.DESGASTE_FRENOS.value: lambda: BrakeWearAvailabilityChecker(initial_data).get_availability(),
        }

        total_time = 0
        # Check the availability for each variable
        for column in self.columns_to_check:
            start_calculation_time = time.time()
            try:
                calculation = checker_plugins[column]()
                complete_calculation.append(calculation["availability_data"])
                global_data.append(calculation["data_for_global"])

                del calculation
                gc.collect()
            # pylint: disable=broad-except
            except Exception as error:
                print(f"Error calculating the availability for {column}: {error}")
                continue
            end_calculation_time = time.time()
            total_time += end_calculation_time - start_calculation_time

        # Calculate the global availability
        global_availability = GlobalAvailabilityChecker(global_data).get_availability()
        complete_calculation.append(global_availability["availability_data"])

        availability = pd.concat(complete_calculation)

        # Liberar memoria después de concatenar los cálculos completos
        del complete_calculation, global_availability
        gc.collect()
        print(f"Total time to calculate the availability for all variables: {round(total_time,2)}s")
        return availability
