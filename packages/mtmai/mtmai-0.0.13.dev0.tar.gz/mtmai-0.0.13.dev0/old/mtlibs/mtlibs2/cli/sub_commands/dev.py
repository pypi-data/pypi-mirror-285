import asyncio
import os
from git.repo import Repo
from pathlib import Path
from csservices import portforward
import time

print("启动基于nfs的开发环境")

WORKSPACE_ROOT = "/workspace2"
AZ_REPO_PASSWORD = "x2hx4x3hpmrmf2xx7hrtieaxlovfwqorqzb3nyoh75eyqevs6dca"
AZ_REPO_USER = "hcode007"

async def on_command(args):
    """启动容器作为开发环境"""
    print("dev 参数：", args)
    project = args.project
    repo = args.repo
    print(f"准备源码 {project}, {repo}",flush=True)
    azure_gitclone(project,repo)
    print("就绪",flush=True)
    while True:
        time.sleep(1)

def azure_gitclone(project, repo, branch="master"):
    """clone 位于azure 上的仓库源码"""
    local_path = f"{WORKSPACE_ROOT}/{project}/{repo}"
    if Path(local_path).exists():
        print(f"目标路径{local_path}存在，跳过gitclone")
    else:
        print(f"本地路径${local_path}")
        Repo.clone_from(
            f"https://{AZ_REPO_USER}:{AZ_REPO_PASSWORD}@dev.azure.com/{AZ_REPO_USER}/{project}/_git/{repo}",
            to_path=local_path,
            # branch=branch
            )
        print(f"克隆{project}.{project}完成", flush=True)