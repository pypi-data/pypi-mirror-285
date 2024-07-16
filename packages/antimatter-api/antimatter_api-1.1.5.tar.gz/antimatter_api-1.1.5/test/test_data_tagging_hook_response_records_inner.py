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

from antimatter_api.models.data_tagging_hook_response_records_inner import DataTaggingHookResponseRecordsInner

class TestDataTaggingHookResponseRecordsInner(unittest.TestCase):
    """DataTaggingHookResponseRecordsInner unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DataTaggingHookResponseRecordsInner:
        """Test DataTaggingHookResponseRecordsInner
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `DataTaggingHookResponseRecordsInner`
        """
        model = DataTaggingHookResponseRecordsInner()
        if include_optional:
            return DataTaggingHookResponseRecordsInner(
                elements = [
                    antimatter_api.models.tag_set.TagSet(
                        capsule_tags = [
                            antimatter_api.models.tag.Tag(
                                name = 'tag.antimatter.io/pii/name', 
                                value = '', 
                                type = 'string', 
                                source = '', 
                                hook_version = '4.072888001528021798096225500850762068629.39333975650685139102691291732729478601482026', )
                            ], 
                        span_tags = [
                            antimatter_api.models.tag_set_span_tags_inner.TagSet_spanTags_inner(
                                start = 56, 
                                end = 56, 
                                tags = [
                                    antimatter_api.models.tag.Tag(
                                        name = 'tag.antimatter.io/pii/name', 
                                        value = '', 
                                        type = 'string', 
                                        source = '', 
                                        hook_version = '4.072888001528021798096225500850762068629.39333975650685139102691291732729478601482026', )
                                    ], )
                            ], )
                    ]
            )
        else:
            return DataTaggingHookResponseRecordsInner(
                elements = [
                    antimatter_api.models.tag_set.TagSet(
                        capsule_tags = [
                            antimatter_api.models.tag.Tag(
                                name = 'tag.antimatter.io/pii/name', 
                                value = '', 
                                type = 'string', 
                                source = '', 
                                hook_version = '4.072888001528021798096225500850762068629.39333975650685139102691291732729478601482026', )
                            ], 
                        span_tags = [
                            antimatter_api.models.tag_set_span_tags_inner.TagSet_spanTags_inner(
                                start = 56, 
                                end = 56, 
                                tags = [
                                    antimatter_api.models.tag.Tag(
                                        name = 'tag.antimatter.io/pii/name', 
                                        value = '', 
                                        type = 'string', 
                                        source = '', 
                                        hook_version = '4.072888001528021798096225500850762068629.39333975650685139102691291732729478601482026', )
                                    ], )
                            ], )
                    ],
        )
        """

    def testDataTaggingHookResponseRecordsInner(self):
        """Test DataTaggingHookResponseRecordsInner"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
