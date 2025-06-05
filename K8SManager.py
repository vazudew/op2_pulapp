from pulumi import  ComponentResource, ResourceOptions
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s


class K8SManagerArgs:
    def __init__(self, eks_cluster_name, instance_type, desired, max_size, min_size, app_name,imageDigest):
        self.eks_cluster_name = eks_cluster_name
        self.instance_type = instance_type
        self.desired = desired
        self.max_size = max_size
        self.min_size = min_size
        self.app_name = app_name
        self.imageDigest = imageDigest


class K8SManager(ComponentResource):
    def __init__(self, name: str, args: K8SManagerArgs, opts: ResourceOptions = None):
        super().__init__("custom:app:K8SManager", name, {}, opts)
        child_opts = ResourceOptions(parent=self)

        # Create an EKS cluster
        eks_cluster = eks.Cluster(
            args.eks_cluster_name,
            instance_type=args.instance_type,
            desired_capacity=args.desired,
            min_size=args.min_size,
            max_size=args.max_size,
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
                                image=args.imageDigest,
                                ports=[k8s.core.v1.ContainerPortArgs(container_port=80)],
                            )
                        ],
                    ),
                ),
            ),
            opts=ResourceOptions(provider=k8s_provider, replace_on_changes=["spec.template.spec.containers[*].image"]),
        )

        service = k8s.core.v1.Service(f"{args.app_name}",
            spec=k8s.core.v1.ServiceSpecArgs(
                selector={"app": f"{args.app_name}"},
                ports=[k8s.core.v1.ServicePortArgs(port=80, target_port=80)],
                type="LoadBalancer",
            ),
            opts=ResourceOptions(provider=k8s_provider),
        )
        self.app_alb_url = service.status.load_balancer.ingress[0].apply(lambda ingress: ingress.hostname or ingress.ip)
        self.register_outputs({})    