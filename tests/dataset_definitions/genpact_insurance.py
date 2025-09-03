from enum import Enum

class GenpactInsuranceTestColumnNames(Enum):
    '''
    Based on the Genpact Insurance dataset
    '''

    # Metrics
    CLAIMS_EXPENSE = "claims_expense"
    COMBINED_RATIO = "combined_ratio"
    LOSS_RATIO = "loss_ratio"

    # Dimensions
    COUNTRY = "country"
    DISTRIBUTION_CHANNEL = "distribution_channel"
    GEO = "geo"
    LINE_OF_BUSINESS = "line_of_business"

    # Some example dim values
    GEO__EUROPE = "europe"
    LINE_OF_BUSINESS__GROUP = "group"

    # Time Granularities
    MONTH = "max_time_month"
    QUARTER = "max_time_quarter"
    YEAR = "max_time_year"
