from __future__ import annotations


def infer(**kwargs) -> dict:
    """
    Execute infer task.

    Parameters
    ----------
    **kwargs : dict
        Nefertem client, resources, run_config, run_id

    Returns
    -------
    dict
        Nefertem run info.
    """
    client = kwargs.get("client")
    resources = kwargs.get("resources")
    run_config = kwargs.get("run_config")
    run_id = kwargs.get("run_id")

    with client.create_run(resources, run_config, run_id=run_id) as nt_run:
        nt_run.infer()
        nt_run.log_schema()
        nt_run.persist_schema()
    return nt_run.run_info.to_dict()


def profile(**kwargs) -> dict:
    """
    Execute profile task.

    Parameters
    ----------
    **kwargs : dict
        Nefertem client, resources, run_config, run_id

    Returns
    -------
    dict
        Nefertem run info.
    """
    client = kwargs.get("client")
    resources = kwargs.get("resources")
    run_config = kwargs.get("run_config")
    run_id = kwargs.get("run_id")

    with client.create_run(resources, run_config, run_id=run_id) as nt_run:
        nt_run.profile()
        nt_run.log_profile()
        nt_run.persist_profile()
    return nt_run.run_info.to_dict()


def validate(**kwargs) -> dict:
    """
    Execute validate task.

    Parameters
    ----------
    **kwargs : dict
        Nefertem client, resources, run_config, run_id, constraints and error_report

    Returns
    -------
    dict
        Nefertem run info.
    """
    client = kwargs.get("client")
    resources = kwargs.get("resources")
    run_config = kwargs.get("run_config")
    run_id = kwargs.get("run_id")
    constraints = kwargs.get("constraints")
    error_report = kwargs.get("error_report", "partial")

    if constraints is None:
        raise ValueError("Constraints cannot be None.")

    with client.create_run(resources, run_config, run_id=run_id) as nt_run:
        nt_run.validate(constraints=constraints, error_report=error_report)
        nt_run.log_report()
        nt_run.persist_report()
    return nt_run.run_info.to_dict()


def metric(**kwargs) -> dict:
    """
    Execute metric task.

    Parameters
    ----------
    **kwargs : dict
        Nefertem client, resources, run_config, run_id and metrics

    Returns
    -------
    dict
        Nefertem run info.
    """
    client = kwargs.get("client")
    resources = kwargs.get("resources")
    run_config = kwargs.get("run_config")
    run_id = kwargs.get("run_id")
    metrics = kwargs.get("metrics")

    if metrics is None:
        raise ValueError("Metrics cannot be None.")

    with client.create_run(resources, run_config, run_id=run_id) as nt_run:
        nt_run.metric(metrics=metrics)
        nt_run.log_metric()
        nt_run.persist_metric()
    return nt_run.run_info.to_dict()
