import os
import stat
import uuid
from pathlib import Path
from time import sleep
from typing import Optional, List, Dict, Tuple

import paramiko
import typer
from paramiko.client import SSHClient
from paramiko.config import SSHConfig
from paramiko.hostkeys import HostKeys
from paramiko.sftp_attr import SFTPAttributes
from paramiko.sftp_client import SFTPClient
from thestage_core.entities.file_item import FileItemEntity
from thestage_core.services.filesystem_service import FileSystemServiceCore

from thestage.exceptions.remote_server_exception import RemoteServerException
from thestage.helpers.logger.app_logger import app_logger
from thestage.entities.enums.shell_type import ShellType
from thestage.i18n.translation import __
from thestage.services.clients.thestage_api.dtos.sftp_path_helper import SftpPathHelper

old_value: int = 0


class RemoteServerService(object):

    def __init__(
            self,
            file_system_service: FileSystemServiceCore,
    ):
        self.__file_system_service = file_system_service

    def __get_client(
            self,
            ip_address: str,
            username: str,
    ) -> Optional[SSHClient]:
        config_by_ip = None
        ssh_path = self.__file_system_service.get_ssh_path()
        ssh_config_path = ssh_path.joinpath('config')
        #ssh_config_path = Path('~/.ssh/config')
        config_path = ssh_config_path.expanduser()
        if config_path.exists():
            config = SSHConfig.from_path(config_path)
            config_by_ip = config.lookup(ip_address)
        client = SSHClient()
        try:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if config_by_ip:
                key_file_name = config_by_ip['identityfile'][0] if config_by_ip and 'identityfile' in config_by_ip and len(config_by_ip['identityfile']) > 0 else None
                client.connect(
                    hostname=ip_address,
                    username=username,
                    timeout=60,
                    allow_agent=False if key_file_name else True,
                    look_for_keys=False if key_file_name else True,
                    key_filename=key_file_name.replace('.pub', '') if key_file_name else None,
                )
            else:
                client.connect(
                    hostname=ip_address,
                    username=username,
                    timeout=60,
                )
            return client

        except Exception as ex:
            if client:
                client.close()
                typer.echo(f"Error connect to {ip_address} by {username} ({ex})")
            app_logger.error(f"Error connect to {ip_address} by {username} ({ex})")
            raise RemoteServerException(
                message=__("Error connect to remote server"),
                ip_address=ip_address,
                username=username,
            )

    @staticmethod
    def is_shell_present(
            lines: List[str],
    ) -> Optional[ShellType]:
        bash_present, sh_present = False, False
        for line in lines:
            if 'bin/bash' in line:
                bash_present = True
                break
            elif 'bin/sh' in line:
                sh_present = True

        if bash_present:
            return ShellType.BASH
        if sh_present:
            return ShellType.SH
        else:
            return None

    def get_shell_from_container(
            self,
            ip_address: str,
            username: str,
            docker_name: str,
    ) -> Optional[ShellType]:
        client: Optional[SSHClient] = self.__get_client(ip_address=ip_address, username=username)
        stdin, stdout, stderr = client.exec_command(f'docker exec -it {docker_name} cat /etc/shells', get_pty=True)
        shell = self.is_shell_present(lines=stdout.readlines())
        client.close()

        return shell

    def check_if_host_in_list_known(self, ip_address: str) -> bool:
        try:
            #os.system(f"ssh-keygen -F 34.198.189.175")
            ssh_path = self.__file_system_service.get_ssh_path()
            known_host_path = ssh_path.joinpath('known_hosts')
            if known_host_path.exists():
                host_keys = HostKeys(filename=str(known_host_path.absolute()))
                result = host_keys.lookup(ip_address)
                if result is not None:
                    return True
                else:
                    return False
        except Exception as ex:
            raise FileNotFoundError(f"Error read ssh known host file: {ex}")
        return False

    def connect_to_instance(
            self,
            ip_address: str,
            username: str,
    ):
        try:
            os.system(f"ssh {username}@{ip_address}")
        except Exception as ex:
            app_logger.error(f"Error connect to {ip_address} by {username} ({ex})")
            raise RemoteServerException(
                message=__("Error connect to remote server"),
                ip_address=ip_address,
                username=username,
            )

    def connect_to_container(
            self,
            ip_address: str,
            username: str,
            docker_name: str,
            shell: ShellType
    ):
        try:
            os.system(f"ssh -tt {username}@{ip_address} 'docker exec -it {docker_name} {shell.value}'")
        except Exception as ex:
            app_logger.exception(f"Error connect to {ip_address} by {username} ({ex})")
            raise RemoteServerException(
                message=__("Error connect to remote server"),
                ip_address=ip_address,
                username=username,
            )

    @staticmethod
    def find_path_mapping(
            directory_mapping: Dict[str, str],
            destination_path: Optional[str] = None,
    ) -> Optional[str]:

        template = destination_path if destination_path else '/public'

        if not directory_mapping:
            typer.echo(__("Can not find mapping folders"))
            raise typer.Exit(1)

        for key, value in directory_mapping.items():
            if value == template:
                return key
        return None

    @staticmethod
    def check_path_mapping(
            directory_mapping: Dict[str, str],
            path: Optional[str],
            is_upload: bool = True,
            is_folder: bool = False,
    ) -> Optional[SftpPathHelper]:
        if not directory_mapping:
            typer.echo(__("Can not find mapping folders"))
            raise typer.Exit(1)

        public_src, public_desc = None, None

        for key, value in directory_mapping.items():
            #template = value if is_upload else key
            template = value

            if value == '/public':
                #public_src = key if is_upload else value
                #public_desc = value if is_upload else key
                public_src = value
                public_desc = key

            if template in path:
                path_list = path.split('/')
                return SftpPathHelper(
                    tmp_container_path='/'.join(path_list[0:-1]),
                    tmp_instance_path='/'.join(path.replace(template, key).split('/')[0:-1]),
                    item_name=path_list[-1],
                )

        if public_src == None:
            typer.echo(__("Can't found public folder"))
            raise typer.Exit(1)

        tmp_folder = f"{uuid.uuid4()}"
        path_list = path.split('/')
        last = path_list[-1]

        return SftpPathHelper(
            tmp_container_path=f"{public_src}/{tmp_folder}",
            tmp_instance_path=f"{public_desc}/{tmp_folder}",
            tmp_folder_path=f"{public_src}/{tmp_folder}",
            item_name=last,
        )

    def __upload_one_file(
            self,
            sftp: SFTPClient,
            src_path: str,
            dest_path: str,
            file_name: str,
            file_size: [int] = 100
    ) -> bool:
        has_error = False
        try:
            with typer.progressbar(length=file_size, label=__("Copy %file_name%", {'file_name': file_name})) as progress:
                def __show_result_copy(size: int, full_size: int):
                    global old_value
                    progress.update(size - (old_value or 0))
                    old_value = size
                sftp.put(localpath=src_path, remotepath=f"{dest_path}", callback=__show_result_copy)
            typer.echo(__('Complete copy %file_name%', {'file_name': file_name}))
        except FileNotFoundError as err:
            app_logger.exception(f"Error put file {file_name} to container (file ot found): {err}")
            typer.echo(__("Error put file, file not found on server"))
            has_error = True
        except Exception as err2:
            typer.echo(err2)
            app_logger.exception(f"Error put file {file_name} to container: {err2}")
            typer.echo(__("Error put file, undefined server error"))
            has_error = True

        return has_error

    def __make_dirs_by_sftp(
            self,
            sftp: SFTPClient,
            path: str,
    ):
        full_path = ''
        for item in path.split('/'):
            if item == '':
                continue
            try:
                full_path += f'/{item}'
                sftp.chdir(full_path)  # Test if remote_path exists
            except IOError:
                sftp.mkdir(full_path)  # Create remote_path
                sftp.chdir(full_path)

    def __upload_list_files(
            self,
            sftp: SFTPClient,
            src_item: FileItemEntity,
            dest_path: str,
    ):
        if src_item.is_file:
            # need create folder if use dynamic folder
            paths = dest_path.split('/')
            new_name_file = paths[-1]
            real_dest_path = '/'.join(paths[0:-1])
            self.__make_dirs_by_sftp(sftp=sftp, path=real_dest_path)

            self.__upload_one_file(
                sftp=sftp,
                src_path=src_item.path,
                dest_path=dest_path,
                file_name=new_name_file,
                file_size=src_item.file_size,
            )
        elif src_item.is_folder:
            self.__make_dirs_by_sftp(sftp=sftp, path=dest_path)
            #server_dir = f"{dest_path}/{src_item.name}"
            #self.__make_dirs_by_sftp(sftp=sftp, path=server_dir)

            for item in src_item.children:
                self.__upload_list_files(
                    sftp=sftp,
                    src_item=item,
                    dest_path=f"{dest_path}/{item.name}",
                )

    def __download_one_file(
            self,
            sftp: SFTPClient,
            src_path: str,
            dest_path: str,
            file_name: str,
            file_size: [int] = 100
    ) -> bool:
        has_error = False
        try:
            with typer.progressbar(length=file_size, label=__("Copy %file_name%", {'file_name': file_name})) as progress:
                def __show_result_copy(size: int, full_size: int):
                    global old_value
                    progress.update(size - (old_value or 0))
                    old_value = size
                sftp.get(remotepath=src_path, localpath=f"{dest_path}", callback=__show_result_copy)
            typer.echo(__('Complete copy %file_name%', {'file_name': file_name}))
        except FileNotFoundError as err:
            app_logger.exception(f"Error get file {file_name} from container (file ot found): {err}")
            typer.echo(__("Error get file, file not found on server"))
            has_error = True
        except Exception as err2:
            typer.echo(err2)
            app_logger.exception(f"Error get file {file_name} from container: {err2}")
            typer.echo(__("Error get file, undefined server error"))
            has_error = True

        return has_error

    def __download_list_files(
            self,
            sftp: SFTPClient,
            src_item: FileItemEntity,
            dest_path: str,
    ):
        if src_item.is_file:
            self.__file_system_service.get_path('/'.join(dest_path.split('/')[0:-1]), auto_create=True)
            self.__download_one_file(
                sftp=sftp,
                src_path=src_item.path,
                dest_path=dest_path,
                file_name=src_item.name,
                file_size=src_item.file_size,
            )
        elif src_item.is_folder:
            server_dir = self.__file_system_service.get_path(str(Path(dest_path).joinpath(src_item.name)), auto_create=True)
            for item in src_item.children:
                self.__download_list_files(
                    sftp=sftp,
                    src_item=item,
                    dest_path=str(server_dir.joinpath(item.name)) if item.is_file else str(server_dir),
                )

    @staticmethod
    def find_sftp_server_path(
            client: SSHClient,
    ) -> Optional[str]:
        stdin, stdout, stderr = client.exec_command(f'whereis sftp-server', get_pty=True)
        for line in stdout.readlines():
            pre_line = line.replace('sftp-server:', '')
            for command in pre_line.strip().split(' '):
                tmp = command.strip()
                if tmp:
                    if tmp.endswith('/sftp-server'):
                        return tmp
        return None

    def copy_data_on_container(
            self,
            client: SSHClient,
            docker_name: str,
            src_path: str,
            dest_path: str,
            is_recursive: bool = False,
    ):
        self.start_command_on_container(
            client=client,
            docker_name=docker_name,
            command='cp ' + ('-R' if is_recursive else '') + f' {src_path}' + f' {dest_path}',
        )
        # TODO: dont now how, need check for copy end!!!!
        sleep(3)

    @staticmethod
    def start_command_on_container(
            client: SSHClient,
            docker_name: str,
            command: str,
    ):
        stdin, stdout, stderr = client.exec_command(f'docker exec -it {docker_name} {command}', get_pty=True)
        for line in stdout.readlines():
            pass

    def upload_data_to_container(
            self,
            ip_address: str,
            username: str,
            docker_name: str,
            src_path: str,
            dest_path: str,
            path_helper: SftpPathHelper,
            is_folder: bool = False,
    ):
        has_error = False
        client: Optional[SSHClient] = self.__get_client(ip_address=ip_address, username=username)
        sftp_server_path = self.find_sftp_server_path(client=client)

        if not sftp_server_path:
            typer.echo(__('No sftp server is installed on your instance'))
            raise typer.Exit(1)

        chan = client.get_transport().open_session()
        #chan.exec_command("sudo su -c /usr/lib/openssh/sftp-server")
        chan.exec_command(f"sudo su -c {sftp_server_path}")
        sftp = paramiko.SFTPClient(chan)

        try:
            files: List[FileItemEntity] = self.__file_system_service.get_path_items(src_path)
            for item in files:
                self.__upload_list_files(
                    sftp=sftp,
                    src_item=item,
                    dest_path=path_helper.tmp_instance_path_with_name(),
                )

            if path_helper.tmp_folder_path:
                # copy to dest_path
                self.start_command_on_container(
                    client=client,
                    docker_name=docker_name,
                    command='cp ' + ('-R' if is_folder else '') + f' {path_helper.tmp_container_path_with_name()}' + f' {dest_path}',
                )

        except FileNotFoundError as err:
            app_logger.error(f"Error put file to container {ip_address}, {username} (file ot found): {err}")
            typer.echo(__("Error put file, file not found on server"))
            has_error = True
        finally:
            if path_helper.tmp_folder_path:
                self.start_command_on_container(
                    client=client,
                    docker_name=docker_name,
                    command='rm -R ' + f'{path_helper.tmp_folder_path}',
                )
            sftp.close()

        client.close()
        if has_error:
            typer.Exit(1)

    def __read_remote_path_items(self, sftp: SFTPClient, folder: str) -> List[FileItemEntity]:
        path_items = []
        root_stat = sftp.stat(folder)
        parent = FileItemEntity(
            name=folder.split('/')[-1],
            path=folder,
            is_file=stat.S_ISREG(root_stat.st_mode),
            is_folder=stat.S_ISDIR(root_stat.st_mode),
            file_size=root_stat.st_size,
        )
        path_items.append(parent)
        if parent.is_folder:
            sftp.chdir(folder)
            for item in sftp.listdir_attr():
                next_path = f'{folder}/{item.filename}'
                is_dir = stat.S_ISDIR(item.st_mode)
                is_file = stat.S_ISREG(item.st_mode)
                if is_file:
                    parent.children.append(FileItemEntity(
                        name=item.filename,
                        path=next_path,
                        is_file=is_file,
                        is_folder=is_dir,
                        file_size=item.st_size,
                    ))
                elif is_dir:
                    parent.children.extend(self.__read_remote_path_items(
                        sftp=sftp,
                        folder=next_path,
                    ))
        return path_items

    def download_data_to_container(
            self,
            ip_address: str,
            username: str,
            docker_name: str,
            src_path: str,
            dest_path: str,
            path_helper: SftpPathHelper,
            is_folder: bool = False,
    ):
        has_error = False
        client: Optional[SSHClient] = self.__get_client(ip_address=ip_address, username=username)

        sftp_server_path = self.find_sftp_server_path(client=client)

        if not sftp_server_path:
            typer.echo(__('No sftp server is installed on your instance'))
            raise typer.Exit(1)

        chan = client.get_transport().open_session()
        #chan.exec_command("sudo su -c /usr/lib/openssh/sftp-server")
        chan.exec_command(f"sudo su -c {sftp_server_path}")
        sftp = paramiko.SFTPClient(chan)

        try:
            if path_helper.tmp_folder_path:
                self.__make_dirs_by_sftp(sftp=sftp, path=path_helper.tmp_instance_path)
                self.copy_data_on_container(
                    client=client,
                    docker_name=docker_name,
                    is_recursive=is_folder,
                    src_path=src_path,
                    dest_path=path_helper.tmp_container_path if is_folder else path_helper.tmp_container_path_with_name(),
                )

            files: List[FileItemEntity] = self.__read_remote_path_items(
                sftp=sftp,
                folder=path_helper.tmp_instance_path_with_name(),
            )

            for item in files:
                self.__download_list_files(
                    sftp=sftp,
                    src_item=item,
                    dest_path=dest_path,
                )
        except FileNotFoundError as err:
            print(err)
            app_logger.error(f"Error put file to container {ip_address}, {username} (file ot found): {err}")
            typer.echo(__("Error put file, file not found on server"))
            has_error = True
        finally:
            if path_helper.tmp_folder_path:
                # remove temporary path
                self.start_command_on_container(
                    client=client,
                    docker_name=docker_name,
                    command='rm -R ' + f'{path_helper.tmp_folder_path}',
                )
            sftp.close()

        client.close()
        if has_error:
            typer.Exit(1)
