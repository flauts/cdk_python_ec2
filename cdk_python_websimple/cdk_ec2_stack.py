from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput,
    CfnTag,
)
from constructs import Construct

class CdkEc2Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Basic VPC
        # vpc = ec2.Vpc.from_vpc_attributes(
        #     self,'vpc',
        #     vpc_id='vpc-00efc54137e6a9ef2',
        #     availability_zones=['us-east-1c','us-east-1f'],
        #     subnet_ids=['subnet-00c42d57b278f4b67','subnet-0a73734857f8400a0'],
        # )
        vpc = ec2.Vpc(
            self,
            "cdk-ec2-vpc",
            max_azs=2, #max_availabity zones
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public-subnet-1",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
        )

        # Create Security Group
        # sec_group = ec2.SecurityGroup.from_security_group_id(
        #     self, 'launch-wizard-1','sg-0c77723568ab75889')
        sec_group = ec2.SecurityGroup(
            self, "sec-group-cdk-ec2", vpc=vpc, allow_all_outbound=True
        )

        # Create Security Group Ingress Rule
        sec_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access"
        )
        sec_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "allow HTTP access"
        )

        # Create Key Pair (use an existing key pair name for real usage)
        key_name = "vockey"

        # Create User Data Script
        user_data_script = ec2.UserData.for_linux()
        user_data_script.add_commands(
            "apt install -y apache2 git",
            "mkdir -p /var/www/html",  # Ensure the target directory exists
            "git clone https://github.com/flauts/websimple.git /var/www/html/websimple"  # Clone repository
        )

        # Create EC2 instance
        instance = ec2.Instance(
            self,
            "mv-cdk",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=vpc,
            security_group=sec_group,
            associate_public_ip_address=True,
            key_name=key_name,
            user_data=user_data_script
        )

        # Output Instance ID
        CfnOutput(self, "InstanceId", value=instance.instance_id)
        CfnOutput(self, "InstancePublicIP",
                  value=instance.instance_public_ip,
                  description="IP pública de la instancia"
                  )


        CfnOutput(self, "websimpleURL",
                  value=f"http://{instance.instance_public_ip}/websimple",
                  description="URL de websimple"
                  )

        CfnOutput(self, "webplantillaURL",
                  value=f"http://{instance.instance_public_ip}/webplantilla",
                  description="URL de webplantilla"
                  )
