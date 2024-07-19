import shlex
import re
import maya.api.OpenMaya as om
from cwmaya.template.helpers import attribute_factory as attrs
from cwmaya.template.helpers import context as ctx
from cwstorm.dsl.cmd import Cmd
import cwmaya.helpers.const as k
import json
import base64


def initialize(longPrefix, shortPrefix, outputPlug):
    """
    Create the static attributes for a maya batch script widget.

    Parameters:
    longPrefix (str): The long prefix used for attribute names.
    shortPrefix (str): The short prefix used for attribute names.
    outputPlug (MObject): The output plug to connect the attributes.

    Returns:
    dict: A dictionary containing the created attributes.
    """
    result = {}

    result["useScript"] = attrs.makeBoolAttribute(
        f"{longPrefix}UseScript", f"{shortPrefix}us"
    )

    result["scene"] = attrs.makeStringAttribute(
        f"{longPrefix}Scene", f"{shortPrefix}sf"
    )

    result["script"] = attrs.makeStringAttribute(
        f"{longPrefix}Script", f"{shortPrefix}sc"
    )

    result["args"] = attrs.makeStringAttribute(
        f"{longPrefix}Args", f"{shortPrefix}ag", array=True
    )
    result["argsType"] = attrs.makeEnumAttribute(
        f"{longPrefix}ArgsType",
        f"{shortPrefix}at",
        options=k.DATATYPES,
        default=k.DATATYPES.index(k.TYPE_INT),
    )

    kwargs = attrs.makeKwargsAttribute(f"{longPrefix}Kwargs", f"{shortPrefix}kw")

    result["kwargs"] = kwargs["compound"]
    result["kwargsName"] = kwargs["name"]
    result["kwargsValue"] = kwargs["value"]
    result["kwargsType"] = kwargs["type"]

    top_level_attrs = [
        "useScript",
        "scene",
        "script",
        "args",
        "argsType",
        "kwargs",
    ]

    # make an output plug so we can easily get the command string any time.
    result["output"] = attrs.makeStringAttribute(
        f"{longPrefix}OutScript",
        f"{shortPrefix}oc",
        hidden=False,
        writable=False,
        keyable=False,
        storable=False,
        readable=True,
    )
    om.MPxNode.addAttribute(result["output"])

    # make sure these attributes affect d the script output to update.
    for attr in top_level_attrs:
        om.MPxNode.addAttribute(result[attr])
        om.MPxNode.attributeAffects(result[attr], outputPlug)
        om.MPxNode.attributeAffects(result[attr], result["output"])

    return result


def getValues(data, python_script_attrs):
    """
    Retrieve values from the data block based on the provided attributes.

    Parameters:
    data (MDataBlock): The data block containing the attribute values.
    python_script_attrs (dict): A dictionary of attribute objects.

    Returns:
    dict: A dictionary containing the retrieved values.
    """
    result = {}

    result["useScript"] = data.inputValue(python_script_attrs["useScript"]).asBool()

    result["scene"] = data.inputValue(python_script_attrs["scene"]).asString()

    result["script"] = data.inputValue(python_script_attrs["script"]).asString()

    result["args"] = []
    array_handle = data.inputArrayValue(python_script_attrs["args"])
    while not array_handle.isDone():
        arg = array_handle.inputValue().asString().strip()
        if arg:
            result["args"].append(arg)
        array_handle.next()

    result["argsType"] = data.inputValue(python_script_attrs["argsType"]).asShort()

    result["kwargs"] = []
    array_handle = data.inputArrayValue(python_script_attrs["kwargs"])
    while not array_handle.isDone():
        name = (
            array_handle.inputValue()
            .child(python_script_attrs["kwargsName"])
            .asString()
            .strip()
        )
        value = (
            array_handle.inputValue()
            .child(python_script_attrs["kwargsValue"])
            .asString()
            .strip()
        )
        type = (
            array_handle.inputValue().child(python_script_attrs["kwargsType"]).asShort()
        )

        if name and value:
            result["kwargs"].append({"name": name, "value": value, "type": type})
        array_handle.next()

    return result


def computePythonScript(script_values, context=None):
    """
    Compute the maya -batch script based on given values and context.

    Parameters:
    script_values (dict): A dictionary containing script-related values.
    context (dict, optional): A dictionary containing context for interpolation. Defaults to None.

    Returns:
    str: The computed batch command string.
    
    Since maya -batch can only take MEL scripts and commands, we can't directly run python scripts. However, we want a mechanism to allow users to create python scripts with arbitrary function signatures and arguments.
    
    We tried generating the python script and wrapping it in MEL's python() command, but this failed due to nested quote escaping hell.
    
    To avoid this limitation, we now put the script name, args, kwargs, and the datatype of each arg in a json structure, base64 encode it, and pass it to a MEL script in Maya on the render node. The MEL script (pyPayloadExecutor) will decode the payload and run the python script with the given arguments.
    """

    if not script_values["useScript"]:
        return []

    script = script_values["script"]
    args = script_values["args"]
    args_datatype = k.DATATYPES[script_values["argsType"]]
    kwargs = script_values["kwargs"]

    scene = ctx.interpolate(script_values["scene"], context)

    payload = {
        "script": script,
        "args": [],
        "kwargs": [],
    }

    for arg in args:
        parameter = ctx.interpolate(arg, context)
        payload["args"] += [parameter, args_datatype]

    for kwarg in kwargs:
        name = kwarg["name"]
        value = ctx.interpolate(kwarg["value"], context)
        datatype = k.DATATYPES[kwarg["type"]]
        payload["kwargs"] += [name, value, datatype]

    json_payload = json.dumps(payload)
    b64_payload = base64.b64encode(json_payload.encode("utf-8")).decode("utf-8")

    mayaprojdir = ctx.interpolate("{mayaprojdir}", context)

    executor_script = "pyPayloadExecutor"
    # batch_cmd = f'maya -batch -proj "{mayaprojdir}" -file "{scene}" -script "{executor_script}.mel" -command "{executor_script}(\\"{b64_payload}\\")"'
    return [
        "maya",
        "-batch",
        "-proj",
        f'"{mayaprojdir}"',
        "-file",
        f'"{scene}"',
        "-script",
        f'"{executor_script}.mel"',
        "-command",
        f'"{executor_script}(\\\"{b64_payload}\\\")"',
    ]
    
    # return batch_cmd


def toCmd(command):
    return Cmd(*shlex.split(command))
