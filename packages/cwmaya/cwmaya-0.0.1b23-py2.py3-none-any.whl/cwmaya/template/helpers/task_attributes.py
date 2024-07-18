import maya.api.OpenMaya as om
from cwmaya.template.helpers import attribute_factory as attrs
from cwmaya.template.helpers import packages
from cwmaya.template.helpers import context as ctx
from cwstorm.dsl.task import Task
from cwstorm.dsl.cmd import Cmd

import shlex


def initialize(longPrefix, shortPrefix, outputPlug):
    """Create the static attributes for the export column."""
    result = {}

    result["label"] = attrs.makeStringAttribute(
        f"{longPrefix}Label", f"{shortPrefix}lb"
    )

    result["instanceType"] = attrs.makeStringAttribute(
        f"{longPrefix}InstanceType", f"{shortPrefix}it"
    )

    result["preemptible"] = attrs.makeBoolAttribute(
        f"{longPrefix}Preemptible", f"{shortPrefix}pt"
    )

    result["software"] = attrs.makeStringAttribute(
        f"{longPrefix}Software", f"{shortPrefix}sw", array=True
    )

    result["commands"] = attrs.makeStringAttribute(
        f"{longPrefix}Commands", f"{shortPrefix}cm", array=True
    )

    environment = attrs.makeKvPairsAttribute(
        f"{longPrefix}Environment", f"{shortPrefix}nv"
    )

    result["environment"] = environment["compound"]
    result["environmentKey"] = environment["key"]
    result["environmentValue"] = environment["value"]
    result["extraAssets"] = attrs.makeStringAttribute(
        f"{longPrefix}ExtraAssets", f"{shortPrefix}ea", array=True
    )

    result["output_path"] = attrs.makeStringAttribute(
        f"{longPrefix}OutputPath", f"{shortPrefix}op"
    )

    top_level_attrs = [
        "label",
        "instanceType",
        "preemptible",
        "software",
        "commands",
        "environment",
        "extraAssets",
        "output_path",
    ]
    for attr in top_level_attrs:
        om.MPxNode.addAttribute(result[attr])
        om.MPxNode.attributeAffects(result[attr], outputPlug)

    return result


def getValues(data, task_attrs):
    result = {}

    result["label"] = data.inputValue(task_attrs["label"]).asString()
    result["instance_type"] = data.inputValue(task_attrs["instanceType"]).asString()
    result["preemptible"] = data.inputValue(task_attrs["preemptible"]).asBool()

    result["output_path"] = data.inputValue(task_attrs["output_path"]).asString()

    result["software"] = []
    array_handle = data.inputArrayValue(task_attrs["software"])
    while not array_handle.isDone():
        software = array_handle.inputValue().asString().strip()
        if software:
            result["software"].append(software)
        array_handle.next()

    result["commands"] = []
    array_handle = data.inputArrayValue(task_attrs["commands"])
    while not array_handle.isDone():
        cmd = array_handle.inputValue().asString().strip()
        if cmd:
            result["commands"].append(cmd)
        array_handle.next()

    result["environment"] = []
    array_handle = data.inputArrayValue(task_attrs["environment"])
    while not array_handle.isDone():
        key = (
            array_handle.inputValue()
            .child(task_attrs["environmentKey"])
            .asString()
            .strip()
        )
        value = (
            array_handle.inputValue()
            .child(task_attrs["environmentValue"])
            .asString()
            .strip()
        )
        if key and value:
            result["environment"].append({"key": key, "value": value})
        array_handle.next()

    result["extra_assets"] = []
    array_handle = data.inputArrayValue(task_attrs["extraAssets"])
    while not array_handle.isDone():
        path = array_handle.inputValue().asString().strip()
        if path:
            result["extra_assets"].append(path)
        array_handle.next()

    return result


def computeTask(task_values, context=None, env_amendments=[]):
    """Compute the common task."""

    name = ctx.interpolate(task_values["label"], context)
    task = Task(name)

    task.hardware(task_values["instance_type"])
    task.preemptible(task_values["preemptible"])

    for command in task_values["commands"]:
        command = ctx.interpolate(command, context)
        task.push_commands(Cmd(*shlex.split(command)))

    software_list = task_values["software"]
    package_ids, environment = packages.get_packages_data(software_list)

    env_entries = task_values["environment"] + env_amendments

    extra_environment = [
        {"key": entry["key"], "value": ctx.interpolate(entry["value"], context)}
        for entry in env_entries
    ]

    environment += extra_environment

    env_dict = packages.composeEnvVars(environment)
    task.env(env_dict)
    task.packages(*package_ids)

    task.lifecycle({"minsec": 0, "maxsec": 3600})
    task.initial_state("START")

    output_path = ctx.interpolate(task_values["output_path"], context)
    task.output_path(output_path)

    return task
