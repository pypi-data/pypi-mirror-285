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

from antimatter_api.models.domain_insert_write_context_classifier_rule200_response import DomainInsertWriteContextClassifierRule200Response

class TestDomainInsertWriteContextClassifierRule200Response(unittest.TestCase):
    """DomainInsertWriteContextClassifierRule200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DomainInsertWriteContextClassifierRule200Response:
        """Test DomainInsertWriteContextClassifierRule200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `DomainInsertWriteContextClassifierRule200Response`
        """
        model = DomainInsertWriteContextClassifierRule200Response()
        if include_optional:
            return DomainInsertWriteContextClassifierRule200Response(
                rule_id = 'rl-w8q6zgckec0l3o4g'
            )
        else:
            return DomainInsertWriteContextClassifierRule200Response(
                rule_id = 'rl-w8q6zgckec0l3o4g',
        )
        """

    def testDomainInsertWriteContextClassifierRule200Response(self):
        """Test DomainInsertWriteContextClassifierRule200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
