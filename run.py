from providers import NbrbRateProvider
import datetime

provider = NbrbRateProvider()
print provider.get_currencies()
print provider.get_rates("USD", datetime.date(2016, 1, 1), datetime.date(2016, 2, 26))
print provider.get_rates_on_date(datetime.date(2016, 2, 26))