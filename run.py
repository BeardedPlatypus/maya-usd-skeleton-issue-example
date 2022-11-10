"""
run.py provides a repeatable import/export roundtrip for the sample_data.usda
contained in the usd_data directory. 

It illustrates the issue with 'CopyToPrim' and related export methods not triggering
when the API schema is applied to a skeleton.

See the README for additional details
"""
from maya import cmds
from pathlib import Path
import os

# Ensure the plugins are loaded.
if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
    cmds.loadPlugin("mayaUsdPlugin")

if not cmds.pluginInfo("joint_example", query=True, loaded=True):
    cmds.loadPlugin("joint_example")

# Create a new scene to not have pollution from previous tests.
cmds.file(new=True, f=True)  
usd_data_dir = Path(os.environ["REPO_ROOT"]) / "usd_data"

# Define a with adaptor and without adaptor to illustrate it not working in either case.
schemas = ["WithAdaptorAPI", "WithoutAdaptorAPI"]  

# -> Import the data: this works as expected.
import_path = usd_data_dir / "sample_data.usda"
cmds.mayaUSDImport(file=import_path, primPath="/", apiSchema=schemas)

# -> Export the data: this does not write the data associated with the APIs to the skeleton.
export_path = usd_data_dir / "exported_data.usda"
cmds.mayaUSDExport(file=export_path, apiSchema=schemas, exportSkels="auto")