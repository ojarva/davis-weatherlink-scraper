from bs4 import BeautifulSoup
import datetime
import pprint
import re
import requests
import sys


class WeatherLink(object):

    def __init__(self):
        self.parser = WeatherLinkParser()

    def get(self, username):
        response = requests.get("http://www.weatherlink.com/user/%s/index.php?view=summary&headers=1&type=1" % username)
        if response.url == "http://www.weatherlink.com/error.php" or response.status_code != 200:
            raise ValueError("Invalid username")
        return self.parser.parse(response.content)


class WeatherLinkParser(object):
    """ Parses WeatherLink summary page data."""

    def __init__(self, content=None):
        self.content = content
        self._parsed = None
        self.parse(content)

    @property
    def _empty_data(self):
        return dict({
            "meta": {"timestamp": None, "name": None},
            "data": {
                "12 Hour Forecast": {"current": {"raw_value": None}},
                "Average Wind Speed": {"10min": {"unit": None, "value": None}, "2min": {"unit": None, "value": None}},
                "Bar Trend": {"current": {"raw_value": None}},
                "Barometer": {"current": {"unit": None, "value": None}, "today_high": {"timestamp": None, "unit": None, "value": None}, "today_low": {"timestamp": None, "unit": None, "value": None}},
                "Dew Point": {"current": {"unit": None, "value": None}, "today_high": {"timestamp": None, "unit": None, "value": None}, "today_low": {"timestamp": None, "unit": None, "value": None}},
                "Heat Index": {"current": {"unit": None, "value": None}, "today_high": {"timestamp": None, "unit": None, "value": None}},
                "Inside Humidity": {"current": {"unit": None, "value": None}, "today_high": {"timestamp": None, "unit": None, "value": None}, "today_low": {"timestamp": None, "unit": None, "value": None}},
                "Inside Temp": {"current": {"unit": None, "value": None}, "today_high": {"timestamp": None, "unit": None, "value": None}, "today_low": {"timestamp": None, "unit": None, "value": None}},
                "Last Hour Rain": {"current": {"unit": "mm", "value": None}},
                "Outside Humidity": {"current": {"unit": None, "value": None}, "today_high": {"timestamp": None, "unit": None, "value": None}, "today_low": {"timestamp": None, "unit": None, "value": None}},
                "Outside Temp": {"current": {"unit": None, "value": None}, "today_high": {"timestamp": None, "unit": None, "value": None}, "today_low": {"timestamp": None, "unit": None, "value": None}},
                "Rain": {"current": {"unit": "mm/h", "value": None}, "day": {"unit": "mm", "value": None}, "month": {"unit": "mm", "value": None}, "storm": {"unit": "mm", "value": None}, "year": {"unit": "mm", "value": None}},
                "Wind Chill": {"current": {"unit": None, "value": None}, "today_high": {"timestamp": None, "unit": None, "value": None}},
                "Wind Direction": {"current": {"text": None, "unit": None, "value": None}},
                "Wind Gust Speed": {"2min": {"unit": None, "value": None}},
                "Wind Speed": {"current": {"unit": None, "value": None}, "today_high": {"timestamp": None, "unit": None, "value": None}}
            },
        })

    def parse_timestamp(self, timestamp):
        """ Current Conditions as of 12:01 Wednesday, September 9, 2015 """
        timestamp = timestamp.replace("Current Conditions as of ", "")
        return datetime.datetime.strptime(timestamp, "%H:%M %A, %B %d, %Y")

    def parse_value(self, raw_value, extra=None):
        def format_value(value, unit):
            if unit == "KT":
                # Knots, convert to m/s
                value = round(value * 0.514444444, 1)
                unit = "m/s"
            elif unit == "F":
                # Fahrenheit, convert to C
                value = round((value - 32) * 5.0 / 9.0, 1)
                unit = "C"
            elif unit == "\"":
                if extra == "barometer":
                    # inHg. Convert to hPa
                    value = round(value * 33.8639, 1)
                    unit = "hPa"
                else:
                    # inches. Convert to mm
                    value = round(value * 25.4, 1)
                    unit = "mm"
            elif unit == "\"/Hour":
                # inches. Convert to mm/hour
                value = round(value * 25.4, 1)
                unit = "mm/h"
            elif unit == "mm/Hour":
                unit = "mm/h"
            elif unit == "Mph":
                unit = "m/s"
                value = round(value * 0.44704, 1)
            elif unit == "km/h":
                unit = "m/s"
                value = round(value / 3.6, 1)
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

        for unit in ("%", "hPa", "mm/Hour", "mm", "mb", "\""):
            parsed = try_with_unit(raw_value, unit)
            if parsed is not None:
                return parsed
        if raw_value == "Calm":
            return {"unit": "m/s", "value": 0, "raw_value": "Calm"}
        return {"raw_value": raw_value}

    def parse(self, content=None):
        if content is None:
            content = self.content

        if content is None:
            return

        self._parsed = self._empty_data

        bs = BeautifulSoup(content, "html.parser")
        current_section = None
        table = bs.find_all("table")[2]
        for row in table.find_all("tr"):
            row_header_processed = False
            current_row = None
            values = []
            for td in row.find_all("td"):
                colspan = td.get("colspan")
                classes = td.get("class", [])
                if "summary_station_name" in classes:
                    self._parsed["meta"]["name"] = td.string
                    continue
                if "summary_timestamp" in classes:
                    self._parsed["meta"]["timestamp"] = self.parse_timestamp(td.string)
                    continue

                if colspan == "6":
                    continue
                if "summary_header_label" in classes:
                    current_section = td.string
                    continue

                if "summary_data" in classes:
                    if not row_header_processed:
                        row_header_processed = True
                        current_row = td.string
                        continue
                    if td.string != u"\xa0":
                        if current_section == "Station Summary":
                            if len(values) == 0:
                                # Current value
                                if current_row == "Barometer":
                                    extra = "barometer"
                                else:
                                    extra = None
                                if current_row == "Wind Direction":
                                    try:
                                        text_item, degrees = td.string.split(u"\xa0")
                                        degrees = int(degrees.replace(u"\xb0", ""))
                                        self._parsed["data"][current_row]["current"] = {"unit": "deg", "value": degrees, "text": text_item}
                                    except ValueError:
                                        pass
                                else:
                                    value = td.string
                                    self._parsed["data"][current_row]["current"].update(self.parse_value(value, extra))
                            if len(values) == 1:
                                self._parsed["data"][current_row]["today_high"].update(self.parse_value(td.string, extra))
                            if len(values) == 2:
                                self._parsed["data"][current_row]["today_high"]["timestamp"] = td.string
                            if len(values) == 3:
                                self._parsed["data"][current_row]["today_low"].update(self.parse_value(td.string, extra))
                            if len(values) == 4:
                                self._parsed["data"][current_row]["today_low"]["timestamp"] = td.string

                        if current_section == "Wind":
                            if len(values) == 0:
                                self._parsed["data"][current_row]["2min"].update(self.parse_value(td.string))
                            if len(values) == 1:
                                self._parsed["data"][current_row]["10min"].update(self.parse_value(td.string))

                        if current_section == "Rain":
                            if len(values) == 0:
                                self._parsed["data"][current_row]["current"].update(self.parse_value(td.string))
                            if len(values) == 1:
                                self._parsed["data"][current_row]["day"].update(self.parse_value(td.string))
                            if len(values) == 2:
                                self._parsed["data"][current_row]["storm"].update(self.parse_value(td.string))
                            if len(values) == 3:
                                self._parsed["data"][current_row]["month"].update(self.parse_value(td.string))
                            if len(values) == 4:
                                self._parsed["data"][current_row]["year"].update(self.parse_value(td.string))

                        values.append(td.string)

        return self._parsed
