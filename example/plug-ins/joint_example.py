import maya
import maya.cmds as cmds
import maya.api.OpenMaya as api
import mayaUsd.lib


def maya_useNewApi():
    pass

class JointAdaptor(mayaUsd.lib.SchemaApiAdaptor):
    @property
    def maya_object_name(self):
        return api.MFnDependencyNode(self.mayaObject).name()

    def CanAdaptForImport(self, jobArgs):
        print(f"CanAdaptForImport: {self.maya_object_name}")
        return True

    def ApplySchemaForImport(self, primReaderArgs, context):
        print(f"ApplySchemaForImport: {self.maya_object_name}")
        return True

    def CopyFromPrim(self, prim, args, context):
        value = prim.GetAttribute("example:data").Get()
        print(f"CopyFromPrim: mayaObject: {self.maya_object_name} | prim: {prim.GetName()} | value: {value}")

        # Add a simple boolean to indicate we imported data on it.
        cmds.select(self.maya_object_name)
        cmds.addAttr(longName="with_adaptor", attributeType="bool")
        attr = "{}.{}".format(self.maya_object_name, "with_adaptor")
        cmds.setAttr(attr, True)
        return True

    def CanAdaptForExport(self, jobArgs):
        if not cmds.attributeQuery("with_adaptor", node=self.maya_object_name, exists=True):
            return False

        print(f"CanAdaptForExport: {self.maya_object_name}")
        return True

    def CopyToPrim(self, prim, usdTime, valueWriter):
        print(f"CopyToPrim: mayaObject: {self.maya_object_name} | prim: {prim.GetName()}")
        prim.GetAttribute("example:data").Set("this-was-exported")
        return True


def initializePlugin(object):
    if not maya.cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
        maya.cmds.loadPlugin("mayaUsdPlugin")

    mayaUsd.lib.SchemaApiAdaptor.Register(JointAdaptor, "entity", "WithAdaptorAPI")


def uninitializePlugin(object):
    mayaUsd.lib.SchemaApiAdaptor.Unregister(JointAdaptor, "entity", "WithAdaptorAPI")
