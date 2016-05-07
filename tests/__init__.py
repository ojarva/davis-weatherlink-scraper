import unittest
import datetime

import davis_weatherlink_scraper


class TestParsing(unittest.TestCase):
    def _parse_file(self, filename):
        with open(filename) as contents:
            return davis_weatherlink_scraper.WeatherLinkParser(contents.read())

    def test_us_units(self):
        """ Check US units conversion to metric """
        parser = self._parse_file("testdata/us-units.html")
        content = parser.parse()
        self.assertIn("data", content)
        self.assertIn("meta", content)
        self.assertIn("timestamp", content["meta"])
        self.assertIn("name", content["meta"])
        self.assertEqual("SANDWICH SHIP SUPPLY", content["meta"]["name"])
        self.assertEqual(datetime.datetime(2015, 9, 9, 8, 5), content["meta"]["timestamp"])

        for data_field, items in content["data"].items():
            for subfield, data in items.items():
                if "unit" in data:
                    self.assertIn(data["unit"], ("C", "m/s", "hPa", "%", "deg"))
        self.assertEqual(22.6, content["data"]["Inside Temp"]["current"]["value"])

    def test_calm_parsing(self):
        """ Validate calm wind values are parsed properly """
        parser = self._parse_file("testdata/hsksatama-calm.html")
        content = parser.parse()
        self.assertEqual(0, content["data"]["Wind Speed"]["current"]["value"])
        self.assertEqual("Calm", content["data"]["Wind Speed"]["current"]["raw_value"])


if __name__ == '__main__':
    unittest.main()
