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

from .._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.interface(jsii_type="shady-island.networking.ISecretHttpHeader")
class ISecretHttpHeader(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''Interface for SecretHttpHeader.'''

    @builtins.property
    @jsii.member(jsii_name="headerName")
    def header_name(self) -> builtins.str:
        '''The name of the secret header.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="headerValue")
    def header_value(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''The value of the secret header.'''
        ...

    @jsii.member(jsii_name="createListenerCondition")
    def create_listener_condition(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition:
        '''Get a ListenerCondition that represents this secret header.

        :return: The appropriate ListenerCondition.
        '''
        ...

    @jsii.member(jsii_name="createOriginCustomHeaders")
    def create_origin_custom_headers(
        self,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''Gets the custom headers for a CloudFront origin configuration.

        :return: An object with the header name and header value.
        '''
        ...


class _ISecretHttpHeaderProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''Interface for SecretHttpHeader.'''

    __jsii_type__: typing.ClassVar[str] = "shady-island.networking.ISecretHttpHeader"

    @builtins.property
    @jsii.member(jsii_name="headerName")
    def header_name(self) -> builtins.str:
        '''The name of the secret header.'''
        return typing.cast(builtins.str, jsii.get(self, "headerName"))

    @builtins.property
    @jsii.member(jsii_name="headerValue")
    def header_value(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''The value of the secret header.'''
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, jsii.get(self, "headerValue"))

    @jsii.member(jsii_name="createListenerCondition")
    def create_listener_condition(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition:
        '''Get a ListenerCondition that represents this secret header.

        :return: The appropriate ListenerCondition.
        '''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition, jsii.invoke(self, "createListenerCondition", []))

    @jsii.member(jsii_name="createOriginCustomHeaders")
    def create_origin_custom_headers(
        self,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''Gets the custom headers for a CloudFront origin configuration.

        :return: An object with the header name and header value.
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.invoke(self, "createOriginCustomHeaders", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISecretHttpHeader).__jsii_proxy_class__ = lambda : _ISecretHttpHeaderProxy


@jsii.implements(ISecretHttpHeader)
class SecretHttpHeader(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.SecretHttpHeader",
):
    '''Configure a secret header an ALB can require for every request.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        header_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new SecretHttpHeader.

        :param scope: - The parent scope.
        :param id: - The construct identifier.
        :param header_name: The name of the secret HTTP header. Default: - X-Secret-Passphrase
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__150cf8e22f1e7d05a47117e8f77da25561199d5daa7118eb196893fa55cfd796)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SecretHttpHeaderProps(header_name=header_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecret")
    @builtins.classmethod
    def from_secret(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> ISecretHttpHeader:
        '''Create a SecretHttpHeader from an existing Secrets Manager secret.

        The secret must be in JSON format and have two fields: ``name`` and ``value``.

        :param scope: - The parent scope.
        :param id: - The ID for the new construct.
        :param secret: - The existing Secrets Manager secret.

        :return: The new ISecretHttpHeader
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40fccea94b7e684de60e1f55e353e1a03b85c56db9135f4d67a939d5448d4694)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast(ISecretHttpHeader, jsii.sinvoke(cls, "fromSecret", [scope, id, secret]))

    @jsii.member(jsii_name="createListenerCondition")
    def create_listener_condition(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition:
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ListenerCondition, jsii.invoke(self, "createListenerCondition", []))

    @jsii.member(jsii_name="createOriginCustomHeaders")
    def create_origin_custom_headers(
        self,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.invoke(self, "createOriginCustomHeaders", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="defaultHeaderName")
    def default_header_name(cls) -> builtins.str:
        '''Gets the default header name.

        :return: the default header name
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "defaultHeaderName"))

    @builtins.property
    @jsii.member(jsii_name="headerName")
    def header_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerName"))

    @builtins.property
    @jsii.member(jsii_name="headerValue")
    def header_value(self) -> _aws_cdk_ceddda9d.SecretValue:
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, jsii.get(self, "headerValue"))

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The Secrets Manager secret that contains the name and value of the header.'''
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.get(self, "secret"))


