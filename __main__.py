"""This is the Pulumi entrypoint, where in declaratively defined resources are provisioned on aws"""

import pulumi
from image_manager import ImageManager, ImageManagerArgs
from k8s_manager import K8SManager, K8SManagerArgs
from vpc_manager import VPCManager, VPCManagerArgs

# fetch all the configuration parameters
config = pulumi.Config()
CONFIG_VAL = config.get("config_val")
min_cluster_size = config.get_int("minClusterSize", 3)
max_cluster_size = config.get_int("maxClusterSize", 6)
desired_cluster_size = config.get_int("desiredClusterSize", 3)
eks_node_instance_type = config.get("eksNodeInstanceType", "t3.medium")
vpc_network_cidr = config.get("vpcNetworkCidr", "10.0.0.0/16")


# create image bundle, setup network infra and then spin up EKS to deploy app
image_manager = ImageManager("op2-plapp", ImageManagerArgs(context="app", config_val=CONFIG_VAL))
vpc_manager = VPCManager("op2-plapp-vpc", VPCManagerArgs(vpc_name = "op2-plapp-vpc",
                                                         enable_dns_hostnames=True,
                                                         cidr_block="172.16.0.0/16"))
k8s_manager = K8SManager("eks-cluster",
                         K8SManagerArgs(eks_cluster_name="eks-cluster",
                                        instance_type=eks_node_instance_type,
                                        desired = desired_cluster_size,
                                        max_size= max_cluster_size , min_size=min_cluster_size,
                                        app_name="op2-plapp",image_digest=image_manager.image_digest,
                                        vpc_id = vpc_manager.vpc_id,
                                        public_subnets = vpc_manager.public_subnet_ids,
                                        private_subnets = vpc_manager.private_subnet_ids
                                        ))

#output values
pulumi.export("op2_plapp_url", k8s_manager.app_alb_url)
pulumi.export("deployment_status", k8s_manager.deployment_status)
pulumi.export('image_digest', image_manager.image_digest)
pulumi.export('image_name', image_manager.image_name)
pulumi.export("eks_vpc_id", vpc_manager.vpc_id)
pulumi.export("eks_vpc_public_subnets", vpc_manager.public_subnet_ids)
pulumi.export("eks_vpc_private_subnets", vpc_manager.private_subnet_ids)
