from pulumi import  ComponentResource, ResourceOptions
import pulumi_awsx as awsx

class VPCManagerArgs:
    """Arguments Class to store various VPC values"""
    def __init__(self, vpc_name,
                 enable_dns_hostnames, cidr_block):
        """constructor of the arguments class, to store assigned values"""
        self.vpc_name = vpc_name
        self.enable_dns_hostnames = enable_dns_hostnames
        self.cidr_block = cidr_block

class VPCManager(ComponentResource):
    """Class to create a VPC with preferred CIDR block, having public and private subnets
    in each AZ"""

    def __init__(self, name: str, args: VPCManagerArgs, opts: ResourceOptions = None):
        """constructor of the component resource, for VPC"""
        super().__init__("custom:app:VPCManager", name, {}, opts)

        # Create a VPC for the EKS cluster
        vpc = awsx.ec2.Vpc(args.vpc_name,
            enable_dns_hostnames=args.enable_dns_hostnames,
            cidr_block=args.cidr_block)
        self.public_subnet_ids = vpc.public_subnet_ids
        self.private_subnet_ids = vpc.private_subnet_ids
        self.vpc_id = vpc.vpc_id
        self.register_outputs({})