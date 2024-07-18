# Copyright (c) Alibaba, Inc. and its affiliates.

import fnmatch
import os
import re
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Dict, List, Optional, Union

from modelscope.hub.api import HubApi, ModelScopeConfig
from modelscope.hub.errors import InvalidParameter
from modelscope.hub.utils.utils import model_id_to_group_owner_name
from modelscope.utils.constant import (DEFAULT_DATASET_REVISION,
                                       DEFAULT_MODEL_REVISION,
                                       REPO_TYPE_DATASET, REPO_TYPE_MODEL,
                                       REPO_TYPE_SUPPORT)
from modelscope.utils.logger import get_logger
from .file_download import (create_temporary_directory_and_cache,
                            download_file, get_file_download_url)

logger = get_logger()


def snapshot_download(
    model_id: str,
    revision: Optional[str] = DEFAULT_MODEL_REVISION,
    cache_dir: Union[str, Path, None] = None,
    user_agent: Optional[Union[Dict, str]] = None,
    local_files_only: Optional[bool] = False,
    cookies: Optional[CookieJar] = None,
    ignore_file_pattern: Optional[Union[str, List[str]]] = None,
    allow_file_pattern: Optional[Union[str, List[str]]] = None,
    local_dir: Optional[str] = None,
) -> str:
    """Download all files of a repo.
    Downloads a whole snapshot of a repo's files at the specified revision. This
    is useful when you want all files from a repo, because you don't know which
    ones you will need a priori. All files are nested inside a folder in order
    to keep their actual filename relative to that folder.

    An alternative would be to just clone a repo but this would require that the
    user always has git and git-lfs installed, and properly configured.

    Args:
        model_id (str): A user or an organization name and a repo name separated by a `/`.
        revision (str, optional): An optional Git revision id which can be a branch name, a tag, or a
            commit hash. NOTE: currently only branch and tag name is supported
        cache_dir (str, Path, optional): Path to the folder where cached files are stored, model will
            be save as cache_dir/model_id/THE_MODEL_FILES.
        user_agent (str, dict, optional): The user-agent info in the form of a dictionary or a string.
        local_files_only (bool, optional): If `True`, avoid downloading the file and return the path to the
            local cached file if it exists.
        cookies (CookieJar, optional): The cookie of the request, default None.
        ignore_file_pattern (`str` or `List`, *optional*, default to `None`):
            Any file pattern to be ignored in downloading, like exact file names or file extensions.
        allow_file_pattern (`str` or `List`, *optional*, default to `None`):
            Any file pattern to be downloading, like exact file names or file extensions.
        local_dir (str, optional): Specific local directory path to which the file will be downloaded.
    Raises:
        ValueError: the value details.

    Returns:
        str: Local folder path (string) of repo snapshot

    Note:
        Raises the following errors:
        - [`EnvironmentError`](https://docs.python.org/3/library/exceptions.html#EnvironmentError)
        if `use_auth_token=True` and the token cannot be found.
        - [`OSError`](https://docs.python.org/3/library/exceptions.html#OSError) if
        ETag cannot be determined.
        - [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError)
        if some parameter value is invalid
    """
    return _snapshot_download(
        model_id,
        repo_type=REPO_TYPE_MODEL,
        revision=revision,
        cache_dir=cache_dir,
        user_agent=user_agent,
        local_files_only=local_files_only,
        cookies=cookies,
        ignore_file_pattern=ignore_file_pattern,
        allow_file_pattern=allow_file_pattern,
        local_dir=local_dir)


