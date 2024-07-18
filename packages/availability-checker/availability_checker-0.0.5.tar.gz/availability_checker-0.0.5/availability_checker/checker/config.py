"""
Handle Configurations
"""

from enum import Enum


class AvailablePluginsColsToCheck(Enum):
    """
    Enum for the available plugins variables to check
    """

    ID_RUTA = "idRuta"
    TIPO_BUS = "tipoBus"
    COORDENADAS = "coordenadas"
    TECNOLOGIA_MOTOR = "tecnologiaMotor"
    TIPO_FRENOS = "tipoFreno"
    VELOCIDAD_VEHICULO = "velocidadVehiculo"
    ACELERACION_VEHICULO = "aceleracionVehiculo"
    TEMPERATURA_MOTOR = "temperaturaMotor"
    PRESION_ACEITE_MOTOR = "presionAceiteMotor"
    REVOLUCIONES_MOTOR = "revolucionesMotor"
    DESGASTE_FRENOS = "estadoDesgasteFrenos"
    KILOMETROS_ODOMETRO = "kilometrosOdometro"
    NIVEL_TANQUE_COMBUSTIBLE = "nivelTanqueCombustible"
    TEMPERATURA_STS = "temperaturaSts"
    MEM_RAM_STS = "memRamSts"
