# coding: utf-8

"""
    Nuon

    API for managing nuon apps, components, and installs.

    The version of the OpenAPI document: 0.19.15
    Contact: support@nuon.co
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from nuon.models.app_app_input import AppAppInput

class TestAppAppInput(unittest.TestCase):
    """AppAppInput unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> AppAppInput:
        """Test AppAppInput
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `AppAppInput`
        """
        model = AppAppInput()
        if include_optional:
            return AppAppInput(
                app_input_id = '',
                created_at = '',
                created_by_id = '',
                default = '',
                description = '',
                id = '',
                name = '',
                org_id = '',
                required = True,
                updated_at = ''
            )
        else:
            return AppAppInput(
        )
        """

    def testAppAppInput(self):
        """Test AppAppInput"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
