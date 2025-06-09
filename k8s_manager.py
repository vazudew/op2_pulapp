"""This ComponentResource abstracts and simplifies all K8S (EKS) operations"""

import pulumi_eks as eks
import pulumi_kubernetes as k8s
from pulumi import  ComponentResource, ResourceOptions

class K8SManagerArgs:
    """Arguments Class to store various EKS and container image values"""

    def __init__(self, eks_cluster_name,
                 instance_type, desired, max_size,
                 min_size, app_name, image_digest,
                 vpc_id, public_subnets, private_subnets):
        
        """constructor of the arguments class, to store assigned values"""
        self.eks_cluster_name = eks_cluster_name
        self.instance_type = instance_type
        self.desired = desired
        self.max_size = max_size
        self.min_size = min_size
        self.app_name = app_name
        self.image_digest = image_digest
        self.k8s_vpc_id = vpc_id
        self.k8s_public_subnet_ids = public_subnets
        self.k8s_private_subnet_ids = private_subnets

class K8SManager(ComponentResource):
    """Class to create an EKS cluster, deploy containers,
    expose them with service and an ELB on AWS"""

    def __init__(self, name: str, args: K8SManagerArgs, opts: ResourceOptions = None):
        """constructor of the component resource, for all k8s operations on EKS"""
        super().__init__("custom:app:K8SManager", name, {}, opts)

        # Create the EKS cluster
        eks_cluster = eks.Cluster(args.eks_cluster_name,
            # Put the cluster in the new VPC created earlier
            vpc_id=args.k8s_vpc_id,
            # Use the "API" authentication mode to support access entries
            authentication_mode=eks.AuthenticationMode.API,
            # Public subnets will be used for load balancers
            public_subnet_ids=args.k8s_public_subnet_ids,
            # Private subnets will be used for cluster nodes
            private_subnet_ids=args.k8s_private_subnet_ids,
            # Change configuration values to change any of the following settings
            instance_type=args.instance_type,
            desired_capacity=args.desired,
            min_size=args.min_size,
            max_size=args.max_size,
            # Do not give worker nodes a public IP address
            node_associate_public_ip_address=False,
            # Change these values for a private cluster (VPN access required)
            endpoint_private_access=False,
            endpoint_public_access=True
            )

        # Create a Kubernetes provider to interact with EKS cluster
        k8s_provider = k8s.Provider("k8s-provider", kubeconfig=eks_cluster.kubeconfig)

        deployment = k8s.apps.v1.Deployment(f"{args.app_name}-deployment",
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(
                    match_labels={"app": f"{args.app_name}"},
                ),
                replicas=2,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels={"app": f"{args.app_name}"}),
                    spec=k8s.core.v1.PodSpecArgs(
                        containers=[
                            k8s.core.v1.ContainerArgs(
                                name=f"{args.app_name}",
                                image=args.image_digest,
                                ports=[k8s.core.v1.ContainerPortArgs(container_port=80)],
                            )
                        ],
                    ),
                ),
            ),
            opts=ResourceOptions(
                provider=k8s_provider,
                replace_on_changes=["spec.template.spec.containers[*].image"]
                ),
        )

        service = k8s.core.v1.Service(f"{args.app_name}",
            spec=k8s.core.v1.ServiceSpecArgs(
                selector={"app": f"{args.app_name}"},
                ports=[k8s.core.v1.ServicePortArgs(port=80, target_port=80)],
                type="LoadBalancer",
            ),
            opts=ResourceOptions(provider=k8s_provider),
        )
        self.app_alb_url = service.status.load_balancer.ingress[0].apply(
            lambda ingress: ingress.hostname or ingress.ip
            )
        self.deployment_status = deployment.status
        self.register_outputs({})
