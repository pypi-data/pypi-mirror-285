import os
import shutil
from pathlib import Path
from typing import Dict, Optional, List


from thestage_core.entities.file_item import FileItemEntity
from thestage_core.exceptions.file_system_exception import FileSystemException


class FileSystemServiceCore:

    def get_ssh_path(self) -> Optional[Path]:
        home_path = self.get_home_path()
        ssh_path = home_path.joinpath('.ssh')
        if not ssh_path.exists():
            raise FileSystemException("Not found .ssh conf path, you can't connect to remote host")
        return ssh_path

    def get_home_path(self) -> Optional[Path]:
        try:
            return Path.home()
        except RuntimeError | OSError:
            raise FileSystemException("Error read home user folder")

    def create_if_not_exists(self, path: Path) -> Path:
        if not path.exists():
            try:
                path.mkdir(exist_ok=True, parents=True)
            except FileNotFoundError as ex1:
                raise FileSystemException(message="Not found this path")
            except OSError as ex2:
                raise FileSystemException(message="We can not make dir")
        return path

    def create_if_not_exists_file(self, path: Path) -> Path:
        if not path.exists():
            try:
                path.touch(exist_ok=True)
            except FileNotFoundError as ex1:
                raise FileSystemException(message="Not found this path")
            except OSError as ex2:
                raise FileSystemException(message="We can not make file")
        return path

    def get_path(self, directory: str, auto_create: bool = True) -> Path:
        path = Path(directory)
        if auto_create:
            self.create_if_not_exists(path)
        return path

    def __is_folder(self, path: Path, with_exception: bool = True) -> bool:
        if not path.is_dir():
            if with_exception:
                raise FileSystemException(message="Please set up working directory as folder not file")
            else:
                return False
        return True

    def is_folder(self, folder: str, auto_create: bool = True, with_exception: bool = True) -> bool:
        path = self.get_path(folder, auto_create)
        return self.__is_folder(path=path, with_exception=with_exception)

    def is_folder_empty(self, folder: str, auto_create: bool = True) -> bool:
        path = self.get_path(folder, auto_create)
        if not path.exists():
            return True
        self.__is_folder(path)
        objects = os.listdir(path)
        if len(objects) == 0:
            return True
        else:
            return False

    def print_folder_items(self, folder: str) -> List[str]:
        path = self.get_path(folder)
        result = []
        if not path.exists():
            return result
        self.__is_folder(path)
        objects = os.listdir(path)

        if objects:
            for item in objects:
                result.append(item)
        return result

    def is_folder_exists(self, folder: str, auto_create: bool = True) -> bool:
        path = self.get_path(folder, auto_create=auto_create)
        if path.exists():
            return True
        else:
            return False

    def find_in_text_file(self, file: str, find: str) -> bool:
        path = self.get_path(file, auto_create=False)
        if path and path.exists():
            with open(path, 'r') as file:
                for line in file.readlines():
                    if find in line:
                        return True
        return False

    def add_line_to_text_file(self, file: str, new_line: str):
        path = self.get_path(file, auto_create=False)
        if path and path.exists():
            with open(path, 'a') as file:
                file.write(new_line)
                file.write('\n')

    def check_if_path_exist(self, file: str) -> bool:
        path = self.get_path(file, auto_create=False)
        if path.exists():
            return True
        else:
            return False

    def get_path_items(self, folder: str) -> List[FileItemEntity]:
        path = self.get_path(folder, auto_create=False)
        path_items = []
        if not path.exists():
            return path_items

        parent = FileItemEntity.build_from_path(path=path)
        path_items.append(parent)
        if path.is_dir():
            objects = os.listdir(path)
            if objects:
                for item in objects:
                    elem = path.joinpath(item)
                    if elem.is_dir():
                        parent.children.extend(self.get_path_items(folder=str(elem)))
                    else:
                        parent.children.append(FileItemEntity.build_from_path(path=elem))
        return path_items

    def remove_folder(self, path: str):
        real_path = self.get_path(directory=path, auto_create=False)
        if real_path and real_path.exists():
            shutil.rmtree(real_path)
