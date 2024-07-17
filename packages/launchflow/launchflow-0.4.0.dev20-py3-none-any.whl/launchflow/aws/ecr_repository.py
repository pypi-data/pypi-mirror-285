from dataclasses import dataclass
from typing import Literal

from launchflow.aws.resource import AWSResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.node import Outputs
from launchflow.resource import TofuInputs


@dataclass
class ECRRepositoryOutputs(Outputs):
    repository_url: str


@dataclass
class ECRRepositoryInputs(TofuInputs):
    force_delete: bool
    image_tag_mutability: Literal["MUTABLE", "IMMUTABLE"]


class ECRRepository(AWSResource[ECRRepositoryOutputs]):
    """A resource for creating an ECR repository.
    Can be used to store container images.

    Like all [Resources](/docs/concepts/resources), this class configures itself across multiple [Environments](/docs/concepts/environments).

    ## Example Usage
    ```python
    import launchflow as lf

    ecr_repository = lf.aws.ECRRepository("my-ecr-repository")
    ```
    """
    product = ResourceProduct.AWS_ECR_REPOSITORY

    def __init__(
        self,
        name: str,
        force_delete: bool = True,
        image_tag_mutability: Literal["MUTABLE", "IMMUTABLE"] = "MUTABLE",
    ) -> None:
        """Create a new ECRRepository resource.

        **Args**:
        - `name`: The name of the ECRRepository resource. This must be globally unique.
        - `force_delete`: Whether to force delete the repository when the environment is deleted.
        - `image_tag_mutability`: The image tag mutability for the repository.
        """
        super().__init__(
            name=name,
            replacement_arguments={"format", "location"},
        )
        self.force_delete = force_delete
        self.image_tag_mutability = image_tag_mutability

    def inputs(self, environment_type: EnvironmentType) -> ECRRepositoryInputs:
        return ECRRepositoryInputs(
            resource_id=self.resource_id,
            force_delete=self.force_delete,
            image_tag_mutability=self.image_tag_mutability,
        )
