# (C) 2022 Taavi Väänänen <hi@taavi.wtf>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
from typing import Callable, Dict, Optional, Set

import pytest
from toolforge_weld.api_client import ToolforgeClient
from toolforge_weld.kubernetes_config import fake_kube_config

from tjf_cli.api import handle_http_exception
from tjf_cli.cli import RUN_ARGS
from tjf_cli.loader import calculate_changes, jobs_are_same

SIMPLE_TEST_JOB = {
    "name": "test-job",
    "command": "./myothercommand.py -v",
    "image": "bullseye",
    "emails": "none",
    "mount": "none",
}

SIMPLE_TEST_JOB_API = {
    "name": "test-job",
    "cmd": "./myothercommand.py -v",
    "image": "bullseye",
    "image_state": "stable",
    "filelog": "True",
    "status_short": "Running",
    "status_long": (
        "Last run at 2022-10-08T09:28:37Z. Pod in 'Running' phase. "
        "State 'running'. Started at '2022-10-08T09:28:39Z'."
    ),
    "emails": "none",
    "retry": 0,
    "mount": "none",
}


@pytest.fixture()
def mock_api(requests_mock) -> ToolforgeClient:
    server = "http://nonexistent"

    requests_mock.get(f"{server}/jobs/", json=[SIMPLE_TEST_JOB_API])

    yield ToolforgeClient(
        server=server,
        user_agent="xyz",
        kubeconfig=fake_kube_config(),
        exception_handler=handle_http_exception,
    )


def merge(first: Dict, second: Dict, unset=None) -> Dict:
    data = {**first, **second}
    if unset:
        for key in unset:
            del data[key]
    return data


