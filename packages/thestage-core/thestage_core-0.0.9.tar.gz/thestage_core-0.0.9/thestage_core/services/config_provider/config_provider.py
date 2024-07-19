import configparser
import json
import os
from json import JSONDecodeError
from pathlib import Path
from typing import Optional, Dict, Any

from thestage_core.entities.enums.repo_type import RepoType

from thestage_core.config import THESTAGE_CONFIG_DIR, THESTAGE_CONFIG_FILE, THESTAGE_AUTH_TOKEN, THESTAGE_API_URL
from thestage_core.entities.enums.config_type import ConfigType
from thestage_core.services.filesystem_service import FileSystemServiceCore
from thestage_core.entities.config_entity import ConfigEntity, MainConfigEntity
from thestage_core.exceptions.file_system_exception import FileSystemException


class ConfigProviderCore:

    _current_path: Optional[Path] = None
    _local_config_path: Optional[Path] = None
    _local_config_file: Optional[Path] = None
    _global_config_path: Optional[Path] = None
    _global_config_file: Optional[Path] = None
    _config_parser: configparser.ConfigParser
    _file_system_service = FileSystemServiceCore
    _auto_create: bool = True

    def __init__(
            self,
            project_path: Optional[str] = None,
            auto_create: bool = True,
            only_global: bool = False,
    ):
        self._file_system_service = FileSystemServiceCore()
        self._auto_create = auto_create
        if not only_global:
            self._current_path = self._file_system_service.get_path(project_path, self._auto_create)

        self._config_parser = configparser.ConfigParser()
        self._get_config_paths(only_global=only_global)
        self.init_config_files(auto_create=self._auto_create, only_global=only_global)

    def _get_config_paths(self, only_global: bool = False):
        folder_name = self.__get_config_folder_name()
        if not only_global:
            self._local_config_path = self._current_path.joinpath(folder_name)
        else:
            self._local_config_path = None

        home_dir = self._file_system_service.get_home_path()
        self._global_config_path = home_dir.joinpath(folder_name)

    def __get_config_folder_name(self,) -> Path:
        return self._file_system_service.get_path(f"{THESTAGE_CONFIG_DIR}", False)

    def __get_config_file_name(self,) -> Path:
        return self._file_system_service.get_path(f"{THESTAGE_CONFIG_FILE}", False)

    def init_config_files(self, auto_create: bool = True, only_global: bool = False) -> None:
        # create local config
        if not only_global:
            if self._local_config_path and auto_create:
                self._file_system_service.create_if_not_exists(self._local_config_path)

            self._local_config_file = self._local_config_path.joinpath(self.__get_config_file_name())
            if auto_create and (not self._local_config_file or not self._local_config_file.exists()):
                self._file_system_service.create_if_not_exists_file(self._local_config_file)

        # create global config
        if self._global_config_path:
            if not self._global_config_path.exists():
                self._file_system_service.create_if_not_exists(self._global_config_path)

        self._global_config_file = self._global_config_path.joinpath(self.__get_config_file_name())
        if auto_create and (not self._global_config_file or not self._global_config_file.exists()):
            self._file_system_service.create_if_not_exists_file(self._global_config_file)

    @staticmethod
    def _read_data_from_env() -> Optional[Dict[str, Any]]:
        result = {}
        tsr_auth_token = THESTAGE_AUTH_TOKEN
        tsr_config_file_name = THESTAGE_CONFIG_FILE
        tsr_config_local_dir = THESTAGE_CONFIG_DIR
        tsr_config_api_url = THESTAGE_API_URL

        if tsr_auth_token or tsr_config_file_name or tsr_config_local_dir:
            result = {}
            result['main'] = {}
            if tsr_auth_token:
                result['main']['thestage_auth_token'] = tsr_auth_token
            if tsr_config_file_name:
                result['main']['thestage_config_file_name'] = tsr_config_file_name
            if tsr_config_local_dir:
                result['main']['thestage_config_local_dir'] = tsr_config_local_dir
            if tsr_config_api_url:
                result['main']['thestage_api_url'] = tsr_config_api_url

        return result

    def __read_config_file(self, path: Path) -> Dict[str, Any]:
        result = {}
        try:
            if path and path.exists():
                with path.open("r") as file:
                    try:
                        if os.stat(path).st_size != 0:
                            result = json.load(file)
                    except JSONDecodeError:
                        pass
        except OSError:
            raise FileSystemException("Error open local config file")
        return result

    def _read_full_local_config(self,) -> Dict[str, Any]:
        return self.__read_config_file(self._local_config_file)

    def _read_full_global_config(self,) -> Dict[str, Any]:
        return self.__read_config_file(self._global_config_file)

    @staticmethod
    def __update_values_dict(src: Dict, new_values: Dict):
        if 'main' in new_values:
            if 'main' in src:
                src['main'].update(new_values['main'])
            else:
                src['main'] = new_values['main']

    def get_full_config(self, only_global: bool = False) -> ConfigEntity:
        values = {}

        # for now only global
        config_type: ConfigType = ConfigType.GLOBAL

        # read global data
        data = self._read_full_global_config()
        if data:
            self.__update_values_dict(src=values, new_values=data)
            config_type: ConfigType = ConfigType.GLOBAL

        if not only_global:
            # read local data
            data = self._read_full_local_config()
            if data:
                self.__update_values_dict(src=values, new_values=data)
                config_type: ConfigType = ConfigType.LOCAL

        # read end data
        data = self._read_data_from_env()

        if data:
            self.__update_values_dict(src=values, new_values=data)
        #if data:
        #    config_type: ConfigType = ConfigType.ENV

        config = ConfigEntity.model_validate(values)
        if self._current_path:
            config.runtime.working_directory = str(self._current_path)
        config.runtime.config_type = config_type
        if self._local_config_path and not config.main.config_local_path:
            config.main.config_local_path = str(self._local_config_path)
        if self._global_config_path and not config.main.config_global_path:
            config.main.config_global_path = str(self._global_config_path)

        return config

    def create_runtime_config(
            self,
            token: Optional[str] = None,
            repo_url: Optional[str] = None,
            no_dialog: bool = False,
    ) -> ConfigEntity:

        config = self.get_full_config()
        if not (config.main and config.main.auth_token):
            config.main.auth_token = token

        if self._current_path:
            config.runtime.working_directory = str(self._current_path)

        if not config.runtime.config_type:
            config.runtime.config_type = ConfigType.UNKNOWN

        if no_dialog:
            config.runtime.config_type = ConfigType.LOCAL

        if repo_url:
            config.runtime.repo_url = repo_url
            config.runtime.repo_type = RepoType.CLIENT

        return config

    @staticmethod
    def __save_config_file(data: Dict, file_path: Path):
        with open(file_path, 'w') as configfile:
            json.dump(data, configfile, indent=1)

    def save_local_config(self, tmp_config: ConfigEntity):

        data = self._read_full_local_config()
        data.update(tmp_config.model_dump(exclude_none=True, by_alias=True, exclude={'runtime', 'RUNTIME'}))

        self.__save_config_file(data=data, file_path=self._local_config_file)

    def save_global_config(self, tmp_config: ConfigEntity):
        data = self._read_full_global_config()
        data.update(tmp_config.model_dump(exclude_none=True, by_alias=True, exclude={'runtime', 'RUNTIME'}))
        self.__save_config_file(data=data, file_path=self._global_config_file)

    def save_token_to_config(self, config_type: ConfigType, token: str):
        tmp_config = ConfigEntity()
        tmp_config.main = MainConfigEntity(
            thestage_auth_token=token,
        )

        self.save_full_config(config=tmp_config, config_type=config_type)

    def save_full_config(self, config: ConfigEntity, config_type: ConfigType):

        if config_type == ConfigType.LOCAL:
            self.save_local_config(config)
        elif config_type == ConfigType.GLOBAL:
            self.save_global_config(config)

    def remove_all_config(self,):
        self.remove_global_config()
        self.remove_local_config()
        self.remove_config_env()

    def remove_global_config(self,):
        if self._global_config_path and self._global_config_path.exists():
            self._file_system_service.remove_folder(str(self._global_config_path))

    def remove_local_config(self,):
        if self._local_config_path and self._local_config_path.exists():
            self._file_system_service.remove_folder(str(self._local_config_path))

    @staticmethod
    def remove_config_env():
        os.unsetenv('THESTAGE_CONFIG_DIR')
        os.unsetenv('THESTAGE_CONFIG_FILE')
        os.unsetenv('THESTAGE_CLI_ENV')
        os.unsetenv('THESTAGE_API_URL')
        os.unsetenv('THESTAGE_LOG_FILE')
        os.unsetenv('THESTAGE_AUTH_TOKEN')
