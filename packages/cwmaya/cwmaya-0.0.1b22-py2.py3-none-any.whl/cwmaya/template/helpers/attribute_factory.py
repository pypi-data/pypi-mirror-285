"""
Make commonly needed attributes with sensible defaults.

Use kwarg to override defaults.
"""

import maya.api.OpenMaya as om
import cwmaya.helpers.const as k



def makeIntAttribute(attr_name, short_name, **kwargs):
    """
    Create an int attribute.
    """
    default = kwargs.get("default", 0)
    attr = om.MFnNumericAttribute()
    result = attr.create(attr_name, short_name, om.MFnNumericData.kInt, default)
    attr.writable = kwargs.get("writable", True)
    attr.keyable = kwargs.get("keyable", True)
    attr.storable = kwargs.get("storable", True)
    if "min" in kwargs:
        attr.setMin(kwargs["min"])
    if "max" in kwargs:
        attr.setMax(kwargs["max"])
    return result


def makeBoolAttribute(attr_name, short_name, **kwargs):
    """
    Create a bool attribute.
    """
    default = kwargs.get("default", True)
    attr = om.MFnNumericAttribute()
    result = attr.create(attr_name, short_name, om.MFnNumericData.kBoolean, default)
    attr.writable = kwargs.get("writable", True)
    attr.keyable = kwargs.get("keyable", True)
    attr.storable = kwargs.get("storable", True)
    return result


def makeStringAttribute(attr_name, short_name, **kwargs):
    """
    Create a string attribute.
    """
    attr = om.MFnTypedAttribute()
    result = attr.create(attr_name, short_name, om.MFnData.kString)
    attr.hidden = kwargs.get("hidden", False)
    attr.writable = kwargs.get("writable", True)
    attr.readable = kwargs.get("readable", True)
    attr.keyable = kwargs.get("keyable", True)
    attr.storable = kwargs.get("storable", True)
    attr.array = kwargs.get("array", False)
    return result


def makeKvPairsAttribute(attr_name, short_name, **kwargs):
    """
    Create a key-value pairs attribute.
    """
    cAttr = om.MFnCompoundAttribute()
    tAttr = om.MFnTypedAttribute()

    result_key = tAttr.create(f"{attr_name}Key", f"{short_name}k", om.MFnData.kString)
    result_value = tAttr.create(
        f"{attr_name}Value", f"{short_name}v", om.MFnData.kString
    )
    result_compound = cAttr.create(attr_name, short_name)
    cAttr.hidden = kwargs.get("hidden", False)
    cAttr.writable = kwargs.get("writable", True)
    cAttr.array = True
    cAttr.addChild(result_key)
    cAttr.addChild(result_value)
    return {"compound": result_compound, "key": result_key, "value": result_value}


def makeTimeAttribute(attr_name, short_name, **kwargs):
    """
    Create a time attribute.
    """
    attr = om.MFnUnitAttribute()
    result = attr.create(attr_name, short_name, om.MFnUnitAttribute.kTime)
    attr.writable = kwargs.get("writable", True)
    attr.keyable = kwargs.get("keyable", True)
    attr.storable = kwargs.get("storable", True)
    return result

def makeEnumAttribute(attr_name, short_name, options, **kwargs):
    """
    Create an enum attribute.
    """
    attr = om.MFnEnumAttribute()
    result = attr.create(attr_name, short_name, kwargs.get("default",0))
    for i, option in enumerate(options):
        attr.addField(option, i)
    attr.writable = kwargs.get("writable", True)
    attr.keyable = kwargs.get("keyable", True)
    attr.storable = kwargs.get("storable", True)
    return result

def makeKwargsAttribute(attr_name, short_name):
    """
    Create a key-value pairs attribute.
    """
    cAttr = om.MFnCompoundAttribute()
    tAttr = om.MFnTypedAttribute()

    result_name = tAttr.create(f"{attr_name}Name", f"{short_name}n", om.MFnData.kString)
    result_value = tAttr.create(
        f"{attr_name}Value", f"{short_name}v", om.MFnData.kString
    )
    result_type = makeEnumAttribute(
        f"{attr_name}Type", f"{short_name}t", options=k.DATATYPES,  default=k.DATATYPES.index(k.TYPE_INT)
    )

    result_compound = cAttr.create(attr_name, short_name)
    cAttr.hidden = False
    cAttr.writable = True
    cAttr.array = True
    cAttr.addChild(result_name)
    cAttr.addChild(result_value)
    cAttr.addChild(result_type)
    return {"compound": result_compound, "name": result_name, "value": result_value, "type": result_type}
