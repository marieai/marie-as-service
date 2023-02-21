import inspect
import os
import sys
from typing import Dict, Any

import marie.helper
from marie.conf.helper import load_yaml
from marie.messaging import (
    Toast,
    NativeToastHandler,
    AmazonMQToastHandler,
    PsqlToastHandler,
)
from marie.utils.device import gpu_device_count

from marie.constants import (
    __model_path__,
    __config_dir__,
    __marie_home__,
    __cache_path__,
)

from marie_server.rest_extension import extend_rest_interface


def setup_toast_events(toast_config: Dict[str, Any]):

    print(toast_config)
    native_config = toast_config["native"]
    psql_config = toast_config["psql"]
    amazon_config = toast_config["amazon-mq"]

    Toast.register(NativeToastHandler("/tmp/events.json"), native=True)
    Toast.register(PsqlToastHandler(psql_config), native=False)
    Toast.register(AmazonMQToastHandler(amazon_config), native=False)


if __name__ == "__main__":
    if "NO_VERSION_CHECK" not in os.environ:
        from marie_server.helper import is_latest_version

        is_latest_version(github_repo="marie-as-service")

    from marie import Flow

    import torch

    torch.set_float32_matmul_precision("high")
    torch.backends.cudnn.benchmark = False
    # print(torch._dynamo.list_backends())e

    if len(sys.argv) > 1:
        if sys.argv[1] == "-i":
            _input = sys.stdin.read()
        else:
            _input = sys.argv[1]
    else:
        _input = "torch-flow.yml"

    _config_file = "marie.yml"

    print(f"__model_path__ = {__model_path__}")
    print(f"__config_dir__ = {__config_dir__}")
    print(f"__marie_home__ = {__marie_home__}")
    print(f"__cache_path__ = {__cache_path__}")
    print(f"_input = {_input}")
    print(f"_config_file = {_config_file}")
    print(f"CONTEXT.gpu_device_count = {gpu_device_count()}")

    # Load the config file and setup the toast events
    config = load_yaml(
        _input,
        substitute=True,
        context={
            "gpu_device_count": gpu_device_count(),
        },
    )

    print(config)
    if "toast" not in config:
        config["toast"] = {}

    setup_toast_events(config["toast"])

    os.exit()
    f = Flow.load_config(
        # _input,
        config,
        extra_search_paths=[os.path.dirname(inspect.getfile(inspect.currentframe()))],
        substitute=True,
        context={
            "gpu_device_count": gpu_device_count(),
        },
    )

    marie.helper.extend_rest_interface = extend_rest_interface

    with f:
        f.block()