@pytest.mark.parametrize(
    "config,api,expected",
    [
        [SIMPLE_TEST_JOB, SIMPLE_TEST_JOB_API, True],
        # basic parameter change
        [merge(SIMPLE_TEST_JOB, {"image": "tf-foobar"}), SIMPLE_TEST_JOB_API, False],
        [SIMPLE_TEST_JOB, merge(SIMPLE_TEST_JOB_API, {"image": "tf-foobar"}), False],
        # optional parameter change
        [merge(SIMPLE_TEST_JOB, {"schedule": "* * * * *"}), SIMPLE_TEST_JOB_API, False],
        [SIMPLE_TEST_JOB, merge(SIMPLE_TEST_JOB_API, {"schedule": "* * * * *"}), False],
        # emails are complicated
        [merge(SIMPLE_TEST_JOB, {}, unset=["emails"]), SIMPLE_TEST_JOB_API, True],
        [merge(SIMPLE_TEST_JOB, {"emails": "onfailure"}), SIMPLE_TEST_JOB_API, False],
        [SIMPLE_TEST_JOB, merge(SIMPLE_TEST_JOB_API, {"emails": "onfailure"}), False],
        # so is logging
        [merge(SIMPLE_TEST_JOB, {"no-filelog": False}), SIMPLE_TEST_JOB_API, True],
        [merge(SIMPLE_TEST_JOB, {"filelog": True}), SIMPLE_TEST_JOB_API, True],
        [merge(SIMPLE_TEST_JOB, {"no-filelog": True}), SIMPLE_TEST_JOB_API, False],
        [merge(SIMPLE_TEST_JOB, {"filelog": False}), SIMPLE_TEST_JOB_API, False],
        [SIMPLE_TEST_JOB, merge(SIMPLE_TEST_JOB_API, {"filelog": "False"}), False],
        # and retries
        [merge(SIMPLE_TEST_JOB, {"retry": 0}), SIMPLE_TEST_JOB_API, True],
        [merge(SIMPLE_TEST_JOB, {"retry": 1}), SIMPLE_TEST_JOB_API, False],
        [SIMPLE_TEST_JOB, merge(SIMPLE_TEST_JOB_API, {"retry": 2}), False],
        # filelog_stdout
        [
            merge(SIMPLE_TEST_JOB, {"filelog-stdout": "xyz"}),
            merge(SIMPLE_TEST_JOB_API, {"filelog_stdout": "xyz"}),
            True,
        ],
        [merge(SIMPLE_TEST_JOB, {"filelog-stdout": "xyz"}), SIMPLE_TEST_JOB_API, False],
        [SIMPLE_TEST_JOB, merge(SIMPLE_TEST_JOB_API, {"filelog_stdout": "xyz"}), False],
        # filelog_stderr
        [
            merge(SIMPLE_TEST_JOB, {"filelog-stderr": "xyz"}),
            merge(SIMPLE_TEST_JOB_API, {"filelog_stderr": "xyz"}),
            True,
        ],
        [merge(SIMPLE_TEST_JOB, {"filelog-stderr": "xyz"}), SIMPLE_TEST_JOB_API, False],
        [SIMPLE_TEST_JOB, merge(SIMPLE_TEST_JOB_API, {"filelog_stderr": "xyz"}), False],
        # health-check
        # [
        #     SIMPLE_TEST_JOB,
        #     merge(SIMPLE_TEST_JOB_API, {"health_check": None}),
        #     True,
        # ],
        # [merge(SIMPLE_TEST_JOB, {"health-check-script": "/healthcheck.sh"}), SIMPLE_TEST_JOB_API, False],
        # [
        #     SIMPLE_TEST_JOB,
        #     merge(
        #         SIMPLE_TEST_JOB_API,
        #         {"health_check": {"type": "script", "script": "/healthcheck.sh"}},
        #     ),
        #     False,
        # ],
        # [
        #     merge(SIMPLE_TEST_JOB, {"health-check-script": "/healthcheck.sh"}),
        #     merge(
        #         SIMPLE_TEST_JOB_API,
        #         {"health_check": {"type": "script", "script": "/healthcheck.sh"}},
        #     ),
        #     True,
        # ],
        # port
        [SIMPLE_TEST_JOB, merge(SIMPLE_TEST_JOB_API, {"port": None}), True],
        [merge(SIMPLE_TEST_JOB, {"port": 8080}), SIMPLE_TEST_JOB_API, False],
        [SIMPLE_TEST_JOB, merge(SIMPLE_TEST_JOB_API, {"port": 8080}), False],
        [
            merge(SIMPLE_TEST_JOB, {"port": 8080}),
            merge(SIMPLE_TEST_JOB_API, {"port": 8080}),
            True,
        ],
    ],
)
def test_jobs_are_same(config: Dict, api: Dict, expected: bool):
    assert (
        jobs_are_same(job_config=config, job_keys=RUN_ARGS.keys(), api_obj=api)
        == expected
    )


@pytest.mark.parametrize(
    "jobs_data,filter,add,modify,yaml_warning",
    [
        # simple cases
        [[], None, set(), set(), False],
        [[SIMPLE_TEST_JOB], None, set(), set(), False],
        # job data changes
        [[merge(SIMPLE_TEST_JOB, {"mem": "2Gi"})], None, set(), {"test-job"}, False],
        # new job
        [
            [merge(SIMPLE_TEST_JOB, {"name": "new-test-job"})],
            None,
            {"new-test-job"},
            set(),
            False,
        ],
        # configured jobs do not match filter
        [[SIMPLE_TEST_JOB], lambda s: False, set(), set(), False],
        # filter set and matches
        [[SIMPLE_TEST_JOB], lambda s: True, set(), set(), False],
        [
            [merge(SIMPLE_TEST_JOB, {"mem": "2Gi"})],
            lambda s: True,
            set(),
            {"test-job"},
            False,
        ],
        # unknown yaml keys
        [[merge(SIMPLE_TEST_JOB, {"xyz": "xyz"})], None, set(), set(), True],
    ],
)
def test_calculate_changes(
    caplog,
    mock_api: ToolforgeClient,
    jobs_data: Dict,
    filter: Optional[Callable[[str], bool]],
    add: Set[str],
    modify: Set[str],
    yaml_warning,
):
    result = calculate_changes(
        conf=mock_api,
        configured_job_data=jobs_data,
        job_keys=RUN_ARGS.keys(),
        filter=filter,
    )

    assert result.add == add
    assert result.modify == modify
    assert yaml_warning == ("Unknown key" in caplog.text)
