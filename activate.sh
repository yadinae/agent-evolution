#!/bin/bash
# 激活共享 Python 环境
source /home/admin/.venv-shared/bin/activate
export PYTHONPATH="/home/admin/projects/agent-evolution:$PYTHONPATH"
echo "已激活共享 venv: /home/admin/.venv-shared"
echo "Python: $(which python)"
