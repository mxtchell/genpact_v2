from ar_analytics.helpers.utils import SharedFn

class InsuranceSharedFn(SharedFn):
    def __init__(self):
        super().__init__()

    def get_formatted_num(self, num: float | int | str, met_format: str, pretty_num=False, signed=False):
        return super().get_formatted_num(num, met_format, True, signed) 