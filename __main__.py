import base64
import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
import json 

from ImageManager import ImageManager, ImageManagerArgs
from K8SManager import K8SManager, K8SManagerArgs


config = pulumi.Config()
config_val = config.get("config_val")

image_manager = ImageManager("op2-plapp", ImageManagerArgs(context="app", config_val=config_val))
k8s_manager = K8SManager("eks-cluster", K8SManagerArgs(eks_cluster_name="eks-cluster", instance_type="t2.medium", desired=2, max_size=2, min_size=1, app_name="op2-plapp",imageDigest=image_manager.imageDigest))

#output values
pulumi.export("op2_plapp_url", k8s_manager.app_alb_url)
pulumi.export('imageDigest', image_manager.imageDigest)
pulumi.export('imageName', image_manager.image_name)