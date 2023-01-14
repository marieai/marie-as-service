# Marie AI Server

## Install


```shell
DOCKER_BUILDKIT=1 docker build . --build-arg PIP_TAG="[standard]" -f ./Dockerfiles/server.Dockerfile  -t marieai/marie-server:3.0-cuda

DOCKER_BUILDKIT=1 docker build . -f ./Dockerfiles/server.Dockerfile  -t marieai/marie-server:3.0-cuda
```

## Get Started
[Configuring Github Actions in a multi-directory repository structure](https://medium.com/@owumifestus/configuring-github-actions-in-a-multi-directory-repository-structure-c4d2b04e6312)
