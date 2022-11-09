import maya
import maya.api.OpenMaya as api
import mayaUsd.lib


def maya_useNewApi():
    pass


class JointAdaptor(mayaUsd.lib.SchemaApiAdaptor):
    @property
    def maya_object_name(self):
        return api.MFnDependencyNode(self.mayaObject).name()

    def print(self, msg):
        print(f"{self.__name__}: {msg}")

    def CanAdaptForImport(self, jobArgs):
        self.print(f"CanAdaptForImport: {self.maya_object_name}")
        return True

    def ApplySchemaForImport(self, primReaderArgs, context):
        self.print(f"ApplySchemaForImport: {self.maya_object_name}")
        return True

    def CopyFromPrim(self, prim, args, context):
        value = prim.GetAttribute("example:data").Get()
        self.print(f"CopyFromPrim: mayaObject: {self.maya_object_name} | prim: {prim.GetName()} | value: {value}")
        return True

    def CanAdaptForExport(self, jobArgs):
        self.print(f"CanAdaptForExport: {self.maya_object_name}")
        return True

    def CopyToPrim(self, prim, usdTime, valueWriter):
        self.print(f"CopyToPrim: mayaObject: {self.maya_object_name} | prim: {prim.GetName()}")
        value = prim.GetAttribute("example:data").Set("this-was-exported")
        return True

    
def initializePlugin(object):
    if not maya.cmds.plugInfo("mayaUsdPlugin", query=True, loaded=True):
        maya.cmds.loadPlugin("mayaUsdPlugin")

    mayaUsd.lib.SchemaApiAdaptor.Register(JointAdaptor, "entity", "WithAdaptorAPI")


def uninitializePlugin(object):
    mayaUsd.lib.SchemaApiAdaptor.Unregister(JointAdaptor, "entity", "WithAdaptorAPI")
