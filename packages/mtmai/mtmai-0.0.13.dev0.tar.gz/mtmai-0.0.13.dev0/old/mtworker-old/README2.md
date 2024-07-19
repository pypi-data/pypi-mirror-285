# 常用命令

python3 mtworker/main.py worker --api=https://mtxtrpcv3.vercel.app/api/worker/config

python3 mtworker/main.py beat --api=https://mtxtrpcv3.vercel.app/api/worker/config

mtworker --api=https://local3502.yuepa8.com/api/worker/config --beat=1

python3 -m mtworker --api=https://dev8000.yuepa8.com/api/mtworker/worker_bootstrap/ --beat=1

python3 -m mtworker https://dev8000.yuepa8.com/api/mtworker/worker_bootstrap/
python3 -m mtworker https://dev3502.yuepa8.com/api/task/get
python3 -m mtworker worker https://mtxtrpcv3.vercel.app

python3 -m mtworker celery-worker
python3 -m mtworker celery-worker redis://:feihuo321@db.yuepa8.com:18002/0

## 库收集

- [pypyr] pypyr automation task runner
- [基于 nodejs 的任务调度器], https://github.com/graphile/worker

## 文档收集：

- 线程的使用: https://superfastpython.com/threading-in-python/
