import datetime
from pathlib import Path
from typing import Optional, List, Tuple

import git
import typer
from git import Remote, Repo, GitCommandError, Commit, Head, RemoteReference
from thestage_core.services.filesystem_service import FileSystemServiceCore

from thestage.exceptions.git_access_exception import GitAccessException


class GitLocalClient:
    __base_name_remote: str = 'origin'
    __base_name_local: str = 'main'
    __git_ignore_tsr_line: str = '/.thestage/'

    __special_main_branches = ['main', 'master']

    __base_git_url: str = 'https://github.com/'

    def __init__(
            self,
            file_system_service: FileSystemServiceCore,
    ):
        self.__file_system_service = file_system_service

    def __get_repo(self, path: str) -> Repo:
        return git.Repo(path)

    def is_present_local_git(self, path: str) -> bool:
        git_path = self.__file_system_service.get_path(path)
        if not git_path.exists():
            return False

        git_path = git_path.joinpath('.git')
        if not git_path.exists():
            return False

        result = git.repo.base.is_git_dir(git_path)
        return result

    def get_remote(self, path: str) -> Optional[List[Remote]]:
        is_git_repo = self.is_present_local_git(path=path)
        if is_git_repo:
            repo = git.Repo(path)
            remotes: Optional[List[Remote]] = list(repo.remotes) if repo.remotes else []
            return remotes
        return None

    def has_remote(self, path: str) -> bool:
        remotes: Optional[List[Remote]] = self.get_remote(path)
        return True if remotes is not None and len(remotes) > 0 else False

    def has_changes(self, path: str) -> bool:
        repo = self.__get_repo(path=path)
        is_dirty = repo.is_dirty()
        if is_dirty:
            return True
        return False

    def init_repository(
            self,
            path: str,
    ) -> Optional[Repo]:

        repo = git.Repo.init(path)
        if repo:
            # default git name master, rename to main - sync wih github
            repo.git.branch("-M", self.__base_name_local)
        return repo

    def add_remote_to_repo(
            self,
            path: str,
            remote_url: str,
            remote_name: str,
    ) -> bool:
        repo = self.__get_repo(path=path)
        remotes: List[Remote] = repo.remotes
        not_present = True
        if remotes:
            item = list(filter(lambda x: x.name == remote_name, remotes))
            if len(item) > 0:
                not_present = False

        if not_present:
            remote: Remote = repo.create_remote(
                name=self.__base_name_remote,
                url=remote_url,
            )
            if remote:
                return True
            else:
                return False
        else:
            return True

    def git_fetch(self, path: str):
        repo = self.__get_repo(path=path)
        if repo:
            remote: Remote = repo.remote(self.__base_name_remote)
            if remote:
                try:
                    remote.fetch()
                except GitCommandError as base_ex:
                    msg = base_ex.stderr
                    if msg and 'fatal: Could not read from remote repository' in msg:
                        raise GitAccessException(
                            message='You dont have access to repository, or repository not found.',
                            url=self.build_http_repo_url(git_path=remote.url),
                            dop_message=msg,
                        )
                    else:
                        raise base_ex

    def git_pull(self, path: str, branch: Optional[str] = None):
        repo = self.__get_repo(path=path)
        if repo:
            local_branch = self.__base_name_local
            if branch:
                if self.__base_name_remote in branch:
                    local_branch = branch.replace(f"{self.__base_name_remote}/", '').strip()
                else:
                    local_branch = branch

            repo.git.pull(self.__base_name_remote, local_branch)

    def find_main_branches(self, path: str) -> Tuple[Optional[str], bool]:
        repo = self.__get_repo(path=path)
        if repo:
            for ref in repo.git.branch('-a').split('\n'):
                for main_branch in self.__special_main_branches:
                    if main_branch in ref.split('/'):
                        if 'remotes/' in ref:
                            return ref.replace('remotes/', '').strip(), True
                        else:
                            return ref.strip(), False

        return None, False

    def git_checkout(self, path: str, branch: Optional[str] = None):
        repo = self.__get_repo(path=path)
        if repo:
            branch_name = repo.active_branch.name if repo.active_branch else self.__base_name_local
            if branch:
                branch_name = branch

            repo.git.checkout('-b', branch_name.strip())

    def add_new_branch(self, path: str, new_branch_name: Optional[str] = None,) -> Optional[Head]:
        # TODO: check and changes on future, fucking branches
        repo = self.__get_repo(path=path)
        if repo:
            branch = self.find_main_branches(path=path)
            if branch:
                return branch
            else:
                branch_name = new_branch_name if new_branch_name else self.__base_name_local

            origin = repo.remote(self.__base_name_remote)
            if origin:
                repo.create_head(self.__base_name_local, origin.refs.main)  # create local branch "master" from remote "master"
                repo.heads.main.set_tracking_branch(origin.refs.main)  # set local "master" to track remote "master
                repo.heads.master.checkout()

            #if new_branch_name:
                branch = repo.create_head(branch_name)
            #else:
                # if we want added special branch - main - first branch
                #origin = repo.remote(self.__base_name_remote)
            #    repo.head.reference = repo.create_head(branch_name)
                # Create new remote ref and set it to track.
            #    rem_ref = RemoteReference(repo, f"refs/remotes/{self.__base_name_remote}/{branch_name}")
            #    repo.head.reference.set_tracking_branch(rem_ref)

            return branch
        return None

    def build_http_repo_url(self, git_path: str) -> str:
        start_path_pos = git_path.find(":")
        pre_url = git_path[start_path_pos+1:]
        url = pre_url.replace('.git', '')
        return self.__base_git_url + url

    def clone(self, url: str, path: str, ) -> Optional[Repo]:
        try:
            return git.Repo.clone_from(url=url, to_path=path)
        except GitCommandError as base_ex:
            msg = base_ex.stderr
            if msg and 'Repository not found' in msg and 'correct access rights' in msg:
                raise GitAccessException(
                    message='You dont have access to repository, or repository not found.',
                    url=self.build_http_repo_url(git_path=url),
                    dop_message=msg,
                )
            else:
                raise base_ex

    def commit_local_changes(
            self,
            path: str,
            with_push: bool = False,
            author: Optional[str] = None,
            name: Optional[str] = None,
    ) -> Optional[str]:
        repo = self.__get_repo(path=path)
        commit_name = name if name else f"Auto commit {str(datetime.datetime.now().date())}"
        commit = repo.git.commit('--all', '--allow-empty', '-m', commit_name, )
        if with_push:
            self.push_changes(path=path, branch_name=repo.active_branch.name)
        return commit

    def push_changes(
            self,
            path: str,
            branch_name: str,
    ):
        repo = self.__get_repo(path=path)
        origin = repo.remote(self.__base_name_remote)
        if origin:
            repo.git.push('-u', origin.name, branch_name)

    def get_latest_commit(self, path: str, ) -> Optional[Commit]:
        repo = self.__get_repo(path=path)
        if repo:
            return repo.head.commit
        else:
            return None

    def _get_gitignore_path(self, path: str) -> Path:
        git_path = self.__file_system_service.get_path(path)
        return git_path.joinpath('.gitignore')

    def git_add_by_path(self, repo_path: str, file_path: str):
        repo = self.__get_repo(path=repo_path)
        if repo:
            repo.index.add(items=[file_path])

    def add_to_gitignore(self, path: str):

        gitignore_path = self._get_gitignore_path(path=path)
        if not gitignore_path.exists():
            self.__file_system_service.create_if_not_exists_file(gitignore_path)
            self.git_add_by_path(repo_path=path, file_path=str(gitignore_path))

        is_present_tsr = self.__file_system_service.find_in_text_file(file=str(gitignore_path),
                                                                      find=self.__git_ignore_tsr_line)
        if not is_present_tsr:
            self.__file_system_service.add_line_to_text_file(file=str(gitignore_path),
                                                             new_line=self.__git_ignore_tsr_line)
