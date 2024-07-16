# coding: utf-8

"""
    Antimatter Public API

    Interact with the Antimatter Cloud API

    The version of the OpenAPI document: 1.1.5
    Contact: support@antimatter.io
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from antimatter_api.models.domain_control_log_entry import DomainControlLogEntry

class TestDomainControlLogEntry(unittest.TestCase):
    """DomainControlLogEntry unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DomainControlLogEntry:
        """Test DomainControlLogEntry
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `DomainControlLogEntry`
        """
        model = DomainControlLogEntry()
        if include_optional:
            return DomainControlLogEntry(
                domain = 'dm-dFZPn3BZqho',
                id = 'bf325375e030fccba00917317c574773',
                time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                session = 'sn-w8q6zgckec0l3o4gi7xhk0',
                url = '',
                summary = '',
                description = {
                    'key' : ''
                    },
                issuer = '',
                principal = ''
            )
        else:
            return DomainControlLogEntry(
                domain = 'dm-dFZPn3BZqho',
                id = 'bf325375e030fccba00917317c574773',
                time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                session = 'sn-w8q6zgckec0l3o4gi7xhk0',
                url = '',
                summary = '',
                description = {
                    'key' : ''
                    },
                issuer = '',
                principal = '',
        )
        """

    def testDomainControlLogEntry(self):
        """Test DomainControlLogEntry"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
