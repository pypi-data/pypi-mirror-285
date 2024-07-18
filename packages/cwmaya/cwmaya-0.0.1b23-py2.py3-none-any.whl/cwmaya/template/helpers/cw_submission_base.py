import maya.api.OpenMaya as om
import json
from cwmaya.template.helpers import attribute_factory as attrs
from cwmaya.template.helpers import job_attributes
from cwstorm.serializers import default as serializer
from cwstorm.dsl.dag_node import DagNode


def maya_useNewAPI():
    pass


class cwSubmission(om.MPxNode):

    aJob = None

    aOutput = None
    aTokens = None

    id = om.MTypeId(0x880501)

    @staticmethod
    def creator():
        return cwSubmission()

    @classmethod
    def isAbstractClass(cls):
        return True

    @classmethod
    def initialize(cls):

        cls.aLastLoaded = attrs.makeIntAttribute(
            "lastLoadedTemplate", "llt", hidden=True, keyable=False
        )
        om.MPxNode.addAttribute(cls.aLastLoaded)

        cls.aOutput = attrs.makeStringAttribute(
            "output",
            "out",
            hidden=False,
            writable=False,
            keyable=False,
            storable=False,
            readable=True,
        )
        om.MPxNode.addAttribute(cls.aOutput)

        cls.aTokens = attrs.makeStringAttribute(
            "tokens",
            "tok",
            hidden=False,
            writable=False,
            keyable=False,
            storable=False,
            readable=True,
        )
        om.MPxNode.addAttribute(cls.aTokens)

        cls.aJob = job_attributes.initialize(cls.aOutput)

    def compute(self, plug, data):

        if plug == self.aTokens:
            json_str = self.computeTokens(data)
            handle = data.outputValue(self.aTokens)
            handle.setString(json_str)
            data.setClean(plug)
            return self
        elif plug == self.aOutput:
            DagNode.reset()
            job = self.computeJob(data)
            result = json.dumps(serializer.serialize(job))
            handle = data.outputValue(self.aOutput)
            handle.setString(result)
            data.setClean(plug)
            return self
        return None

    def computeTokens(self, data):
        raise NotImplementedError

    def computeJob(self, data):
        raise NotImplementedError
