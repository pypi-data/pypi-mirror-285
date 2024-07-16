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

from antimatter_api.models.domain_peer_config import DomainPeerConfig

class TestDomainPeerConfig(unittest.TestCase):
    """DomainPeerConfig unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DomainPeerConfig:
        """Test DomainPeerConfig
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `DomainPeerConfig`
        """
        model = DomainPeerConfig()
        if include_optional:
            return DomainPeerConfig(
                export_identity_providers = [
                    'ar2c3v8s7djuy2zme'
                    ],
                export_all_identity_providers = True,
                export_facts = [
                    'ar2c3v8s7djuy2zme'
                    ],
                export_all_facts = True,
                export_read_contexts = [
                    'ar2c3v8s7djuy2zme'
                    ],
                export_all_read_contexts = True,
                export_write_contexts = [
                    'ar2c3v8s7djuy2zme'
                    ],
                export_all_write_contexts = True,
                export_capabilities = [
                    'ar1c2v7s6djuy1zme'
                    ],
                export_all_capabilities = True,
                export_domain_policy = True,
                export_root_encryption_keys = True,
                export_capsule_access_log = True,
                export_control_log = True,
                export_capsule_manifest = True,
                export_billing = True,
                export_admin_contact = True,
                nicknames = [
                    ''
                    ],
                import_alias = 'ar2c3v8s7djuy2zme',
                forward_billing = True,
                forward_admin_communications = True,
                import_identity_providers = [
                    'ar2c3v8s7djuy2zme'
                    ],
                import_all_identity_providers = True,
                import_facts = [
                    'ar2c3v8s7djuy2zme'
                    ],
                import_all_facts = True,
                import_read_contexts = [
                    'ar2c3v8s7djuy2zme'
                    ],
                import_all_read_contexts = True,
                import_write_contexts = [
                    'ar2c3v8s7djuy2zme'
                    ],
                import_all_write_contexts = True,
                import_capabilities = [
                    'ar1c2v7s6djuy1zme'
                    ],
                import_all_capabilities = True,
                import_domain_policy = True,
                import_root_encryption_keys = True,
                import_precedence = 56,
                import_capsule_access_log = True,
                import_control_log = True,
                import_capsule_manifest = True,
                display_name = '0'
            )
        else:
            return DomainPeerConfig(
                display_name = '0',
        )
        """

    def testDomainPeerConfig(self):
        """Test DomainPeerConfig"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
