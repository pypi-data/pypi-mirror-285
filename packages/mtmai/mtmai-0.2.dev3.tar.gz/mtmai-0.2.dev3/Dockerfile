FROM gitgit188/hfbase:latest AS base

FROM base AS mtmai
WORKDIR /app/mtmai
COPY ./pyproject.toml .
RUN python --version
# RUN python -m pip --no-cache-dir install -r requirements.txt --upgrade

RUN sudo chown -R $(id -u) .
RUN python -m pip --no-cache-dir install -e .
COPY ./src ./src


EXPOSE 8080
ENV PORT 8080
CMD ["fastapi", "run", "app/main.py","--host","0.0.0.0","", "--port", "8080"]