def dataset_snapshot_download(
    dataset_id: str,
    revision: Optional[str] = DEFAULT_DATASET_REVISION,
    cache_dir: Union[str, Path, None] = None,
    local_dir: Optional[str] = None,
    user_agent: Optional[Union[Dict, str]] = None,
    local_files_only: Optional[bool] = False,
    cookies: Optional[CookieJar] = None,
    ignore_file_pattern: Optional[Union[str, List[str]]] = None,
    allow_file_pattern: Optional[Union[str, List[str]]] = None,
) -> str:
    """Download raw files of a dataset.
    Downloads all files at the specified revision. This
    is useful when you want all files from a dataset, because you don't know which
    ones you will need a priori. All files are nested inside a folder in order
    to keep their actual filename relative to that folder.

    An alternative would be to just clone a dataset but this would require that the
    user always has git and git-lfs installed, and properly configured.

    Args:
        dataset_id (str): A user or an organization name and a dataset name separated by a `/`.
        revision (str, optional): An optional Git revision id which can be a branch name, a tag, or a
            commit hash. NOTE: currently only branch and tag name is supported
        cache_dir (str, Path, optional): Path to the folder where cached files are stored, dataset will
            be save as cache_dir/dataset_id/THE_DATASET_FILES.
        local_dir (str, optional): Specific local directory path to which the file will be downloaded.
        user_agent (str, dict, optional): The user-agent info in the form of a dictionary or a string.
        local_files_only (bool, optional): If `True`, avoid downloading the file and return the path to the
            local cached file if it exists.
        cookies (CookieJar, optional): The cookie of the request, default None.
        ignore_file_pattern (`str` or `List`, *optional*, default to `None`):
            Any file pattern to be ignored in downloading, like exact file names or file extensions.
            Use regression is deprecated.
        allow_file_pattern (`str` or `List`, *optional*, default to `None`):
            Any file pattern to be downloading, like exact file names or file extensions.
    Raises:
        ValueError: the value details.

    Returns:
        str: Local folder path (string) of repo snapshot

    Note:
        Raises the following errors:
        - [`EnvironmentError`](https://docs.python.org/3/library/exceptions.html#EnvironmentError)
        if `use_auth_token=True` and the token cannot be found.
        - [`OSError`](https://docs.python.org/3/library/exceptions.html#OSError) if
        ETag cannot be determined.
        - [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError)
        if some parameter value is invalid
    """
    return _snapshot_download(
        dataset_id,
        repo_type=REPO_TYPE_DATASET,
        revision=revision,
        cache_dir=cache_dir,
        user_agent=user_agent,
        local_files_only=local_files_only,
        cookies=cookies,
        ignore_file_pattern=ignore_file_pattern,
        allow_file_pattern=allow_file_pattern,
        local_dir=local_dir)


