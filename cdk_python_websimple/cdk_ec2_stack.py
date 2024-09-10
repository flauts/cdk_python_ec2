from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
    aws_s3_assets as assets,
    CfnOutput, DefaultStackSynthesizer,
)
import aws_cdk.aws_codebuild as codebuild

from constructs import Construct

class CdkEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Basic VPC
        vpc = ec2.Vpc.from_vpc_attributes(
            self,'vpc',
            vpc_id='vpc-00efc54137e6a9ef2',
            availability_zones=['us-east-1c','us-east-1f'],
            public_subnet_ids=['subnet-00c42d57b278f4b67','subnet-0a73734857f8400a0'],
        )
        # vpc = ec2.Vpc(
        #     self,
        #     "cdk-ec2-vpc",
        #     max_azs=2, #max_availabity zones
        #     subnet_configuration=[
        #         ec2.SubnetConfiguration(
        #             name="public-subnet-1",
        #             subnet_type=ec2.SubnetType.PUBLIC,
        #             cidr_mask=24,
        #         )
        #     ],
        # )
        existing_bucket_name = "cf-templates-iw9mos24h2jo-us-east-1"
        bucket = s3.Bucket.from_bucket_name(self, "ExistingBucket", existing_bucket_name)
        # cfn_role = iam.Role.from_role_arn(self, "LabRole", "arn:aws:iam::172067734210:role/LabRole")

        # Now use this bucket for assets
        # asset = assets.Asset(self, "MyAsset",
        #                      path="./",
        #                      bucket=bucket
        #                      )

        # Create Security Group
        sec_group = ec2.SecurityGroup.from_security_group_id(
            self, 'launch-wizard-1','sg-0c77723568ab75889')
        # sec_group = ec2.SecurityGroup(
        #     self, "sec-group-cdk-ec2", vpc=vpc, allow_all_outbound=True
        # )

        # Create Security Group Ingress Rule
        # sec_group.add_ingress_rule(
        #     ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access"
        # )
        # sec_group.add_ingress_rule(
        #     ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "allow HTTP access"
        # )

        # Create Key Pair (use an existing key pair name for real usage)
        key_name = ec2.KeyPair.from_key_pair_name(self,'cdk-ec2-keypair','vockey')
        existing_role_arn = "arn:aws:iam::172067734210:role/LabRole"
        self.synthesizer = DefaultStackSynthesizer(
            file_assets_bucket_name=existing_bucket_name,
            qualifier="cdk"
        )
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
            machine_image=ec2.MachineImage.generic_linux({"us-east-1":"ami-0aa28dab1f2852040"}),
            vpc=vpc,
            security_group=sec_group,
            associate_public_ip_address=True,
            key_pair=key_name,
            user_data=user_data_script,
        )
        bucket.grant_read_write(instance.role)

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
