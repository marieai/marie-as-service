# Marie AI Server

## Install


```shell
DOCKER_BUILDKIT=1 docker build . --build-arg PIP_TAG="standard" -f ./Dockerfiles/server.Dockerfile  -t marieai/marie-server:3.0-cuda

DOCKER_BUILDKIT=1 docker build . -f ./Dockerfiles/server.Dockerfile  -t marieai/marie-server:3.0-cuda
```


## Execute 


```shell
docker run --gpus all --rm -it marieai/marie-server:3.0-cuda
```

```shell
docker run --gpus all --rm -it --network=host -e JINA_MP_START_METHOD='spawn' -e MARIE_DEFAULT_MOUNT='/etc/marie' -v /mnt/data/marie-ai/config:/etc/marie/config:ro -v /mnt/data/marie-ai/model_zoo:/etc/marie/model_zoo:rw marieai/marie-server:3.0-cuda
```

Passing custom environment arguments:

```shell
docker run --gpus all --rm -it --network=host -e JINA_LOG_LEVEL=debug -e MARIE_DEFAULT_MOUNT='/etc/marie' -v /mnt/data/marie-ai/config:/etc/marie/config:ro -v /mnt/data/marie-ai/model_zoo:/etc/marie/model_zoo:rw marieai/marie-server:3.0-cuda /etc/marie/config/service/torch-flow.yml
```

## Get Started

[Configuring Github Actions in a multi-directory repository structure](https://medium.com/@owumifestus/configuring-github-actions-in-a-multi-directory-repository-structure-c4d2b04e6312)
