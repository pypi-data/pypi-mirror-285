from collections import defaultdict
from ciopath.gpath_list import PathList
from cwstorm.dsl.dag_node import DagNode
from cwstorm.dsl.upload import Upload

import os
import re
import hashlib
import base64

# regex to exclude any files in a __pycache__ directory or ending with .pyc
EXCLUDE_REGEX = re.compile(r".*(__pycache__|\.pyc)$")


def generate_upload_task(files, name):
    """Generate the upload tasks."""
    up = Upload(name)
    up.initial_state("START")
    for f in files:
        path = f.strip()
        try:
            size = os.path.getsize(path)
            md5 = calc_md5(path)

            file_data = {
                "path": path,
                "size": size,
                "md5": md5,
            }

            up.push_files(file_data)
        except OSError as e:
            print(f"Error accessing file {path}: {e}")
    return up


def calc_md5(file_path):
    """Calculate both the hexadecimal and Base64-encoded MD5 checksums of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except OSError as ex:
        print(f"Error reading file {file_path}: {ex}")
        return None, None

    md5_digest = hash_md5.digest()

    return base64.b64encode(md5_digest).decode("utf-8")


class Resolver(object):
    """Class to resolve and optimize task filesets."""

    def __init__(self):
        self.tasks = {}

    def add(self, task, files):
        """Add a task with its required files.

        Use the tasks name as a key
        """
        path_list = PathList()
        path_list.add(*files)
        path_list.real_files()
        real_filepaths = [p.fslash() for p in path_list]
        real_filepaths = [p for p in real_filepaths if not EXCLUDE_REGEX.match(p)]

        if not task.name() in self.tasks:
            self.tasks[task.name()] = set()
        self.tasks[task.name()].update(real_filepaths)

    def resolve(self):
        """Resolve the tasks into optimized filesets and create connections."""
        fileset_names, task_to_filesets = self._optimize_filesets()

        upload_nodes = {}

        for index, (fileset_name, fileset) in enumerate(fileset_names.items()):
            upl = generate_upload_task(fileset, fileset_name)
            upl.step(0).order(index)
            upload_nodes[fileset_name] = upl

        for task, filesets in task_to_filesets.items():
            task_node = DagNode.instances.get(task)
            for fileset in filesets:
                upload_node = upload_nodes[fileset]
                task_node.add(upload_node)

    def _optimize_filesets(self):
        """
        Optimize filesets to be mutually exclusive and connect tasks accordingly.

        We have several task nodes where each task node can specify a set of files it needs.

        This algorithm attempts to keep the graph clean by making Upload node contents mutually exclusive. The result is that each file appears in one Upload node at most.

        Files are assigned to Upload nodes in such a way as to minimize the number of Upload nodes, while ensuring that no task waits for a file it does not depend on.

        Each Upload node is connected to the task(s) that need the files it contains.

        Example:

        taskA: {file1, file2, file3}
        taskB: {file1, file2, file3, file4}
        taskC: {file2, file3}

        We generate the following Upload nodes:

        Upload1: {file1}
        Upload2: {file2, file3}
        Upload3: {file4}

        And the connections are:

        taskA <- fileSet1, fileSet2
        taskB <- fileSet1, fileSet2, fileSet3
        taskC <- fileSet2

        """

        # Create mapping of each file to the tasks that need it
        file_to_tasks = defaultdict(set)
        for task, files in self.tasks.items():
            for file in files:
                file_to_tasks[file].add(task)

        # Create a mapping of task sets to files (reverse previous mapping)
        task_set_to_files = defaultdict(set)
        for file, task_set in file_to_tasks.items():
            task_set_to_files[frozenset(task_set)].add(file)

        # Generate the connections and associations
        task_to_filesets = defaultdict(list)
        fileset_names = {}
        fileset_to_name = {}

        for idx, (task_set, files) in enumerate(task_set_to_files.items(), 1):
            fileset_name = f"fileSet{idx}"
            fileset_names[fileset_name] = files
            fileset_to_name[frozenset(files)] = fileset_name

            for task in task_set:
                task_to_filesets[task].append(fileset_name)

        return fileset_names, task_to_filesets
