import unittest

import mechanize

from src.experiment import parse_usage_string, parse_usage_data, to_gb

class MyTestCase(unittest.TestCase):

    def test_good_string(self):
        usage = parse_usage_string('CABLE MODEM Up to 1234 Download/234 Upload MAC: AB:CD You have used 432: 321 upload & 111 download. Your limit is 1212. You have 987 remaining.')
        self.assertEqual(8, len(usage))
        self.assertTrue(all(isinstance(x, tuple) for x in usage))

    def test_month_begin_string(self):
        usage = parse_usage_string('CABLE MODEM Up to 500Mbps Download/12Mbps Upload MAC: AB:CD:XX:XX:XX:XX')
        self.assertEqual(3, len(usage))
        self.assertTrue(all(isinstance(x, tuple) for x in usage))
        usage = parse_usage_string('INTERNET MODEM Up to 500Mbps Download/12Mbps Upload MAC: 50:09:59:72:D6:39')
        self.assertEqual(3, len(usage))
        self.assertTrue(all(isinstance(x, tuple) for x in usage))

    def test_find_usage_data(self):
        data = '''{"content":"
        <div class=\\"label\\">Monthly Cycle:</div><div class=\\"value\\">20 Days Remaining</div>
        <div class=\\"label\\">Data Used:</div><div class=\\"value\\">300.6 GB</div>
        "}'''.replace('\n', '')
        usage = parse_usage_data(data)
        self.assertEqual(2, len(usage))
        self.assertTrue(all(isinstance(x, tuple) for x in usage))

    def test_to_gb(self):
        self.assertEqual(12000, to_gb('12 TB'))
        self.assertEqual(12, to_gb('12 GB'))
        self.assertEqual(0.012, to_gb('12 MB'))
        self.assertEqual(0.000012, to_gb('12 KB'))

    def test_mechanize(self):
        br = mechanize.Browser()
        br.open("https://www.brctv.com/login")

if __name__ == '__main__':
    unittest.main()
