import re

import maya.api.OpenMaya as om
from cwmaya.template.helpers import attribute_factory as attrs
from cioseq.sequence import Sequence


def initialize(outputPlug, outputTokensPlug):

    result = {}

    result["chunkSize"] = attrs.makeIntAttribute("chunkSize", "csz", default=1, min=0)
    result["useCustomRange"] = attrs.makeBoolAttribute("useCustomRange", "ucr")
    result["customRange"] = attrs.makeStringAttribute("customRange", "crn")
    result["useScoutFrames"] = attrs.makeBoolAttribute("useScoutFrames", "usf")
    result["scoutFrames"] = attrs.makeStringAttribute("scoutFrames", "scf")
    result["startFrame"] = attrs.makeTimeAttribute("startFrame", "stf")
    result["endFrame"] = attrs.makeTimeAttribute("endFrame", "enf")
    result["byFrame"] = attrs.makeIntAttribute("byFrame", "byf", default=1, min=1)

    for attr in result.values():
        om.MPxNode.addAttribute(attr)
        om.MPxNode.attributeAffects(attr, outputPlug)
        om.MPxNode.attributeAffects(attr, outputTokensPlug)

    return result


def getSequences(data, frames_attributes):
    if not frames_attributes:
        return None

    result = {"main_sequence": None, "scout_sequence": None}
    chunk_size = data.inputValue(frames_attributes["chunkSize"]).asInt()
    use_custom_range = data.inputValue(frames_attributes["useCustomRange"]).asBool()

    if use_custom_range:
        custom_range = data.inputValue(frames_attributes["customRange"]).asString()
        result["main_sequence"] = Sequence.create(
            custom_range, chunk_size=chunk_size, chunk_strategy="progressions"
        )
    else:
        start_frame = (
            data.inputValue(frames_attributes["startFrame"])
            .asTime()
            .asUnits(om.MTime.uiUnit())
        )
        end_frame = (
            data.inputValue(frames_attributes["endFrame"])
            .asTime()
            .asUnits(om.MTime.uiUnit())
        )
        by_frame = data.inputValue(frames_attributes["byFrame"]).asInt()
        result["main_sequence"] = Sequence.create(
            int(start_frame),
            int(end_frame),
            by_frame,
            chunk_size=chunk_size,
            chunk_strategy="progressions",
        )

    use_scout_frames = data.inputValue(frames_attributes["useScoutFrames"]).asBool()

    if use_scout_frames:
        scout_frames = data.inputValue(frames_attributes["scoutFrames"]).asString()

        match = re.compile(r"^(auto|fml)[, :]+(\d+)$").match(scout_frames)

        if match:
            keyword = match.group(1)
            samples = int(match.group(2))
            if keyword == "auto":
                result["scout_sequence"] = result["main_sequence"].subsample(samples)
            elif keyword == "fml":
                result["scout_sequence"] = result["main_sequence"].calc_fml(samples)
        else:
            try:
                result["scout_sequence"] = Sequence.create(scout_frames)
            except (ValueError, TypeError):
                pass
    return result
