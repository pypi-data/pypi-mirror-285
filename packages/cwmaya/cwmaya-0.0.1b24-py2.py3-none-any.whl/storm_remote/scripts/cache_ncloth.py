import os
import maya.cmds as cmds
import maya.mel as mel

# Description:
# Create cache files on disk for the select ncloth object(s) according
# to the specified flags described below.

#  /Applications/Autodesk/maya2024/Maya.app/Contents/scripts/others/doCreateNclothCache.mel

# $args[0] = time range mode:
#     time range mode = 0 : use $args[1] and $args[2] as start-end
#     time range mode = 1 : use render globals
#     time range mode = 2 : use timeline
# $args[1] = start frame (if time range mode == 0)
# $args[2] = end frame (if time range mode == 0)
# $args[3] = cache file distribution, either "OneFile" or "OneFilePerFrame"
# $args[4] = 0/1, whether to refresh during caching
# $args[5] = directory for cache files, if "", then use project data dir
# $args[6] = 0/1, whether to create a cache per geometry
# $args[7] = name of cache file. An empty string can be used to specify that an auto-generated name is acceptable.
# $args[8] = 0/1, whether the specified cache name is to be used as a prefix
# $args[9] = action to perform: "add", "replace", "merge" or "mergeDelete"
# $args[10] = force save even if it overwrites existing files
# $args[11] = simulation rate, the rate at which the cloth simulation is forced to run
# $args[12] = sample mulitplier, the rate at which samples are written, as a multiple of simulation rate.
# $args[13] = 0/1, whether modifications should be inherited from the cache about to be replaced.
# $args[14] = 0/1, whether to store doubles as floats
# $args[15] = cache format type: mcc or mcx.


# doCreateNclothCache 5 { "3", "1", "50", "OneFilePerFrame", "1", "",                                                             "0", "", "0", "add",     "0",  "1",  "1", "0", "1", "mcx" }
# doCreateNclothCache 5 { "0", "0", "10", "OneFilePerFrame", "0", "/Volumes/xhf/dev/cio/cwmaya/cwmaya/projects/siggraph/storm/cache", "0", "", "0", "replace", "1",  "1",  "1", "0", "0", "mcx" }
def doit(
    *objects,
    start_frame=0,
    end_frame=50,
    cache_per_geometry=False,
    cache_name="",
    simulation_rate=1,
    sample_multiplier=1,
):
    # Set the cache directory
    try:
        cmds.select(*objects)

        cmds.workspace(fileRule=["storm_ncache", "storm/cache"])
        cmds.workspace(fileRule=["storm_scenes", "storm/scenes"])

        cache_directory = cmds.workspace(
            expandName=cmds.workspace(fileRuleEntry="storm_ncache")
        )

        cache_per_geometry = "1" if cache_per_geometry else "0"

        mel_cmd = (
            "doCreateNclothCache 5 {"
            + '"0", '  # time range mode
            + f'"{start_frame}", "{end_frame}", '  # start and end frame
            + '"OneFilePerFrame", '  # cache file distribution
            + '"0", '  # refresh during caching
            + f'"{cache_directory}", '  # directory for cache files
            + f'"{cache_per_geometry}", '  # create a cache per geometry
            + f'"{cache_name}", '  # name of cache file
            + '"0", '  # cache name is not used as a prefix
            + '"replace", '  # replace existing caches
            + '"1", '  # force save even if it overwrites existing files
            + f' "{simulation_rate}", '  # simulation rate
            + f' "{sample_multiplier}", '  # sample multiplier
            + '"0", '  # do not inherited mods from the cache about to be replaced
            + '"0", '  # store doubles as floats
            + '"mcx"'  # cache format type
            + "}"
        )

        print(mel_cmd)

        mel.eval(mel_cmd)

        # #make a directory for the scene file
        out_scenes_directory = cmds.workspace(
            expandName=cmds.workspace(fileRuleEntry="storm_scenes")
        )
        cmds.sysFile(out_scenes_directory, makeDir=True)
        short_name = cmds.file(q=True, sceneName=True, shortName=True)
        out_scene_path = os.path.join(out_scenes_directory, short_name)

        # # Save the file
        cmds.file(rename=out_scene_path)
        cmds.file(save=True, type="mayaAscii")
    except Exception as e:
        print(e)
        return False
    return True
