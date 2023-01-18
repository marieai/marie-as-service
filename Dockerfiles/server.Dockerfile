ARG MARIE_VERSION=3.0

#FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu20.04
FROM marieai/marie:${MARIE_VERSION}-cuda

ARG APP_NAME=marie-server
WORKDIR /${APP_NAME}

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# constant, wont invalidate cache
LABEL org.opencontainers.image.vendor="Marie AI" \
      org.opencontainers.image.licenses="Apache 2.0" \
      org.opencontainers.image.title="MarieAI " \
      org.opencontainers.image.description="Build multimodal AI services via cloud native technologies" \
      org.opencontainers.image.authors="hello@marieai.co" \
      org.opencontainers.image.url="https://github.com/marieai/marie-ai" \
      org.opencontainers.image.documentation="https://docs.marieai.co"


COPY server /server
# given by builder
ARG PIP_TAG

RUN python --version
RUN pip install flask_restful

RUN pip install --default-timeout=1000 --compile /server/ \
    && if [ -n "${PIP_TAG}" ]; then pip install --default-timeout=1000 --compile "/server[${PIP_TAG}]" ; fi

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USER_NAME=${APP_NAME}
ARG GROUP_NAME=${APP_NAME}

RUN groupadd -g ${GROUP_ID} ${USER_NAME} &&\
    useradd -l -u ${USER_ID} -g ${USER_NAME} ${GROUP_NAME} &&\
    mkdir /home/${USER_NAME} &&\
    chown ${USER_NAME}:${GROUP_NAME} /home/${USER_NAME} &&\
    chown -R ${USER_NAME}:${GROUP_NAME} /${APP_NAME}/

USER ${USER_NAME}

#ENTRYPOINT ["marie", "flow"]
ENTRYPOINT ["python", "-m", "marie_server"]
#ENTRYPOINT ["pip", "show", "timm"]

