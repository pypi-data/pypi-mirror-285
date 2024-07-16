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

from antimatter_api.models.new_fact_type_definition_arguments_inner import NewFactTypeDefinitionArgumentsInner

class TestNewFactTypeDefinitionArgumentsInner(unittest.TestCase):
    """NewFactTypeDefinitionArgumentsInner unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> NewFactTypeDefinitionArgumentsInner:
        """Test NewFactTypeDefinitionArgumentsInner
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `NewFactTypeDefinitionArgumentsInner`
        """
        model = NewFactTypeDefinitionArgumentsInner()
        if include_optional:
            return NewFactTypeDefinitionArgumentsInner(
                name = 'aqXzyCBw3_uufVPIP0',
                description = ''
            )
        else:
            return NewFactTypeDefinitionArgumentsInner(
                name = 'aqXzyCBw3_uufVPIP0',
                description = '',
        )
        """

    def testNewFactTypeDefinitionArgumentsInner(self):
        """Test NewFactTypeDefinitionArgumentsInner"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
