import unittest

from src.experiment import parse_usage_string

class MyTestCase(unittest.TestCase):

    def test_good_string(self):
        usage = parse_usage_string('CABLE MODEM Up to 1234 Download/234 Upload MAC: AB:CD You have used 432: 321 upload & 111 download. Your limit is 1212. You have 987 remaining.')
        self.assertEqual(len(usage), 8)

    def test_month_begin_string(self):
        usage = parse_usage_string('CABLE MODEM Up to 500Mbps Download/12Mbps Upload MAC: AB:CD:XX:XX:XX:XX')
        self.assertEqual(len(usage), 3)

if __name__ == '__main__':
    unittest.main()
