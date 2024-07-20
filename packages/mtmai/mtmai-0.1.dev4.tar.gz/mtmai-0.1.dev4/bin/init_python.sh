#!/usr/bin/env bash

init_python_311(){
    (echo "y\n" | pyenv install 3.11) || true && pyenv global 3.11
}

setup_transformers(){
    # 设置 基于 transformers 的开发 ai 开发环境。
    # 参考： https://github.com/huggingface/transformers/blob/main/docs/source/zh/installation.md
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    # pip install -r requirements.txt
    pip install -e . && pip install -e .[dev]
    # 确定环境正常
    python -c "from transformers import pipeline; print(pipeline('sentiment-analysis')('I love you'))"
}
init_python_311
setup_transformers
