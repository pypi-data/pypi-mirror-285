import os
import shutil
import time
from pathlib import Path
from datetime import datetime


class PersistentStorage:
    """ Connect to Persistent Storage """

    def __init__(self, base=None):
        """ Initialize the class
        -----------------------------
        """
        if os.name == 'nt':
            root = os.getcwd()
        else:
            root = '/mnt/datascience-persistent-store-file-share/'

        if base is not None:
            self.base_path = os.path.join(root, base)
        else:
            self.base_path = root

        self.connect()

    def format_path(self, path, sub_path=None):
        if self.base_path in path:
            format_path = path
        else:
            format_path = os.path.join(self.base_path, path)

        if sub_path is not None:
            format_path = os.path.join(format_path, sub_path)

        return format_path

    def if_exists(self, path):
        path = self.format_path(path)
        obj = Path(path)
        status = obj.exists()
        return status

    def connect(self):
        if not self.if_exists(self.base_path):
            raise ValueError("The current project doesn't have access to persistent storage, please check YAML file.")

    def return_base_path(self):
        return self.base_path

    def return_input_path(self, path):
        path = self.format_path(path)
        return path

    def create_folder(self, path):
        created = True
        folder_path = self.format_path(path)
        try:
            Path(folder_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(e)
            created = False

        return created

    def list_folders(self, path):
        folder_path = self.format_path(path)
        try:
            if self.if_exists(folder_path):
                folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
                folders.sort()
            else:
                folders = []
        except Exception as e:
            raise Exception(e)

        return folders

    def create_file(self, data, path, file_name=None):
        created = True
        folder_path = self.format_path(path)
        if file_name is None:
            file_path = os.path.join(folder_path, datetime.now().strftime("%H_%M_%S_%f"))
        else:
            file_path = os.path.join(folder_path, file_name)

        try:
            if type(data) == bytes:
                with open(file_path, 'wb') as f:
                    f.write(data)
                    f.close()
            else:
                with open(file_path, 'w') as f:
                    f.write(data)
                    f.close()
        except Exception as e:
            print(e)
            created = False

        return created

    def list_files(self, path):
        folder_path = self.format_path(path)
        try:
            if self.if_exists(folder_path):
                files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                files.sort()
            else:
                files = []
        except Exception as e:
            raise Exception(e)

        return files

    def move_files(self, source_folder, target_folder, source_files=None, move_all=False):
        source_path = self.format_path(source_folder)
        target_path = self.format_path(target_folder)
        if source_files is None:
            source_files = self.list_files(source_folder)
            all_source_files = source_files
            i = 0
            while len(source_files) > 0 and i <= 5:
                for f in source_files:
                    incoming_file_path = os.path.join(source_path, f)
                    received_file_path = os.path.join(target_path, f)
                    shutil.move(incoming_file_path, received_file_path)

                time.sleep(5)
                source_files = self.list_files(source_folder)
                all_source_files.extend(source_files)
                if not move_all:
                    i += 1

        else:
            all_source_files = source_files
            for f in source_files:
                incoming_file_path = os.path.join(source_path, f)
                received_file_path = os.path.join(target_path, f)
                shutil.move(incoming_file_path, received_file_path)

        target_files = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]
        moved_files = list(set(all_source_files) & set(target_files))
        moved_files.sort()
        return moved_files

    def move_file(self, source_file_path, target_file_path):
        try:
            if self.if_exists(source_file_path) & Path(source_file_path).is_file():
                shutil.move(source_file_path, target_file_path)
            return True
        except Exception as e:
            print(e)
            return False

    def get_create_time(self, path):
        path = self.format_path(path)
        if self.if_exists(path):
            create_time = os.path.getmtime(path)
            return create_time
        else:
            return None

    def delete_folder(self, path):
        folder_path = self.format_path(path)
        delete = True
        try:
            if self.if_exists(folder_path):
                shutil.rmtree(folder_path)
        except Exception as e:
            print(e)
            delete = False

        return delete

    def delete_file(self, path):
        file_path = self.format_path(path)
        delete = True
        try:
            if self.if_exists(file_path) & Path(path).is_file():
                os.remove(file_path)
        except Exception as e:
            print(e)
            delete = False

        return delete
