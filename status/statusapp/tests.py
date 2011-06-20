"""
The test module. To run tests, change directory to status and run
'python manage.py test statusapp'.
"""
from statusapp.views import _is_ip_in_subnet, _get_exit_policy
import django.test

class IpInSubnetTest(django.test.TestCase):
    """
    Test the _is_ip_in_subnet function
    """

    def test_range(self):
        """
        Test that the subnet bit, when provided, is handled correctly
        """
        self.assertEqual(_is_ip_in_subnet('0.0.0.0', '0.0.0.0/8'), 
                True)
        self.assertEqual(_is_ip_in_subnet('0.255.255.255', '0.0.0.0/8'), 
                True)
        self.assertEqual(_is_ip_in_subnet('1.0.0.0', '0.0.0.0/8'), 
                False)
        self.assertEqual(_is_ip_in_subnet('129.255.255.255', '128.0.0.0/7'), 
                True)
        self.assertEqual(_is_ip_in_subnet('130.0.0.0', '128.0.0.0/7'), 
                False)
        self.assertEqual(_is_ip_in_subnet('127.255.255.255', '128.0.0.0/7'), 
                False)

    def test_expressions(self):
        """
        Test that the function behaves properly when no subnet bit is provided
        """
        self.assertEqual(_is_ip_in_subnet('129.133.1.125', '*'), True)
        self.assertEqual(_is_ip_in_subnet('129.133.1.125', '129.133.1.126'), 
                False)

class ExitPolicyTest(django.test.TestCase):
    """
    Test the _get_exit_policy function
    """

    def test_get_policy(self):
        """
        Test that, given an arbitrary raw descriptor, exit policy information
        is properly collected
        """
        rawdesc = "router testrouter\ninfo here it is\nfield this is another \
                one\naccept 129.133.8.19:80\naccept 209.59.220.195:80\naccept \
                69.164.213.224:41231\nreject *:*\njunk more of it is here"
        self.assertEqual(_get_exit_policy(rawdesc), ['accept 129.133.8.19:80', \
                'accept 209.59.220.195:80', 'accept \
                69.164.213.224:41231', 'reject *:*'])

