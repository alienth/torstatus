"""
The test module. To run tests, change directory to status and run
'python manage.py test statusapp'.
"""
import django.test
from statusapp.views.helpers import is_ip_in_subnet, is_ipaddress, \
        is_port


class IpInSubnetTest(django.test.TestCase):
    """
    Test the is_ip_in_subnet function.
    """

    def test_range(self):
        """
        Test that the subnet bit, when provided, is handled correctly.
        """
        self.assertEqual(is_ip_in_subnet('0.0.0.0', '0.0.0.0/8'),
                True)
        self.assertEqual(is_ip_in_subnet('0.255.255.255', '0.0.0.0/8'),
                True)
        self.assertEqual(is_ip_in_subnet('1.0.0.0', '0.0.0.0/8'),
                False)
        self.assertEqual(is_ip_in_subnet('129.255.255.255', '128.0.0.0/7'),
                True)
        self.assertEqual(is_ip_in_subnet('130.0.0.0', '128.0.0.0/7'),
                False)
        self.assertEqual(is_ip_in_subnet('127.255.255.255', '128.0.0.0/7'),
                False)

    def test_expressions(self):
        """
        Test that the function behaves properly when no subnet bit is provided.
        """
        self.assertEqual(is_ip_in_subnet('129.133.1.125', '*'), True)
        self.assertEqual(is_ip_in_subnet('129.133.1.125', '129.133.1.126'),
                False)


class IpAddressTest(django.test.TestCase):
    """
    Test the is_ipaddress function.
    """

    def test_is_ip(self):
        """
        Test that the function ensures that IP addresses must consist of
        four integer values between 0 and 255, inclusive, separated
        by periods.
        """
        self.assertEqual(is_ipaddress('255.33.12.0'), True)
        self.assertEqual(is_ipaddress('256.33.12.0'), False)
        self.assertEqual(is_ipaddress('a.33.12.0'), False)
        self.assertEqual(is_ipaddress('255.33.120'), False)
        self.assertEqual(is_ipaddress('255.-1.120.0'), False)
        self.assertEqual(is_ipaddress('255.31.1.0.3'), False)


class PortTest(django.test.TestCase):
    """
    Test the is_port function.
    """

    def test_is_port(self):
        """
        Test that the function ensure that ports must consist of integer
        values between 0 and 65535, inclusive.
        """
        self.assertEqual(is_port('0'), True)
        self.assertEqual(is_port('0.5'), False)
        self.assertEqual(is_port('-1'), False)
        self.assertEqual(is_port('65535'), True)
        self.assertEqual(is_port('65536'), False)
