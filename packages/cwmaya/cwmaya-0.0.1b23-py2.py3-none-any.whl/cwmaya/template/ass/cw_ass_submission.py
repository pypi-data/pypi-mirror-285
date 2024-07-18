# from __future__ import unicode_literals
import json
import shlex

from cwmaya.template.helpers.cw_submission_base import cwSubmission
from cwstorm.dsl.cmd import Cmd
from cwstorm.dsl.task import Task
from cwstorm.serializers import default as serializer

# pylint: disable=import-error
import maya.api.OpenMaya as om


def maya_useNewAPI():
    pass


class cwAssSubmission(cwSubmission):

    aAexTask = None
    aAexPerTask = None

    aRenTask = None
    aRenUseCustomRange = None
    aRenCustomRange = None
    aRenStartFrame = None
    aRenEndFrame = None
    aRenByFrame = None
    aRenAnimation = None
    aRenPerTask = None  # chunk size

    aCmpTask = None
    aQtmTask = None
    aTrkTask = None
    aSlkTask = None

    id = om.MTypeId(0x880502)

    def __init__(self):
        """Initialize the class."""
        super(cwAssSubmission, self).__init__()

    @staticmethod
    def creator():
        return cwAssSubmission()

    @classmethod
    def isAbstractClass(cls):
        return False

    @classmethod
    def initialize(cls):
        """Create the static attributes."""
        om.MPxNode.inheritAttributesFrom("cwSubmission")

        cls.initializeAex()
        cls.initializeRen()
        cls.aCmpTask = cls.initializeTaskAttributes("cmp", "cm")
        cls.aQtmTask = cls.initializeTaskAttributes("qtm", "qt")
        cls.aTrkTask = cls.initializeTaskAttributes("trk", "tk")
        cls.aSlkTask = cls.initializeTaskAttributes("slk", "sk")

    @classmethod
    def initializeAex(cls):
        """Create the static attributes for the export column."""

        cls.aAexTask = cls.initializeTaskAttributes("aex", "ax")
        cls.aAexPerTask = cls.makeIntAttribute("aexPerTask", "expt", default=1, min=1)
        om.MPxNode.addAttribute(cls.aAexPerTask)
        om.MPxNode.attributeAffects(cls.aAexPerTask, cls.aOutput)

    @classmethod
    def initializeRen(cls):
        """Create the static attributes for the render column."""

        cls.aRenTask = cls.initializeTaskAttributes("ren", "rn")

        cls.aRenPerTask = cls.makeIntAttribute("renPerTask", "rnpt", default=1, min=1)
        cls.aRenUseCustomRange = cls.makeBoolAttribute("renUseCustomRange", "rnucr")
        cls.aRenCustomRange = cls.makeStringAttribute("renCustomRange", "rncr")
        cls.aRenStartFrame = cls.makeTimeAttribute("renStartFrame", "rnsf")
        cls.aRenEndFrame = cls.makeTimeAttribute("renEndFrame", "rnef")
        cls.aRenByFrame = cls.makeIntAttribute("renByFrame", "rnbf")
        cls.aRenAnimation = cls.makeBoolAttribute("renAnimation", "rna")

        om.MPxNode.addAttribute(cls.aRenPerTask)
        om.MPxNode.addAttribute(cls.aRenUseCustomRange)
        om.MPxNode.addAttribute(cls.aRenCustomRange)
        om.MPxNode.addAttribute(cls.aRenStartFrame)
        om.MPxNode.addAttribute(cls.aRenEndFrame)
        om.MPxNode.addAttribute(cls.aRenByFrame)
        om.MPxNode.addAttribute(cls.aRenAnimation)

        om.MPxNode.attributeAffects(cls.aRenPerTask, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aRenUseCustomRange, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aRenCustomRange, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aRenStartFrame, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aRenEndFrame, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aRenByFrame, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aRenAnimation, cls.aOutput)

    def compute(self, plug, data):
        """Compute output json from input attribs."""
        if not ((plug == self.aOutput)):
            return None

        job = self.computeJob(data)

        quicktime_task = self.computeQuicktime(data)
        slack_task = self.computeSlack(data)
        comp_task = self.computeCmp(data)
        track_task = self.computeTrk(data)

        job.add(slack_task)
        slack_task.add(quicktime_task)
        quicktime_task.add(comp_task)
        job.add(track_task)
        track_task.add(quicktime_task)

        result = json.dumps(serializer.serialize(job), indent=4)

        handle = data.outputValue(self.aOutput)
        handle.setString(result)

        data.setClean(plug)
        return self

    @classmethod
    def computeQuicktime(cls, data):
        """Compute the quicktime task."""
        task_values = cls.getTaskValues(data, cls.aQtmTask)

        task = Task("Make Quicktime")

        task.hardware(task_values["instance_type"])
        for command in task_values["commands"]:
            task.commands(Cmd(*shlex.split(command)))

        env_dict = cls.composeEnvVars(task_values["environment"])
        env_dict["SOFTWARE"] = (":").join(task_values["software"])
        task.env(env_dict)
        task.status("WAITING")
        task.lifecycle({"minsec": 30, "maxsec": 1500})
        task.initial_state("START")
        return task

    @classmethod
    def computeSlack(cls, data):
        """Compute the slack task."""
        task_values = cls.getTaskValues(data, cls.aSlkTask)
        task = Task("Send Slack message")
        task.hardware(task_values["instance_type"])
        for command in task_values["commands"]:
            task.commands(Cmd(*shlex.split(command)))
        env_dict = cls.composeEnvVars(task_values["environment"])
        env_dict["SOFTWARE"] = (":").join(task_values["software"])
        task.env(env_dict)
        task.status("WAITING")
        task.lifecycle({"minsec": 30, "maxsec": 1500})
        task.initial_state("START")
        return task

    @classmethod
    def computeCmp(cls, data):
        """Compute the compare task."""
        task_values = cls.getTaskValues(data, cls.aCmpTask)
        task = Task("Composite")
        task.hardware(task_values["instance_type"])
        for command in task_values["commands"]:
            task.commands(Cmd(*shlex.split(command)))
        env_dict = cls.composeEnvVars(task_values["environment"])
        env_dict["SOFTWARE"] = (":").join(task_values["software"])
        task.env(env_dict)
        task.status("WAITING")
        task.lifecycle({"minsec": 30, "maxsec": 1500})
        task.initial_state("START")
        return task

    @classmethod
    def computeTrk(cls, data):
        """Compute the tracking task."""
        task_values = cls.getTaskValues(data, cls.aTrkTask)
        task = Task("Track")
        task.hardware(task_values["instance_type"])
        for command in task_values["commands"]:
            task.commands(Cmd(*shlex.split(command)))
        env_dict = cls.composeEnvVars(task_values["environment"])
        env_dict["SOFTWARE"] = (":").join(task_values["software"])
        task.env(env_dict)
        task.status("WAITING")
        task.lifecycle({"minsec": 30, "maxsec": 1500})
        task.initial_state("START")
        return task
