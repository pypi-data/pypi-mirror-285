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

import pandas as pd

class Checker:
    """
    Entry point for the availability checker
    """
    def __init__(self, df: pd.DataFrame):
        """
        Constructor for the availability checker
        """
        self.df = df

    def check_availability(self) -> str:
        """
        Method to check the availability of the variables
        """
        return 'working'