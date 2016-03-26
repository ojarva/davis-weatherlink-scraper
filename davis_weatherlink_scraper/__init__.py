from bs4 import BeautifulSoup
import datetime
import pprint
import re
import requests
import sys


class WeatherLink:

    def __init__(self):
        self.parser = WeatherLinkParser()
        pass

    def get(self, username):
        response = requests.get("http://www.weatherlink.com/user/%s/index.php?view=summary&headers=1&type=1" % username)
        return self.parser.parse(response.content)


class WeatherLinkParser:
    """ Parses WeatherLink summary page data."""

    def __init__(self, content=None):
        self.content = content
        self._parsed = None
        self.parse(content)

    def parse_timestamp(self, timestamp):
        """ Current Conditions as of 12:01 Wednesday, September 9, 2015 """
        timestamp = timestamp.replace("Current Conditions as of ", "")
        return datetime.datetime.strptime(timestamp, "%H:%M %A, %B %d, %Y")

    def parse_value(self, raw_value):
        def format_value(value, unit):
            if unit == "KT":
                # Knots, convert to m/s
                value = value * 0.514444444
                unit = "m/s"
            elif unit == "F":
                # Fahrenheit, convert to C
                value = (value - 32) * 5.0 / 9.0
                unit = "C"
            elif unit == "\"":
                # inches. Convert to mm
                value = value * 25.4
                unit = "mm"
            elif unit == "\"/Hour":
                # inches. Convert to mm/hour
                value = value * 25.4
                unit = "mm/h"
            elif unit == "mm/Hour":
                unit = "mm/h"
            elif unit == "Mph":
                unit = "m/s"
                value = value * 0.44704
            elif unit == "km/h":
                unit = "m/s"
                value = value / 3.6
            elif unit == "mb":
                unit = "mb"
            return {"unit": unit, "value": value}

        def try_with_unit(raw_value, unit):
            if unit in raw_value:
                value = raw_value.replace(unit, "")
                try:
                    value = float(value)
                    return format_value(value, unit)
                except ValueError:
                    return None
            return None
        splitted = raw_value.split(" ")
        if len(splitted) == 2:
            # Try converting value to float
            try:
                value = float(splitted[0])
                return format_value(value, splitted[1])
            except ValueError:
                pass

        for unit in ("%", "hPa", "mm/Hour", "mm", "mb"):
            parsed = try_with_unit(raw_value, unit)
            if parsed is not None:
                return parsed
        return {"raw_value": raw_value}

    def parse(self):
        parse(self.content)

    def parse(self, content):
        self.content = content
        if content is None:
            return

        self._parsed = {"meta": {"name": None, "timestamp": None},
                        "data": {}}

        bs = BeautifulSoup(content, "html.parser")
        current_section = None
        table = bs.find_all("table")[2]
        for row in table.find_all("tr"):
            row_header_processed = False
            current_row = None
            row_processed = False
            values = []
            for td in row.find_all("td"):
                colspan = td.get("colspan")
                classes = td.get("class", [])
                if "summary_station_name" in classes:
                    self._parsed["meta"]["name"] = td.string
                    row_processed = True
                    continue
                if "summary_timestamp" in classes:
                    self._parsed["meta"]["timestamp"] = self.parse_timestamp(td.string)
                    row_processed = True
                    continue

                if colspan == "6":
                    row_processed = True
                    continue
                if "summary_header_label" in classes:
                    current_section = td.string
                    row_processed = True
                    continue

                if "summary_data" in classes:
                    if not row_header_processed:
                        row_header_processed = True
                        current_row = td.string
                        self._parsed["data"][current_row] = {}
                        continue
                    if td.string != u"\xa0":
                        if current_section == "Station Summary":
                            if len(values) == 0:
                                # Current value
                                if current_row == "Wind Direction":
                                    value = re.match("([SWNE]{1,3})", td.string)
                                    if value:
                                        value = value.group(0)
                                else:
                                    value = td.string
                                self._parsed["data"][current_row]["current"] = self.parse_value(value)
                            if len(values) == 1:
                                self._parsed["data"][current_row]["today_high"] = self.parse_value(td.string)
                            if len(values) == 2:
                                self._parsed["data"][current_row]["today_high"]["timestamp"] = td.string
                            if len(values) == 3:
                                self._parsed["data"][current_row]["today_low"] = self.parse_value(td.string)
                            if len(values) == 4:
                                self._parsed["data"][current_row]["today_low"]["timestamp"] = td.string

                        if current_section == "Wind":
                            if len(values) == 0:
                                self._parsed["data"][current_row]["current"] = self.parse_value(td.string)
                            if len(values) == 1:
                                self._parsed["data"][current_row]["2min"] = self.parse_value(td.string)
                            if len(values) == 2:
                                self._parsed["data"][current_row]["10min"] = self.parse_value(td.string)

                        if current_section == "Rain":
                            if len(values) == 0:
                                self._parsed["data"][current_row]["current"] = self.parse_value(td.string)
                            if len(values) == 1:
                                self._parsed["data"][current_row]["day"] = self.parse_value(td.string)
                            if len(values) == 2:
                                self._parsed["data"][current_row]["storm"] = self.parse_value(td.string)
                            if len(values) == 3:
                                self._parsed["data"][current_row]["month"] = self.parse_value(td.string)
                            if len(values) == 4:
                                self._parsed["data"][current_row]["year"] = self.parse_value(td.string)

                        values.append(td.string)

        return self._parsed


def main():
    b = WeatherLink()
    pprint.pprint(b.get("maroren"))
    return 0

if __name__ == '__main__':
    sys.exit(main())
