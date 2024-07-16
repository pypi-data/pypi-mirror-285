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

from antimatter_api.models.write_context_regex_rule import WriteContextRegexRule

class TestWriteContextRegexRule(unittest.TestCase):
    """WriteContextRegexRule unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> WriteContextRegexRule:
        """Test WriteContextRegexRule
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `WriteContextRegexRule`
        """
        model = WriteContextRegexRule()
        if include_optional:
            return WriteContextRegexRule(
                id = 'rl-w8q6zgckec0l3o4g',
                pattern = '',
                match_on_key = True,
                span_tags = [
                    antimatter_api.models.write_context_classifier_tag.WriteContextClassifierTag(
                        name = 'tag.antimatter.io/pii/name', 
                        value = '', 
                        type = 'string', )
                    ],
                capsule_tags = [
                    antimatter_api.models.write_context_classifier_tag.WriteContextClassifierTag(
                        name = 'tag.antimatter.io/pii/name', 
                        value = '', 
                        type = 'string', )
                    ]
            )
        else:
            return WriteContextRegexRule(
                pattern = '',
                match_on_key = True,
                span_tags = [
                    antimatter_api.models.write_context_classifier_tag.WriteContextClassifierTag(
                        name = 'tag.antimatter.io/pii/name', 
                        value = '', 
                        type = 'string', )
                    ],
                capsule_tags = [
                    antimatter_api.models.write_context_classifier_tag.WriteContextClassifierTag(
                        name = 'tag.antimatter.io/pii/name', 
                        value = '', 
                        type = 'string', )
                    ],
        )
        """

    def testWriteContextRegexRule(self):
        """Test WriteContextRegexRule"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
