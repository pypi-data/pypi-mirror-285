import maya.api.OpenMaya as om
from cwmaya.template.helpers import attribute_factory as attrs
from cwmaya.template.helpers import context as ctx
from cwstorm.dsl.job import Job



def initialize(outputPlug):
    """
    Initializes attributes for a Storm Job and sets up dependency relations.

    Args:
        outputPlug (om.MObject): The output plug of the node that will be affected by the custom attributes.

    Returns:
        dict: A dictionary containing the created attributes and their corresponding MObjects.
    """
    result = {}
    result["label"] = attrs.makeStringAttribute("label", "lbl")
    result["description"] = attrs.makeStringAttribute("description", "desc")
    result["projectName"] = attrs.makeStringAttribute("projectName", "prn")
    result["currentTime"] = attrs.makeTimeAttribute("currentTime", "ct")
    result["locationTag"] = attrs.makeStringAttribute("location", "loc")
    result["author"] = attrs.makeStringAttribute("author", "ath")

    metadata = attrs.makeKvPairsAttribute("metadata", "mtd")
    result["metadata"] = metadata["compound"]
    result["metadataKey"] = metadata["key"]
    result["metadataValue"] = metadata["value"]

    top_level_attrs = [
        "label",
        "description",
        "projectName",
        "currentTime",
        "locationTag",
        "author",
        "metadata",
    ]
    for attr in top_level_attrs:

        om.MPxNode.addAttribute(result[attr])
        om.MPxNode.attributeAffects(result[attr], outputPlug)

    return result


def getValues(data, job_attrs):
    """
    Retrieves values from the node's data block.

    Manages complex data structures like metadata.

    Args:
        data (om.MDataBlock): The data block from which the values are retrieved.
        job_attrs (dict): A dictionary mapping attribute names to their corresponding MObjects.

    Returns:
        dict: A dictionary containing the values of the specified attributes.
    """
    result = {}
    result["label"] = data.inputValue(job_attrs["label"]).asString()
    result["description"] = data.inputValue(job_attrs["description"]).asString()
    result["project_name"] = data.inputValue(job_attrs["projectName"]).asString()

    metadata = {}
    array_handle = data.inputArrayValue(job_attrs["metadata"])
    while not array_handle.isDone():
        key = (
            array_handle.inputValue().child(job_attrs["metadataKey"]).asString().strip()
        )
        value = (
            array_handle.inputValue()
            .child(job_attrs["metadataValue"])
            .asString()
            .strip()
        )
        metadata[key] = value
        array_handle.next()
    result["metadata"] = metadata
    result["current_time"] = (
        data.inputValue(job_attrs["currentTime"]).asTime().asUnits(om.MTime.uiUnit())
    )
    result["location"] = data.inputValue(job_attrs["locationTag"]).asString()
    result["author"] = data.inputValue(job_attrs["author"]).asString()

    return result


def computeJob(job_values, context=None):
    """
    Creates a Storm Job object with the provided job values and optional context for string interpolation.

    Args:
        job_values (dict): A dictionary containing values necessary to create a Job object.
        context (dict, optional): A dictionary providing context for string formatting. Defaults to None.

    Returns:
        Job: An instantiated Job object with the specified attributes and metadata applied.
    """
    if not context:
        context = {}
    name = ctx.interpolate(job_values["label"], context)
    job = Job(name)
    metadata = job_values["metadata"]
    # loop through metadata and resolve values with context
    for key, value in metadata.items():
        metadata[key] = ctx.interpolate(value, context)
    job.metadata(metadata)

    job.project(job_values["project_name"])

    comment = ctx.interpolate(job_values["description"], context)
    job.comment(comment)

    author = ctx.interpolate(job_values["author"], context)
    job.author(author)

    location = ctx.interpolate(job_values["location"], context)
    job.location(location)
    
    return job
