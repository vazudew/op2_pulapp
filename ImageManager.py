from pulumi import asset, Input, Output, ComponentResource, ResourceOptions
from pulumi_aws import s3
from pulumi_docker import  Image, DockerBuildArgs, RegistryArgs
import pulumi_aws as aws
import base64

# Get registry info (creds and endpoint) so we can build/publish to it.
def getRegistryInfo(rid):
    creds = aws.ecr.get_credentials(registry_id=rid)
    decoded = base64.b64decode(creds.authorization_token).decode()
    parts = decoded.split(':')
    if len(parts) != 2:
        raise Exception("Invalid credentials")
    return RegistryArgs(
        server=creds.proxy_endpoint,
        username=parts[0],
        password=parts[1],
    )

class ImageManagerArgs:
    def __init__(self, config_val, context):
        self.config_val = config_val
        self.context = context


class ImageManager(ComponentResource):
    def __init__(self, name: str, args: ImageManagerArgs, opts: ResourceOptions = None):
        super().__init__("custom:app:ImageManager", name, {}, opts)
        child_opts = ResourceOptions(parent=self)
        # Create a private ECR registry.
        repo = aws.ecr.Repository(name, force_delete=True)
        registryInfo = repo.registry_id.apply(getRegistryInfo)
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
            registry=registryInfo,
        )
        self.imageDigest = image.repo_digest
        self.image_name = image.image_name
        self.register_outputs({})    

