import inspect
import os
import sys
import marie.helper

from marie_server.rest_extension import extend_rest_interface

if __name__ == '__main__':
    if 'NO_VERSION_CHECK' not in os.environ:
        from marie_server.helper import is_latest_version

        is_latest_version(github_repo='marie-as-service')

    from marie import Flow

    if len(sys.argv) > 1:
        if sys.argv[1] == '-i':
            _input = sys.stdin.read()
        else:
            _input = sys.argv[1]
    else:
        _input = 'torch-flow.yml'

    f = Flow.load_config(
        _input,
        extra_search_paths=[os.path.dirname(inspect.getfile(inspect.currentframe()))],
    )

    marie.helper.extend_rest_interface = extend_rest_interface

    with f:
        f.block()
