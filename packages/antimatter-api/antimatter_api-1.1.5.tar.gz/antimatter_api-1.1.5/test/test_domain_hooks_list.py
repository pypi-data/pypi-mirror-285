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

from antimatter_api.models.domain_hooks_list import DomainHooksList

class TestDomainHooksList(unittest.TestCase):
    """DomainHooksList unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DomainHooksList:
        """Test DomainHooksList
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `DomainHooksList`
        """
        model = DomainHooksList()
        if include_optional:
            return DomainHooksList(
                hooks = [
                    antimatter_api.models.domain_hooks_list_hooks_inner.DomainHooksList_hooks_inner(
                        name = 'ar1c2v7s6djuy1z', 
                        url = '', 
                        version = '', 
                        summary = '', 
                        description = '', 
                        output_span_tags = [
                            ''
                            ], 
                        output_capsule_tags = [
                            ''
                            ], )
                    ]
            )
        else:
            return DomainHooksList(
        )
        """

    def testDomainHooksList(self):
        """Test DomainHooksList"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
