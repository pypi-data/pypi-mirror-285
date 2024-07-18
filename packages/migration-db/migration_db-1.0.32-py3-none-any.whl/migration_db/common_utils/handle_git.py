# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 8/28/2023 4:57 PM
@Description: Description
@File: git.py
"""
import subprocess

from git import Repo

from common_utils.calc_time import calc_func_time


@calc_func_time
def git_clone_with_credentials(url, username, password, repo_path, branch_name="master"):
    # 构造Git命令
    git_command = f'git -c http.sslVerify=false -c credential.helper=store ' \
                  f'-c credential.helper="!f() {{ echo username={username}; echo password={password}; }}; f" ' \
                  f'clone -b {branch_name} {url} {repo_path}'

    # 执行Git命令
    process = subprocess.Popen(git_command, shell=True)
    process.wait()


def get_git_directory_structure(repo_path):
    # 执行git命令，获取目录结构
    command = ['git', 'ls-tree', '--name-only', '-r', 'HEAD']
    output = subprocess.check_output(command, cwd=repo_path).decode().strip()

    # 解析输出结果，按行分割
    lines = output.split('\n')

    # 返回目录结构列表
    return lines


def is_latest(repo_path, branch_name='master'):
    # 打开本地仓库
    repo = Repo(repo_path)

    # 获取远程分支
    remote_branch = repo.remote().refs[branch_name]

    # 拉取最新的提交记录
    repo.git.fetch()

    # 获取本地分支的最新提交记录
    local_commits = list(repo.iter_commits(branch_name))

    # 比较本地分支和远程分支的提交记录数量
    return not (len(local_commits) < remote_branch.commit.count())


def git_pull(repo_path, branch_name='master'):
    # 打开本地仓库
    repo = Repo(repo_path)

    # 切换到目标分支
    repo.git.checkout(branch_name)

    repo.git.stash()
    stashes = repo.git.stash('list')
    if len(stashes) > 0:
        repo.git.stash('drop')

    # 拉取最新的提交记录
    repo.git.pull()


def git_add_safe(repo_path):
    # 构造Git命令
    git_command = f'git config --global --add safe.directory "{repo_path}"'

    # 执行Git命令
    process = subprocess.Popen(git_command, shell=True)
    process.wait()


def configure_git_credentials(repo_path, url, username, password):
    credential_info = f"url={url}\nusername={username}\npassword={password}\n"
    credential_store_path = f"{repo_path}/.git-credentials"

    # 将凭证信息写入临时的.git-credentials文件中
    with open(credential_store_path, 'w') as f:
        f.write(credential_info)

    # 配置Git使用临时的.git-credentials文件
    process = subprocess.Popen(['git', 'config', '--local', 'credential.helper', 'store'], cwd=repo_path)
    process.communicate()

    # 存储凭证信息
    process = subprocess.Popen(['git', 'credential', 'approve'], cwd=repo_path, stdin=subprocess.PIPE)
    process.communicate(input=credential_info.encode())