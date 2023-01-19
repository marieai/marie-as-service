import inspect
import os
import sys
import marie.helper
from marie.utils.device import gpu_device_count

from marie.constants import (
    __model_path__,
    __config_dir__,
    __marie_home__,
    __cache_path__,
)

from marie_server.rest_extension import extend_rest_interface


if __name__ == "__main__":
    if "NO_VERSION_CHECK" not in os.environ:
        from marie_server.helper import is_latest_version

        is_latest_version(github_repo="marie-as-service")

    from marie import Flow

    if len(sys.argv) > 1:
        if sys.argv[1] == "-i":
            _input = sys.stdin.read()
        else:
            _input = sys.argv[1]
    else:
        _input = "torch-flow.yml"

    print(f"__model_path__ = {__model_path__}")
    print(f"__config_dir__ = {__config_dir__}")
    print(f"__marie_home__ = {__marie_home__}")
    print(f"__cache_path__ = {__cache_path__}")
    print(f"_input = {_input}")
    print(gpu_device_count())

    f = Flow.load_config(
        _input,
        extra_search_paths=[os.path.dirname(inspect.getfile(inspect.currentframe()))],
        substitute=True,
        context={
            'gpu_device_count': gpu_device_count(),
        },
    )

    # Downloading: "https://github.com/pytorch/fairseq/zipball/main" to /home/marie-server/.cache/torch/hub/main.zip
    marie.helper.extend_rest_interface = extend_rest_interface

    with f:
        f.block()