@jsii.data_type(
    jsii_type="shady-island.networking.SecretHttpHeaderProps",
    jsii_struct_bases=[],
    name_mapping={"header_name": "headerName"},
)
class SecretHttpHeaderProps:
    def __init__(self, *, header_name: typing.Optional[builtins.str] = None) -> None:
        '''Properties for the SecretHttpHeader constructor.

        :param header_name: The name of the secret HTTP header. Default: - X-Secret-Passphrase
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c95f74423d937b8be51b1b147dac2d7c254b40cc4b250c45909e61f91bd46e8)
            check_type(argname="argument header_name", value=header_name, expected_type=type_hints["header_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if header_name is not None:
            self._values["header_name"] = header_name

    @builtins.property
    def header_name(self) -> typing.Optional[builtins.str]:
        '''The name of the secret HTTP header.

        :default: - X-Secret-Passphrase
        '''
        result = self._values.get("header_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretHttpHeaderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.networking.TargetOptions",
    jsii_struct_bases=[
        _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroupProps
    ],
    name_mapping={
        "deregistration_delay": "deregistrationDelay",
        "health_check": "healthCheck",
        "target_group_name": "targetGroupName",
        "target_type": "targetType",
        "vpc": "vpc",
        "load_balancing_algorithm_type": "loadBalancingAlgorithmType",
        "port": "port",
        "protocol": "protocol",
        "protocol_version": "protocolVersion",
        "slow_start": "slowStart",
        "stickiness_cookie_duration": "stickinessCookieDuration",
        "stickiness_cookie_name": "stickinessCookieName",
        "targets": "targets",
        "hostnames": "hostnames",
        "priority": "priority",
    },
)
class TargetOptions(
    _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroupProps,
):
    def __init__(
        self,
        *,
        deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        target_group_name: typing.Optional[builtins.str] = None,
        target_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        load_balancing_algorithm_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType] = None,
        port: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        slow_start: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        stickiness_cookie_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        stickiness_cookie_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]] = None,
        hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Options for adding a new target group.

        :param deregistration_delay: The amount of time for Elastic Load Balancing to wait before deregistering a target. The range is 0-3600 seconds. Default: 300
        :param health_check: Health check configuration. Default: - The default value for each property in this configuration varies depending on the target.
        :param target_group_name: The name of the target group. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen. Default: - Automatically generated.
        :param target_type: The type of targets registered to this TargetGroup, either IP or Instance. All targets registered into the group must be of this type. If you register targets to the TargetGroup in the CDK app, the TargetType is determined automatically. Default: - Determined automatically.
        :param vpc: The virtual private cloud (VPC). only if ``TargetType`` is ``Ip`` or ``InstanceId`` Default: - undefined
        :param load_balancing_algorithm_type: The load balancing algorithm to select targets for routing requests. Default: TargetGroupLoadBalancingAlgorithmType.ROUND_ROBIN
        :param port: The port on which the target receives traffic. This is not applicable for Lambda targets. Default: - Determined from protocol if known
        :param protocol: The protocol used for communication with the target. This is not applicable for Lambda targets. Default: - Determined from port if known
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param slow_start: The time period during which the load balancer sends a newly registered target a linearly increasing share of the traffic to the target group. The range is 30-900 seconds (15 minutes). Default: 0
        :param stickiness_cookie_duration: The stickiness cookie expiration period. Setting this value enables load balancer stickiness. After this period, the cookie is considered stale. The minimum value is 1 second and the maximum value is 7 days (604800 seconds). Default: Duration.days(1)
        :param stickiness_cookie_name: The name of an application-based stickiness cookie. Names that start with the following prefixes are not allowed: AWSALB, AWSALBAPP, and AWSALBTG; they're reserved for use by the load balancer. Note: ``stickinessCookieName`` parameter depends on the presence of ``stickinessCookieDuration`` parameter. If ``stickinessCookieDuration`` is not set, ``stickinessCookieName`` will be omitted. Default: - If ``stickinessCookieDuration`` is set, a load-balancer generated cookie is used. Otherwise, no stickiness is defined.
        :param targets: The targets to add to this target group. Can be ``Instance``, ``IPAddress``, or any self-registering load balancing target. If you use either ``Instance`` or ``IPAddress`` as targets, all target must be of the same type. Default: - No targets.
        :param hostnames: The hostnames on which traffic is served.
        :param priority: The priority of the listener rule. Default: - Automatically determined
        '''
        if isinstance(health_check, dict):
            health_check = _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck(**health_check)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efa2d39cd1f01bf3758addd640ec7d1a822d75c3cc97424ddff8b739dca8d900)
            check_type(argname="argument deregistration_delay", value=deregistration_delay, expected_type=type_hints["deregistration_delay"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument target_group_name", value=target_group_name, expected_type=type_hints["target_group_name"])
            check_type(argname="argument target_type", value=target_type, expected_type=type_hints["target_type"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument load_balancing_algorithm_type", value=load_balancing_algorithm_type, expected_type=type_hints["load_balancing_algorithm_type"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument protocol_version", value=protocol_version, expected_type=type_hints["protocol_version"])
            check_type(argname="argument slow_start", value=slow_start, expected_type=type_hints["slow_start"])
            check_type(argname="argument stickiness_cookie_duration", value=stickiness_cookie_duration, expected_type=type_hints["stickiness_cookie_duration"])
            check_type(argname="argument stickiness_cookie_name", value=stickiness_cookie_name, expected_type=type_hints["stickiness_cookie_name"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument hostnames", value=hostnames, expected_type=type_hints["hostnames"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deregistration_delay is not None:
            self._values["deregistration_delay"] = deregistration_delay
        if health_check is not None:
            self._values["health_check"] = health_check
        if target_group_name is not None:
            self._values["target_group_name"] = target_group_name
        if target_type is not None:
            self._values["target_type"] = target_type
        if vpc is not None:
            self._values["vpc"] = vpc
        if load_balancing_algorithm_type is not None:
            self._values["load_balancing_algorithm_type"] = load_balancing_algorithm_type
        if port is not None:
            self._values["port"] = port
        if protocol is not None:
            self._values["protocol"] = protocol
        if protocol_version is not None:
            self._values["protocol_version"] = protocol_version
        if slow_start is not None:
            self._values["slow_start"] = slow_start
        if stickiness_cookie_duration is not None:
            self._values["stickiness_cookie_duration"] = stickiness_cookie_duration
        if stickiness_cookie_name is not None:
            self._values["stickiness_cookie_name"] = stickiness_cookie_name
        if targets is not None:
            self._values["targets"] = targets
        if hostnames is not None:
            self._values["hostnames"] = hostnames
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def deregistration_delay(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The amount of time for Elastic Load Balancing to wait before deregistering a target.

        The range is 0-3600 seconds.

        :default: 300
        '''
        result = self._values.get("deregistration_delay")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def health_check(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck]:
        '''Health check configuration.

        :default: - The default value for each property in this configuration varies depending on the target.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-targetgroup.html#aws-resource-elasticloadbalancingv2-targetgroup-properties
        '''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck], result)

    @builtins.property
    def target_group_name(self) -> typing.Optional[builtins.str]:
        '''The name of the target group.

        This name must be unique per region per account, can have a maximum of
        32 characters, must contain only alphanumeric characters or hyphens, and
        must not begin or end with a hyphen.

        :default: - Automatically generated.
        '''
        result = self._values.get("target_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType]:
        '''The type of targets registered to this TargetGroup, either IP or Instance.

        All targets registered into the group must be of this type. If you
        register targets to the TargetGroup in the CDK app, the TargetType is
        determined automatically.

        :default: - Determined automatically.
        '''
        result = self._values.get("target_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The virtual private cloud (VPC).

        only if ``TargetType`` is ``Ip`` or ``InstanceId``

        :default: - undefined
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def load_balancing_algorithm_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType]:
        '''The load balancing algorithm to select targets for routing requests.

        :default: TargetGroupLoadBalancingAlgorithmType.ROUND_ROBIN
        '''
        result = self._values.get("load_balancing_algorithm_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The port on which the target receives traffic.

        This is not applicable for Lambda targets.

        :default: - Determined from protocol if known
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol used for communication with the target.

        This is not applicable for Lambda targets.

        :default: - Determined from port if known
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def protocol_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion]:
        '''The protocol version to use.

        :default: ApplicationProtocolVersion.HTTP1
        '''
        result = self._values.get("protocol_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion], result)

    @builtins.property
    def slow_start(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The time period during which the load balancer sends a newly registered target a linearly increasing share of the traffic to the target group.

        The range is 30-900 seconds (15 minutes).

        :default: 0
        '''
        result = self._values.get("slow_start")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def stickiness_cookie_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The stickiness cookie expiration period.

        Setting this value enables load balancer stickiness.

        After this period, the cookie is considered stale. The minimum value is
        1 second and the maximum value is 7 days (604800 seconds).

        :default: Duration.days(1)
        '''
        result = self._values.get("stickiness_cookie_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def stickiness_cookie_name(self) -> typing.Optional[builtins.str]:
        '''The name of an application-based stickiness cookie.

        Names that start with the following prefixes are not allowed: AWSALB, AWSALBAPP,
        and AWSALBTG; they're reserved for use by the load balancer.

        Note: ``stickinessCookieName`` parameter depends on the presence of ``stickinessCookieDuration`` parameter.
        If ``stickinessCookieDuration`` is not set, ``stickinessCookieName`` will be omitted.

        :default: - If ``stickinessCookieDuration`` is set, a load-balancer generated cookie is used. Otherwise, no stickiness is defined.

        :see: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/sticky-sessions.html
        '''
        result = self._values.get("stickiness_cookie_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]]:
        '''The targets to add to this target group.

        Can be ``Instance``, ``IPAddress``, or any self-registering load balancing
        target. If you use either ``Instance`` or ``IPAddress`` as targets, all
        target must be of the same type.

        :default: - No targets.
        '''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]], result)

    @builtins.property
    def hostnames(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The hostnames on which traffic is served.'''
        result = self._values.get("hostnames")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''The priority of the listener rule.

        :default: - Automatically determined
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebLoadBalancing(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.networking.WebLoadBalancing",
):
    '''A utility for creating a public-facing Application Load Balancer.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
        require_known_hostname: typing.Optional[builtins.bool] = None,
        require_secret_header: typing.Optional[builtins.bool] = None,
        secret_header_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    ) -> None:
        '''Creates a new WebLoadBalancing.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param certificates: The certificate to attach to the load balancer and CloudFront distribution.
        :param vpc: The VPC where these resources should be deployed.
        :param idle_timeout: The load balancer idle timeout, in seconds. If you have a reverse proxy in front of this load balancer, such as CloudFront, this number should be less than the reverse proxy's request timeout. Default: - 59 seconds
        :param ip_address_type: The type of IP addresses to use (IPv4 or Dual Stack). Default: - IPv4 only
        :param require_known_hostname: Forbid requests that ask for an unknown hostname. Requests for an unknown hostname will receive an HTTP 421 status response. Default: - false
        :param require_secret_header: Forbid requests that are missing an HTTP header with a specific value. If this option is set to ``true``, this construct will provide a new ``SecretHttpHeader`` accessible on the ``secretHeader`` property. Requests without the correct header name and value will receive an HTTP 421 status response. Default: - false
        :param secret_header_name: The name of the secret HTTP header. Providing this option implies that ``requireSecretHeader`` is ``true``. Default: - X-Secret-Passphrase
        :param security_group: A security group for the load balancer itself. Default: - A new security group will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56342186b82314e198297a3e5364d68b3f8d14f18d4e2c17b5f18a47bffc93d3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebLoadBalancingProps(
            certificates=certificates,
            vpc=vpc,
            idle_timeout=idle_timeout,
            ip_address_type=ip_address_type,
            require_known_hostname=require_known_hostname,
            require_secret_header=require_secret_header,
            secret_header_name=secret_header_name,
            security_group=security_group,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addTarget")
    def add_target(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget,
        *,
        hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
        priority: typing.Optional[jsii.Number] = None,
        load_balancing_algorithm_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType] = None,
        port: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        slow_start: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        stickiness_cookie_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        stickiness_cookie_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]] = None,
        deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        target_group_name: typing.Optional[builtins.str] = None,
        target_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup:
        '''Adds a target to the listener.

        If the following options are left undefined, these defaults will be used.

        - ``port``: 443
        - ``protocol``: HTTPS
        - ``deregistrationDelay``: load balancer idle timeout
        - ``healthCheck.path``: /
        - ``healthCheck.healthyThresholdCount``: 2
        - ``healthCheck.interval``: 30 seconds
        - ``healthCheck.timeout``: 29 seconds

        :param id: - The ID of the new target group.
        :param target: - The load balancing target to receive traffic.
        :param hostnames: The hostnames on which traffic is served.
        :param priority: The priority of the listener rule. Default: - Automatically determined
        :param load_balancing_algorithm_type: The load balancing algorithm to select targets for routing requests. Default: TargetGroupLoadBalancingAlgorithmType.ROUND_ROBIN
        :param port: The port on which the target receives traffic. This is not applicable for Lambda targets. Default: - Determined from protocol if known
        :param protocol: The protocol used for communication with the target. This is not applicable for Lambda targets. Default: - Determined from port if known
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param slow_start: The time period during which the load balancer sends a newly registered target a linearly increasing share of the traffic to the target group. The range is 30-900 seconds (15 minutes). Default: 0
        :param stickiness_cookie_duration: The stickiness cookie expiration period. Setting this value enables load balancer stickiness. After this period, the cookie is considered stale. The minimum value is 1 second and the maximum value is 7 days (604800 seconds). Default: Duration.days(1)
        :param stickiness_cookie_name: The name of an application-based stickiness cookie. Names that start with the following prefixes are not allowed: AWSALB, AWSALBAPP, and AWSALBTG; they're reserved for use by the load balancer. Note: ``stickinessCookieName`` parameter depends on the presence of ``stickinessCookieDuration`` parameter. If ``stickinessCookieDuration`` is not set, ``stickinessCookieName`` will be omitted. Default: - If ``stickinessCookieDuration`` is set, a load-balancer generated cookie is used. Otherwise, no stickiness is defined.
        :param targets: The targets to add to this target group. Can be ``Instance``, ``IPAddress``, or any self-registering load balancing target. If you use either ``Instance`` or ``IPAddress`` as targets, all target must be of the same type. Default: - No targets.
        :param deregistration_delay: The amount of time for Elastic Load Balancing to wait before deregistering a target. The range is 0-3600 seconds. Default: 300
        :param health_check: Health check configuration. Default: - The default value for each property in this configuration varies depending on the target.
        :param target_group_name: The name of the target group. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen. Default: - Automatically generated.
        :param target_type: The type of targets registered to this TargetGroup, either IP or Instance. All targets registered into the group must be of this type. If you register targets to the TargetGroup in the CDK app, the TargetType is determined automatically. Default: - Determined automatically.
        :param vpc: The virtual private cloud (VPC). only if ``TargetType`` is ``Ip`` or ``InstanceId`` Default: - undefined

        :return: The new Application Target Group
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7e0fb1b7097e928299c71e17989f2f1e1385330c18446d1a211d9b57fa16cc8)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = TargetOptions(
            hostnames=hostnames,
            priority=priority,
            load_balancing_algorithm_type=load_balancing_algorithm_type,
            port=port,
            protocol=protocol,
            protocol_version=protocol_version,
            slow_start=slow_start,
            stickiness_cookie_duration=stickiness_cookie_duration,
            stickiness_cookie_name=stickiness_cookie_name,
            targets=targets,
            deregistration_delay=deregistration_delay,
            health_check=health_check,
            target_group_name=target_group_name,
            target_type=target_type,
            vpc=vpc,
        )

        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationTargetGroup, jsii.invoke(self, "addTarget", [id, target, options]))

    @builtins.property
    @jsii.member(jsii_name="listener")
    def listener(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener:
        '''The HTTPS listener.'''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener, jsii.get(self, "listener"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer:
        '''The load balancer itself.'''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer, jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="secretHeader")
    def secret_header(self) -> typing.Optional[ISecretHttpHeader]:
        '''The secret header (if ``requireSecretHeader`` was set to ``true``).'''
        return typing.cast(typing.Optional[ISecretHttpHeader], jsii.get(self, "secretHeader"))


@jsii.data_type(
    jsii_type="shady-island.networking.WebLoadBalancingProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificates": "certificates",
        "vpc": "vpc",
        "idle_timeout": "idleTimeout",
        "ip_address_type": "ipAddressType",
        "require_known_hostname": "requireKnownHostname",
        "require_secret_header": "requireSecretHeader",
        "secret_header_name": "secretHeaderName",
        "security_group": "securityGroup",
    },
)
class WebLoadBalancingProps:
    def __init__(
        self,
        *,
        certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
        require_known_hostname: typing.Optional[builtins.bool] = None,
        require_secret_header: typing.Optional[builtins.bool] = None,
        secret_header_name: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    ) -> None:
        '''Constructor properties for WebLoadBalancing.

        :param certificates: The certificate to attach to the load balancer and CloudFront distribution.
        :param vpc: The VPC where these resources should be deployed.
        :param idle_timeout: The load balancer idle timeout, in seconds. If you have a reverse proxy in front of this load balancer, such as CloudFront, this number should be less than the reverse proxy's request timeout. Default: - 59 seconds
        :param ip_address_type: The type of IP addresses to use (IPv4 or Dual Stack). Default: - IPv4 only
        :param require_known_hostname: Forbid requests that ask for an unknown hostname. Requests for an unknown hostname will receive an HTTP 421 status response. Default: - false
        :param require_secret_header: Forbid requests that are missing an HTTP header with a specific value. If this option is set to ``true``, this construct will provide a new ``SecretHttpHeader`` accessible on the ``secretHeader`` property. Requests without the correct header name and value will receive an HTTP 421 status response. Default: - false
        :param secret_header_name: The name of the secret HTTP header. Providing this option implies that ``requireSecretHeader`` is ``true``. Default: - X-Secret-Passphrase
        :param security_group: A security group for the load balancer itself. Default: - A new security group will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cf2c4b4f6d95905cc594637cb1f8523593a0d81a22f8200dc8eec640482dee1)
            check_type(argname="argument certificates", value=certificates, expected_type=type_hints["certificates"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument ip_address_type", value=ip_address_type, expected_type=type_hints["ip_address_type"])
            check_type(argname="argument require_known_hostname", value=require_known_hostname, expected_type=type_hints["require_known_hostname"])
            check_type(argname="argument require_secret_header", value=require_secret_header, expected_type=type_hints["require_secret_header"])
            check_type(argname="argument secret_header_name", value=secret_header_name, expected_type=type_hints["secret_header_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificates": certificates,
            "vpc": vpc,
        }
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if ip_address_type is not None:
            self._values["ip_address_type"] = ip_address_type
        if require_known_hostname is not None:
            self._values["require_known_hostname"] = require_known_hostname
        if require_secret_header is not None:
            self._values["require_secret_header"] = require_secret_header
        if secret_header_name is not None:
            self._values["secret_header_name"] = secret_header_name
        if security_group is not None:
            self._values["security_group"] = security_group

    @builtins.property
    def certificates(
        self,
    ) -> typing.List[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''The certificate to attach to the load balancer and CloudFront distribution.'''
        result = self._values.get("certificates")
        assert result is not None, "Required property 'certificates' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where these resources should be deployed.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The load balancer idle timeout, in seconds.

        If you have a reverse proxy in front of this load balancer, such as
        CloudFront, this number should be less than the reverse proxy's request
        timeout.

        :default: - 59 seconds
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def ip_address_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType]:
        '''The type of IP addresses to use (IPv4 or Dual Stack).

        :default: - IPv4 only
        '''
        result = self._values.get("ip_address_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType], result)

    @builtins.property
    def require_known_hostname(self) -> typing.Optional[builtins.bool]:
        '''Forbid requests that ask for an unknown hostname.

        Requests for an unknown hostname will receive an HTTP 421 status response.

        :default: - false
        '''
        result = self._values.get("require_known_hostname")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_secret_header(self) -> typing.Optional[builtins.bool]:
        '''Forbid requests that are missing an HTTP header with a specific value.

        If this option is set to ``true``, this construct will provide a new
        ``SecretHttpHeader`` accessible on the ``secretHeader`` property.

        Requests without the correct header name and value will receive an HTTP 421
        status response.

        :default: - false
        '''
        result = self._values.get("require_secret_header")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def secret_header_name(self) -> typing.Optional[builtins.str]:
        '''The name of the secret HTTP header.

        Providing this option implies that ``requireSecretHeader`` is ``true``.

        :default: - X-Secret-Passphrase
        '''
        result = self._values.get("secret_header_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''A security group for the load balancer itself.

        :default: - A new security group will be created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebLoadBalancingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ISecretHttpHeader",
    "SecretHttpHeader",
    "SecretHttpHeaderProps",
    "TargetOptions",
    "WebLoadBalancing",
    "WebLoadBalancingProps",
]

publication.publish()

def _typecheckingstub__150cf8e22f1e7d05a47117e8f77da25561199d5daa7118eb196893fa55cfd796(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    header_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40fccea94b7e684de60e1f55e353e1a03b85c56db9135f4d67a939d5448d4694(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c95f74423d937b8be51b1b147dac2d7c254b40cc4b250c45909e61f91bd46e8(
    *,
    header_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efa2d39cd1f01bf3758addd640ec7d1a822d75c3cc97424ddff8b739dca8d900(
    *,
    deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    target_group_name: typing.Optional[builtins.str] = None,
    target_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    load_balancing_algorithm_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType] = None,
    port: typing.Optional[jsii.Number] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    slow_start: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    stickiness_cookie_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    stickiness_cookie_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]] = None,
    hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
    priority: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56342186b82314e198297a3e5364d68b3f8d14f18d4e2c17b5f18a47bffc93d3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
    require_known_hostname: typing.Optional[builtins.bool] = None,
    require_secret_header: typing.Optional[builtins.bool] = None,
    secret_header_name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7e0fb1b7097e928299c71e17989f2f1e1385330c18446d1a211d9b57fa16cc8(
    id: builtins.str,
    target: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget,
    *,
    hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
    priority: typing.Optional[jsii.Number] = None,
    load_balancing_algorithm_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetGroupLoadBalancingAlgorithmType] = None,
    port: typing.Optional[jsii.Number] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    slow_start: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    stickiness_cookie_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    stickiness_cookie_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancerTarget]] = None,
    deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    target_group_name: typing.Optional[builtins.str] = None,
    target_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.TargetType] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cf2c4b4f6d95905cc594637cb1f8523593a0d81a22f8200dc8eec640482dee1(
    *,
    certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
    require_known_hostname: typing.Optional[builtins.bool] = None,
    require_secret_header: typing.Optional[builtins.bool] = None,
    secret_header_name: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
) -> None:
    """Type checking stubs"""
    pass
