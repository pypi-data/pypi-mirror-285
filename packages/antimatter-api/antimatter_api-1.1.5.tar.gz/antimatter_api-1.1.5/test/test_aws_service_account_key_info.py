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

from antimatter_api.models.aws_service_account_key_info import AWSServiceAccountKeyInfo

class TestAWSServiceAccountKeyInfo(unittest.TestCase):
    """AWSServiceAccountKeyInfo unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> AWSServiceAccountKeyInfo:
        """Test AWSServiceAccountKeyInfo
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `AWSServiceAccountKeyInfo`
        """
        model = AWSServiceAccountKeyInfo()
        if include_optional:
            return AWSServiceAccountKeyInfo(
                access_key_id = '',
                secret_access_key = '',
                key_arn = '',
                provider_name = 'aws_sa'
            )
        else:
            return AWSServiceAccountKeyInfo(
                access_key_id = '',
                secret_access_key = '',
                key_arn = '',
        )
        """

    def testAWSServiceAccountKeyInfo(self):
        """Test AWSServiceAccountKeyInfo"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
