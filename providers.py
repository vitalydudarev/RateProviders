import urllib
import xml.dom.minidom
import datetime
import collections

# Provides currency rates from the National Bank of the Republic of Belarus website
class NbrbRateProvider:
    MAX_RESPONSE_COUNT = 365
    DATE_FORMAT = "%m/%d/%Y"
    
    url_on_date = "http://www.nbrb.by/Services/XmlExRates.aspx?ondate="
    url_range = "http://www.nbrb.by/Services/XmlExRatesDyn.aspx?curId={ccyId}&fromDate={from}&toDate={to}"
    url_currencies = "http://www.nbrb.by/Services/XmlExRatesRef.aspx"

    def get_rates(self, currency, fromDate, toDate):
        currencies = self.get_currencies()
        if currencies.has_key(currency):
            ccyId = currencies[currency]
        else:
            raise Exception("Unsupported currency.")

        result = { }
        periods = self.__get_periods(fromDate, toDate)

        for key, value in periods.iteritems():
            url = self.url_range\
            .replace("{ccyId}", ccyId)\
            .replace("{from}", self.__date_to_string(key))\
            .replace("{to}", self.__date_to_string(value))
            
            resp = self.__get_response(url)
            partial_result = self.__parse_range(resp)
            result.update(partial_result)

        return collections.OrderedDict(sorted(result.items()))

    def get_rates_on_date(self, date = None):
        if date == None:
            date = datetime.datetime.now()
        resp = self.__get_response(self.url_on_date + self.__date_to_string(date))
        return self.__parse(resp)

    def get_currencies(self):
        resp = self.__get_response(self.url_currencies)
        return self.__parse_currencies(resp)

    def __get_periods(self, fromDate, toDate):
        result = { }
        last = fromDate - datetime.timedelta(days = 1)
        duration = (toDate - fromDate).days + 1

        while duration > 0:
            if duration > self.MAX_RESPONSE_COUNT:
                len = self.MAX_RESPONSE_COUNT
            else:
                len = duration

            current = last + datetime.timedelta(days = 1)
            last = last + datetime.timedelta(days = len)
            duration = duration - len

            result[current] = last

        return result

    def __get_response(self, url):
        u = urllib.urlopen(url)
        return u.read()

    def __date_to_string(self, date):
        return date.strftime(self.DATE_FORMAT)

    def __string_to_date(self, str):
        return datetime.datetime.strptime(str, self.DATE_FORMAT)

    def __parse_currencies(self, str):
        result = { }
        doc = xml.dom.minidom.parseString(str)
        response = doc.documentElement
        elements = response.getElementsByTagName("Currency")

        for element in elements:
            ccyId = element.getAttribute('Id')
            charCode = element.getElementsByTagName('CharCode')[0].childNodes[0].data
            result[charCode] = ccyId

        return result

    def __parse_range(self, str):
        result = { }
        doc = xml.dom.minidom.parseString(str)
        response = doc.documentElement
        elements = response.getElementsByTagName("Record")

        for element in elements:
            date = element.getAttribute('Date')
            rate = float(element.getElementsByTagName('Rate')[0].childNodes[0].data)
            result[self.__string_to_date(date)] = rate

        return result

    def __parse(self, str):
        result = { }
        doc = xml.dom.minidom.parseString(str)
        response = doc.documentElement
        elements = response.getElementsByTagName("Currency")

        for element in elements:
            currency = element.getElementsByTagName('CharCode')[0].childNodes[0].data
            scale = float(element.getElementsByTagName('Scale')[0].childNodes[0].data)
            rate = float(element.getElementsByTagName('Rate')[0].childNodes[0].data) / scale
            result[currency] = rate

        return result
