
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import Enum


class Module(Enum):
    CORE="core"
    ORACLE="oracle"
    PORTFOLIO="portfolio"


### DOMAIN : ORACLE
class SubModule(Enum):
    FINCORE="fincore"
    GYMCORE="gymcore"
    SPORTSCORE="sportscore"
    HEALTHCORE="healthcore"
    ENVICORE="envicore"
    POLICORE="policore"
    CUSTOM="custom"

class BaseDataCategory(Enum):
    HISTORIC = "historic" # Historical data, usually accurate and complete
    REAL_TIME="realtime" # Real-time data, not always certain, can have error
    ANALYTICS="analytics" # Analytical data andx modelling, derived from historical and prediction data
    PREDICTIVE="predictive" # Predictive data, based on models and simulations
    HISTORIC_OPINION="histopinion" # Opinions and subjective data about the past, msotly unverified but recorded facts and ideas
    SIMULATION_HISTORIC = "simhistoric" # Simulates past events
    SIMULATION_REAL_TIME = "simrealtime" #  Simulates live data streams
    SIMULATION_ANALYTICS = "simanalytics" #  Simulates live data streams
    SIMULATION_PREDICTIVE="simpredictive" # Simulated data, used for testing and training