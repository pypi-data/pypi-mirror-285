# coding: utf-8

"""
    Nuon

    API for managing nuon apps, components, and installs.

    The version of the OpenAPI document: 0.19.187
    Contact: support@nuon.co
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json




from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from nuon.models.app_account import AppAccount
from nuon.models.app_connected_github_vcs_config import AppConnectedGithubVCSConfig
from nuon.models.app_public_git_vcs_config import AppPublicGitVCSConfig
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class AppTerraformModuleComponentConfig(BaseModel):
    """
    AppTerraformModuleComponentConfig
    """ # noqa: E501
    component_config_connection_id: Optional[StrictStr] = Field(default=None, description="parent reference")
    connected_github_vcs_config: Optional[AppConnectedGithubVCSConfig] = None
    created_at: Optional[StrictStr] = None
    created_by: Optional[AppAccount] = None
    created_by_id: Optional[StrictStr] = None
    env_vars: Optional[Dict[str, StrictStr]] = None
    id: Optional[StrictStr] = None
    public_git_vcs_config: Optional[AppPublicGitVCSConfig] = None
    updated_at: Optional[StrictStr] = None
    variables: Optional[Dict[str, StrictStr]] = None
    version: Optional[StrictStr] = Field(default=None, description="terraform configuration values")
    __properties: ClassVar[List[str]] = ["component_config_connection_id", "connected_github_vcs_config", "created_at", "created_by", "created_by_id", "env_vars", "id", "public_git_vcs_config", "updated_at", "variables", "version"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of AppTerraformModuleComponentConfig from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={
            },
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of connected_github_vcs_config
        if self.connected_github_vcs_config:
            _dict['connected_github_vcs_config'] = self.connected_github_vcs_config.to_dict()
        # override the default output from pydantic by calling `to_dict()` of created_by
        if self.created_by:
            _dict['created_by'] = self.created_by.to_dict()
        # override the default output from pydantic by calling `to_dict()` of public_git_vcs_config
        if self.public_git_vcs_config:
            _dict['public_git_vcs_config'] = self.public_git_vcs_config.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of AppTerraformModuleComponentConfig from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "component_config_connection_id": obj.get("component_config_connection_id"),
            "connected_github_vcs_config": AppConnectedGithubVCSConfig.from_dict(obj.get("connected_github_vcs_config")) if obj.get("connected_github_vcs_config") is not None else None,
            "created_at": obj.get("created_at"),
            "created_by": AppAccount.from_dict(obj.get("created_by")) if obj.get("created_by") is not None else None,
            "created_by_id": obj.get("created_by_id"),
            "env_vars": obj.get("env_vars"),
            "id": obj.get("id"),
            "public_git_vcs_config": AppPublicGitVCSConfig.from_dict(obj.get("public_git_vcs_config")) if obj.get("public_git_vcs_config") is not None else None,
            "updated_at": obj.get("updated_at"),
            "variables": obj.get("variables"),
            "version": obj.get("version")
        })
        return _obj


