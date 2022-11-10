# Illustration of `maya-usd` adaptors not working when exporting skeletons

[`maya-usd`](https://github.com/Autodesk/maya-usd) is used to import and export USD 
files within Maya. It comes with a framework that allows you to modify the USD import
and export behaviour. Primarily, this is done by writing custom `SchemaApiAdaptors` or
import and export chasers. For the most part this works well, however, it fails when
exporting skeleton data with API schemas applied to them. When a custom adaptor is 
registered for these API schemas, they are not triggered at all, and the default 
roundtrip behaviour seems absent as well. This seems to be a bug. The purpose of this
repository is to provide a simple set of steps to reproduce it.

## Prerequisites

In order to run the reproduction steps the following is necessary:

* VS Code
* Maya 2022
* maya-usd 0.19 or 0.20.

## Reproduction steps

1. Clone this repository
2. Open this folder within VS Code
3. Start the `Maya 2022` task in VS Code (this will ensure the env is set correctly)
4. Run the [`run.py`](/run.py) script within Maya through the script editor

## Expected behaviour

### Correctly exported `exported_data.usda`

When we import [`sample_data.usda`](/usd_data/sample_data.usda) we load all data associated with
the `WithAdaptorAPI` and `WithoutAdaptorAPI`. When we export this data again, we would expect
the following (updated) data to be available in `exported_data.usda`:

* `arm` Mesh prim:
    * `WithAdaptorAPI` applied
    * `WithoutAdaptorAPI` applied
    * `example:data`: updated to `"this-was-exported"`
    * `example:default_data`: `"this-will-be-kept-the-same"` same as in `sample_data.usda`
* `joint1` Skeleton prim:
    * `WithAdaptorAPI` applied
    * `WithoutAdaptorAPI` applied
    * `example:data`: updated to `"this-was-exported"`
    * `example:default_data`: `"this-will-be-kept-the-same"` same as in `sample_data.usda`

This would look like this in the `.usd` file:

```
    def Mesh "arm" (
        prepend apiSchemas = ["WithoutAdaptorAPI", "WithAdaptorAPI", "MaterialBindingAPI"]
    )
    {
        ...
        string example:data = "this-was-exported"
        string example:default_data = "this-will-be-kept-the-same"
        ...
    }

    def Skeleton "skeleton" (
        prepend apiSchemas = ["WithoutAdaptorAPI", "WithAdaptorAPI", "SkelBindingAPI"]
    )
        ...
        string example:data = "this-was-exported"
        string example:default_data = "this-will-be-kept-the-same"
        ...
    {
```

### Execution of the `JointAdaptor`

We expect all of the adaptor logic in [`joint_example.py`](/example/plug-ins/joint_example.py)
to be executed for both the `arm` Mesh prim and `joint1` Skeleton prim. This would mean we should see the following output in Maya's script window:

```
# Importing '<...>\usd_data\sample_data.usda' # 
CanAdaptForImport: arm
ApplySchemaForImport: arm
CopyFromPrim: mayaObject: arm | prim: arm | value: this-will-be-altered
CanAdaptForImport: skeleton
ApplySchemaForImport: skeleton
CopyFromPrim: mayaObject: skeleton | prim: skeleton | value: this-will-be-altered
# Opening layer 'F:/git/external/maya-usd-skeleton-issue-example/usd_data/exported_data.usda' for writing # 
CanAdaptForExport: arm
CanAdaptForExport: arm
CopyToPrim: mayaObject: arm | prim: arm
CanAdaptForExport: skeleton
CopyToPrim: mayaObject: skeleton | prim: skeleton 
# Saving stage # 
```

## Actual behaviour

The Mesh exports correctly, however the skeleton does not. This can be seen in the actual output
when running [`run.py`](/run.py):

```
# Importing '<...>\usd_data\sample_data.usda' # 
CanAdaptForImport: arm
ApplySchemaForImport: arm
CopyFromPrim: mayaObject: arm | prim: arm | value: this-will-be-altered
CanAdaptForImport: skeleton
ApplySchemaForImport: skeleton
CopyFromPrim: mayaObject: skeleton | prim: skeleton | value: this-will-be-altered
# Opening layer 'F:/git/external/maya-usd-skeleton-issue-example/usd_data/exported_data.usda' for writing # 
CanAdaptForExport: arm
CanAdaptForExport: arm
CopyToPrim: mayaObject: arm | prim: arm
# Saving stage # 
```

Note that the we do have the same messages for the `arm` prim, but that the export messages are
absent for the `joint1` skeleton prim. This can be seen by inspecting the `exported_data.usda` as
well:

```
    def Mesh "arm" (
        prepend apiSchemas = ["WithoutAdaptorAPI", "WithAdaptorAPI", "MaterialBindingAPI"]
    )
    {
        ...
        string example:data = "this-was-exported"
        string example:default_data = "this-will-be-kept-the-same"
        ...
    }

    def Skeleton "skeleton" (
        prepend apiSchemas = ["SkelBindingAPI"]
    )
    {
        uniform matrix4d[] bindTransforms = ...
        uniform token[] joints = ["joint1", "joint1/joint2", "joint1/joint2/joint3"]
        uniform matrix4d[] restTransforms = ...
        rel skel:animationSource = </group1/skeleton/Animation>
        matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1) )
        uniform token[] xformOpOrder = ["xformOp:transform"]

        def SkelAnimation "Animation"
        {
            uniform token[] joints = ["joint1"]
            quatf[] rotations = [(0.99960554, 0, 0.028086055, 0)]
            half3[] scales = [(1, 1, 1)]
            float3[] translations = [(0.16728887, 0, 0.03475939)]
        }
    }
```
_note that the properties on the `arm` and the values on `skeleton` were removed for brevity/readability_

The API schemas are missing, and no data has been copied. To me this behaviour is either a bug, 
a missing feature, or an oversight.
