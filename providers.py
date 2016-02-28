import urllib
import xml.dom.minidom
import datetime

# Provides currency rates from the National Bank of the Republic of Belarus website
class NbrbRateProvider:
    url_on_date = "http://www.nbrb.by/Services/XmlExRates.aspx?ondate="
    url_range = "http://www.nbrb.by/Services/XmlExRatesDyn.aspx?curId={ccyId}&fromDate={from}&toDate={to}"
    url_currencies = "http://www.nbrb.by/Services/XmlExRatesRef.aspx"

    def get_rates(self, currency, fromDate, toDate):
        currencies = self.get_currencies()
        if currencies.has_key(currency):
            ccyId = currencies[currency]
        else:
            raise Exception("Unsupported currency.")

        url = self.url_range.replace("{ccyId}", ccyId).replace("{from}", self.__date_to_string(fromDate)).replace("{to}", self.__date_to_string(toDate))
        resp = self.__get_response(url)
        return self.__parse_range(resp)

    def get_rates_on_date(self, date = None):
        if date == None:
            date = datetime.datetime.now()
        resp = self.__get_response(self.url_on_date + self.__date_to_string(date))
        return self.__parse(resp)

    def get_currencies(self):
        resp = self.__get_response(self.url_currencies)
        return self.__parse_currencies(resp)

    def __get_response(self, url):
        u = urllib.urlopen(url)
        return u.read()

    def __date_to_string(self, date):
        return date.strftime("%m/%d/%Y")

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
            result[date] = rate

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
