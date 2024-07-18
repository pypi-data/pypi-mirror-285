# from __future__ import unicode_literals
import os
import json

from cwmaya.template.helpers.cw_submission_base import cwSubmission
from cwmaya.template.helpers import (
    task_attributes,
    frames_attributes,
    python_script_attributes,
    job_attributes,
    context,
    upload_helpers,
    assets,
)


# pylint: disable=import-error
import maya.api.OpenMaya as om


def maya_useNewAPI():
    pass


class cwSimRenderSubmission(cwSubmission):

    # Declare
    aSimTask = None
    aRenderTask = None
    aQuicktimeTask = None
    aFramesAttributes = None
    aSimScript = None

    id = om.MTypeId(0x880504)

    def __init__(self):
        """Initialize the class."""
        super(cwSimRenderSubmission, self).__init__()

    @staticmethod
    def creator():
        return cwSimRenderSubmission()

    @classmethod
    def isAbstractClass(cls):
        return False

    @classmethod
    def initialize(cls):
        """Create the static attributes."""
        om.MPxNode.inheritAttributesFrom("cwSubmission")
        cls.aSimTask = task_attributes.initialize("sim", "sm", cls.aOutput)
        cls.aRenderTask = task_attributes.initialize("rnd", "rd", cls.aOutput)
        cls.aQuicktimeTask = task_attributes.initialize("qtm", "qt", cls.aOutput)
        cls.aFramesAttributes = frames_attributes.initialize(cls.aOutput, cls.aTokens)

        cls.aSimScript = python_script_attributes.initialize("sim", "sm", cls.aOutput)

    def compute(self, plug, data):
        """Compute the output json from the input attributes."""
        if plug == self.aSimScript["output"]:
            sequences = frames_attributes.getSequences(data, self.aFramesAttributes)
            chunk = sequences["main_sequence"].chunks()[0]
            this_node = om.MFnDependencyNode(self.thisMObject())
            static_context = context.getStatic(this_node, sequences)
            dynamic_context = context.getDynamic(static_context, chunk)
            values = python_script_attributes.getValues(data, self.aSimScript)
            command = python_script_attributes.computePythonScript(
                values, context=dynamic_context
            )
            handle = data.outputValue(self.aSimScript["output"])
            handle.setString(command)
            data.setClean(plug)
            return self
        else:
            return super(cwSimRenderSubmission, self).compute(plug, data)

    def computeTokens(self, data):
        """Compute output json from input attributes."""
        sequences = frames_attributes.getSequences(data, self.aFramesAttributes)
        this_node = om.MFnDependencyNode(self.thisMObject())
        static_context = context.getStatic(this_node, sequences)
        chunk = sequences["main_sequence"].chunks()[0]
        dynamic_context = context.getDynamic(static_context, chunk)
        result = json.dumps(dynamic_context)
        return result

    def computeJob(self, data):
        """Compute output json from input attributes."""

        sequences = frames_attributes.getSequences(data, self.aFramesAttributes)
        this_node = om.MFnDependencyNode(self.thisMObject())
        static_context = context.getStatic(this_node, sequences)

        job_values = job_attributes.getValues(data, self.aJob)
        sim_values = task_attributes.getValues(data, self.aSimTask)
        render_values = task_attributes.getValues(data, self.aRenderTask)
        quicktime_values = task_attributes.getValues(data, self.aQuicktimeTask)

        main_sequence = sequences["main_sequence"]
        scout_sequence = sequences["scout_sequence"] or []

        # Generate context with the first chunk for the job and other single tasks so that users don't get confused when they accidentally use a dynamic token, such as `start`, when the particular field is not in a series task.
        chunk = main_sequence.chunks()[0]
        dynamic_context = context.getDynamic(static_context, chunk)

        job = job_attributes.computeJob(job_values, context=dynamic_context)
        job.step(4).order(0)

        # Create a resolver to optimize the distribution of files in Upload tasks
        upload_resolver = upload_helpers.Resolver()

        sim_task = task_attributes.computeTask(
            sim_values,
            context=dynamic_context,
            env_amendments=[{"key": "[MAYA_MODULE_PATH]", "value": "{remotemodule}"}],
        )

        ### If the user has specified a python script, replace any existing commands with the script

        script_values = python_script_attributes.getValues(data, self.aSimScript)
        command = python_script_attributes.computePythonScript(
            script_values, context=dynamic_context
        )
        if command != "":
            cmd = python_script_attributes.toCmd(command)
            sim_task.commands(cmd)  # overwrites any existing commands

        sim_task.step(1).order(0)

        upload_resolver.add(sim_task, sim_values["extra_assets"])

        scraped_assets = assets.scrape()
        upload_resolver.add(sim_task, scraped_assets)

        quicktime_task = task_attributes.computeTask(
            quicktime_values, context=dynamic_context
        )
        quicktime_task.step(3).order(0)
        upload_resolver.add(quicktime_task, quicktime_values["extra_assets"])

        job.add(quicktime_task)

        for i, chunk in enumerate(main_sequence.chunks()):
            dynamic_context = context.getDynamic(static_context, chunk)
            render_task = task_attributes.computeTask(
                render_values, context=dynamic_context
            )
            render_task.step(2).order(i)
            upload_resolver.add(render_task, render_values["extra_assets"])
            upload_resolver.add(render_task, scraped_assets)
            if scout_sequence:
                if chunk.intersects(scout_sequence):
                    render_task.initial_state("START")
                else:
                    render_task.initial_state("HOLD")
            quicktime_task.add(render_task)
            render_task.add(sim_task)

        upload_resolver.resolve()

        return job
