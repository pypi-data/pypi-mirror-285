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

from antimatter_api.models.fact_policy_rules_inner_arguments_inner import FactPolicyRulesInnerArgumentsInner

class TestFactPolicyRulesInnerArgumentsInner(unittest.TestCase):
    """FactPolicyRulesInnerArgumentsInner unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> FactPolicyRulesInnerArgumentsInner:
        """Test FactPolicyRulesInnerArgumentsInner
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `FactPolicyRulesInnerArgumentsInner`
        """
        model = FactPolicyRulesInnerArgumentsInner()
        if include_optional:
            return FactPolicyRulesInnerArgumentsInner(
                any = True,
                source = 'domainIdentity',
                capability = 'ic3::ss6djuy1zme',
                value = ''
            )
        else:
            return FactPolicyRulesInnerArgumentsInner(
        )
        """

    def testFactPolicyRulesInnerArgumentsInner(self):
        """Test FactPolicyRulesInnerArgumentsInner"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
