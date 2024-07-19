r'''
# CDK construct lib

Welcome to Toumoro's AWS Service Wrapper CDK Construct Library! This library is designed to make it easy and efficient to deploy and manage AWS services within your CDK projects. Whether you're provisioning infrastructure for a simple web application or orchestrating a complex cloud-native architecture, this library aims to streamline your development process by providing high-level constructs for common AWS services.

## Features

* Simplified Service Provisioning: Easily create and configure AWS services using intuitive CDK constructs.
* Best Practices Built-In: Leverage pre-configured settings and defaults based on AWS best practices to ensure reliable and secure deployments.
* Modular and Extensible: Compose your infrastructure using modular constructs, allowing for flexibility and reusability across projects.

# Contributing to CDK Construct Toumoro

[Contributing](CONTRIBUTING.md)

# Examples

[Examples](examples/README.md)

# Documentation API

[API](API.md)

# Developpement Guide

[AWS CDK Design Guidelines](https://github.com/aws/aws-cdk/blob/main/docs/DESIGN_GUIDELINES.md)

## Naming Conventions

1. *Prefixes*:

   * *Cfn* for CloudFormation resources.
   * *Fn* for constructs generating CloudFormation functions.
   * *As* for abstract classes.
   * *I* for interfaces.
   * *Vpc* for constructs related to Virtual Private Cloud.
   * *Lambda* for constructs related to AWS Lambda.
   * Example: CfnStack, FnSub, Aspects, IVpc, VpcNetwork, LambdaFunction.
2. *Construct Names*:

   * Use descriptive names that reflect the purpose of the construct.
   * CamelCase for multi-word names.
   * Avoid abbreviations unless they are widely understood.
   * Example: VpcBasic, RdsAuroraMysqlServerLess.
3. *Property Names*:

   * Follow AWS resource naming conventions where applicable.
   * Use camelCase for property names.
   * Use clear and concise names that reflect the purpose of the property.
   * Example: bucketName, vpcId, functionName.
4. *Method Names*:

   * Use verbs or verb phrases to describe actions performed by methods.
   * Use camelCase.
   * Example: addBucketPolicy, createVpc, invokeLambda.
5. *Interface Names*:

   * Interfaces begging uppercase I are reserverd to AWS CDK library.
   * Start with an prefix TmI
   * Use clear and descriptive names.
   * Example: TmIInstance, TmISecurityGroup, TmIVpc.
6. *Module Names*:

   * Use lowercase with hyphens for separating words.
   * Be descriptive but concise.
   * Follow a hierarchy if necessary, e.g., aws-cdk.aws_s3 for S3-related constructs.
   * Example: aws-cdk.aws_s3, aws-cdk.aws_ec2, aws-cdk.aws_lambda.
7. *Variable Names*:

   * Use descriptive names.
   * CamelCase for multi-word names.
   * Keep variable names concise but meaningful.
   * Example: instanceCount, subnetIds, roleArn.
8. *Enum and Constant Names*:

   * Use uppercase for constants.
   * CamelCase for multi-word names.
   * Be descriptive about the purpose of the constant or enum.
   * Example: MAX_RETRIES, HTTP_STATUS_CODES, VPC_CONFIG.
9. *File Names*:

   * Use lowercase with hyphens for separating words.
   * Reflect the content of the file.
   * Include version numbers if necessary.
   * Example: s3-bucket-stack.ts, vpc-network.ts, lambda-function.ts.
10. *Documentation Comments*:

    * Use JSDoc or similar conventions to provide clear documentation for each construct, method, property, etc.
    * Ensure that the documentation is up-to-date and accurately reflects the purpose and usage of the code.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.pipelines as _aws_cdk_pipelines_ceddda9d
import constructs as _constructs_77d1e7e8


class TmPipeline(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmPipeline",
):
    '''(experimental) A CDK construct that creates a CodePipeline.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        pipeline_name: builtins.str,
        repo_branch: builtins.str,
        repo_name: builtins.str,
        primary_output_directory: typing.Optional[builtins.str] = None,
        synth_command: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the PipelineCdk class.

        :param scope: The parent construct.
        :param id: The name of the construct.
        :param pipeline_name: (experimental) The name of the pipeline.
        :param repo_branch: (experimental) The branch of the repository to use.
        :param repo_name: (experimental) The name of the repository.
        :param primary_output_directory: (experimental) The primary output directory.
        :param synth_command: (experimental) The command to run in the synth step.

        :default: - No default properties.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a993414424d3e58108b1515d1ae43df55fcea9a5bf26c77d45647cea67364f8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TmPipelineProps(
            pipeline_name=pipeline_name,
            repo_branch=repo_branch,
            repo_name=repo_name,
            primary_output_directory=primary_output_directory,
            synth_command=synth_command,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> _aws_cdk_pipelines_ceddda9d.CodePipeline:
        '''(experimental) The CodePipeline created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodePipeline, jsii.get(self, "pipeline"))


@jsii.data_type(
    jsii_type="tm-cdk-constructs.TmPipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "pipeline_name": "pipelineName",
        "repo_branch": "repoBranch",
        "repo_name": "repoName",
        "primary_output_directory": "primaryOutputDirectory",
        "synth_command": "synthCommand",
    },
)
class TmPipelineProps:
    def __init__(
        self,
        *,
        pipeline_name: builtins.str,
        repo_branch: builtins.str,
        repo_name: builtins.str,
        primary_output_directory: typing.Optional[builtins.str] = None,
        synth_command: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param pipeline_name: (experimental) The name of the pipeline.
        :param repo_branch: (experimental) The branch of the repository to use.
        :param repo_name: (experimental) The name of the repository.
        :param primary_output_directory: (experimental) The primary output directory.
        :param synth_command: (experimental) The command to run in the synth step.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c90f448d2c851abcb766597516c1d94417ef3eed41e3bc82a985a84bd6ff2854)
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
            check_type(argname="argument repo_branch", value=repo_branch, expected_type=type_hints["repo_branch"])
            check_type(argname="argument repo_name", value=repo_name, expected_type=type_hints["repo_name"])
            check_type(argname="argument primary_output_directory", value=primary_output_directory, expected_type=type_hints["primary_output_directory"])
            check_type(argname="argument synth_command", value=synth_command, expected_type=type_hints["synth_command"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "pipeline_name": pipeline_name,
            "repo_branch": repo_branch,
            "repo_name": repo_name,
        }
        if primary_output_directory is not None:
            self._values["primary_output_directory"] = primary_output_directory
        if synth_command is not None:
            self._values["synth_command"] = synth_command

    @builtins.property
    def pipeline_name(self) -> builtins.str:
        '''(experimental) The name of the pipeline.

        :stability: experimental
        '''
        result = self._values.get("pipeline_name")
        assert result is not None, "Required property 'pipeline_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo_branch(self) -> builtins.str:
        '''(experimental) The branch of the repository to use.

        :stability: experimental
        '''
        result = self._values.get("repo_branch")
        assert result is not None, "Required property 'repo_branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo_name(self) -> builtins.str:
        '''(experimental) The name of the repository.

        :stability: experimental
        '''
        result = self._values.get("repo_name")
        assert result is not None, "Required property 'repo_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def primary_output_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) The primary output directory.

        :stability: experimental
        '''
        result = self._values.get("primary_output_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synth_command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The command to run in the synth step.

        :stability: experimental
        '''
        result = self._values.get("synth_command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TmPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TmRdsAuroraMysqlServerless(
    _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmRdsAuroraMysqlServerless",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        enable_global: typing.Optional[builtins.bool] = None,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
        credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        enable_data_api: typing.Optional[builtins.bool] = None,
        iam_authentication: typing.Optional[builtins.bool] = None,
        instance_identifier_base: typing.Optional[builtins.str] = None,
        instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
        instances: typing.Optional[jsii.Number] = None,
        instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
        monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
        parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
        serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
        subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    ) -> None:
        '''(experimental) Represents a class that creates an RDS Aurora MySQL Serverless database cluster.

        :param scope: -
        :param id: -
        :param enable_global: (experimental) Enable the creation of a Global Cluster for the RDS cluster.
        :param engine: What kind of database to start.
        :param backtrack_window: The number of seconds to set a cluster's target backtrack window to. This feature is only supported by the Aurora MySQL database engine and cannot be enabled on existing clusters. Default: 0 seconds (no backtrack)
        :param backup: Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - no log exports
        :param cloudwatch_logs_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: - logs never expire
        :param cloudwatch_logs_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - a new role is created.
        :param cluster_identifier: An optional identifier for the cluster. Default: - A name is automatically generated.
        :param copy_tags_to_snapshot: Whether to copy tags to the snapshot when a snapshot is created. Default: - true
        :param credentials: Credentials for the administrative user. Default: - A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password
        :param default_database_name: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
        :param deletion_protection: Indicates whether the DB cluster should have deletion protection enabled. Default: - true if ``removalPolicy`` is RETAIN, ``undefined`` otherwise, which will not enable deletion protection. To disable deletion protection after it has been enabled, you must explicitly set this value to ``false``.
        :param domain: Directory ID for associating the DB cluster with a specific Active Directory. Necessary for enabling Kerberos authentication. If specified, the DB cluster joins the given Active Directory, enabling Kerberos authentication. If not specified, the DB cluster will not be associated with any Active Directory, and Kerberos authentication will not be enabled. Default: - DB cluster is not associated with an Active Directory; Kerberos authentication is not enabled.
        :param domain_role: The IAM role to be used when making API calls to the Directory Service. The role needs the AWS-managed policy ``AmazonRDSDirectoryServiceAccess`` or equivalent. Default: - If ``DatabaseClusterBaseProps.domain`` is specified, a role with the ``AmazonRDSDirectoryServiceAccess`` policy is automatically created.
        :param enable_data_api: Whether to enable the Data API for the cluster. Default: - false
        :param iam_authentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
        :param instance_identifier_base: Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - clusterIdentifier is used with the word "Instance" appended. If clusterIdentifier is not provided, the identifier is automatically generated.
        :param instance_props: (deprecated) Settings for the individual instances that are launched.
        :param instances: (deprecated) How many replicas/instances to create. Has to be at least 1. Default: 2
        :param instance_update_behaviour: The ordering of updates for instances. Default: InstanceUpdateBehaviour.BULK
        :param monitoring_interval: The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instances. Default: no enhanced monitoring
        :param monitoring_role: Role that will be used to manage DB instances monitoring. Default: - A role is automatically created for you
        :param network_type: The network type of the DB instance. Default: - IPV4
        :param parameter_group: Additional parameters to pass to the database engine. Default: - No parameter group.
        :param parameters: The parameters in the DBClusterParameterGroup to create automatically. You can only specify parameterGroup or parameters but not both. You need to use a versioned engine to auto-generate a DBClusterParameterGroup. Default: - None
        :param port: What port to listen on. Default: - The default for the engine is used.
        :param preferred_maintenance_window: A preferred maintenance window day/time range. Should be specified as a range ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC). Example: 'Sun:23:45-Mon:00:15' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param readers: A list of instances to create as cluster reader instances. Default: - no readers are created. The cluster will have a single writer/reader
        :param removal_policy: The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        :param s3_export_buckets: S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportRole`` is used. For MySQL: Default: - None
        :param s3_export_role: Role that will be associated with this DB cluster to enable S3 export. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportBuckets`` is used. For MySQL: Default: - New role is created if ``s3ExportBuckets`` is set, no role is defined otherwise
        :param s3_import_buckets: S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportRole`` is used. For MySQL: Default: - None
        :param s3_import_role: Role that will be associated with this DB cluster to enable S3 import. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportBuckets`` is used. For MySQL: Default: - New role is created if ``s3ImportBuckets`` is set, no role is defined otherwise
        :param security_groups: Security group. Default: a new security group is created.
        :param serverless_v2_max_capacity: The maximum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 40, 40.5, 41, and so on. The largest value that you can use is 128 (256GB). The maximum capacity must be higher than 0.5 ACUs. Default: 2
        :param serverless_v2_min_capacity: The minimum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 8, 8.5, 9, and so on. The smallest value that you can use is 0.5. Default: 0.5
        :param storage_encrypted: Whether to enable storage encryption. Default: - true if storageEncryptionKey is provided, false otherwise
        :param storage_encryption_key: The KMS key for storage encryption. If specified, ``storageEncrypted`` will be set to ``true``. Default: - if storageEncrypted is true then the default master key, no key otherwise
        :param storage_type: The storage type to be associated with the DB cluster. Default: - DBClusterStorageType.AURORA_IOPT1
        :param subnet_group: Existing subnet group for the cluster. Default: - a new subnet group will be created.
        :param vpc: What subnets to run the RDS instances in. Must be at least 2 subnets in two different AZs.
        :param vpc_subnets: Where to place the instances within the VPC. Default: - the Vpc default strategy if not specified.
        :param writer: The instance to use for the cluster writer. Default: required if instanceProps is not provided

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc939679af82c57cdfc24824fb9ec6ef0580d01390aa5c263b878d67d4912115)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TmRdsAuroraMysqlServerlessProps(
            enable_global=enable_global,
            engine=engine,
            backtrack_window=backtrack_window,
            backup=backup,
            cloudwatch_logs_exports=cloudwatch_logs_exports,
            cloudwatch_logs_retention=cloudwatch_logs_retention,
            cloudwatch_logs_retention_role=cloudwatch_logs_retention_role,
            cluster_identifier=cluster_identifier,
            copy_tags_to_snapshot=copy_tags_to_snapshot,
            credentials=credentials,
            default_database_name=default_database_name,
            deletion_protection=deletion_protection,
            domain=domain,
            domain_role=domain_role,
            enable_data_api=enable_data_api,
            iam_authentication=iam_authentication,
            instance_identifier_base=instance_identifier_base,
            instance_props=instance_props,
            instances=instances,
            instance_update_behaviour=instance_update_behaviour,
            monitoring_interval=monitoring_interval,
            monitoring_role=monitoring_role,
            network_type=network_type,
            parameter_group=parameter_group,
            parameters=parameters,
            port=port,
            preferred_maintenance_window=preferred_maintenance_window,
            readers=readers,
            removal_policy=removal_policy,
            s3_export_buckets=s3_export_buckets,
            s3_export_role=s3_export_role,
            s3_import_buckets=s3_import_buckets,
            s3_import_role=s3_import_role,
            security_groups=security_groups,
            serverless_v2_max_capacity=serverless_v2_max_capacity,
            serverless_v2_min_capacity=serverless_v2_min_capacity,
            storage_encrypted=storage_encrypted,
            storage_encryption_key=storage_encryption_key,
            storage_type=storage_type,
            subnet_group=subnet_group,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            writer=writer,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="tm-cdk-constructs.TmRdsAuroraMysqlServerlessProps",
    jsii_struct_bases=[_aws_cdk_aws_rds_ceddda9d.DatabaseClusterProps],
    name_mapping={
        "engine": "engine",
        "backtrack_window": "backtrackWindow",
        "backup": "backup",
        "cloudwatch_logs_exports": "cloudwatchLogsExports",
        "cloudwatch_logs_retention": "cloudwatchLogsRetention",
        "cloudwatch_logs_retention_role": "cloudwatchLogsRetentionRole",
        "cluster_identifier": "clusterIdentifier",
        "copy_tags_to_snapshot": "copyTagsToSnapshot",
        "credentials": "credentials",
        "default_database_name": "defaultDatabaseName",
        "deletion_protection": "deletionProtection",
        "domain": "domain",
        "domain_role": "domainRole",
        "enable_data_api": "enableDataApi",
        "iam_authentication": "iamAuthentication",
        "instance_identifier_base": "instanceIdentifierBase",
        "instance_props": "instanceProps",
        "instances": "instances",
        "instance_update_behaviour": "instanceUpdateBehaviour",
        "monitoring_interval": "monitoringInterval",
        "monitoring_role": "monitoringRole",
        "network_type": "networkType",
        "parameter_group": "parameterGroup",
        "parameters": "parameters",
        "port": "port",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "readers": "readers",
        "removal_policy": "removalPolicy",
        "s3_export_buckets": "s3ExportBuckets",
        "s3_export_role": "s3ExportRole",
        "s3_import_buckets": "s3ImportBuckets",
        "s3_import_role": "s3ImportRole",
        "security_groups": "securityGroups",
        "serverless_v2_max_capacity": "serverlessV2MaxCapacity",
        "serverless_v2_min_capacity": "serverlessV2MinCapacity",
        "storage_encrypted": "storageEncrypted",
        "storage_encryption_key": "storageEncryptionKey",
        "storage_type": "storageType",
        "subnet_group": "subnetGroup",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "writer": "writer",
        "enable_global": "enableGlobal",
    },
)
class TmRdsAuroraMysqlServerlessProps(_aws_cdk_aws_rds_ceddda9d.DatabaseClusterProps):
    def __init__(
        self,
        *,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
        credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        enable_data_api: typing.Optional[builtins.bool] = None,
        iam_authentication: typing.Optional[builtins.bool] = None,
        instance_identifier_base: typing.Optional[builtins.str] = None,
        instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
        instances: typing.Optional[jsii.Number] = None,
        instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
        monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
        parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
        serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
        subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
        enable_global: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param engine: What kind of database to start.
        :param backtrack_window: The number of seconds to set a cluster's target backtrack window to. This feature is only supported by the Aurora MySQL database engine and cannot be enabled on existing clusters. Default: 0 seconds (no backtrack)
        :param backup: Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - no log exports
        :param cloudwatch_logs_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: - logs never expire
        :param cloudwatch_logs_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - a new role is created.
        :param cluster_identifier: An optional identifier for the cluster. Default: - A name is automatically generated.
        :param copy_tags_to_snapshot: Whether to copy tags to the snapshot when a snapshot is created. Default: - true
        :param credentials: Credentials for the administrative user. Default: - A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password
        :param default_database_name: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
        :param deletion_protection: Indicates whether the DB cluster should have deletion protection enabled. Default: - true if ``removalPolicy`` is RETAIN, ``undefined`` otherwise, which will not enable deletion protection. To disable deletion protection after it has been enabled, you must explicitly set this value to ``false``.
        :param domain: Directory ID for associating the DB cluster with a specific Active Directory. Necessary for enabling Kerberos authentication. If specified, the DB cluster joins the given Active Directory, enabling Kerberos authentication. If not specified, the DB cluster will not be associated with any Active Directory, and Kerberos authentication will not be enabled. Default: - DB cluster is not associated with an Active Directory; Kerberos authentication is not enabled.
        :param domain_role: The IAM role to be used when making API calls to the Directory Service. The role needs the AWS-managed policy ``AmazonRDSDirectoryServiceAccess`` or equivalent. Default: - If ``DatabaseClusterBaseProps.domain`` is specified, a role with the ``AmazonRDSDirectoryServiceAccess`` policy is automatically created.
        :param enable_data_api: Whether to enable the Data API for the cluster. Default: - false
        :param iam_authentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
        :param instance_identifier_base: Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - clusterIdentifier is used with the word "Instance" appended. If clusterIdentifier is not provided, the identifier is automatically generated.
        :param instance_props: (deprecated) Settings for the individual instances that are launched.
        :param instances: (deprecated) How many replicas/instances to create. Has to be at least 1. Default: 2
        :param instance_update_behaviour: The ordering of updates for instances. Default: InstanceUpdateBehaviour.BULK
        :param monitoring_interval: The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instances. Default: no enhanced monitoring
        :param monitoring_role: Role that will be used to manage DB instances monitoring. Default: - A role is automatically created for you
        :param network_type: The network type of the DB instance. Default: - IPV4
        :param parameter_group: Additional parameters to pass to the database engine. Default: - No parameter group.
        :param parameters: The parameters in the DBClusterParameterGroup to create automatically. You can only specify parameterGroup or parameters but not both. You need to use a versioned engine to auto-generate a DBClusterParameterGroup. Default: - None
        :param port: What port to listen on. Default: - The default for the engine is used.
        :param preferred_maintenance_window: A preferred maintenance window day/time range. Should be specified as a range ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC). Example: 'Sun:23:45-Mon:00:15' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param readers: A list of instances to create as cluster reader instances. Default: - no readers are created. The cluster will have a single writer/reader
        :param removal_policy: The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        :param s3_export_buckets: S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportRole`` is used. For MySQL: Default: - None
        :param s3_export_role: Role that will be associated with this DB cluster to enable S3 export. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportBuckets`` is used. For MySQL: Default: - New role is created if ``s3ExportBuckets`` is set, no role is defined otherwise
        :param s3_import_buckets: S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportRole`` is used. For MySQL: Default: - None
        :param s3_import_role: Role that will be associated with this DB cluster to enable S3 import. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportBuckets`` is used. For MySQL: Default: - New role is created if ``s3ImportBuckets`` is set, no role is defined otherwise
        :param security_groups: Security group. Default: a new security group is created.
        :param serverless_v2_max_capacity: The maximum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 40, 40.5, 41, and so on. The largest value that you can use is 128 (256GB). The maximum capacity must be higher than 0.5 ACUs. Default: 2
        :param serverless_v2_min_capacity: The minimum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 8, 8.5, 9, and so on. The smallest value that you can use is 0.5. Default: 0.5
        :param storage_encrypted: Whether to enable storage encryption. Default: - true if storageEncryptionKey is provided, false otherwise
        :param storage_encryption_key: The KMS key for storage encryption. If specified, ``storageEncrypted`` will be set to ``true``. Default: - if storageEncrypted is true then the default master key, no key otherwise
        :param storage_type: The storage type to be associated with the DB cluster. Default: - DBClusterStorageType.AURORA_IOPT1
        :param subnet_group: Existing subnet group for the cluster. Default: - a new subnet group will be created.
        :param vpc: What subnets to run the RDS instances in. Must be at least 2 subnets in two different AZs.
        :param vpc_subnets: Where to place the instances within the VPC. Default: - the Vpc default strategy if not specified.
        :param writer: The instance to use for the cluster writer. Default: required if instanceProps is not provided
        :param enable_global: (experimental) Enable the creation of a Global Cluster for the RDS cluster.

        :stability: experimental
        '''
        if isinstance(backup, dict):
            backup = _aws_cdk_aws_rds_ceddda9d.BackupProps(**backup)
        if isinstance(instance_props, dict):
            instance_props = _aws_cdk_aws_rds_ceddda9d.InstanceProps(**instance_props)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb6185862d0dbafb21639371b5cfdd31758e49cf957284e1d423cbd3bf7cc8a)
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument backtrack_window", value=backtrack_window, expected_type=type_hints["backtrack_window"])
            check_type(argname="argument backup", value=backup, expected_type=type_hints["backup"])
            check_type(argname="argument cloudwatch_logs_exports", value=cloudwatch_logs_exports, expected_type=type_hints["cloudwatch_logs_exports"])
            check_type(argname="argument cloudwatch_logs_retention", value=cloudwatch_logs_retention, expected_type=type_hints["cloudwatch_logs_retention"])
            check_type(argname="argument cloudwatch_logs_retention_role", value=cloudwatch_logs_retention_role, expected_type=type_hints["cloudwatch_logs_retention_role"])
            check_type(argname="argument cluster_identifier", value=cluster_identifier, expected_type=type_hints["cluster_identifier"])
            check_type(argname="argument copy_tags_to_snapshot", value=copy_tags_to_snapshot, expected_type=type_hints["copy_tags_to_snapshot"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument default_database_name", value=default_database_name, expected_type=type_hints["default_database_name"])
            check_type(argname="argument deletion_protection", value=deletion_protection, expected_type=type_hints["deletion_protection"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument domain_role", value=domain_role, expected_type=type_hints["domain_role"])
            check_type(argname="argument enable_data_api", value=enable_data_api, expected_type=type_hints["enable_data_api"])
            check_type(argname="argument iam_authentication", value=iam_authentication, expected_type=type_hints["iam_authentication"])
            check_type(argname="argument instance_identifier_base", value=instance_identifier_base, expected_type=type_hints["instance_identifier_base"])
            check_type(argname="argument instance_props", value=instance_props, expected_type=type_hints["instance_props"])
            check_type(argname="argument instances", value=instances, expected_type=type_hints["instances"])
            check_type(argname="argument instance_update_behaviour", value=instance_update_behaviour, expected_type=type_hints["instance_update_behaviour"])
            check_type(argname="argument monitoring_interval", value=monitoring_interval, expected_type=type_hints["monitoring_interval"])
            check_type(argname="argument monitoring_role", value=monitoring_role, expected_type=type_hints["monitoring_role"])
            check_type(argname="argument network_type", value=network_type, expected_type=type_hints["network_type"])
            check_type(argname="argument parameter_group", value=parameter_group, expected_type=type_hints["parameter_group"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument preferred_maintenance_window", value=preferred_maintenance_window, expected_type=type_hints["preferred_maintenance_window"])
            check_type(argname="argument readers", value=readers, expected_type=type_hints["readers"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument s3_export_buckets", value=s3_export_buckets, expected_type=type_hints["s3_export_buckets"])
            check_type(argname="argument s3_export_role", value=s3_export_role, expected_type=type_hints["s3_export_role"])
            check_type(argname="argument s3_import_buckets", value=s3_import_buckets, expected_type=type_hints["s3_import_buckets"])
            check_type(argname="argument s3_import_role", value=s3_import_role, expected_type=type_hints["s3_import_role"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument serverless_v2_max_capacity", value=serverless_v2_max_capacity, expected_type=type_hints["serverless_v2_max_capacity"])
            check_type(argname="argument serverless_v2_min_capacity", value=serverless_v2_min_capacity, expected_type=type_hints["serverless_v2_min_capacity"])
            check_type(argname="argument storage_encrypted", value=storage_encrypted, expected_type=type_hints["storage_encrypted"])
            check_type(argname="argument storage_encryption_key", value=storage_encryption_key, expected_type=type_hints["storage_encryption_key"])
            check_type(argname="argument storage_type", value=storage_type, expected_type=type_hints["storage_type"])
            check_type(argname="argument subnet_group", value=subnet_group, expected_type=type_hints["subnet_group"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument writer", value=writer, expected_type=type_hints["writer"])
            check_type(argname="argument enable_global", value=enable_global, expected_type=type_hints["enable_global"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "engine": engine,
        }
        if backtrack_window is not None:
            self._values["backtrack_window"] = backtrack_window
        if backup is not None:
            self._values["backup"] = backup
        if cloudwatch_logs_exports is not None:
            self._values["cloudwatch_logs_exports"] = cloudwatch_logs_exports
        if cloudwatch_logs_retention is not None:
            self._values["cloudwatch_logs_retention"] = cloudwatch_logs_retention
        if cloudwatch_logs_retention_role is not None:
            self._values["cloudwatch_logs_retention_role"] = cloudwatch_logs_retention_role
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if copy_tags_to_snapshot is not None:
            self._values["copy_tags_to_snapshot"] = copy_tags_to_snapshot
        if credentials is not None:
            self._values["credentials"] = credentials
        if default_database_name is not None:
            self._values["default_database_name"] = default_database_name
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if domain is not None:
            self._values["domain"] = domain
        if domain_role is not None:
            self._values["domain_role"] = domain_role
        if enable_data_api is not None:
            self._values["enable_data_api"] = enable_data_api
        if iam_authentication is not None:
            self._values["iam_authentication"] = iam_authentication
        if instance_identifier_base is not None:
            self._values["instance_identifier_base"] = instance_identifier_base
        if instance_props is not None:
            self._values["instance_props"] = instance_props
        if instances is not None:
            self._values["instances"] = instances
        if instance_update_behaviour is not None:
            self._values["instance_update_behaviour"] = instance_update_behaviour
        if monitoring_interval is not None:
            self._values["monitoring_interval"] = monitoring_interval
        if monitoring_role is not None:
            self._values["monitoring_role"] = monitoring_role
        if network_type is not None:
            self._values["network_type"] = network_type
        if parameter_group is not None:
            self._values["parameter_group"] = parameter_group
        if parameters is not None:
            self._values["parameters"] = parameters
        if port is not None:
            self._values["port"] = port
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if readers is not None:
            self._values["readers"] = readers
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if s3_export_buckets is not None:
            self._values["s3_export_buckets"] = s3_export_buckets
        if s3_export_role is not None:
            self._values["s3_export_role"] = s3_export_role
        if s3_import_buckets is not None:
            self._values["s3_import_buckets"] = s3_import_buckets
        if s3_import_role is not None:
            self._values["s3_import_role"] = s3_import_role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if serverless_v2_max_capacity is not None:
            self._values["serverless_v2_max_capacity"] = serverless_v2_max_capacity
        if serverless_v2_min_capacity is not None:
            self._values["serverless_v2_min_capacity"] = serverless_v2_min_capacity
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if storage_encryption_key is not None:
            self._values["storage_encryption_key"] = storage_encryption_key
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if subnet_group is not None:
            self._values["subnet_group"] = subnet_group
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if writer is not None:
            self._values["writer"] = writer
        if enable_global is not None:
            self._values["enable_global"] = enable_global

    @builtins.property
    def engine(self) -> _aws_cdk_aws_rds_ceddda9d.IClusterEngine:
        '''What kind of database to start.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IClusterEngine, result)

    @builtins.property
    def backtrack_window(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The number of seconds to set a cluster's target backtrack window to.

        This feature is only supported by the Aurora MySQL database engine and
        cannot be enabled on existing clusters.

        :default: 0 seconds (no backtrack)

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Managing.Backtrack.html
        '''
        result = self._values.get("backtrack_window")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def backup(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps]:
        '''Backup settings.

        :default:

        - Backup retention period for automated backups is 1 day.
        Backup preferred window is set to a 30-minute window selected at random from an
        8-hour block of time for each AWS Region, occurring on a random day of the week.

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html#USER_WorkingWithAutomatedBackups.BackupWindow
        '''
        result = self._values.get("backup")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps], result)

    @builtins.property
    def cloudwatch_logs_exports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of log types that need to be enabled for exporting to CloudWatch Logs.

        :default: - no log exports
        '''
        result = self._values.get("cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cloudwatch_logs_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``Infinity``.

        :default: - logs never expire
        '''
        result = self._values.get("cloudwatch_logs_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def cloudwatch_logs_retention_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

        :default: - a new role is created.
        '''
        result = self._values.get("cloudwatch_logs_retention_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''An optional identifier for the cluster.

        :default: - A name is automatically generated.
        '''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_tags_to_snapshot(self) -> typing.Optional[builtins.bool]:
        '''Whether to copy tags to the snapshot when a snapshot is created.

        :default: - true
        '''
        result = self._values.get("copy_tags_to_snapshot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def credentials(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials]:
        '''Credentials for the administrative user.

        :default: - A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials], result)

    @builtins.property
    def default_database_name(self) -> typing.Optional[builtins.str]:
        '''Name of a database which is automatically created inside the cluster.

        :default: - Database is not created in cluster.
        '''
        result = self._values.get("default_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deletion_protection(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the DB cluster should have deletion protection enabled.

        :default:

        - true if ``removalPolicy`` is RETAIN, ``undefined`` otherwise, which will not enable deletion protection.
        To disable deletion protection after it has been enabled, you must explicitly set this value to ``false``.
        '''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Directory ID for associating the DB cluster with a specific Active Directory.

        Necessary for enabling Kerberos authentication. If specified, the DB cluster joins the given Active Directory, enabling Kerberos authentication.
        If not specified, the DB cluster will not be associated with any Active Directory, and Kerberos authentication will not be enabled.

        :default: - DB cluster is not associated with an Active Directory; Kerberos authentication is not enabled.
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role to be used when making API calls to the Directory Service.

        The role needs the AWS-managed policy
        ``AmazonRDSDirectoryServiceAccess`` or equivalent.

        :default: - If ``DatabaseClusterBaseProps.domain`` is specified, a role with the ``AmazonRDSDirectoryServiceAccess`` policy is automatically created.
        '''
        result = self._values.get("domain_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def enable_data_api(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable the Data API for the cluster.

        :default: - false
        '''
        result = self._values.get("enable_data_api")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def iam_authentication(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts.

        :default: false
        '''
        result = self._values.get("iam_authentication")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_identifier_base(self) -> typing.Optional[builtins.str]:
        '''Base identifier for instances.

        Every replica is named by appending the replica number to this string, 1-based.

        :default:

        - clusterIdentifier is used with the word "Instance" appended.
        If clusterIdentifier is not provided, the identifier is automatically generated.
        '''
        result = self._values.get("instance_identifier_base")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceProps]:
        '''(deprecated) Settings for the individual instances that are launched.

        :deprecated: - use writer and readers instead

        :stability: deprecated
        '''
        result = self._values.get("instance_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceProps], result)

    @builtins.property
    def instances(self) -> typing.Optional[jsii.Number]:
        '''(deprecated) How many replicas/instances to create.

        Has to be at least 1.

        :default: 2

        :deprecated: - use writer and readers instead

        :stability: deprecated
        '''
        result = self._values.get("instances")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_update_behaviour(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour]:
        '''The ordering of updates for instances.

        :default: InstanceUpdateBehaviour.BULK
        '''
        result = self._values.get("instance_update_behaviour")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour], result)

    @builtins.property
    def monitoring_interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instances.

        :default: no enhanced monitoring
        '''
        result = self._values.get("monitoring_interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def monitoring_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role that will be used to manage DB instances monitoring.

        :default: - A role is automatically created for you
        '''
        result = self._values.get("monitoring_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def network_type(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType]:
        '''The network type of the DB instance.

        :default: - IPV4
        '''
        result = self._values.get("network_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType], result)

    @builtins.property
    def parameter_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup]:
        '''Additional parameters to pass to the database engine.

        :default: - No parameter group.
        '''
        result = self._values.get("parameter_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The parameters in the DBClusterParameterGroup to create automatically.

        You can only specify parameterGroup or parameters but not both.
        You need to use a versioned engine to auto-generate a DBClusterParameterGroup.

        :default: - None
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''What port to listen on.

        :default: - The default for the engine is used.
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''A preferred maintenance window day/time range. Should be specified as a range ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC).

        Example: 'Sun:23:45-Mon:00:15'

        :default:

        - 30-minute window selected at random from an 8-hour block of time for
        each AWS Region, occurring on a random day of the week.

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_UpgradeDBInstance.Maintenance.html#Concepts.DBMaintenance
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]]:
        '''A list of instances to create as cluster reader instances.

        :default: - no readers are created. The cluster will have a single writer/reader
        '''
        result = self._values.get("readers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update.

        :default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def s3_export_buckets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]]:
        '''S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ExportRole`` is used.

        For MySQL:

        :default: - None

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/postgresql-s3-export.html
        '''
        result = self._values.get("s3_export_buckets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]], result)

    @builtins.property
    def s3_export_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role that will be associated with this DB cluster to enable S3 export.

        This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ExportBuckets`` is used.

        For MySQL:

        :default: - New role is created if ``s3ExportBuckets`` is set, no role is defined otherwise

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/postgresql-s3-export.html
        '''
        result = self._values.get("s3_export_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def s3_import_buckets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]]:
        '''S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ImportRole`` is used.

        For MySQL:

        :default: - None

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Migrating.html
        '''
        result = self._values.get("s3_import_buckets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]], result)

    @builtins.property
    def s3_import_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role that will be associated with this DB cluster to enable S3 import.

        This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ImportBuckets`` is used.

        For MySQL:

        :default: - New role is created if ``s3ImportBuckets`` is set, no role is defined otherwise

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Migrating.html
        '''
        result = self._values.get("s3_import_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Security group.

        :default: a new security group is created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def serverless_v2_max_capacity(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster.

        You can specify ACU values in half-step increments, such as 40, 40.5, 41, and so on.
        The largest value that you can use is 128 (256GB).

        The maximum capacity must be higher than 0.5 ACUs.

        :default: 2

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.setting-capacity.html#aurora-serverless-v2.max_capacity_considerations
        '''
        result = self._values.get("serverless_v2_max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def serverless_v2_min_capacity(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster.

        You can specify ACU values in half-step increments, such as 8, 8.5, 9, and so on.
        The smallest value that you can use is 0.5.

        :default: 0.5

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.setting-capacity.html#aurora-serverless-v2.max_capacity_considerations
        '''
        result = self._values.get("serverless_v2_min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_encrypted(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable storage encryption.

        :default: - true if storageEncryptionKey is provided, false otherwise
        '''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def storage_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key for storage encryption.

        If specified, ``storageEncrypted`` will be set to ``true``.

        :default: - if storageEncrypted is true then the default master key, no key otherwise
        '''
        result = self._values.get("storage_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def storage_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType]:
        '''The storage type to be associated with the DB cluster.

        :default: - DBClusterStorageType.AURORA_IOPT1
        '''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType], result)

    @builtins.property
    def subnet_group(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup]:
        '''Existing subnet group for the cluster.

        :default: - a new subnet group will be created.
        '''
        result = self._values.get("subnet_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''What subnets to run the RDS instances in.

        Must be at least 2 subnets in two different AZs.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the instances within the VPC.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def writer(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]:
        '''The instance to use for the cluster writer.

        :default: required if instanceProps is not provided
        '''
        result = self._values.get("writer")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance], result)

    @builtins.property
    def enable_global(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the creation of a Global Cluster for the RDS cluster.

        :stability: experimental
        '''
        result = self._values.get("enable_global")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TmRdsAuroraMysqlServerlessProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TmVpcBase(
    _aws_cdk_aws_ec2_ceddda9d.Vpc,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmVpcBase",
):
    '''(experimental) A VPC construct that creates a VPC with public and private subnets.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        range_cidr: builtins.str,
        enable_endpoints: typing.Optional[typing.Sequence[builtins.str]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        cidr: typing.Optional[builtins.str] = None,
        create_internet_gateway: typing.Optional[builtins.bool] = None,
        default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
        enable_dns_hostnames: typing.Optional[builtins.bool] = None,
        enable_dns_support: typing.Optional[builtins.bool] = None,
        flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        ip_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol] = None,
        ipv6_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        reserved_azs: typing.Optional[jsii.Number] = None,
        restrict_default_security_group: typing.Optional[builtins.bool] = None,
        subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpn_gateway: typing.Optional[builtins.bool] = None,
        vpn_gateway_asn: typing.Optional[jsii.Number] = None,
        vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) The VPC created by the construct.

        :param scope: -
        :param id: -
        :param range_cidr: (experimental) The CIDR block for the VPC.
        :param enable_endpoints: (experimental) Indicates whether to enable the S3 endpoint for the VPC.
        :param availability_zones: Availability zones this VPC spans. Specify this option only if you do not specify ``maxAzs``. Default: - a subset of AZs of the stack
        :param cidr: (deprecated) The CIDR range to use for the VPC, e.g. '10.0.0.0/16'. Should be a minimum of /28 and maximum size of /16. The range will be split across all subnets per Availability Zone. Default: Vpc.DEFAULT_CIDR_RANGE
        :param create_internet_gateway: If set to false then disable the creation of the default internet gateway. Default: true
        :param default_instance_tenancy: The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy. Default: DefaultInstanceTenancy.Default (shared) tenancy
        :param enable_dns_hostnames: Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true. Default: true
        :param enable_dns_support: Indicates whether the DNS resolution is supported for the VPC. If this attribute is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames to IP addresses is not enabled. If this attribute is true, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC IPv4 network range plus two will succeed. Default: true
        :param flow_logs: Flow logs to add to this VPC. Default: - No flow logs.
        :param gateway_endpoints: Gateway endpoints to add to this VPC. Default: - None.
        :param ip_addresses: The Provider to use to allocate IPv4 Space to your VPC. Options include static allocation or from a pool. Note this is specific to IPv4 addresses. Default: ec2.IpAddresses.cidr
        :param ip_protocol: The protocol of the vpc. Options are IPv4 only or dual stack. Default: IpProtocol.IPV4_ONLY
        :param ipv6_addresses: The Provider to use to allocate IPv6 Space to your VPC. Options include amazon provided CIDR block. Note this is specific to IPv6 addresses. Default: Ipv6Addresses.amazonProvided
        :param max_azs: Define the maximum number of AZs to use in this region. If the region has more AZs than you want to use (for example, because of EIP limits), pick a lower number here. The AZs will be sorted and picked from the start of the list. If you pick a higher number than the number of AZs in the region, all AZs in the region will be selected. To use "all AZs" available to your account, use a high number (such as 99). Be aware that environment-agnostic stacks will be created with access to only 2 AZs, so to use more than 2 AZs, be sure to specify the account and region on your stack. Specify this option only if you do not specify ``availabilityZones``. Default: 3
        :param nat_gateway_provider: What type of NAT provider to use. Select between NAT gateways or NAT instances. NAT gateways may not be available in all AWS regions. Default: NatProvider.gateway()
        :param nat_gateways: The number of NAT Gateways/Instances to create. The type of NAT gateway or instance will be determined by the ``natGatewayProvider`` parameter. You can set this number lower than the number of Availability Zones in your VPC in order to save on NAT cost. Be aware you may be charged for cross-AZ data traffic instead. Default: - One NAT gateway/instance per Availability Zone
        :param nat_gateway_subnets: Configures the subnets which will have NAT Gateways/Instances. You can pick a specific group of subnets by specifying the group name; the picked subnets must be public subnets. Only necessary if you have more than one public subnet group. Default: - All public subnets.
        :param reserved_azs: Define the number of AZs to reserve. When specified, the IP space is reserved for the azs but no actual resources are provisioned. Default: 0
        :param restrict_default_security_group: If set to true then the default inbound & outbound rules will be removed from the default security group. Default: true if '@aws-cdk/aws-ec2:restrictDefaultSecurityGroup' is enabled, false otherwise
        :param subnet_configuration: Configure the subnets to build for each AZ. Each entry in this list configures a Subnet Group; each group will contain a subnet for each Availability Zone. For example, if you want 1 public subnet, 1 private subnet, and 1 isolated subnet in each AZ provide the following:: new ec2.Vpc(this, 'VPC', { subnetConfiguration: [ { cidrMask: 24, name: 'ingress', subnetType: ec2.SubnetType.PUBLIC, }, { cidrMask: 24, name: 'application', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS, }, { cidrMask: 28, name: 'rds', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, } ] }); Default: - The VPC CIDR will be evenly divided between 1 public and 1 private subnet per AZ.
        :param vpc_name: The VPC name. Since the VPC resource doesn't support providing a physical name, the value provided here will be recorded in the ``Name`` tag Default: this.node.path
        :param vpn_connections: VPN connections to this VPC. Default: - No connections.
        :param vpn_gateway: Indicates whether a VPN gateway should be created and attached to this VPC. Default: - true when vpnGatewayAsn or vpnConnections is specified
        :param vpn_gateway_asn: The private Autonomous System Number (ASN) for the VPN gateway. Default: - Amazon default ASN.
        :param vpn_route_propagation: Where to propagate VPN routes. Default: - On the route tables associated with private subnets. If no private subnets exists, isolated subnets are used. If no isolated subnets exists, public subnets are used.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbbf384773ee5d4094012bcdf005cac4c749df363829f0efba57bdfc122d59a1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TmVpcProps(
            range_cidr=range_cidr,
            enable_endpoints=enable_endpoints,
            availability_zones=availability_zones,
            cidr=cidr,
            create_internet_gateway=create_internet_gateway,
            default_instance_tenancy=default_instance_tenancy,
            enable_dns_hostnames=enable_dns_hostnames,
            enable_dns_support=enable_dns_support,
            flow_logs=flow_logs,
            gateway_endpoints=gateway_endpoints,
            ip_addresses=ip_addresses,
            ip_protocol=ip_protocol,
            ipv6_addresses=ipv6_addresses,
            max_azs=max_azs,
            nat_gateway_provider=nat_gateway_provider,
            nat_gateways=nat_gateways,
            nat_gateway_subnets=nat_gateway_subnets,
            reserved_azs=reserved_azs,
            restrict_default_security_group=restrict_default_security_group,
            subnet_configuration=subnet_configuration,
            vpc_name=vpc_name,
            vpn_connections=vpn_connections,
            vpn_gateway=vpn_gateway,
            vpn_gateway_asn=vpn_gateway_asn,
            vpn_route_propagation=vpn_route_propagation,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="tm-cdk-constructs.TmVpcProps",
    jsii_struct_bases=[_aws_cdk_aws_ec2_ceddda9d.VpcProps],
    name_mapping={
        "availability_zones": "availabilityZones",
        "cidr": "cidr",
        "create_internet_gateway": "createInternetGateway",
        "default_instance_tenancy": "defaultInstanceTenancy",
        "enable_dns_hostnames": "enableDnsHostnames",
        "enable_dns_support": "enableDnsSupport",
        "flow_logs": "flowLogs",
        "gateway_endpoints": "gatewayEndpoints",
        "ip_addresses": "ipAddresses",
        "ip_protocol": "ipProtocol",
        "ipv6_addresses": "ipv6Addresses",
        "max_azs": "maxAzs",
        "nat_gateway_provider": "natGatewayProvider",
        "nat_gateways": "natGateways",
        "nat_gateway_subnets": "natGatewaySubnets",
        "reserved_azs": "reservedAzs",
        "restrict_default_security_group": "restrictDefaultSecurityGroup",
        "subnet_configuration": "subnetConfiguration",
        "vpc_name": "vpcName",
        "vpn_connections": "vpnConnections",
        "vpn_gateway": "vpnGateway",
        "vpn_gateway_asn": "vpnGatewayAsn",
        "vpn_route_propagation": "vpnRoutePropagation",
        "range_cidr": "rangeCidr",
        "enable_endpoints": "enableEndpoints",
    },
)
class TmVpcProps(_aws_cdk_aws_ec2_ceddda9d.VpcProps):
    def __init__(
        self,
        *,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        cidr: typing.Optional[builtins.str] = None,
        create_internet_gateway: typing.Optional[builtins.bool] = None,
        default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
        enable_dns_hostnames: typing.Optional[builtins.bool] = None,
        enable_dns_support: typing.Optional[builtins.bool] = None,
        flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        ip_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol] = None,
        ipv6_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        reserved_azs: typing.Optional[jsii.Number] = None,
        restrict_default_security_group: typing.Optional[builtins.bool] = None,
        subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpn_gateway: typing.Optional[builtins.bool] = None,
        vpn_gateway_asn: typing.Optional[jsii.Number] = None,
        vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
        range_cidr: builtins.str,
        enable_endpoints: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Represents the configuration for a VPC.

        :param availability_zones: Availability zones this VPC spans. Specify this option only if you do not specify ``maxAzs``. Default: - a subset of AZs of the stack
        :param cidr: (deprecated) The CIDR range to use for the VPC, e.g. '10.0.0.0/16'. Should be a minimum of /28 and maximum size of /16. The range will be split across all subnets per Availability Zone. Default: Vpc.DEFAULT_CIDR_RANGE
        :param create_internet_gateway: If set to false then disable the creation of the default internet gateway. Default: true
        :param default_instance_tenancy: The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy. Default: DefaultInstanceTenancy.Default (shared) tenancy
        :param enable_dns_hostnames: Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true. Default: true
        :param enable_dns_support: Indicates whether the DNS resolution is supported for the VPC. If this attribute is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames to IP addresses is not enabled. If this attribute is true, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC IPv4 network range plus two will succeed. Default: true
        :param flow_logs: Flow logs to add to this VPC. Default: - No flow logs.
        :param gateway_endpoints: Gateway endpoints to add to this VPC. Default: - None.
        :param ip_addresses: The Provider to use to allocate IPv4 Space to your VPC. Options include static allocation or from a pool. Note this is specific to IPv4 addresses. Default: ec2.IpAddresses.cidr
        :param ip_protocol: The protocol of the vpc. Options are IPv4 only or dual stack. Default: IpProtocol.IPV4_ONLY
        :param ipv6_addresses: The Provider to use to allocate IPv6 Space to your VPC. Options include amazon provided CIDR block. Note this is specific to IPv6 addresses. Default: Ipv6Addresses.amazonProvided
        :param max_azs: Define the maximum number of AZs to use in this region. If the region has more AZs than you want to use (for example, because of EIP limits), pick a lower number here. The AZs will be sorted and picked from the start of the list. If you pick a higher number than the number of AZs in the region, all AZs in the region will be selected. To use "all AZs" available to your account, use a high number (such as 99). Be aware that environment-agnostic stacks will be created with access to only 2 AZs, so to use more than 2 AZs, be sure to specify the account and region on your stack. Specify this option only if you do not specify ``availabilityZones``. Default: 3
        :param nat_gateway_provider: What type of NAT provider to use. Select between NAT gateways or NAT instances. NAT gateways may not be available in all AWS regions. Default: NatProvider.gateway()
        :param nat_gateways: The number of NAT Gateways/Instances to create. The type of NAT gateway or instance will be determined by the ``natGatewayProvider`` parameter. You can set this number lower than the number of Availability Zones in your VPC in order to save on NAT cost. Be aware you may be charged for cross-AZ data traffic instead. Default: - One NAT gateway/instance per Availability Zone
        :param nat_gateway_subnets: Configures the subnets which will have NAT Gateways/Instances. You can pick a specific group of subnets by specifying the group name; the picked subnets must be public subnets. Only necessary if you have more than one public subnet group. Default: - All public subnets.
        :param reserved_azs: Define the number of AZs to reserve. When specified, the IP space is reserved for the azs but no actual resources are provisioned. Default: 0
        :param restrict_default_security_group: If set to true then the default inbound & outbound rules will be removed from the default security group. Default: true if '@aws-cdk/aws-ec2:restrictDefaultSecurityGroup' is enabled, false otherwise
        :param subnet_configuration: Configure the subnets to build for each AZ. Each entry in this list configures a Subnet Group; each group will contain a subnet for each Availability Zone. For example, if you want 1 public subnet, 1 private subnet, and 1 isolated subnet in each AZ provide the following:: new ec2.Vpc(this, 'VPC', { subnetConfiguration: [ { cidrMask: 24, name: 'ingress', subnetType: ec2.SubnetType.PUBLIC, }, { cidrMask: 24, name: 'application', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS, }, { cidrMask: 28, name: 'rds', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, } ] }); Default: - The VPC CIDR will be evenly divided between 1 public and 1 private subnet per AZ.
        :param vpc_name: The VPC name. Since the VPC resource doesn't support providing a physical name, the value provided here will be recorded in the ``Name`` tag Default: this.node.path
        :param vpn_connections: VPN connections to this VPC. Default: - No connections.
        :param vpn_gateway: Indicates whether a VPN gateway should be created and attached to this VPC. Default: - true when vpnGatewayAsn or vpnConnections is specified
        :param vpn_gateway_asn: The private Autonomous System Number (ASN) for the VPN gateway. Default: - Amazon default ASN.
        :param vpn_route_propagation: Where to propagate VPN routes. Default: - On the route tables associated with private subnets. If no private subnets exists, isolated subnets are used. If no isolated subnets exists, public subnets are used.
        :param range_cidr: (experimental) The CIDR block for the VPC.
        :param enable_endpoints: (experimental) Indicates whether to enable the S3 endpoint for the VPC.

        :stability: experimental
        '''
        if isinstance(nat_gateway_subnets, dict):
            nat_gateway_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**nat_gateway_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6215cfcb5e410d0a1155ca30efab18d6b3cf0f425461591df31e65ec5978275e)
            check_type(argname="argument availability_zones", value=availability_zones, expected_type=type_hints["availability_zones"])
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
            check_type(argname="argument create_internet_gateway", value=create_internet_gateway, expected_type=type_hints["create_internet_gateway"])
            check_type(argname="argument default_instance_tenancy", value=default_instance_tenancy, expected_type=type_hints["default_instance_tenancy"])
            check_type(argname="argument enable_dns_hostnames", value=enable_dns_hostnames, expected_type=type_hints["enable_dns_hostnames"])
            check_type(argname="argument enable_dns_support", value=enable_dns_support, expected_type=type_hints["enable_dns_support"])
            check_type(argname="argument flow_logs", value=flow_logs, expected_type=type_hints["flow_logs"])
            check_type(argname="argument gateway_endpoints", value=gateway_endpoints, expected_type=type_hints["gateway_endpoints"])
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument ip_protocol", value=ip_protocol, expected_type=type_hints["ip_protocol"])
            check_type(argname="argument ipv6_addresses", value=ipv6_addresses, expected_type=type_hints["ipv6_addresses"])
            check_type(argname="argument max_azs", value=max_azs, expected_type=type_hints["max_azs"])
            check_type(argname="argument nat_gateway_provider", value=nat_gateway_provider, expected_type=type_hints["nat_gateway_provider"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument nat_gateway_subnets", value=nat_gateway_subnets, expected_type=type_hints["nat_gateway_subnets"])
            check_type(argname="argument reserved_azs", value=reserved_azs, expected_type=type_hints["reserved_azs"])
            check_type(argname="argument restrict_default_security_group", value=restrict_default_security_group, expected_type=type_hints["restrict_default_security_group"])
            check_type(argname="argument subnet_configuration", value=subnet_configuration, expected_type=type_hints["subnet_configuration"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
            check_type(argname="argument vpn_connections", value=vpn_connections, expected_type=type_hints["vpn_connections"])
            check_type(argname="argument vpn_gateway", value=vpn_gateway, expected_type=type_hints["vpn_gateway"])
            check_type(argname="argument vpn_gateway_asn", value=vpn_gateway_asn, expected_type=type_hints["vpn_gateway_asn"])
            check_type(argname="argument vpn_route_propagation", value=vpn_route_propagation, expected_type=type_hints["vpn_route_propagation"])
            check_type(argname="argument range_cidr", value=range_cidr, expected_type=type_hints["range_cidr"])
            check_type(argname="argument enable_endpoints", value=enable_endpoints, expected_type=type_hints["enable_endpoints"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "range_cidr": range_cidr,
        }
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if cidr is not None:
            self._values["cidr"] = cidr
        if create_internet_gateway is not None:
            self._values["create_internet_gateway"] = create_internet_gateway
        if default_instance_tenancy is not None:
            self._values["default_instance_tenancy"] = default_instance_tenancy
        if enable_dns_hostnames is not None:
            self._values["enable_dns_hostnames"] = enable_dns_hostnames
        if enable_dns_support is not None:
            self._values["enable_dns_support"] = enable_dns_support
        if flow_logs is not None:
            self._values["flow_logs"] = flow_logs
        if gateway_endpoints is not None:
            self._values["gateway_endpoints"] = gateway_endpoints
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if ip_protocol is not None:
            self._values["ip_protocol"] = ip_protocol
        if ipv6_addresses is not None:
            self._values["ipv6_addresses"] = ipv6_addresses
        if max_azs is not None:
            self._values["max_azs"] = max_azs
        if nat_gateway_provider is not None:
            self._values["nat_gateway_provider"] = nat_gateway_provider
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if nat_gateway_subnets is not None:
            self._values["nat_gateway_subnets"] = nat_gateway_subnets
        if reserved_azs is not None:
            self._values["reserved_azs"] = reserved_azs
        if restrict_default_security_group is not None:
            self._values["restrict_default_security_group"] = restrict_default_security_group
        if subnet_configuration is not None:
            self._values["subnet_configuration"] = subnet_configuration
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name
        if vpn_connections is not None:
            self._values["vpn_connections"] = vpn_connections
        if vpn_gateway is not None:
            self._values["vpn_gateway"] = vpn_gateway
        if vpn_gateway_asn is not None:
            self._values["vpn_gateway_asn"] = vpn_gateway_asn
        if vpn_route_propagation is not None:
            self._values["vpn_route_propagation"] = vpn_route_propagation
        if enable_endpoints is not None:
            self._values["enable_endpoints"] = enable_endpoints

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Availability zones this VPC spans.

        Specify this option only if you do not specify ``maxAzs``.

        :default: - a subset of AZs of the stack
        '''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cidr(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The CIDR range to use for the VPC, e.g. '10.0.0.0/16'.

        Should be a minimum of /28 and maximum size of /16. The range will be
        split across all subnets per Availability Zone.

        :default: Vpc.DEFAULT_CIDR_RANGE

        :deprecated: Use ipAddresses instead

        :stability: deprecated
        '''
        result = self._values.get("cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_internet_gateway(self) -> typing.Optional[builtins.bool]:
        '''If set to false then disable the creation of the default internet gateway.

        :default: true
        '''
        result = self._values.get("create_internet_gateway")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def default_instance_tenancy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy]:
        '''The default tenancy of instances launched into the VPC.

        By setting this to dedicated tenancy, instances will be launched on
        hardware dedicated to a single AWS customer, unless specifically specified
        at instance launch time. Please note, not all instance types are usable
        with Dedicated tenancy.

        :default: DefaultInstanceTenancy.Default (shared) tenancy
        '''
        result = self._values.get("default_instance_tenancy")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy], result)

    @builtins.property
    def enable_dns_hostnames(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the instances launched in the VPC get public DNS hostnames.

        If this attribute is true, instances in the VPC get public DNS hostnames,
        but only if the enableDnsSupport attribute is also set to true.

        :default: true
        '''
        result = self._values.get("enable_dns_hostnames")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_dns_support(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the DNS resolution is supported for the VPC.

        If this attribute is false, the Amazon-provided DNS server in the VPC that
        resolves public DNS hostnames to IP addresses is not enabled. If this
        attribute is true, queries to the Amazon provided DNS server at the
        169.254.169.253 IP address, or the reserved IP address at the base of the
        VPC IPv4 network range plus two will succeed.

        :default: true
        '''
        result = self._values.get("enable_dns_support")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def flow_logs(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.FlowLogOptions]]:
        '''Flow logs to add to this VPC.

        :default: - No flow logs.
        '''
        result = self._values.get("flow_logs")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.FlowLogOptions]], result)

    @builtins.property
    def gateway_endpoints(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions]]:
        '''Gateway endpoints to add to this VPC.

        :default: - None.
        '''
        result = self._values.get("gateway_endpoints")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions]], result)

    @builtins.property
    def ip_addresses(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses]:
        '''The Provider to use to allocate IPv4 Space to your VPC.

        Options include static allocation or from a pool.

        Note this is specific to IPv4 addresses.

        :default: ec2.IpAddresses.cidr
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses], result)

    @builtins.property
    def ip_protocol(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol]:
        '''The protocol of the vpc.

        Options are IPv4 only or dual stack.

        :default: IpProtocol.IPV4_ONLY
        '''
        result = self._values.get("ip_protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol], result)

    @builtins.property
    def ipv6_addresses(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses]:
        '''The Provider to use to allocate IPv6 Space to your VPC.

        Options include amazon provided CIDR block.

        Note this is specific to IPv6 addresses.

        :default: Ipv6Addresses.amazonProvided
        '''
        result = self._values.get("ipv6_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses], result)

    @builtins.property
    def max_azs(self) -> typing.Optional[jsii.Number]:
        '''Define the maximum number of AZs to use in this region.

        If the region has more AZs than you want to use (for example, because of
        EIP limits), pick a lower number here. The AZs will be sorted and picked
        from the start of the list.

        If you pick a higher number than the number of AZs in the region, all AZs
        in the region will be selected. To use "all AZs" available to your
        account, use a high number (such as 99).

        Be aware that environment-agnostic stacks will be created with access to
        only 2 AZs, so to use more than 2 AZs, be sure to specify the account and
        region on your stack.

        Specify this option only if you do not specify ``availabilityZones``.

        :default: 3
        '''
        result = self._values.get("max_azs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateway_provider(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider]:
        '''What type of NAT provider to use.

        Select between NAT gateways or NAT instances. NAT gateways
        may not be available in all AWS regions.

        :default: NatProvider.gateway()
        '''
        result = self._values.get("nat_gateway_provider")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''The number of NAT Gateways/Instances to create.

        The type of NAT gateway or instance will be determined by the
        ``natGatewayProvider`` parameter.

        You can set this number lower than the number of Availability Zones in your
        VPC in order to save on NAT cost. Be aware you may be charged for
        cross-AZ data traffic instead.

        :default: - One NAT gateway/instance per Availability Zone
        '''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateway_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Configures the subnets which will have NAT Gateways/Instances.

        You can pick a specific group of subnets by specifying the group name;
        the picked subnets must be public subnets.

        Only necessary if you have more than one public subnet group.

        :default: - All public subnets.
        '''
        result = self._values.get("nat_gateway_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def reserved_azs(self) -> typing.Optional[jsii.Number]:
        '''Define the number of AZs to reserve.

        When specified, the IP space is reserved for the azs but no actual
        resources are provisioned.

        :default: 0
        '''
        result = self._values.get("reserved_azs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def restrict_default_security_group(self) -> typing.Optional[builtins.bool]:
        '''If set to true then the default inbound & outbound rules will be removed from the default security group.

        :default: true if '@aws-cdk/aws-ec2:restrictDefaultSecurityGroup' is enabled, false otherwise
        '''
        result = self._values.get("restrict_default_security_group")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def subnet_configuration(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration]]:
        '''Configure the subnets to build for each AZ.

        Each entry in this list configures a Subnet Group; each group will contain a
        subnet for each Availability Zone.

        For example, if you want 1 public subnet, 1 private subnet, and 1 isolated
        subnet in each AZ provide the following::

           new ec2.Vpc(this, 'VPC', {
             subnetConfiguration: [
                {
                  cidrMask: 24,
                  name: 'ingress',
                  subnetType: ec2.SubnetType.PUBLIC,
                },
                {
                  cidrMask: 24,
                  name: 'application',
                  subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
                },
                {
                  cidrMask: 28,
                  name: 'rds',
                  subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
                }
             ]
           });

        :default:

        - The VPC CIDR will be evenly divided between 1 public and 1
        private subnet per AZ.
        '''
        result = self._values.get("subnet_configuration")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration]], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''The VPC name.

        Since the VPC resource doesn't support providing a physical name, the value provided here will be recorded in the ``Name`` tag

        :default: this.node.path
        '''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpn_connections(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions]]:
        '''VPN connections to this VPC.

        :default: - No connections.
        '''
        result = self._values.get("vpn_connections")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions]], result)

    @builtins.property
    def vpn_gateway(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether a VPN gateway should be created and attached to this VPC.

        :default: - true when vpnGatewayAsn or vpnConnections is specified
        '''
        result = self._values.get("vpn_gateway")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpn_gateway_asn(self) -> typing.Optional[jsii.Number]:
        '''The private Autonomous System Number (ASN) for the VPN gateway.

        :default: - Amazon default ASN.
        '''
        result = self._values.get("vpn_gateway_asn")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpn_route_propagation(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]]:
        '''Where to propagate VPN routes.

        :default:

        - On the route tables associated with private subnets. If no
        private subnets exists, isolated subnets are used. If no isolated subnets
        exists, public subnets are used.
        '''
        result = self._values.get("vpn_route_propagation")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]], result)

    @builtins.property
    def range_cidr(self) -> builtins.str:
        '''(experimental) The CIDR block for the VPC.

        :stability: experimental
        '''
        result = self._values.get("range_cidr")
        assert result is not None, "Required property 'range_cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enable_endpoints(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Indicates whether to enable the S3 endpoint for the VPC.

        :stability: experimental
        '''
        result = self._values.get("enable_endpoints")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TmVpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TmPipeline",
    "TmPipelineProps",
    "TmRdsAuroraMysqlServerless",
    "TmRdsAuroraMysqlServerlessProps",
    "TmVpcBase",
    "TmVpcProps",
]

publication.publish()

def _typecheckingstub__1a993414424d3e58108b1515d1ae43df55fcea9a5bf26c77d45647cea67364f8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    pipeline_name: builtins.str,
    repo_branch: builtins.str,
    repo_name: builtins.str,
    primary_output_directory: typing.Optional[builtins.str] = None,
    synth_command: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c90f448d2c851abcb766597516c1d94417ef3eed41e3bc82a985a84bd6ff2854(
    *,
    pipeline_name: builtins.str,
    repo_branch: builtins.str,
    repo_name: builtins.str,
    primary_output_directory: typing.Optional[builtins.str] = None,
    synth_command: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc939679af82c57cdfc24824fb9ec6ef0580d01390aa5c263b878d67d4912115(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    enable_global: typing.Optional[builtins.bool] = None,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
    credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
    default_database_name: typing.Optional[builtins.str] = None,
    deletion_protection: typing.Optional[builtins.bool] = None,
    domain: typing.Optional[builtins.str] = None,
    domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    enable_data_api: typing.Optional[builtins.bool] = None,
    iam_authentication: typing.Optional[builtins.bool] = None,
    instance_identifier_base: typing.Optional[builtins.str] = None,
    instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
    instances: typing.Optional[jsii.Number] = None,
    instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
    monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
    parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    port: typing.Optional[jsii.Number] = None,
    preferred_maintenance_window: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
    serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
    storage_encrypted: typing.Optional[builtins.bool] = None,
    storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
    subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb6185862d0dbafb21639371b5cfdd31758e49cf957284e1d423cbd3bf7cc8a(
    *,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
    credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
    default_database_name: typing.Optional[builtins.str] = None,
    deletion_protection: typing.Optional[builtins.bool] = None,
    domain: typing.Optional[builtins.str] = None,
    domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    enable_data_api: typing.Optional[builtins.bool] = None,
    iam_authentication: typing.Optional[builtins.bool] = None,
    instance_identifier_base: typing.Optional[builtins.str] = None,
    instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
    instances: typing.Optional[jsii.Number] = None,
    instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
    monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
    parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    port: typing.Optional[jsii.Number] = None,
    preferred_maintenance_window: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
    serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
    storage_encrypted: typing.Optional[builtins.bool] = None,
    storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
    subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    enable_global: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbbf384773ee5d4094012bcdf005cac4c749df363829f0efba57bdfc122d59a1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    range_cidr: builtins.str,
    enable_endpoints: typing.Optional[typing.Sequence[builtins.str]] = None,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    cidr: typing.Optional[builtins.str] = None,
    create_internet_gateway: typing.Optional[builtins.bool] = None,
    default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
    enable_dns_hostnames: typing.Optional[builtins.bool] = None,
    enable_dns_support: typing.Optional[builtins.bool] = None,
    flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    ip_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol] = None,
    ipv6_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    reserved_azs: typing.Optional[jsii.Number] = None,
    restrict_default_security_group: typing.Optional[builtins.bool] = None,
    subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpn_gateway: typing.Optional[builtins.bool] = None,
    vpn_gateway_asn: typing.Optional[jsii.Number] = None,
    vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6215cfcb5e410d0a1155ca30efab18d6b3cf0f425461591df31e65ec5978275e(
    *,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    cidr: typing.Optional[builtins.str] = None,
    create_internet_gateway: typing.Optional[builtins.bool] = None,
    default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
    enable_dns_hostnames: typing.Optional[builtins.bool] = None,
    enable_dns_support: typing.Optional[builtins.bool] = None,
    flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    ip_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol] = None,
    ipv6_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    reserved_azs: typing.Optional[jsii.Number] = None,
    restrict_default_security_group: typing.Optional[builtins.bool] = None,
    subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpn_gateway: typing.Optional[builtins.bool] = None,
    vpn_gateway_asn: typing.Optional[jsii.Number] = None,
    vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    range_cidr: builtins.str,
    enable_endpoints: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
