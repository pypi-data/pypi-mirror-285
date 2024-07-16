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

from antimatter_api.models.tag_summary_elided_tags_inner import TagSummaryElidedTagsInner

class TestTagSummaryElidedTagsInner(unittest.TestCase):
    """TagSummaryElidedTagsInner unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> TagSummaryElidedTagsInner:
        """Test TagSummaryElidedTagsInner
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `TagSummaryElidedTagsInner`
        """
        model = TagSummaryElidedTagsInner()
        if include_optional:
            return TagSummaryElidedTagsInner(
                tag_name = '',
                num_unique_tags = 56,
                total_occurrences = 56
            )
        else:
            return TagSummaryElidedTagsInner(
                tag_name = '',
                num_unique_tags = 56,
                total_occurrences = 56,
        )
        """

    def testTagSummaryElidedTagsInner(self):
        """Test TagSummaryElidedTagsInner"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
