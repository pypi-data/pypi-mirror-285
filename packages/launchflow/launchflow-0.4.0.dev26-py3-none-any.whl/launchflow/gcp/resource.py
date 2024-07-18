from launchflow.resource import Resource, T


# NOTE: We dont currently add any functionality to GCP resources that the base class
# does not already provide, but we separate the classes for future extensibility.
class GCPResource(Resource[T]):
    pass
