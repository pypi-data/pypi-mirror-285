from typing import Optional

from pydantic import BaseModel, Field

from thestage_core.entities.enums.repo_type import RepoType
from thestage_core.entities.enums.config_type import ConfigType
from thestage_core.services.clients.thestage_api.dtos.user_profile import UserProfileResponse


class MainConfigEntity(BaseModel):
    auth_token: Optional[str] = Field(None, alias='thestage_auth_token')
    config_local_path: Optional[str] = Field(None, alias='thestage_config_local_path')
    config_global_path: Optional[str] = Field(None, alias='thestage_config_global_path')
    config_file_name: Optional[str] = Field(None, alias='thestage_config_file_name')
    config_local_dir: Optional[str] = Field(None, alias='thestage_config_local_dir')
    config_api_link: Optional[str] = Field(None, alias='thestage_api_url')


class RuntimeConfigEntity(BaseModel):
    working_directory: Optional[str] = Field(None, alias='working_directory')
    profile: Optional[UserProfileResponse] = Field(None, alias='profile')
    config_type: ConfigType = Field(None, alias='config_type')
    repo_url: Optional[str] = Field(None, alias='thestage_repo_url')
    repo_type: Optional[RepoType] = Field(RepoType.UNKNOWN, alias='thestage_repo_type')


class ConfigEntity(BaseModel):
    main: MainConfigEntity = Field(default_factory=MainConfigEntity, alias='main')
    runtime: RuntimeConfigEntity = Field(default_factory=RuntimeConfigEntity, alias="runtime")
