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

from antimatter_api.models.domain_get_write_context_classifier_rules200_response import DomainGetWriteContextClassifierRules200Response

class TestDomainGetWriteContextClassifierRules200Response(unittest.TestCase):
    """DomainGetWriteContextClassifierRules200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DomainGetWriteContextClassifierRules200Response:
        """Test DomainGetWriteContextClassifierRules200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `DomainGetWriteContextClassifierRules200Response`
        """
        model = DomainGetWriteContextClassifierRules200Response()
        if include_optional:
            return DomainGetWriteContextClassifierRules200Response(
                rules = [
                    antimatter_api.models.classifier_rule.ClassifierRule(
                        id = 'rl-w8q6zgckec0l3o4g', 
                        comment = '', 
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
                        llm_config = antimatter_api.models.llm_classifier_config.LLMClassifierConfig(
                            model = '', 
                            prompt = '', ), 
                        regex_config = antimatter_api.models.regex_classifier_config.RegexClassifierConfig(
                            pattern = '', 
                            match_on_key = True, ), )
                    ]
            )
        else:
            return DomainGetWriteContextClassifierRules200Response(
        )
        """

    def testDomainGetWriteContextClassifierRules200Response(self):
        """Test DomainGetWriteContextClassifierRules200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
