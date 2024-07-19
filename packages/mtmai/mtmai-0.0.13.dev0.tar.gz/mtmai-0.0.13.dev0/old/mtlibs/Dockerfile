# syntax=docker/dockerfile:1

# 用环境变量的方式标识当前处于docker build环境中。
ARG MTX_DOCKER_BUILD=1
ARG MTX_BUNDLER_PASS
ARG WORKDIR=/app
#####################################################################
## 安装生产环境下必要的软件包
FROM gitgit188/base as mtcms_base
ARG WORKDIR
WORKDIR ${WORKDIR}
RUN pip install mtlibs>0.0.307 -U



#####################################################################
## 解压 测试容器
FROM gitgit188/base as test
ARG MTX_BUNDLER_PASS
ARG MTX_DOCKER_BUILD
ARG WORKDIR
WORKDIR ${WORKDIR}
RUN pip install mtlibs>0.0.308 -U
RUN echo "123" > ${WORKDIR}/hello.txt

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN python3 -m build
RUN pip install --editable .
# 加密打包应用源码
RUN mtbundler
RUN echo "显示打包的结果" && ls -al /