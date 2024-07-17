from dataclasses import dataclass
from typing import Literal

import launchflow as lf
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

        **Args:**
        - `name`: The name of the ECRRepository resource. This must be globally unique.
        - `force_delete`: Whether to force delete the repository when the environment is deleted.
        - `image_tag_mutability`: The image tag mutability for the repository.
        """
        super().__init__(
            name=name,
            replacement_arguments={"format", "location"},
            resource_id=f"{name}-{lf.project}-{lf.environment}",
        )
        self.force_delete = force_delete
        self.image_tag_mutability = image_tag_mutability

    def inputs(self, environment_type: EnvironmentType) -> ECRRepositoryInputs:
        """Get the inputs required for the ECR repository.

        **Args:**
        - `environment_type` (EnvironmentType): The environment type for the ECR repository.

        **Returns:**
        - An `ECRRepositoryInputs` object containing the inputs for the ECR repository.
        """
        return ECRRepositoryInputs(
            resource_id=self.resource_id,
            force_delete=self.force_delete,
            image_tag_mutability=self.image_tag_mutability,
        )
