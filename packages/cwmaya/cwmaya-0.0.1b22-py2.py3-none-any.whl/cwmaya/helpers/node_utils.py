import pymel.core as pm

def next_available_element_plug(array_plug):
    indices = array_plug.getArrayIndices()
    next_available = next(a for a, b in enumerate(indices + [-1]) if a != b)
    return array_plug[next_available]

def next_element_plug(array_plug):
    indices = array_plug.getArrayIndices()
    if not indices:
        return array_plug[0]
    return array_plug[(indices[-1]+1)]