# Reusable exceptions.
# Reusable package-level exceptions.
# All gcv errors should be passed back using these exceptions

# TODO - what does pass mean? is this ok?
class GCVError(Exception):
    pass

class GCVSchemaTestError(GCVError):
    pass

class GCVRuleTestError(GCVError):
    pass

class GCVUnexpectedDataTypeError(GCVError):
    pass

class GCVGeoJsonCheckError(GCVError):
    pass