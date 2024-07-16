# coding: utf-8

"""
    Nuon

    API for managing nuon apps, components, and installs.

    The version of the OpenAPI document: 0.19.162
    Contact: support@nuon.co
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

from nuon.models.app_policy import AppPolicy

class TestAppPolicy(unittest.TestCase):
    """AppPolicy unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> AppPolicy:
        """Test AppPolicy
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `AppPolicy`
        """
        model = AppPolicy()
        if include_optional:
            return AppPolicy(
                created_at = '',
                created_by = nuon.models.app/account.app.Account(
                    account_type = 'auth0', 
                    created_at = '', 
                    email = '', 
                    id = '', 
                    org_ids = [
                        ''
                        ], 
                    orgs = [
                        nuon.models.app/org.app.Org(
                            created_at = '', 
                            created_by = nuon.models.app/account.app.Account(
                                created_at = '', 
                                email = '', 
                                id = '', 
                                permissions = {
                                    'key' : 'unknown'
                                    }, 
                                roles = [
                                    nuon.models.app/role.app.Role(
                                        created_by = , 
                                        created_at = '', 
                                        created_by_id = '', 
                                        id = '', 
                                        policies = [
                                            nuon.models.app/policy.app.Policy(
                                                created_at = '', 
                                                created_by_id = '', 
                                                id = '', 
                                                name = 'org_admin', 
                                                permissions = {
                                                    'key' : ''
                                                    }, 
                                                role_id = '', 
                                                updated_at = '', )
                                            ], 
                                        role_type = 'org_admin', 
                                        updated_at = '', )
                                    ], 
                                subject = '', 
                                updated_at = '', ), 
                            created_by_id = '', 
                            custom_cert = True, 
                            health_checks = [
                                nuon.models.app/org_health_check.app.OrgHealthCheck(
                                    created_at = '', 
                                    created_by_id = '', 
                                    id = '', 
                                    org_id = '', 
                                    status = 'ok', 
                                    status_description = '', 
                                    updated_at = '', )
                                ], 
                            id = '', 
                            latest_health_check = null, 
                            name = '', 
                            notifications_config = nuon.models.app/notifications_config.app.NotificationsConfig(
                                created_at = '', 
                                created_by_id = '', 
                                id = '', 
                                org_id = '', 
                                owner_id = '', 
                                owner_type = '', 
                                slack_webhook_url = '', 
                                updated_at = '', ), 
                            sandbox_mode = True, 
                            status = '', 
                            status_description = '', 
                            updated_at = '', 
                            vcs_connections = [
                                nuon.models.app/vcs_connection.app.VCSConnection(
                                    created_at = '', 
                                    created_by_id = '', 
                                    github_install_id = '', 
                                    id = '', 
                                    updated_at = '', 
                                    vcs_connection_commit = [
                                        nuon.models.app/vcs_connection_commit.app.VCSConnectionCommit(
                                            author_email = '', 
                                            author_name = '', 
                                            component_config_connection_id = '', 
                                            created_at = '', 
                                            created_by_id = '', 
                                            id = '', 
                                            message = '', 
                                            sha = '', 
                                            updated_at = '', )
                                        ], )
                                ], )
                        ], 
                    permissions = {
                        'key' : 'unknown'
                        }, 
                    roles = [
                        nuon.models.app/role.app.Role(
                            created_at = '', 
                            created_by_id = '', 
                            id = '', 
                            updated_at = '', )
                        ], 
                    subject = '', 
                    updated_at = '', ),
                created_by_id = '',
                id = '',
                name = 'org_admin',
                permissions = {
                    'key' : ''
                    },
                role_id = '',
                updated_at = ''
            )
        else:
            return AppPolicy(
        )
        """

    def testAppPolicy(self):
        """Test AppPolicy"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
