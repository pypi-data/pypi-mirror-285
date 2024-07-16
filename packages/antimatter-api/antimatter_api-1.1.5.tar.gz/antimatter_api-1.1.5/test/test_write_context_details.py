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

from antimatter_api.models.write_context_details import WriteContextDetails

class TestWriteContextDetails(unittest.TestCase):
    """WriteContextDetails unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> WriteContextDetails:
        """Test WriteContextDetails
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `WriteContextDetails`
        """
        model = WriteContextDetails()
        if include_optional:
            return WriteContextDetails(
                name = 'ic3::ss7djuy2zme',
                summary = '',
                description = '',
                config = antimatter_api.models.write_context_config_info.WriteContextConfigInfo(
                    key_reuse_ttl = 0, 
                    default_capsule_tags = [
                        antimatter_api.models.write_context_classifier_tag.WriteContextClassifierTag(
                            name = 'tag.antimatter.io/pii/name', 
                            value = '', 
                            type = 'string', )
                        ], 
                    required_hooks = [
                        antimatter_api.models.write_context_config_info_required_hooks_inner.WriteContextConfigInfo_requiredHooks_inner(
                            hook = 'ar1c2v7s6djuy1z', 
                            constraint = '>072888001528021798096225500850762068629.39333975650685139102691291732729478601482026.0912727550417577019298162864882916633228770521', 
                            mode = 'sync', )
                        ], ),
                imported = True,
                source_domain_id = 'dm-dFZPn3BZqho',
                source_domain_name = ''
            )
        else:
            return WriteContextDetails(
                name = 'ic3::ss7djuy2zme',
                summary = '',
                description = '',
                config = antimatter_api.models.write_context_config_info.WriteContextConfigInfo(
                    key_reuse_ttl = 0, 
                    default_capsule_tags = [
                        antimatter_api.models.write_context_classifier_tag.WriteContextClassifierTag(
                            name = 'tag.antimatter.io/pii/name', 
                            value = '', 
                            type = 'string', )
                        ], 
                    required_hooks = [
                        antimatter_api.models.write_context_config_info_required_hooks_inner.WriteContextConfigInfo_requiredHooks_inner(
                            hook = 'ar1c2v7s6djuy1z', 
                            constraint = '>072888001528021798096225500850762068629.39333975650685139102691291732729478601482026.0912727550417577019298162864882916633228770521', 
                            mode = 'sync', )
                        ], ),
                imported = True,
        )
        """

    def testWriteContextDetails(self):
        """Test WriteContextDetails"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
