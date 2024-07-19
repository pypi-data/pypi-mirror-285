# from __future__ import unicode_literals

import json

from cwmaya.template.helpers.cw_submission_base import cwSubmission
from cwmaya.template.helpers import (
    task_attributes,
    frames_attributes,
    job_attributes,
    context,
    upload_helpers,
    assets,
)


# pylint: disable=import-error
import maya.api.OpenMaya as om


def maya_useNewAPI():
    pass


class cwChainSubmission(cwSubmission):

    # Declare
    aWorkTask = None
    aFramesAttributes = None

    id = om.MTypeId(0x880505)

    def __init__(self):
        """Initialize the class."""
        super(cwChainSubmission, self).__init__()

    @staticmethod
    def creator():
        return cwChainSubmission()

    @classmethod
    def isAbstractClass(cls):
        return False

    @classmethod
    def initialize(cls):
        """Create the static attributes."""
        om.MPxNode.inheritAttributesFrom("cwSubmission")
        cls.aWorkTask = task_attributes.initialize("wrk", "wk", cls.aOutput)
        cls.aFramesAttributes = frames_attributes.initialize(cls.aOutput, cls.aTokens)  

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
        work_values = task_attributes.getValues(data, self.aWorkTask)

        main_sequence = sequences["main_sequence"]
        scout_sequence = sequences["scout_sequence"] or []

        # Generate context with the first chunk for the job and other single tasks so that users don't get confused when they accidentally use a dynamic token, such as `start``, when the particular field is not in a series task.
        chunk = main_sequence.chunks()[0]
        dynamic_context = context.getDynamic(static_context, chunk)

        job = job_attributes.computeJob(job_values, context=dynamic_context)

        upload_resolver = upload_helpers.Resolver()

        # get chunks in reverse order to build the chain
        chunks = main_sequence.chunks()
        # chunks.reverse()
        prev_source = None
        for i, chunk in enumerate(chunks):
            dynamic_context = context.getDynamic(static_context, chunk)
            work_task = task_attributes.computeTask(
                work_values, 
                context=dynamic_context,
                env_amendments=[{"key": "[PATH]", "value": "{remotemodule}/bin"}]
            )
            work_task.metadata({"step": i + 1, "order": 0})
            work_task.step(i + 1).order(0)
            upload_resolver.add(work_task, work_values["extra_assets"])
            scraped_assets = assets.scrape()
            upload_resolver.add(work_task, scraped_assets)
            
            if scout_sequence:
                if chunk.intersects(scout_sequence):
                    work_task.initial_state("START")
                else:
                    work_task.initial_state("HOLD")
            if prev_source:
                work_task.add(prev_source)
            prev_source = work_task

        if prev_source:
            job.add(prev_source)
            job.step(prev_source.step() + 1).order(0)

        upload_resolver.resolve()

        return job
