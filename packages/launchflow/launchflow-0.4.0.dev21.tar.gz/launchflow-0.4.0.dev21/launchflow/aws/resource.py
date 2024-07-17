from launchflow.resource import Resource, T


# NOTE: We dont currently add any functionality to AWS resources that the base class
# does not already provide, but we separate the classes for future extensibility.
class AWSResource(Resource[T]):
    pass
