import shlex
import re
import maya.api.OpenMaya as om
from cwmaya.template.helpers import attribute_factory as attrs
from cwmaya.template.helpers import context as ctx
from cwstorm.dsl.cmd import Cmd
import cwmaya.helpers.const as k


def initialize(longPrefix, shortPrefix, outputPlug):
    """Create the static attributes for the export column."""
    result = {}

    result["useScript"] = attrs.makeBoolAttribute(
        f"{longPrefix}UseScript", f"{shortPrefix}us"
    )

    result["wrapBatch"] = attrs.makeBoolAttribute(
        f"{longPrefix}WrapBatch", f"{shortPrefix}wb", default=True
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
        "wrapBatch",
        "script",
        "args",
        "argsType",
        "kwargs",
    ]
    for attr in top_level_attrs:
        om.MPxNode.addAttribute(result[attr])
        om.MPxNode.attributeAffects(result[attr], outputPlug)

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

    om.MPxNode.attributeAffects(result["useScript"], result["output"])
    om.MPxNode.attributeAffects(result["wrapBatch"], result["output"])
    om.MPxNode.attributeAffects(result["script"], result["output"])
    om.MPxNode.attributeAffects(result["args"], result["output"])
    om.MPxNode.attributeAffects(result["argsType"], result["output"])
    om.MPxNode.attributeAffects(result["kwargs"], result["output"])

    return result


def getValues(data, python_script_attrs):
    result = {}

    result["useScript"] = data.inputValue(python_script_attrs["useScript"]).asBool()
    result["wrapBatch"] = data.inputValue(python_script_attrs["wrapBatch"]).asBool()

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
    """Compute the python script."""
    if not script_values["useScript"]:
        return ""
    wrap_batch = script_values["wrapBatch"]
    script = script_values["script"]
    args = script_values["args"]
    args_datatype = k.DATATYPES[script_values["argsType"]]
    kwargs = script_values["kwargs"]

    parameters = []

    for arg in args:
        parameter = ctx.interpolate(arg, context)
        parameters.append(_format(parameter, args_datatype))

    for kwarg in kwargs:
        name = kwarg["name"]
        value = ctx.interpolate(kwarg["value"], context)
        datatype = k.DATATYPES[kwarg["type"]]
        parameter = f"{name}={_format(value, datatype)}"
        parameters.append(parameter)

    paramstr = ", ".join(parameters)
    python_cmd = f"import {script};{script}.doit({paramstr})"
    if not wrap_batch:
        return python_cmd

    mayaprojdir = ctx.interpolate("{mayaprojdir}", context)

    mel_python_cmd = f'python(\\"{python_cmd}\\")'
    batch_cmd = f'mayabatch -proj "{mayaprojdir}" -command "{mel_python_cmd}"'
    return batch_cmd


def esc(s):
    s = re.sub(r"\\", r"\\\\", s)
    s = re.sub(r'"', r'\\"', s)
    s = re.sub(r"'", r"\\'", s)
    return s


def _format(arg, argsType):
    if argsType == k.TYPE_INT:
        return int(arg)
    elif argsType == k.TYPE_STR:
        return f"'{esc(arg)}'"
    else:
        return arg


def toCmd(command):
    return Cmd(*shlex.split(command))