def _snapshot_download(
    repo_id: str,
    *,
    repo_type: Optional[str] = None,
    revision: Optional[str] = DEFAULT_MODEL_REVISION,
    cache_dir: Union[str, Path, None] = None,
    user_agent: Optional[Union[Dict, str]] = None,
    local_files_only: Optional[bool] = False,
    cookies: Optional[CookieJar] = None,
    ignore_file_pattern: Optional[Union[str, List[str]]] = None,
    allow_file_pattern: Optional[Union[str, List[str]]] = None,
    local_dir: Optional[str] = None,
):
    if not repo_type:
        repo_type = REPO_TYPE_MODEL
    if repo_type not in REPO_TYPE_SUPPORT:
        raise InvalidParameter('Invalid repo type: %s, only support: %s' (
            repo_type, REPO_TYPE_SUPPORT))

    temporary_cache_dir, cache = create_temporary_directory_and_cache(
        repo_id, local_dir=local_dir, cache_dir=cache_dir, repo_type=repo_type)

    if local_files_only:
        if len(cache.cached_files) == 0:
            raise ValueError(
                'Cannot find the requested files in the cached path and outgoing'
                ' traffic has been disabled. To enable look-ups and downloads'
                " online, set 'local_files_only' to False.")
        logger.warning('We can not confirm the cached file is for revision: %s'
                       % revision)
        return cache.get_root_location(
        )  # we can not confirm the cached file is for snapshot 'revision'
    else:
        # make headers
        headers = {
            'user-agent':
            ModelScopeConfig.get_user_agent(user_agent=user_agent, )
        }
        _api = HubApi()
        if cookies is None:
            cookies = ModelScopeConfig.get_cookies()
        repo_files = []
        if repo_type == REPO_TYPE_MODEL:
            revision_detail = _api.get_valid_revision_detail(
                repo_id, revision=revision, cookies=cookies)
            revision = revision_detail['Revision']

            snapshot_header = headers if 'CI_TEST' in os.environ else {
                **headers,
                **{
                    'Snapshot': 'True'
                }
            }
            if cache.cached_model_revision is not None:
                snapshot_header[
                    'cached_model_revision'] = cache.cached_model_revision

            repo_files = _api.get_model_files(
                model_id=repo_id,
                revision=revision,
                recursive=True,
                use_cookies=False if cookies is None else cookies,
                headers=snapshot_header,
            )
        elif repo_type == REPO_TYPE_DATASET:
            group_or_owner, name = model_id_to_group_owner_name(repo_id)
            if not revision:
                revision = DEFAULT_DATASET_REVISION
            revision_detail = revision
            files_list_tree = _api.list_repo_tree(
                dataset_name=name,
                namespace=group_or_owner,
                revision=revision,
                root_path='/',
                recursive=True)
            if not ('Code' in files_list_tree
                    and files_list_tree['Code'] == 200):
                print(
                    'Get dataset: %s file list failed, request_id: %s, message: %s'
                    % (repo_id, files_list_tree['RequestId'],
                       files_list_tree['Message']))
                return None
            repo_files = files_list_tree['Data']['Files']

        if ignore_file_pattern is None:
            ignore_file_pattern = []
        if isinstance(ignore_file_pattern, str):
            ignore_file_pattern = [ignore_file_pattern]
        ignore_file_pattern = [
            item if not item.endswith('/') else item + '*'
            for item in ignore_file_pattern
        ]
        ignore_regex_pattern = []
        for file_pattern in ignore_file_pattern:
            if file_pattern.startswith('*'):
                ignore_regex_pattern.append('.' + file_pattern)
            else:
                ignore_regex_pattern.append(file_pattern)

        if allow_file_pattern is not None:
            if isinstance(allow_file_pattern, str):
                allow_file_pattern = [allow_file_pattern]
            allow_file_pattern = [
                item if not item.endswith('/') else item + '*'
                for item in allow_file_pattern
            ]

        for repo_file in repo_files:
            if repo_file['Type'] == 'tree' or \
                    any([fnmatch.fnmatch(repo_file['Path'], pattern) for pattern in ignore_file_pattern]) or \
                    any([re.search(pattern, repo_file['Name']) is not None for pattern in ignore_regex_pattern]):  # noqa E501
                continue

            if allow_file_pattern is not None and allow_file_pattern:
                if not any(
                        fnmatch.fnmatch(repo_file['Path'], pattern)
                        for pattern in allow_file_pattern):
                    continue

            # check model_file is exist in cache, if existed, skip download, otherwise download
            if cache.exists(repo_file):
                file_name = os.path.basename(repo_file['Name'])
                logger.debug(
                    f'File {file_name} already in cache, skip downloading!')
                continue
            if repo_type == REPO_TYPE_MODEL:
                # get download url
                url = get_file_download_url(
                    model_id=repo_id,
                    file_path=repo_file['Path'],
                    revision=revision)
            elif repo_type == REPO_TYPE_DATASET:
                url = _api.get_dataset_file_url(
                    file_name=repo_file['Path'],
                    dataset_name=name,
                    namespace=group_or_owner,
                    revision=revision)

            download_file(url, repo_file, temporary_cache_dir, cache, headers,
                          cookies)

        cache.save_model_version(revision_info=revision_detail)
        return os.path.join(cache.get_root_location())
