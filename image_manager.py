"""This ComponentResource abstracts and simplifies Container Image provsioning"""

import base64
import pulumi_aws as aws
from pulumi import  ComponentResource, ResourceOptions
from pulumi_docker import  Image, DockerBuildArgs, RegistryArgs


def fetch_registry_info(registry_id):
    """Method returns credentials for the ecr repository"""

    credentials = aws.ecr.get_credentials(registry_id=registry_id)
    decoded_credentials = base64.b64decode(credentials.authorization_token).decode()
    credential_pair = decoded_credentials.split(':')

    if len(credential_pair) != 2:
        raise Exception("Invalid credentials")
    return RegistryArgs(
        server=credentials.proxy_endpoint,
        username=credential_pair[0],
        password=credential_pair[1],
    )

class ImageManagerArgs:
    """Arguments Class to store location of Dockerfile and configurable value for container image"""

    def __init__(self, config_val, context):
        """constructor of the arguments class, to store assigned values"""
        self.config_val = config_val
        self.context = context


class ImageManager(ComponentResource):
    """Class initializing and building from dockerfile to create a container image in a ECR repo"""

    def __init__(self, name: str, args: ImageManagerArgs, opts: ResourceOptions = None):
        """constructor of the component resource, to create ECR repo, build an image and push"""
        super().__init__("custom:app:ImageManager", name, {}, opts)

        # Create a private ECR registry.
        repo = aws.ecr.Repository(name, force_delete=True)
        registry_info = repo.registry_id.apply(fetch_registry_info)

        # Build and publish the image.
        image = Image(
            name,
            build=DockerBuildArgs(
                context=args.context,
                platform = "linux/amd64",
                args = {
                    "CONFIGURABLE_VALUE": args.config_val
                }
            ),
            image_name=repo.repository_url,
            registry=registry_info,
        )
        self.image_digest = image.repo_digest
        self.image_name = image.image_name
        self.register_outputs({})
