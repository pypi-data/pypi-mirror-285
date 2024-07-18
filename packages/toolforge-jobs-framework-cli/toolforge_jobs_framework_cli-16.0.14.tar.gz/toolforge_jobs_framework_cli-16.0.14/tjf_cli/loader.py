# (C) 2022 Taavi Väänänen <hi@taavi.wtf>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
from dataclasses import dataclass
from logging import getLogger
from typing import Callable, Dict, List, Optional, Set

from toolforge_weld.api_client import ToolforgeClient

LOGGER = getLogger(__name__)


@dataclass
class LoadChanges:
    add: Set[str]
    modify: Set[str]


def jobs_are_same(job_config: Dict, job_keys: List, api_obj: Dict) -> bool:
    """Determines if a job api object matches its configuration."""

    # TODO: some renames to make things easier. See also T327280
    api_obj["command"] = api_obj["cmd"]
    api_obj["mem"] = api_obj.get("memory", None)
    api_obj["filelog-stdout"] = api_obj.get("filelog_stdout", None)
    api_obj["filelog-stderr"] = api_obj.get("filelog_stderr", None)

    # TODO: explicitely setting default CPU/memory should not count as a difference
    dont_evaluate_here = ["name", "emails", "filelog", "no-filelog", "wait", "retry"]
    # TODO: Investigate and fix bug in health-check-script handling. For now just ignore
    dont_evaluate_here += ["health-check-script"]
    keys = [k for k in job_keys if k not in dont_evaluate_here]
    for key in keys:
        if api_obj.get(key, None) != job_config.get(key, None):
            LOGGER.debug(
                "currently existing job %s has different '%s' than the definition",
                api_obj["name"],
                key,
            )
            return False

    emails_config = job_config.get("emails", "none")
    if api_obj["emails"] != emails_config:
        LOGGER.debug(
            "currently existing job %s has different 'emails' than the definition",
            api_obj["name"],
        )
        return False

    retry_config = job_config.get("retry", 0)
    if api_obj["retry"] != retry_config:
        LOGGER.debug(
            "currently existing job %s has different 'retry' than the definition",
            api_obj["name"],
        )
        return False

    # TODO: make the api emit proper json booleans, See also T327280
    filelog_api = api_obj.get("filelog") in (True, "True")
    filelog_config = job_config.get("filelog", None)
    if filelog_config is None:
        if "no-filelog" in job_config:
            filelog_config = not job_config["no-filelog"]
        else:
            filelog_config = "/" not in job_config["image"]

    if filelog_config != filelog_api:
        LOGGER.debug(
            "currently existing job %s has different 'filelog' than the definition",
            api_obj["name"],
        )
        return False

    LOGGER.debug("currently existing job %s matches its definition", api_obj["name"])
    return True


def calculate_changes(
    conf: ToolforgeClient,
    configured_job_data: Dict,
    job_keys: List[str],
    filter: Optional[Callable[[str], bool]],
) -> LoadChanges:
    for job in configured_job_data:
        for key in job:
            if key not in job_keys:
                LOGGER.warning(f"Unknown key '{key}' in job '{job['name']}' definition")

    wanted_jobs = {
        job["name"]: job
        for job in configured_job_data
        if not filter or filter(job["name"])
    }

    response = conf.get("/jobs/")
    current_job_data = response
    if "messages" in response:
        current_job_data = response["jobs"]

    current_jobs = {
        job["name"]: job
        for job in current_job_data
        if not filter or filter(job["name"])
    }

    to_add = wanted_jobs.keys() - current_jobs.keys()

    # TODO: make it possible to rename a job that is already
    # running by simply changing the name in the loads.yaml file.
    # note that this will require each job having some other
    # immutable unique identifier so we might need to wait on T359650

    to_modify = set()
    for job_name, job_data in wanted_jobs.items():
        if job_name in current_jobs and not jobs_are_same(
            job_config=job_data, job_keys=job_keys, api_obj=current_jobs[job_name]
        ):
            to_modify.add(job_name)

    return LoadChanges(add=to_add, modify=to_modify)
