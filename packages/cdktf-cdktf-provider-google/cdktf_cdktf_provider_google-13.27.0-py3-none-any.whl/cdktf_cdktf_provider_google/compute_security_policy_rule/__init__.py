r'''
# `google_compute_security_policy_rule`

Refer to the Terraform Registry for docs: [`google_compute_security_policy_rule`](https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class ComputeSecurityPolicyRuleA(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleA",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule google_compute_security_policy_rule}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        action: builtins.str,
        priority: jsii.Number,
        security_policy: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        match: typing.Optional[typing.Union["ComputeSecurityPolicyRuleMatchA", typing.Dict[builtins.str, typing.Any]]] = None,
        preconfigured_waf_config: typing.Optional[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        preview: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        project: typing.Optional[builtins.str] = None,
        rate_limit_options: typing.Optional[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsA", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["ComputeSecurityPolicyRuleTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule google_compute_security_policy_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param action: The Action to perform when the rule is matched. The following are the valid actions:. - allow: allow access to target. - deny(STATUS): deny access to target, returns the HTTP response code specified. Valid values for STATUS are 403, 404, and 502. - rate_based_ban: limit client traffic to the configured threshold and ban the client if the traffic exceeds the threshold. Configure parameters for this action in RateLimitOptions. Requires rateLimitOptions to be set. - redirect: redirect to a different target. This can either be an internal reCAPTCHA redirect, or an external URL-based redirect via a 302 response. Parameters for this action can be configured via redirectOptions. This action is only supported in Global Security Policies of type CLOUD_ARMOR. - throttle: limit client traffic to the configured threshold. Configure parameters for this action in rateLimitOptions. Requires rateLimitOptions to be set for this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#action ComputeSecurityPolicyRuleA#action}
        :param priority: An integer indicating the priority of a rule in the list. The priority must be a positive value between 0 and 2147483647. Rules are evaluated from highest to lowest priority where 0 is the highest priority and 2147483647 is the lowest priority. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#priority ComputeSecurityPolicyRuleA#priority}
        :param security_policy: The name of the security policy this rule belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#security_policy ComputeSecurityPolicyRuleA#security_policy}
        :param description: An optional description of this resource. Provide this property when you create the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#description ComputeSecurityPolicyRuleA#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#id ComputeSecurityPolicyRuleA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param match: match block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#match ComputeSecurityPolicyRuleA#match}
        :param preconfigured_waf_config: preconfigured_waf_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#preconfigured_waf_config ComputeSecurityPolicyRuleA#preconfigured_waf_config}
        :param preview: If set to true, the specified action is not enforced. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#preview ComputeSecurityPolicyRuleA#preview}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#project ComputeSecurityPolicyRuleA#project}.
        :param rate_limit_options: rate_limit_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#rate_limit_options ComputeSecurityPolicyRuleA#rate_limit_options}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#timeouts ComputeSecurityPolicyRuleA#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__691f7fcc7d22a9e12d0f0baadf49d6abcd3ba135731c4245351c0262fa8b3fde)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ComputeSecurityPolicyRuleAConfig(
            action=action,
            priority=priority,
            security_policy=security_policy,
            description=description,
            id=id,
            match=match,
            preconfigured_waf_config=preconfigured_waf_config,
            preview=preview,
            project=project,
            rate_limit_options=rate_limit_options,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ComputeSecurityPolicyRuleA resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ComputeSecurityPolicyRuleA to import.
        :param import_from_id: The id of the existing ComputeSecurityPolicyRuleA that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ComputeSecurityPolicyRuleA to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa84346c8250fe4aa3cb3a595f9ecdb997e3fad4998ab8605aeb2a892f236b36)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putMatch")
    def put_match(
        self,
        *,
        config: typing.Optional[typing.Union["ComputeSecurityPolicyRuleMatchConfigA", typing.Dict[builtins.str, typing.Any]]] = None,
        expr: typing.Optional[typing.Union["ComputeSecurityPolicyRuleMatchExprA", typing.Dict[builtins.str, typing.Any]]] = None,
        expr_options: typing.Optional[typing.Union["ComputeSecurityPolicyRuleMatchExprOptionsA", typing.Dict[builtins.str, typing.Any]]] = None,
        versioned_expr: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#config ComputeSecurityPolicyRuleA#config}
        :param expr: expr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#expr ComputeSecurityPolicyRuleA#expr}
        :param expr_options: expr_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#expr_options ComputeSecurityPolicyRuleA#expr_options}
        :param versioned_expr: Preconfigured versioned expression. If this field is specified, config must also be specified. Available preconfigured expressions along with their requirements are: SRC_IPS_V1 - must specify the corresponding srcIpRange field in config. Possible values: ["SRC_IPS_V1"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#versioned_expr ComputeSecurityPolicyRuleA#versioned_expr}
        '''
        value = ComputeSecurityPolicyRuleMatchA(
            config=config,
            expr=expr,
            expr_options=expr_options,
            versioned_expr=versioned_expr,
        )

        return typing.cast(None, jsii.invoke(self, "putMatch", [value]))

    @jsii.member(jsii_name="putPreconfiguredWafConfig")
    def put_preconfigured_waf_config(
        self,
        *,
        exclusion: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param exclusion: exclusion block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#exclusion ComputeSecurityPolicyRuleA#exclusion}
        '''
        value = ComputeSecurityPolicyRulePreconfiguredWafConfig(exclusion=exclusion)

        return typing.cast(None, jsii.invoke(self, "putPreconfiguredWafConfig", [value]))

    @jsii.member(jsii_name="putRateLimitOptions")
    def put_rate_limit_options(
        self,
        *,
        ban_duration_sec: typing.Optional[jsii.Number] = None,
        ban_threshold: typing.Optional[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA", typing.Dict[builtins.str, typing.Any]]] = None,
        conform_action: typing.Optional[builtins.str] = None,
        enforce_on_key: typing.Optional[builtins.str] = None,
        enforce_on_key_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        enforce_on_key_name: typing.Optional[builtins.str] = None,
        exceed_action: typing.Optional[builtins.str] = None,
        exceed_redirect_options: typing.Optional[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA", typing.Dict[builtins.str, typing.Any]]] = None,
        rate_limit_threshold: typing.Optional[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param ban_duration_sec: Can only be specified if the action for the rule is "rate_based_ban". If specified, determines the time (in seconds) the traffic will continue to be banned by the rate limit after the rate falls below the threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#ban_duration_sec ComputeSecurityPolicyRuleA#ban_duration_sec}
        :param ban_threshold: ban_threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#ban_threshold ComputeSecurityPolicyRuleA#ban_threshold}
        :param conform_action: Action to take for requests that are under the configured rate limit threshold. Valid option is "allow" only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#conform_action ComputeSecurityPolicyRuleA#conform_action}
        :param enforce_on_key: Determines the key to enforce the rateLimitThreshold on. Possible values are: - ALL: A single rate limit threshold is applied to all the requests matching this rule. This is the default value if "enforceOnKey" is not configured. - IP: The source IP address of the request is the key. Each IP has this limit enforced separately. - HTTP_HEADER: The value of the HTTP header whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the header value. If no such header is present in the request, the key type defaults to ALL. - XFF_IP: The first IP address (i.e. the originating client IP address) specified in the list of IPs under X-Forwarded-For HTTP header. If no such header is present or the value is not a valid IP, the key defaults to the source IP address of the request i.e. key type IP. - HTTP_COOKIE: The value of the HTTP cookie whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the cookie value. If no such cookie is present in the request, the key type defaults to ALL. - HTTP_PATH: The URL path of the HTTP request. The key value is truncated to the first 128 bytes. - SNI: Server name indication in the TLS session of the HTTPS request. The key value is truncated to the first 128 bytes. The key type defaults to ALL on a HTTP session. - REGION_CODE: The country/region from which the request originates. - TLS_JA3_FINGERPRINT: JA3 TLS/SSL fingerprint if the client connects using HTTPS, HTTP/2 or HTTP/3. If not available, the key type defaults to ALL. - USER_IP: The IP address of the originating client, which is resolved based on "userIpRequestHeaders" configured with the security policy. If there is no "userIpRequestHeaders" configuration or an IP address cannot be resolved from it, the key type defaults to IP. Possible values: ["ALL", "IP", "HTTP_HEADER", "XFF_IP", "HTTP_COOKIE", "HTTP_PATH", "SNI", "REGION_CODE", "TLS_JA3_FINGERPRINT", "USER_IP"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key ComputeSecurityPolicyRuleA#enforce_on_key}
        :param enforce_on_key_configs: enforce_on_key_configs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_configs ComputeSecurityPolicyRuleA#enforce_on_key_configs}
        :param enforce_on_key_name: Rate limit key name applicable only for the following key types: HTTP_HEADER -- Name of the HTTP header whose value is taken as the key value. HTTP_COOKIE -- Name of the HTTP cookie whose value is taken as the key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_name ComputeSecurityPolicyRuleA#enforce_on_key_name}
        :param exceed_action: Action to take for requests that are above the configured rate limit threshold, to either deny with a specified HTTP response code, or redirect to a different endpoint. Valid options are deny(STATUS), where valid values for STATUS are 403, 404, 429, and 502. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#exceed_action ComputeSecurityPolicyRuleA#exceed_action}
        :param exceed_redirect_options: exceed_redirect_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#exceed_redirect_options ComputeSecurityPolicyRuleA#exceed_redirect_options}
        :param rate_limit_threshold: rate_limit_threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#rate_limit_threshold ComputeSecurityPolicyRuleA#rate_limit_threshold}
        '''
        value = ComputeSecurityPolicyRuleRateLimitOptionsA(
            ban_duration_sec=ban_duration_sec,
            ban_threshold=ban_threshold,
            conform_action=conform_action,
            enforce_on_key=enforce_on_key,
            enforce_on_key_configs=enforce_on_key_configs,
            enforce_on_key_name=enforce_on_key_name,
            exceed_action=exceed_action,
            exceed_redirect_options=exceed_redirect_options,
            rate_limit_threshold=rate_limit_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "putRateLimitOptions", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#create ComputeSecurityPolicyRuleA#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#delete ComputeSecurityPolicyRuleA#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#update ComputeSecurityPolicyRuleA#update}.
        '''
        value = ComputeSecurityPolicyRuleTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMatch")
    def reset_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatch", []))

    @jsii.member(jsii_name="resetPreconfiguredWafConfig")
    def reset_preconfigured_waf_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreconfiguredWafConfig", []))

    @jsii.member(jsii_name="resetPreview")
    def reset_preview(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreview", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @jsii.member(jsii_name="resetRateLimitOptions")
    def reset_rate_limit_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRateLimitOptions", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="match")
    def match(self) -> "ComputeSecurityPolicyRuleMatchAOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleMatchAOutputReference", jsii.get(self, "match"))

    @builtins.property
    @jsii.member(jsii_name="preconfiguredWafConfig")
    def preconfigured_waf_config(
        self,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigOutputReference":
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigOutputReference", jsii.get(self, "preconfiguredWafConfig"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitOptions")
    def rate_limit_options(
        self,
    ) -> "ComputeSecurityPolicyRuleRateLimitOptionsAOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleRateLimitOptionsAOutputReference", jsii.get(self, "rateLimitOptions"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ComputeSecurityPolicyRuleTimeoutsOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="matchInput")
    def match_input(self) -> typing.Optional["ComputeSecurityPolicyRuleMatchA"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleMatchA"], jsii.get(self, "matchInput"))

    @builtins.property
    @jsii.member(jsii_name="preconfiguredWafConfigInput")
    def preconfigured_waf_config_input(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRulePreconfiguredWafConfig"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRulePreconfiguredWafConfig"], jsii.get(self, "preconfiguredWafConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="previewInput")
    def preview_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "previewInput"))

    @builtins.property
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitOptionsInput")
    def rate_limit_options_input(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsA"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsA"], jsii.get(self, "rateLimitOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="securityPolicyInput")
    def security_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ComputeSecurityPolicyRuleTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ComputeSecurityPolicyRuleTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0494db04cb5b1f1caeb403ab3d889b55e48eea59cc56416223ae312cb5fcf73d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1184b3c648b0898eac47d0b8ffa6df9229cb50e4cedb33f6077418976f6bb1fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56b173ad9c43ba279beb002ec1b70ce9afcbb424915397ae9333f1c56cb5f566)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="preview")
    def preview(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "preview"))

    @preview.setter
    def preview(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb1a6ca95315f3d93af6a43694e4312cb281fba62b4105a59d6949d2c1651b1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preview", value)

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6b83a45982f4dd220ccf728ccf32e3283d2530568395a232756338e0f720026)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2708c45644fe79b7c84f86b351ed589155d2586c6e08c2ac87c83bb009e7a665)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)

    @builtins.property
    @jsii.member(jsii_name="securityPolicy")
    def security_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityPolicy"))

    @security_policy.setter
    def security_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9357b6cb3d30ccbe9167f3e9a51317c20986025ffea9c25383185ddda1defbe1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityPolicy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleAConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "action": "action",
        "priority": "priority",
        "security_policy": "securityPolicy",
        "description": "description",
        "id": "id",
        "match": "match",
        "preconfigured_waf_config": "preconfiguredWafConfig",
        "preview": "preview",
        "project": "project",
        "rate_limit_options": "rateLimitOptions",
        "timeouts": "timeouts",
    },
)
class ComputeSecurityPolicyRuleAConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        action: builtins.str,
        priority: jsii.Number,
        security_policy: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        match: typing.Optional[typing.Union["ComputeSecurityPolicyRuleMatchA", typing.Dict[builtins.str, typing.Any]]] = None,
        preconfigured_waf_config: typing.Optional[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        preview: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        project: typing.Optional[builtins.str] = None,
        rate_limit_options: typing.Optional[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsA", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["ComputeSecurityPolicyRuleTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param action: The Action to perform when the rule is matched. The following are the valid actions:. - allow: allow access to target. - deny(STATUS): deny access to target, returns the HTTP response code specified. Valid values for STATUS are 403, 404, and 502. - rate_based_ban: limit client traffic to the configured threshold and ban the client if the traffic exceeds the threshold. Configure parameters for this action in RateLimitOptions. Requires rateLimitOptions to be set. - redirect: redirect to a different target. This can either be an internal reCAPTCHA redirect, or an external URL-based redirect via a 302 response. Parameters for this action can be configured via redirectOptions. This action is only supported in Global Security Policies of type CLOUD_ARMOR. - throttle: limit client traffic to the configured threshold. Configure parameters for this action in rateLimitOptions. Requires rateLimitOptions to be set for this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#action ComputeSecurityPolicyRuleA#action}
        :param priority: An integer indicating the priority of a rule in the list. The priority must be a positive value between 0 and 2147483647. Rules are evaluated from highest to lowest priority where 0 is the highest priority and 2147483647 is the lowest priority. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#priority ComputeSecurityPolicyRuleA#priority}
        :param security_policy: The name of the security policy this rule belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#security_policy ComputeSecurityPolicyRuleA#security_policy}
        :param description: An optional description of this resource. Provide this property when you create the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#description ComputeSecurityPolicyRuleA#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#id ComputeSecurityPolicyRuleA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param match: match block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#match ComputeSecurityPolicyRuleA#match}
        :param preconfigured_waf_config: preconfigured_waf_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#preconfigured_waf_config ComputeSecurityPolicyRuleA#preconfigured_waf_config}
        :param preview: If set to true, the specified action is not enforced. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#preview ComputeSecurityPolicyRuleA#preview}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#project ComputeSecurityPolicyRuleA#project}.
        :param rate_limit_options: rate_limit_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#rate_limit_options ComputeSecurityPolicyRuleA#rate_limit_options}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#timeouts ComputeSecurityPolicyRuleA#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(match, dict):
            match = ComputeSecurityPolicyRuleMatchA(**match)
        if isinstance(preconfigured_waf_config, dict):
            preconfigured_waf_config = ComputeSecurityPolicyRulePreconfiguredWafConfig(**preconfigured_waf_config)
        if isinstance(rate_limit_options, dict):
            rate_limit_options = ComputeSecurityPolicyRuleRateLimitOptionsA(**rate_limit_options)
        if isinstance(timeouts, dict):
            timeouts = ComputeSecurityPolicyRuleTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4262c59dde9bd7ab66c95d422d2fce00e6ef6259eff20144ed8cd410969c5f6)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument security_policy", value=security_policy, expected_type=type_hints["security_policy"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument match", value=match, expected_type=type_hints["match"])
            check_type(argname="argument preconfigured_waf_config", value=preconfigured_waf_config, expected_type=type_hints["preconfigured_waf_config"])
            check_type(argname="argument preview", value=preview, expected_type=type_hints["preview"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument rate_limit_options", value=rate_limit_options, expected_type=type_hints["rate_limit_options"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "priority": priority,
            "security_policy": security_policy,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if match is not None:
            self._values["match"] = match
        if preconfigured_waf_config is not None:
            self._values["preconfigured_waf_config"] = preconfigured_waf_config
        if preview is not None:
            self._values["preview"] = preview
        if project is not None:
            self._values["project"] = project
        if rate_limit_options is not None:
            self._values["rate_limit_options"] = rate_limit_options
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def action(self) -> builtins.str:
        '''The Action to perform when the rule is matched. The following are the valid actions:.

        - allow: allow access to target.
        - deny(STATUS): deny access to target, returns the HTTP response code specified. Valid values for STATUS are 403, 404, and 502.
        - rate_based_ban: limit client traffic to the configured threshold and ban the client if the traffic exceeds the threshold. Configure parameters for this action in RateLimitOptions. Requires rateLimitOptions to be set.
        - redirect: redirect to a different target. This can either be an internal reCAPTCHA redirect, or an external URL-based redirect via a 302 response. Parameters for this action can be configured via redirectOptions. This action is only supported in Global Security Policies of type CLOUD_ARMOR.
        - throttle: limit client traffic to the configured threshold. Configure parameters for this action in rateLimitOptions. Requires rateLimitOptions to be set for this.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#action ComputeSecurityPolicyRuleA#action}
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''An integer indicating the priority of a rule in the list.

        The priority must be a positive value between 0 and 2147483647.
        Rules are evaluated from highest to lowest priority where 0 is the highest priority and 2147483647 is the lowest priority.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#priority ComputeSecurityPolicyRuleA#priority}
        '''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def security_policy(self) -> builtins.str:
        '''The name of the security policy this rule belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#security_policy ComputeSecurityPolicyRuleA#security_policy}
        '''
        result = self._values.get("security_policy")
        assert result is not None, "Required property 'security_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''An optional description of this resource. Provide this property when you create the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#description ComputeSecurityPolicyRuleA#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#id ComputeSecurityPolicyRuleA#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def match(self) -> typing.Optional["ComputeSecurityPolicyRuleMatchA"]:
        '''match block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#match ComputeSecurityPolicyRuleA#match}
        '''
        result = self._values.get("match")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleMatchA"], result)

    @builtins.property
    def preconfigured_waf_config(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRulePreconfiguredWafConfig"]:
        '''preconfigured_waf_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#preconfigured_waf_config ComputeSecurityPolicyRuleA#preconfigured_waf_config}
        '''
        result = self._values.get("preconfigured_waf_config")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRulePreconfiguredWafConfig"], result)

    @builtins.property
    def preview(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, the specified action is not enforced.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#preview ComputeSecurityPolicyRuleA#preview}
        '''
        result = self._values.get("preview")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#project ComputeSecurityPolicyRuleA#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rate_limit_options(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsA"]:
        '''rate_limit_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#rate_limit_options ComputeSecurityPolicyRuleA#rate_limit_options}
        '''
        result = self._values.get("rate_limit_options")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsA"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ComputeSecurityPolicyRuleTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#timeouts ComputeSecurityPolicyRuleA#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleAConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchA",
    jsii_struct_bases=[],
    name_mapping={
        "config": "config",
        "expr": "expr",
        "expr_options": "exprOptions",
        "versioned_expr": "versionedExpr",
    },
)
class ComputeSecurityPolicyRuleMatchA:
    def __init__(
        self,
        *,
        config: typing.Optional[typing.Union["ComputeSecurityPolicyRuleMatchConfigA", typing.Dict[builtins.str, typing.Any]]] = None,
        expr: typing.Optional[typing.Union["ComputeSecurityPolicyRuleMatchExprA", typing.Dict[builtins.str, typing.Any]]] = None,
        expr_options: typing.Optional[typing.Union["ComputeSecurityPolicyRuleMatchExprOptionsA", typing.Dict[builtins.str, typing.Any]]] = None,
        versioned_expr: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#config ComputeSecurityPolicyRuleA#config}
        :param expr: expr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#expr ComputeSecurityPolicyRuleA#expr}
        :param expr_options: expr_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#expr_options ComputeSecurityPolicyRuleA#expr_options}
        :param versioned_expr: Preconfigured versioned expression. If this field is specified, config must also be specified. Available preconfigured expressions along with their requirements are: SRC_IPS_V1 - must specify the corresponding srcIpRange field in config. Possible values: ["SRC_IPS_V1"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#versioned_expr ComputeSecurityPolicyRuleA#versioned_expr}
        '''
        if isinstance(config, dict):
            config = ComputeSecurityPolicyRuleMatchConfigA(**config)
        if isinstance(expr, dict):
            expr = ComputeSecurityPolicyRuleMatchExprA(**expr)
        if isinstance(expr_options, dict):
            expr_options = ComputeSecurityPolicyRuleMatchExprOptionsA(**expr_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65174d8f91f150dcac58e1d728372be3b0633231ede5bdd54ea57b7f7df2165c)
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument expr", value=expr, expected_type=type_hints["expr"])
            check_type(argname="argument expr_options", value=expr_options, expected_type=type_hints["expr_options"])
            check_type(argname="argument versioned_expr", value=versioned_expr, expected_type=type_hints["versioned_expr"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config is not None:
            self._values["config"] = config
        if expr is not None:
            self._values["expr"] = expr
        if expr_options is not None:
            self._values["expr_options"] = expr_options
        if versioned_expr is not None:
            self._values["versioned_expr"] = versioned_expr

    @builtins.property
    def config(self) -> typing.Optional["ComputeSecurityPolicyRuleMatchConfigA"]:
        '''config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#config ComputeSecurityPolicyRuleA#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleMatchConfigA"], result)

    @builtins.property
    def expr(self) -> typing.Optional["ComputeSecurityPolicyRuleMatchExprA"]:
        '''expr block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#expr ComputeSecurityPolicyRuleA#expr}
        '''
        result = self._values.get("expr")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleMatchExprA"], result)

    @builtins.property
    def expr_options(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleMatchExprOptionsA"]:
        '''expr_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#expr_options ComputeSecurityPolicyRuleA#expr_options}
        '''
        result = self._values.get("expr_options")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleMatchExprOptionsA"], result)

    @builtins.property
    def versioned_expr(self) -> typing.Optional[builtins.str]:
        '''Preconfigured versioned expression.

        If this field is specified, config must also be specified.
        Available preconfigured expressions along with their requirements are: SRC_IPS_V1 - must specify the corresponding srcIpRange field in config. Possible values: ["SRC_IPS_V1"]

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#versioned_expr ComputeSecurityPolicyRuleA#versioned_expr}
        '''
        result = self._values.get("versioned_expr")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleMatchA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleMatchAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3cf7ec571d9282573fd4c4c528c1177fc318faeee54c39fb28eedd1b34acacc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        src_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param src_ip_ranges: CIDR IP address range. Maximum number of srcIpRanges allowed is 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#src_ip_ranges ComputeSecurityPolicyRuleA#src_ip_ranges}
        '''
        value = ComputeSecurityPolicyRuleMatchConfigA(src_ip_ranges=src_ip_ranges)

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="putExpr")
    def put_expr(self, *, expression: builtins.str) -> None:
        '''
        :param expression: Textual representation of an expression in Common Expression Language syntax. The application context of the containing message determines which well-known feature set of CEL is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#expression ComputeSecurityPolicyRuleA#expression}
        '''
        value = ComputeSecurityPolicyRuleMatchExprA(expression=expression)

        return typing.cast(None, jsii.invoke(self, "putExpr", [value]))

    @jsii.member(jsii_name="putExprOptions")
    def put_expr_options(
        self,
        *,
        recaptcha_options: typing.Union["ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param recaptcha_options: recaptcha_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#recaptcha_options ComputeSecurityPolicyRuleA#recaptcha_options}
        '''
        value = ComputeSecurityPolicyRuleMatchExprOptionsA(
            recaptcha_options=recaptcha_options
        )

        return typing.cast(None, jsii.invoke(self, "putExprOptions", [value]))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="resetExpr")
    def reset_expr(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpr", []))

    @jsii.member(jsii_name="resetExprOptions")
    def reset_expr_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExprOptions", []))

    @jsii.member(jsii_name="resetVersionedExpr")
    def reset_versioned_expr(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersionedExpr", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "ComputeSecurityPolicyRuleMatchConfigAOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleMatchConfigAOutputReference", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="expr")
    def expr(self) -> "ComputeSecurityPolicyRuleMatchExprAOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleMatchExprAOutputReference", jsii.get(self, "expr"))

    @builtins.property
    @jsii.member(jsii_name="exprOptions")
    def expr_options(
        self,
    ) -> "ComputeSecurityPolicyRuleMatchExprOptionsAOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleMatchExprOptionsAOutputReference", jsii.get(self, "exprOptions"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(self) -> typing.Optional["ComputeSecurityPolicyRuleMatchConfigA"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleMatchConfigA"], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="exprInput")
    def expr_input(self) -> typing.Optional["ComputeSecurityPolicyRuleMatchExprA"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleMatchExprA"], jsii.get(self, "exprInput"))

    @builtins.property
    @jsii.member(jsii_name="exprOptionsInput")
    def expr_options_input(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleMatchExprOptionsA"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleMatchExprOptionsA"], jsii.get(self, "exprOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="versionedExprInput")
    def versioned_expr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionedExprInput"))

    @builtins.property
    @jsii.member(jsii_name="versionedExpr")
    def versioned_expr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionedExpr"))

    @versioned_expr.setter
    def versioned_expr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59647a7baa9c1256980a903143cc704b556bc779dc5a6b64ccf48afe0903b676)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "versionedExpr", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ComputeSecurityPolicyRuleMatchA]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRuleMatchA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRuleMatchA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__840439d5051bc274b962eb072c1e27b16c24f61551a3a4c618ac5808980e27e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchConfigA",
    jsii_struct_bases=[],
    name_mapping={"src_ip_ranges": "srcIpRanges"},
)
class ComputeSecurityPolicyRuleMatchConfigA:
    def __init__(
        self,
        *,
        src_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param src_ip_ranges: CIDR IP address range. Maximum number of srcIpRanges allowed is 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#src_ip_ranges ComputeSecurityPolicyRuleA#src_ip_ranges}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5b6ab2577b3c54368655c6d34d83d27c17c78d97c419cb239e85ca822397f13)
            check_type(argname="argument src_ip_ranges", value=src_ip_ranges, expected_type=type_hints["src_ip_ranges"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if src_ip_ranges is not None:
            self._values["src_ip_ranges"] = src_ip_ranges

    @builtins.property
    def src_ip_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''CIDR IP address range. Maximum number of srcIpRanges allowed is 10.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#src_ip_ranges ComputeSecurityPolicyRuleA#src_ip_ranges}
        '''
        result = self._values.get("src_ip_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleMatchConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleMatchConfigAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchConfigAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b04cc9efd64a083969f0780ec78860ce7e37eb4fa1fb1c0f601a36bc49884d0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSrcIpRanges")
    def reset_src_ip_ranges(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSrcIpRanges", []))

    @builtins.property
    @jsii.member(jsii_name="srcIpRangesInput")
    def src_ip_ranges_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "srcIpRangesInput"))

    @builtins.property
    @jsii.member(jsii_name="srcIpRanges")
    def src_ip_ranges(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "srcIpRanges"))

    @src_ip_ranges.setter
    def src_ip_ranges(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36b67d93a953c4a841fee0257bd3fc80202e01d42b4ae546e1dc41981a4314b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "srcIpRanges", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ComputeSecurityPolicyRuleMatchConfigA]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRuleMatchConfigA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRuleMatchConfigA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86b50d2d9301f0976b51e0501aa539e2fbe9b29772586a12f66c8fe7e0ebf4e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchExprA",
    jsii_struct_bases=[],
    name_mapping={"expression": "expression"},
)
class ComputeSecurityPolicyRuleMatchExprA:
    def __init__(self, *, expression: builtins.str) -> None:
        '''
        :param expression: Textual representation of an expression in Common Expression Language syntax. The application context of the containing message determines which well-known feature set of CEL is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#expression ComputeSecurityPolicyRuleA#expression}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e4e1bab806a7c61d681ea6878e985e466a1c79c4e8c7af3d0664434a0ae4256)
            check_type(argname="argument expression", value=expression, expected_type=type_hints["expression"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "expression": expression,
        }

    @builtins.property
    def expression(self) -> builtins.str:
        '''Textual representation of an expression in Common Expression Language syntax.

        The application context of the containing message determines which well-known feature set of CEL is supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#expression ComputeSecurityPolicyRuleA#expression}
        '''
        result = self._values.get("expression")
        assert result is not None, "Required property 'expression' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleMatchExprA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleMatchExprAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchExprAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc9ceda20ac2988a4e62cebf98e9148fda21535ad47e8d8a0398f4809f2212bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="expressionInput")
    def expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expressionInput"))

    @builtins.property
    @jsii.member(jsii_name="expression")
    def expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expression"))

    @expression.setter
    def expression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2740bf3d2a484c57d599f7f9bbc0728459f8d871bb93ab3f48e6e4de9862b6ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expression", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ComputeSecurityPolicyRuleMatchExprA]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRuleMatchExprA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRuleMatchExprA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40b9e433e9c35e26a16d8b5b438d8575cf8e1424bff1cb1c8f02e80bfc57a96a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchExprOptionsA",
    jsii_struct_bases=[],
    name_mapping={"recaptcha_options": "recaptchaOptions"},
)
class ComputeSecurityPolicyRuleMatchExprOptionsA:
    def __init__(
        self,
        *,
        recaptcha_options: typing.Union["ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param recaptcha_options: recaptcha_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#recaptcha_options ComputeSecurityPolicyRuleA#recaptcha_options}
        '''
        if isinstance(recaptcha_options, dict):
            recaptcha_options = ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA(**recaptcha_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__055bf2d0d71f440aa828c41c8a4b4e22a07285e5d79ca34e7394305233e5b60d)
            check_type(argname="argument recaptcha_options", value=recaptcha_options, expected_type=type_hints["recaptcha_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "recaptcha_options": recaptcha_options,
        }

    @builtins.property
    def recaptcha_options(
        self,
    ) -> "ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA":
        '''recaptcha_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#recaptcha_options ComputeSecurityPolicyRuleA#recaptcha_options}
        '''
        result = self._values.get("recaptcha_options")
        assert result is not None, "Required property 'recaptcha_options' is missing"
        return typing.cast("ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleMatchExprOptionsA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleMatchExprOptionsAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchExprOptionsAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca8858b9b4ebb3761b6ef83756ff82ecfe5bb019170a0ec7c422451c940d1e95)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRecaptchaOptions")
    def put_recaptcha_options(
        self,
        *,
        action_token_site_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        session_token_site_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param action_token_site_keys: A list of site keys to be used during the validation of reCAPTCHA action-tokens. The provided site keys need to be created from reCAPTCHA API under the same project where the security policy is created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#action_token_site_keys ComputeSecurityPolicyRuleA#action_token_site_keys}
        :param session_token_site_keys: A list of site keys to be used during the validation of reCAPTCHA session-tokens. The provided site keys need to be created from reCAPTCHA API under the same project where the security policy is created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#session_token_site_keys ComputeSecurityPolicyRuleA#session_token_site_keys}
        '''
        value = ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA(
            action_token_site_keys=action_token_site_keys,
            session_token_site_keys=session_token_site_keys,
        )

        return typing.cast(None, jsii.invoke(self, "putRecaptchaOptions", [value]))

    @builtins.property
    @jsii.member(jsii_name="recaptchaOptions")
    def recaptcha_options(
        self,
    ) -> "ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsAOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsAOutputReference", jsii.get(self, "recaptchaOptions"))

    @builtins.property
    @jsii.member(jsii_name="recaptchaOptionsInput")
    def recaptcha_options_input(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA"], jsii.get(self, "recaptchaOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ComputeSecurityPolicyRuleMatchExprOptionsA]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRuleMatchExprOptionsA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRuleMatchExprOptionsA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4a45ed025a064552c9bd4755e6ce04a1f882ff85380f62c326969858a43cc2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA",
    jsii_struct_bases=[],
    name_mapping={
        "action_token_site_keys": "actionTokenSiteKeys",
        "session_token_site_keys": "sessionTokenSiteKeys",
    },
)
class ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA:
    def __init__(
        self,
        *,
        action_token_site_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        session_token_site_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param action_token_site_keys: A list of site keys to be used during the validation of reCAPTCHA action-tokens. The provided site keys need to be created from reCAPTCHA API under the same project where the security policy is created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#action_token_site_keys ComputeSecurityPolicyRuleA#action_token_site_keys}
        :param session_token_site_keys: A list of site keys to be used during the validation of reCAPTCHA session-tokens. The provided site keys need to be created from reCAPTCHA API under the same project where the security policy is created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#session_token_site_keys ComputeSecurityPolicyRuleA#session_token_site_keys}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a7abf57ca54b23bd0ffd27b075c465845cf1994307e7a784fab7f68c2e30c8a)
            check_type(argname="argument action_token_site_keys", value=action_token_site_keys, expected_type=type_hints["action_token_site_keys"])
            check_type(argname="argument session_token_site_keys", value=session_token_site_keys, expected_type=type_hints["session_token_site_keys"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if action_token_site_keys is not None:
            self._values["action_token_site_keys"] = action_token_site_keys
        if session_token_site_keys is not None:
            self._values["session_token_site_keys"] = session_token_site_keys

    @builtins.property
    def action_token_site_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of site keys to be used during the validation of reCAPTCHA action-tokens.

        The provided site keys need to be created from reCAPTCHA API under the same project where the security policy is created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#action_token_site_keys ComputeSecurityPolicyRuleA#action_token_site_keys}
        '''
        result = self._values.get("action_token_site_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def session_token_site_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of site keys to be used during the validation of reCAPTCHA session-tokens.

        The provided site keys need to be created from reCAPTCHA API under the same project where the security policy is created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#session_token_site_keys ComputeSecurityPolicyRuleA#session_token_site_keys}
        '''
        result = self._values.get("session_token_site_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__432bcd1f8ad5cce52f6af6803e9e39dc45e0447d3078d93f6ae264c77b9fe1df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetActionTokenSiteKeys")
    def reset_action_token_site_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionTokenSiteKeys", []))

    @jsii.member(jsii_name="resetSessionTokenSiteKeys")
    def reset_session_token_site_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionTokenSiteKeys", []))

    @builtins.property
    @jsii.member(jsii_name="actionTokenSiteKeysInput")
    def action_token_site_keys_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "actionTokenSiteKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionTokenSiteKeysInput")
    def session_token_site_keys_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sessionTokenSiteKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="actionTokenSiteKeys")
    def action_token_site_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "actionTokenSiteKeys"))

    @action_token_site_keys.setter
    def action_token_site_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a516228e6148beff957229ec7bb2533c546e034098e6b2e40bce5a8d6350ef31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionTokenSiteKeys", value)

    @builtins.property
    @jsii.member(jsii_name="sessionTokenSiteKeys")
    def session_token_site_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sessionTokenSiteKeys"))

    @session_token_site_keys.setter
    def session_token_site_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b062e24842185c2638e781f43a43d6d839772c897a5812513a70fdad9632037d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionTokenSiteKeys", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1932c30d6536ac49bb7dd8c62fbeb21b6767c86a490bda27f190faac015cf494)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfig",
    jsii_struct_bases=[],
    name_mapping={"exclusion": "exclusion"},
)
class ComputeSecurityPolicyRulePreconfiguredWafConfig:
    def __init__(
        self,
        *,
        exclusion: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param exclusion: exclusion block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#exclusion ComputeSecurityPolicyRuleA#exclusion}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb562d2528ffa364f09b9608349f7fab272682025bec7f690f3a56e24f924d78)
            check_type(argname="argument exclusion", value=exclusion, expected_type=type_hints["exclusion"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclusion is not None:
            self._values["exclusion"] = exclusion

    @builtins.property
    def exclusion(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion"]]]:
        '''exclusion block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#exclusion ComputeSecurityPolicyRuleA#exclusion}
        '''
        result = self._values.get("exclusion")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRulePreconfiguredWafConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion",
    jsii_struct_bases=[],
    name_mapping={
        "target_rule_set": "targetRuleSet",
        "request_cookie": "requestCookie",
        "request_header": "requestHeader",
        "request_query_param": "requestQueryParam",
        "request_uri": "requestUri",
        "target_rule_ids": "targetRuleIds",
    },
)
class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion:
    def __init__(
        self,
        *,
        target_rule_set: builtins.str,
        request_cookie: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie", typing.Dict[builtins.str, typing.Any]]]]] = None,
        request_header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader", typing.Dict[builtins.str, typing.Any]]]]] = None,
        request_query_param: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam", typing.Dict[builtins.str, typing.Any]]]]] = None,
        request_uri: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri", typing.Dict[builtins.str, typing.Any]]]]] = None,
        target_rule_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param target_rule_set: Target WAF rule set to apply the preconfigured WAF exclusion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#target_rule_set ComputeSecurityPolicyRuleA#target_rule_set}
        :param request_cookie: request_cookie block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#request_cookie ComputeSecurityPolicyRuleA#request_cookie}
        :param request_header: request_header block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#request_header ComputeSecurityPolicyRuleA#request_header}
        :param request_query_param: request_query_param block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#request_query_param ComputeSecurityPolicyRuleA#request_query_param}
        :param request_uri: request_uri block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#request_uri ComputeSecurityPolicyRuleA#request_uri}
        :param target_rule_ids: A list of target rule IDs under the WAF rule set to apply the preconfigured WAF exclusion. If omitted, it refers to all the rule IDs under the WAF rule set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#target_rule_ids ComputeSecurityPolicyRuleA#target_rule_ids}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40391ae7f179dc8c8655c6f1aad63d715bc493b602da818c8a3458e66d1d407b)
            check_type(argname="argument target_rule_set", value=target_rule_set, expected_type=type_hints["target_rule_set"])
            check_type(argname="argument request_cookie", value=request_cookie, expected_type=type_hints["request_cookie"])
            check_type(argname="argument request_header", value=request_header, expected_type=type_hints["request_header"])
            check_type(argname="argument request_query_param", value=request_query_param, expected_type=type_hints["request_query_param"])
            check_type(argname="argument request_uri", value=request_uri, expected_type=type_hints["request_uri"])
            check_type(argname="argument target_rule_ids", value=target_rule_ids, expected_type=type_hints["target_rule_ids"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target_rule_set": target_rule_set,
        }
        if request_cookie is not None:
            self._values["request_cookie"] = request_cookie
        if request_header is not None:
            self._values["request_header"] = request_header
        if request_query_param is not None:
            self._values["request_query_param"] = request_query_param
        if request_uri is not None:
            self._values["request_uri"] = request_uri
        if target_rule_ids is not None:
            self._values["target_rule_ids"] = target_rule_ids

    @builtins.property
    def target_rule_set(self) -> builtins.str:
        '''Target WAF rule set to apply the preconfigured WAF exclusion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#target_rule_set ComputeSecurityPolicyRuleA#target_rule_set}
        '''
        result = self._values.get("target_rule_set")
        assert result is not None, "Required property 'target_rule_set' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def request_cookie(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie"]]]:
        '''request_cookie block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#request_cookie ComputeSecurityPolicyRuleA#request_cookie}
        '''
        result = self._values.get("request_cookie")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie"]]], result)

    @builtins.property
    def request_header(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader"]]]:
        '''request_header block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#request_header ComputeSecurityPolicyRuleA#request_header}
        '''
        result = self._values.get("request_header")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader"]]], result)

    @builtins.property
    def request_query_param(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam"]]]:
        '''request_query_param block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#request_query_param ComputeSecurityPolicyRuleA#request_query_param}
        '''
        result = self._values.get("request_query_param")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam"]]], result)

    @builtins.property
    def request_uri(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri"]]]:
        '''request_uri block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#request_uri ComputeSecurityPolicyRuleA#request_uri}
        '''
        result = self._values.get("request_uri")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri"]]], result)

    @builtins.property
    def target_rule_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of target rule IDs under the WAF rule set to apply the preconfigured WAF exclusion.

        If omitted, it refers to all the rule IDs under the WAF rule set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#target_rule_ids ComputeSecurityPolicyRuleA#target_rule_ids}
        '''
        result = self._values.get("target_rule_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ac700cbfcb16216c732003c8012a027e5aad9619e178f123590fbb0eaf0f438)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6dfa535097047ffc24fa47b7d750816a570dda2b7b1b4170a8aca87d3032814)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2c9d9c51b433afaa250a40f4861164ef24d2163685944c0a767fc2e56ae7038)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc8654751fc217c791de50e44b8faeb0d07d360e8e1f178d0f97fd2febec5f0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7b5c1953898e19c481009e46e3a7719c3972f7a167f5b0414b8125c5fbe7164)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59c69a78645843d9f7c12f5a294a34d9eededa8cf829d270efa1f44658247812)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1718f83a7a1d17d6da0da6c3e1c9e86d25abcf62f137f302e02db86c8141d699)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putRequestCookie")
    def put_request_cookie(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88c14ab69049b111694c252ba388d4d3145c513bae1ce6c815f88a6c1740fd1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRequestCookie", [value]))

    @jsii.member(jsii_name="putRequestHeader")
    def put_request_header(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4a861e98aff9d249bae8d0ea3b695c94ffa6126e83e50298627afe7d7fc90f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRequestHeader", [value]))

    @jsii.member(jsii_name="putRequestQueryParam")
    def put_request_query_param(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__205fda1952a03d8a90abf17e97dc24fcd76667832e8ce4e9d2b2f14ef142f1eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRequestQueryParam", [value]))

    @jsii.member(jsii_name="putRequestUri")
    def put_request_uri(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__613da6435808f70e4879826987f764d3c2857c73035eb66761e1253273e5967e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRequestUri", [value]))

    @jsii.member(jsii_name="resetRequestCookie")
    def reset_request_cookie(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestCookie", []))

    @jsii.member(jsii_name="resetRequestHeader")
    def reset_request_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestHeader", []))

    @jsii.member(jsii_name="resetRequestQueryParam")
    def reset_request_query_param(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestQueryParam", []))

    @jsii.member(jsii_name="resetRequestUri")
    def reset_request_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestUri", []))

    @jsii.member(jsii_name="resetTargetRuleIds")
    def reset_target_rule_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetRuleIds", []))

    @builtins.property
    @jsii.member(jsii_name="requestCookie")
    def request_cookie(
        self,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieList":
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieList", jsii.get(self, "requestCookie"))

    @builtins.property
    @jsii.member(jsii_name="requestHeader")
    def request_header(
        self,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderList":
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderList", jsii.get(self, "requestHeader"))

    @builtins.property
    @jsii.member(jsii_name="requestQueryParam")
    def request_query_param(
        self,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamList":
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamList", jsii.get(self, "requestQueryParam"))

    @builtins.property
    @jsii.member(jsii_name="requestUri")
    def request_uri(
        self,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriList":
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriList", jsii.get(self, "requestUri"))

    @builtins.property
    @jsii.member(jsii_name="requestCookieInput")
    def request_cookie_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie"]]], jsii.get(self, "requestCookieInput"))

    @builtins.property
    @jsii.member(jsii_name="requestHeaderInput")
    def request_header_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader"]]], jsii.get(self, "requestHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="requestQueryParamInput")
    def request_query_param_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam"]]], jsii.get(self, "requestQueryParamInput"))

    @builtins.property
    @jsii.member(jsii_name="requestUriInput")
    def request_uri_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri"]]], jsii.get(self, "requestUriInput"))

    @builtins.property
    @jsii.member(jsii_name="targetRuleIdsInput")
    def target_rule_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetRuleIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetRuleSetInput")
    def target_rule_set_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetRuleSetInput"))

    @builtins.property
    @jsii.member(jsii_name="targetRuleIds")
    def target_rule_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetRuleIds"))

    @target_rule_ids.setter
    def target_rule_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b60eb767561d77488b3bcb67308a0fcfc91711ed4c2449025c92db058cbebffb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetRuleIds", value)

    @builtins.property
    @jsii.member(jsii_name="targetRuleSet")
    def target_rule_set(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetRuleSet"))

    @target_rule_set.setter
    def target_rule_set(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66c1b34badb23eaf30a2bfaf34257b552ed7bc320617cf0cdf0ce0b3cfc257bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetRuleSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__143df5906f4f127e92edd0ce325a19b6239abe3e59e5f1f30919065b785af787)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "value": "value"},
)
class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie:
    def __init__(
        self,
        *,
        operator: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param operator: You can specify an exact match or a partial match by using a field operator and a field value. Available options: EQUALS: The operator matches if the field value equals the specified value. STARTS_WITH: The operator matches if the field value starts with the specified value. ENDS_WITH: The operator matches if the field value ends with the specified value. CONTAINS: The operator matches if the field value contains the specified value. EQUALS_ANY: The operator matches if the field value is any value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#operator ComputeSecurityPolicyRuleA#operator}
        :param value: A request field matching the specified value will be excluded from inspection during preconfigured WAF evaluation. The field value must be given if the field operator is not EQUALS_ANY, and cannot be given if the field operator is EQUALS_ANY. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#value ComputeSecurityPolicyRuleA#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f8581d0132a7305f57a2761184c4afaf9083c303e169ec7a5ee824116a5fd3e)
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "operator": operator,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def operator(self) -> builtins.str:
        '''You can specify an exact match or a partial match by using a field operator and a field value.

        Available options:
        EQUALS: The operator matches if the field value equals the specified value.
        STARTS_WITH: The operator matches if the field value starts with the specified value.
        ENDS_WITH: The operator matches if the field value ends with the specified value.
        CONTAINS: The operator matches if the field value contains the specified value.
        EQUALS_ANY: The operator matches if the field value is any value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#operator ComputeSecurityPolicyRuleA#operator}
        '''
        result = self._values.get("operator")
        assert result is not None, "Required property 'operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''A request field matching the specified value will be excluded from inspection during preconfigured WAF evaluation.

        The field value must be given if the field operator is not EQUALS_ANY, and cannot be given if the field operator is EQUALS_ANY.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#value ComputeSecurityPolicyRuleA#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64632fb88e32222927132e713a68270889fc6b59cf5ee45e726b9ce38b7843d3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6eca32181723581b910d50cd854e698ab3bead16a98859cfb6bccc6cfdbc70cd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a3465c60df45faf83b74436f1b7b2c85f3e883b1a75fe5249947082b751523d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e77d64bebcbc875fdd3655a1b9301dfe0bb34881221f18d532a22396971b96b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd26a1772e6616811d315754fe258fafc8fd351abe829741036f85a78a691178)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef3cd6b85ad8b742725f7b83db3e3b0c98b615811b392a4eda90e27af61ee9cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d06f9b82028a4cfb60a4bf3b59423c4cd42fad910b2507c6e68bdfeced4b0a6d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b09bb3a4bc03a2c49f4ed0656a6a3456f3f2b1ac9f93ded380d54942ef9a53a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value)

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41b94c8978368c0a2cd34ab78d16587e7ef2b523511e550447a61eb27b4d5826)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b09b7cdf2de337ce850900cdec51589377d6692280c6b7dedfede19c5fbc01b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "value": "value"},
)
class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader:
    def __init__(
        self,
        *,
        operator: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param operator: You can specify an exact match or a partial match by using a field operator and a field value. Available options: EQUALS: The operator matches if the field value equals the specified value. STARTS_WITH: The operator matches if the field value starts with the specified value. ENDS_WITH: The operator matches if the field value ends with the specified value. CONTAINS: The operator matches if the field value contains the specified value. EQUALS_ANY: The operator matches if the field value is any value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#operator ComputeSecurityPolicyRuleA#operator}
        :param value: A request field matching the specified value will be excluded from inspection during preconfigured WAF evaluation. The field value must be given if the field operator is not EQUALS_ANY, and cannot be given if the field operator is EQUALS_ANY. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#value ComputeSecurityPolicyRuleA#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f577bfeeb81cba99ce321886c45146ce788c259aac52dc13f6bfd27e7f3944ed)
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "operator": operator,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def operator(self) -> builtins.str:
        '''You can specify an exact match or a partial match by using a field operator and a field value.

        Available options:
        EQUALS: The operator matches if the field value equals the specified value.
        STARTS_WITH: The operator matches if the field value starts with the specified value.
        ENDS_WITH: The operator matches if the field value ends with the specified value.
        CONTAINS: The operator matches if the field value contains the specified value.
        EQUALS_ANY: The operator matches if the field value is any value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#operator ComputeSecurityPolicyRuleA#operator}
        '''
        result = self._values.get("operator")
        assert result is not None, "Required property 'operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''A request field matching the specified value will be excluded from inspection during preconfigured WAF evaluation.

        The field value must be given if the field operator is not EQUALS_ANY, and cannot be given if the field operator is EQUALS_ANY.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#value ComputeSecurityPolicyRuleA#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07f6a13b7ba20db39bf5d9f0b16b1ac3b747f6f06274f7191f42e21367a6e761)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bc95de1036940b474f30c5e7f33b2c8a2a00ad324be5a6f8f01c94ed360060b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8db69ece1ae0d43f08b86082ed041514da204d6340b9a9ecbdcb5476195038e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80de57514d7f1918030bc22b3c23dbda6089aa64c55d1eb6efaf83d4c295e323)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48f79d3b034a543796a187b8e43ff8349a2f9f126bb976b1b6d27d1a8e7cc98c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc3c0f7e94beb6ad4b0e11ac7cfe26839e89417fbd55376b8a11451ed3271c7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d896c717fe5677579db1b89b336efdf4a0cdba7c41b6991af3171ddc20dc2992)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94958fa9405db5a495f38b29d5141e311321c065f987842d924166b435fcb774)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value)

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fc6a3287614c8a0d042e2919b15adcacf1f10db6869f64340768d5da0297f48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10ad779a65b439118268f63cfcff5fe19f74aa9d82206c1893db9dd90f4f6bd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "value": "value"},
)
class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam:
    def __init__(
        self,
        *,
        operator: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param operator: You can specify an exact match or a partial match by using a field operator and a field value. Available options: EQUALS: The operator matches if the field value equals the specified value. STARTS_WITH: The operator matches if the field value starts with the specified value. ENDS_WITH: The operator matches if the field value ends with the specified value. CONTAINS: The operator matches if the field value contains the specified value. EQUALS_ANY: The operator matches if the field value is any value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#operator ComputeSecurityPolicyRuleA#operator}
        :param value: A request field matching the specified value will be excluded from inspection during preconfigured WAF evaluation. The field value must be given if the field operator is not EQUALS_ANY, and cannot be given if the field operator is EQUALS_ANY. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#value ComputeSecurityPolicyRuleA#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__902683da211adef53a8b75b82cf7eda73eecffb8b7270b6d864ee1987972ca73)
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "operator": operator,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def operator(self) -> builtins.str:
        '''You can specify an exact match or a partial match by using a field operator and a field value.

        Available options:
        EQUALS: The operator matches if the field value equals the specified value.
        STARTS_WITH: The operator matches if the field value starts with the specified value.
        ENDS_WITH: The operator matches if the field value ends with the specified value.
        CONTAINS: The operator matches if the field value contains the specified value.
        EQUALS_ANY: The operator matches if the field value is any value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#operator ComputeSecurityPolicyRuleA#operator}
        '''
        result = self._values.get("operator")
        assert result is not None, "Required property 'operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''A request field matching the specified value will be excluded from inspection during preconfigured WAF evaluation.

        The field value must be given if the field operator is not EQUALS_ANY, and cannot be given if the field operator is EQUALS_ANY.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#value ComputeSecurityPolicyRuleA#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7071b66a460117ef92ec687e938fb9bd190aabb94d067c63a88ba72a5a8ec19)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2df9801c44cee2b3d653f8f741e37d4a04c9ecf18db9c83ddac240f76c133471)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5f7fa5a7b3170dd962f7581858a700064231bf010fb000e497f899dc2003273)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d91899abf35cc8a8debca80c628fedd06364dc2e9c8b5d9d57ff4525d3c8a5fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbf3c3910672460decd917dc59896304dc4ad12e5b0ad2999fbc3bdb7a2b4702)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c74ef870f5fc34a7478458441a7e0cbf79976fe4a5cd280a4a0453d59686b8b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a0eca5b148867fb5a3cef20f414ee52fa01649234bd2801e02c49551438059a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fc29dfcc505dd38d65027aa21bb919b4ef322c2ec195ffacd7577cc8355d972)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value)

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24b6db40080c91213cec914a56a72e7c6a2e9f444a615db688ebea08b1bc4dbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f32f9ca3978e5f26cd5c35e3818941e759f7637a0321793e712670c60306f31b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "value": "value"},
)
class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri:
    def __init__(
        self,
        *,
        operator: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param operator: You can specify an exact match or a partial match by using a field operator and a field value. Available options: EQUALS: The operator matches if the field value equals the specified value. STARTS_WITH: The operator matches if the field value starts with the specified value. ENDS_WITH: The operator matches if the field value ends with the specified value. CONTAINS: The operator matches if the field value contains the specified value. EQUALS_ANY: The operator matches if the field value is any value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#operator ComputeSecurityPolicyRuleA#operator}
        :param value: A request field matching the specified value will be excluded from inspection during preconfigured WAF evaluation. The field value must be given if the field operator is not EQUALS_ANY, and cannot be given if the field operator is EQUALS_ANY. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#value ComputeSecurityPolicyRuleA#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e61d7ee259265062db01f4f84e317cefc8e947048206499073f0e68038993e0)
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "operator": operator,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def operator(self) -> builtins.str:
        '''You can specify an exact match or a partial match by using a field operator and a field value.

        Available options:
        EQUALS: The operator matches if the field value equals the specified value.
        STARTS_WITH: The operator matches if the field value starts with the specified value.
        ENDS_WITH: The operator matches if the field value ends with the specified value.
        CONTAINS: The operator matches if the field value contains the specified value.
        EQUALS_ANY: The operator matches if the field value is any value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#operator ComputeSecurityPolicyRuleA#operator}
        '''
        result = self._values.get("operator")
        assert result is not None, "Required property 'operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''A request field matching the specified value will be excluded from inspection during preconfigured WAF evaluation.

        The field value must be given if the field operator is not EQUALS_ANY, and cannot be given if the field operator is EQUALS_ANY.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#value ComputeSecurityPolicyRuleA#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7ae78febfeb43d9c5eaf3e9dca168ebfd295ba97149f0683dae93df981b2b60)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a370fb5336bc7e326df26752e7deb8b71ec1c159ee444d6101a99798c3ad69c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8481a2c963472547cae7375fd47fc112eca9d574e1b7649bd41a175384b5a48b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caba8a1efbd9c2af1ddafe181a3664c3aa1036a1ba590df461372c72e6dc4d84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0420df8557688a9f0d5c692c87dcb26bc09b564ba63441236b74de13b51ad401)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c68a2a1e4e10632ed6f77e0b5cccff74e2bc474fdb687934d97bb8aac10886ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd4cd4248d2871da30887d952113c9169570d62964ffe09c99c9df5f0dcd0549)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8da09d0e6eeb43cac700ab4dfd684eaf166e8d9632857019e6641b2c9e1f293f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value)

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f66e96384fcfef4a006891518f38bd49e7dd6696219d4002981e2e7ce20eaeed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f207a85cd235fdc4408f176a1c5048e9d428be8ab62f12e566be769b36ffd41b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ComputeSecurityPolicyRulePreconfiguredWafConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRulePreconfiguredWafConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3e5a4947578043377decb97b3169615f64eabb0c1c4bf939c2f2bf0ed0c106)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putExclusion")
    def put_exclusion(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2f050fec3d00dba590cb85e41bedad411a005db418976d62692ec8d1155cb64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExclusion", [value]))

    @jsii.member(jsii_name="resetExclusion")
    def reset_exclusion(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExclusion", []))

    @builtins.property
    @jsii.member(jsii_name="exclusion")
    def exclusion(self) -> ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionList:
        return typing.cast(ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionList, jsii.get(self, "exclusion"))

    @builtins.property
    @jsii.member(jsii_name="exclusionInput")
    def exclusion_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]]], jsii.get(self, "exclusionInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ComputeSecurityPolicyRulePreconfiguredWafConfig]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRulePreconfiguredWafConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRulePreconfiguredWafConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4b26c87f96de4a5861435bc0fec0ad2993d0bc034d07c6b198c986c4242595b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsA",
    jsii_struct_bases=[],
    name_mapping={
        "ban_duration_sec": "banDurationSec",
        "ban_threshold": "banThreshold",
        "conform_action": "conformAction",
        "enforce_on_key": "enforceOnKey",
        "enforce_on_key_configs": "enforceOnKeyConfigs",
        "enforce_on_key_name": "enforceOnKeyName",
        "exceed_action": "exceedAction",
        "exceed_redirect_options": "exceedRedirectOptions",
        "rate_limit_threshold": "rateLimitThreshold",
    },
)
class ComputeSecurityPolicyRuleRateLimitOptionsA:
    def __init__(
        self,
        *,
        ban_duration_sec: typing.Optional[jsii.Number] = None,
        ban_threshold: typing.Optional[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA", typing.Dict[builtins.str, typing.Any]]] = None,
        conform_action: typing.Optional[builtins.str] = None,
        enforce_on_key: typing.Optional[builtins.str] = None,
        enforce_on_key_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        enforce_on_key_name: typing.Optional[builtins.str] = None,
        exceed_action: typing.Optional[builtins.str] = None,
        exceed_redirect_options: typing.Optional[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA", typing.Dict[builtins.str, typing.Any]]] = None,
        rate_limit_threshold: typing.Optional[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param ban_duration_sec: Can only be specified if the action for the rule is "rate_based_ban". If specified, determines the time (in seconds) the traffic will continue to be banned by the rate limit after the rate falls below the threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#ban_duration_sec ComputeSecurityPolicyRuleA#ban_duration_sec}
        :param ban_threshold: ban_threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#ban_threshold ComputeSecurityPolicyRuleA#ban_threshold}
        :param conform_action: Action to take for requests that are under the configured rate limit threshold. Valid option is "allow" only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#conform_action ComputeSecurityPolicyRuleA#conform_action}
        :param enforce_on_key: Determines the key to enforce the rateLimitThreshold on. Possible values are: - ALL: A single rate limit threshold is applied to all the requests matching this rule. This is the default value if "enforceOnKey" is not configured. - IP: The source IP address of the request is the key. Each IP has this limit enforced separately. - HTTP_HEADER: The value of the HTTP header whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the header value. If no such header is present in the request, the key type defaults to ALL. - XFF_IP: The first IP address (i.e. the originating client IP address) specified in the list of IPs under X-Forwarded-For HTTP header. If no such header is present or the value is not a valid IP, the key defaults to the source IP address of the request i.e. key type IP. - HTTP_COOKIE: The value of the HTTP cookie whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the cookie value. If no such cookie is present in the request, the key type defaults to ALL. - HTTP_PATH: The URL path of the HTTP request. The key value is truncated to the first 128 bytes. - SNI: Server name indication in the TLS session of the HTTPS request. The key value is truncated to the first 128 bytes. The key type defaults to ALL on a HTTP session. - REGION_CODE: The country/region from which the request originates. - TLS_JA3_FINGERPRINT: JA3 TLS/SSL fingerprint if the client connects using HTTPS, HTTP/2 or HTTP/3. If not available, the key type defaults to ALL. - USER_IP: The IP address of the originating client, which is resolved based on "userIpRequestHeaders" configured with the security policy. If there is no "userIpRequestHeaders" configuration or an IP address cannot be resolved from it, the key type defaults to IP. Possible values: ["ALL", "IP", "HTTP_HEADER", "XFF_IP", "HTTP_COOKIE", "HTTP_PATH", "SNI", "REGION_CODE", "TLS_JA3_FINGERPRINT", "USER_IP"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key ComputeSecurityPolicyRuleA#enforce_on_key}
        :param enforce_on_key_configs: enforce_on_key_configs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_configs ComputeSecurityPolicyRuleA#enforce_on_key_configs}
        :param enforce_on_key_name: Rate limit key name applicable only for the following key types: HTTP_HEADER -- Name of the HTTP header whose value is taken as the key value. HTTP_COOKIE -- Name of the HTTP cookie whose value is taken as the key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_name ComputeSecurityPolicyRuleA#enforce_on_key_name}
        :param exceed_action: Action to take for requests that are above the configured rate limit threshold, to either deny with a specified HTTP response code, or redirect to a different endpoint. Valid options are deny(STATUS), where valid values for STATUS are 403, 404, 429, and 502. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#exceed_action ComputeSecurityPolicyRuleA#exceed_action}
        :param exceed_redirect_options: exceed_redirect_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#exceed_redirect_options ComputeSecurityPolicyRuleA#exceed_redirect_options}
        :param rate_limit_threshold: rate_limit_threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#rate_limit_threshold ComputeSecurityPolicyRuleA#rate_limit_threshold}
        '''
        if isinstance(ban_threshold, dict):
            ban_threshold = ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA(**ban_threshold)
        if isinstance(exceed_redirect_options, dict):
            exceed_redirect_options = ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA(**exceed_redirect_options)
        if isinstance(rate_limit_threshold, dict):
            rate_limit_threshold = ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA(**rate_limit_threshold)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c79ab185097daf9e58182b59b3b5ca352314fb25cf6100f6cc5e721e8b36aeec)
            check_type(argname="argument ban_duration_sec", value=ban_duration_sec, expected_type=type_hints["ban_duration_sec"])
            check_type(argname="argument ban_threshold", value=ban_threshold, expected_type=type_hints["ban_threshold"])
            check_type(argname="argument conform_action", value=conform_action, expected_type=type_hints["conform_action"])
            check_type(argname="argument enforce_on_key", value=enforce_on_key, expected_type=type_hints["enforce_on_key"])
            check_type(argname="argument enforce_on_key_configs", value=enforce_on_key_configs, expected_type=type_hints["enforce_on_key_configs"])
            check_type(argname="argument enforce_on_key_name", value=enforce_on_key_name, expected_type=type_hints["enforce_on_key_name"])
            check_type(argname="argument exceed_action", value=exceed_action, expected_type=type_hints["exceed_action"])
            check_type(argname="argument exceed_redirect_options", value=exceed_redirect_options, expected_type=type_hints["exceed_redirect_options"])
            check_type(argname="argument rate_limit_threshold", value=rate_limit_threshold, expected_type=type_hints["rate_limit_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ban_duration_sec is not None:
            self._values["ban_duration_sec"] = ban_duration_sec
        if ban_threshold is not None:
            self._values["ban_threshold"] = ban_threshold
        if conform_action is not None:
            self._values["conform_action"] = conform_action
        if enforce_on_key is not None:
            self._values["enforce_on_key"] = enforce_on_key
        if enforce_on_key_configs is not None:
            self._values["enforce_on_key_configs"] = enforce_on_key_configs
        if enforce_on_key_name is not None:
            self._values["enforce_on_key_name"] = enforce_on_key_name
        if exceed_action is not None:
            self._values["exceed_action"] = exceed_action
        if exceed_redirect_options is not None:
            self._values["exceed_redirect_options"] = exceed_redirect_options
        if rate_limit_threshold is not None:
            self._values["rate_limit_threshold"] = rate_limit_threshold

    @builtins.property
    def ban_duration_sec(self) -> typing.Optional[jsii.Number]:
        '''Can only be specified if the action for the rule is "rate_based_ban".

        If specified, determines the time (in seconds) the traffic will continue to be banned by the rate limit after the rate falls below the threshold.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#ban_duration_sec ComputeSecurityPolicyRuleA#ban_duration_sec}
        '''
        result = self._values.get("ban_duration_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ban_threshold(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA"]:
        '''ban_threshold block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#ban_threshold ComputeSecurityPolicyRuleA#ban_threshold}
        '''
        result = self._values.get("ban_threshold")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA"], result)

    @builtins.property
    def conform_action(self) -> typing.Optional[builtins.str]:
        '''Action to take for requests that are under the configured rate limit threshold. Valid option is "allow" only.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#conform_action ComputeSecurityPolicyRuleA#conform_action}
        '''
        result = self._values.get("conform_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enforce_on_key(self) -> typing.Optional[builtins.str]:
        '''Determines the key to enforce the rateLimitThreshold on.

        Possible values are:

        - ALL: A single rate limit threshold is applied to all the requests matching this rule. This is the default value if "enforceOnKey" is not configured.
        - IP: The source IP address of the request is the key. Each IP has this limit enforced separately.
        - HTTP_HEADER: The value of the HTTP header whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the header value. If no such header is present in the request, the key type defaults to ALL.
        - XFF_IP: The first IP address (i.e. the originating client IP address) specified in the list of IPs under X-Forwarded-For HTTP header. If no such header is present or the value is not a valid IP, the key defaults to the source IP address of the request i.e. key type IP.
        - HTTP_COOKIE: The value of the HTTP cookie whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the cookie value. If no such cookie is present in the request, the key type defaults to ALL.
        - HTTP_PATH: The URL path of the HTTP request. The key value is truncated to the first 128 bytes.
        - SNI: Server name indication in the TLS session of the HTTPS request. The key value is truncated to the first 128 bytes. The key type defaults to ALL on a HTTP session.
        - REGION_CODE: The country/region from which the request originates.
        - TLS_JA3_FINGERPRINT: JA3 TLS/SSL fingerprint if the client connects using HTTPS, HTTP/2 or HTTP/3. If not available, the key type defaults to ALL.
        - USER_IP: The IP address of the originating client, which is resolved based on "userIpRequestHeaders" configured with the security policy. If there is no "userIpRequestHeaders" configuration or an IP address cannot be resolved from it, the key type defaults to IP. Possible values: ["ALL", "IP", "HTTP_HEADER", "XFF_IP", "HTTP_COOKIE", "HTTP_PATH", "SNI", "REGION_CODE", "TLS_JA3_FINGERPRINT", "USER_IP"]

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key ComputeSecurityPolicyRuleA#enforce_on_key}
        '''
        result = self._values.get("enforce_on_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enforce_on_key_configs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs"]]]:
        '''enforce_on_key_configs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_configs ComputeSecurityPolicyRuleA#enforce_on_key_configs}
        '''
        result = self._values.get("enforce_on_key_configs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs"]]], result)

    @builtins.property
    def enforce_on_key_name(self) -> typing.Optional[builtins.str]:
        '''Rate limit key name applicable only for the following key types: HTTP_HEADER -- Name of the HTTP header whose value is taken as the key value.

        HTTP_COOKIE -- Name of the HTTP cookie whose value is taken as the key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_name ComputeSecurityPolicyRuleA#enforce_on_key_name}
        '''
        result = self._values.get("enforce_on_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exceed_action(self) -> typing.Optional[builtins.str]:
        '''Action to take for requests that are above the configured rate limit threshold, to either deny with a specified HTTP response code, or redirect to a different endpoint.

        Valid options are deny(STATUS), where valid values for STATUS are 403, 404, 429, and 502.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#exceed_action ComputeSecurityPolicyRuleA#exceed_action}
        '''
        result = self._values.get("exceed_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exceed_redirect_options(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA"]:
        '''exceed_redirect_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#exceed_redirect_options ComputeSecurityPolicyRuleA#exceed_redirect_options}
        '''
        result = self._values.get("exceed_redirect_options")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA"], result)

    @builtins.property
    def rate_limit_threshold(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA"]:
        '''rate_limit_threshold block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#rate_limit_threshold ComputeSecurityPolicyRuleA#rate_limit_threshold}
        '''
        result = self._values.get("rate_limit_threshold")
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleRateLimitOptionsA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleRateLimitOptionsAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__517ae0201347d559419b0411a9fa4bc30393568baababa6677bc101a8b27b6d8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putBanThreshold")
    def put_ban_threshold(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        interval_sec: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: Number of HTTP(S) requests for calculating the threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#count ComputeSecurityPolicyRuleA#count}
        :param interval_sec: Interval over which the threshold is computed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#interval_sec ComputeSecurityPolicyRuleA#interval_sec}
        '''
        value = ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA(
            count=count, interval_sec=interval_sec
        )

        return typing.cast(None, jsii.invoke(self, "putBanThreshold", [value]))

    @jsii.member(jsii_name="putEnforceOnKeyConfigs")
    def put_enforce_on_key_configs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a60ef09f264e420642506263511c03c94a81b27f34905622199600b9333b0572)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEnforceOnKeyConfigs", [value]))

    @jsii.member(jsii_name="putExceedRedirectOptions")
    def put_exceed_redirect_options(
        self,
        *,
        target: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target: Target for the redirect action. This is required if the type is EXTERNAL_302 and cannot be specified for GOOGLE_RECAPTCHA. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#target ComputeSecurityPolicyRuleA#target}
        :param type: Type of the redirect action. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#type ComputeSecurityPolicyRuleA#type}
        '''
        value = ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA(
            target=target, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putExceedRedirectOptions", [value]))

    @jsii.member(jsii_name="putRateLimitThreshold")
    def put_rate_limit_threshold(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        interval_sec: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: Number of HTTP(S) requests for calculating the threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#count ComputeSecurityPolicyRuleA#count}
        :param interval_sec: Interval over which the threshold is computed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#interval_sec ComputeSecurityPolicyRuleA#interval_sec}
        '''
        value = ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA(
            count=count, interval_sec=interval_sec
        )

        return typing.cast(None, jsii.invoke(self, "putRateLimitThreshold", [value]))

    @jsii.member(jsii_name="resetBanDurationSec")
    def reset_ban_duration_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBanDurationSec", []))

    @jsii.member(jsii_name="resetBanThreshold")
    def reset_ban_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBanThreshold", []))

    @jsii.member(jsii_name="resetConformAction")
    def reset_conform_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConformAction", []))

    @jsii.member(jsii_name="resetEnforceOnKey")
    def reset_enforce_on_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceOnKey", []))

    @jsii.member(jsii_name="resetEnforceOnKeyConfigs")
    def reset_enforce_on_key_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceOnKeyConfigs", []))

    @jsii.member(jsii_name="resetEnforceOnKeyName")
    def reset_enforce_on_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceOnKeyName", []))

    @jsii.member(jsii_name="resetExceedAction")
    def reset_exceed_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExceedAction", []))

    @jsii.member(jsii_name="resetExceedRedirectOptions")
    def reset_exceed_redirect_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExceedRedirectOptions", []))

    @jsii.member(jsii_name="resetRateLimitThreshold")
    def reset_rate_limit_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRateLimitThreshold", []))

    @builtins.property
    @jsii.member(jsii_name="banThreshold")
    def ban_threshold(
        self,
    ) -> "ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdAOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdAOutputReference", jsii.get(self, "banThreshold"))

    @builtins.property
    @jsii.member(jsii_name="enforceOnKeyConfigs")
    def enforce_on_key_configs(
        self,
    ) -> "ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsList":
        return typing.cast("ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsList", jsii.get(self, "enforceOnKeyConfigs"))

    @builtins.property
    @jsii.member(jsii_name="exceedRedirectOptions")
    def exceed_redirect_options(
        self,
    ) -> "ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsAOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsAOutputReference", jsii.get(self, "exceedRedirectOptions"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitThreshold")
    def rate_limit_threshold(
        self,
    ) -> "ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdAOutputReference":
        return typing.cast("ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdAOutputReference", jsii.get(self, "rateLimitThreshold"))

    @builtins.property
    @jsii.member(jsii_name="banDurationSecInput")
    def ban_duration_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "banDurationSecInput"))

    @builtins.property
    @jsii.member(jsii_name="banThresholdInput")
    def ban_threshold_input(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA"], jsii.get(self, "banThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="conformActionInput")
    def conform_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "conformActionInput"))

    @builtins.property
    @jsii.member(jsii_name="enforceOnKeyConfigsInput")
    def enforce_on_key_configs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs"]]], jsii.get(self, "enforceOnKeyConfigsInput"))

    @builtins.property
    @jsii.member(jsii_name="enforceOnKeyInput")
    def enforce_on_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enforceOnKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="enforceOnKeyNameInput")
    def enforce_on_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enforceOnKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="exceedActionInput")
    def exceed_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "exceedActionInput"))

    @builtins.property
    @jsii.member(jsii_name="exceedRedirectOptionsInput")
    def exceed_redirect_options_input(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA"], jsii.get(self, "exceedRedirectOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitThresholdInput")
    def rate_limit_threshold_input(
        self,
    ) -> typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA"]:
        return typing.cast(typing.Optional["ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA"], jsii.get(self, "rateLimitThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="banDurationSec")
    def ban_duration_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "banDurationSec"))

    @ban_duration_sec.setter
    def ban_duration_sec(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ea0ea8fb31a1663b259eb973e0e174b8c5a7c42004d5341710c8a22201d8e60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "banDurationSec", value)

    @builtins.property
    @jsii.member(jsii_name="conformAction")
    def conform_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "conformAction"))

    @conform_action.setter
    def conform_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbe3e1e41a57d010983287acc5c589deab6859c491f3eac4ac76228d7863a9d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "conformAction", value)

    @builtins.property
    @jsii.member(jsii_name="enforceOnKey")
    def enforce_on_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enforceOnKey"))

    @enforce_on_key.setter
    def enforce_on_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58b3d1c7bb4db0cceced61f1fb35abc046ed389d78c49b2fa944d431f9f2b67f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforceOnKey", value)

    @builtins.property
    @jsii.member(jsii_name="enforceOnKeyName")
    def enforce_on_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enforceOnKeyName"))

    @enforce_on_key_name.setter
    def enforce_on_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46f214f36c68191382a49aa64f6ac157e0d00c8e73b9732e6d67239d742e5e07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforceOnKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="exceedAction")
    def exceed_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exceedAction"))

    @exceed_action.setter
    def exceed_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d93b183f633ce88a627fd176f913c47b44595eed0227c75bbf1c5a9ec37a23d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exceedAction", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsA]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c275f8a1d0a807eeead27b982e986ed198276b771c6d3a40a0b4f8145a542738)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA",
    jsii_struct_bases=[],
    name_mapping={"count": "count", "interval_sec": "intervalSec"},
)
class ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA:
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        interval_sec: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: Number of HTTP(S) requests for calculating the threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#count ComputeSecurityPolicyRuleA#count}
        :param interval_sec: Interval over which the threshold is computed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#interval_sec ComputeSecurityPolicyRuleA#interval_sec}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1e8f33aef11460c1cd6d3f46ca83d615ed19ed15806843a10527b0fc4683c31)
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument interval_sec", value=interval_sec, expected_type=type_hints["interval_sec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if interval_sec is not None:
            self._values["interval_sec"] = interval_sec

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''Number of HTTP(S) requests for calculating the threshold.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#count ComputeSecurityPolicyRuleA#count}
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval_sec(self) -> typing.Optional[jsii.Number]:
        '''Interval over which the threshold is computed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#interval_sec ComputeSecurityPolicyRuleA#interval_sec}
        '''
        result = self._values.get("interval_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28b7be881b50a12ec335a13ed247f11526bbf671bd5e40e1aebdb64c70220c6b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCount")
    def reset_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCount", []))

    @jsii.member(jsii_name="resetIntervalSec")
    def reset_interval_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalSec", []))

    @builtins.property
    @jsii.member(jsii_name="countInput")
    def count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalSecInput")
    def interval_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalSecInput"))

    @builtins.property
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3c0351b3d9145548c9bb6167e227c11dde4138177a3b87efe88bc0673268dac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "count", value)

    @builtins.property
    @jsii.member(jsii_name="intervalSec")
    def interval_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "intervalSec"))

    @interval_sec.setter
    def interval_sec(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90f193cc4b031313cb6f921a37efad1b3a86f9b862e5c725e6200599bfe2d65c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalSec", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab8c3b4dd0fb0b4b5a17800b68f58866f14a969306891457c854523ccd02a53d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs",
    jsii_struct_bases=[],
    name_mapping={
        "enforce_on_key_name": "enforceOnKeyName",
        "enforce_on_key_type": "enforceOnKeyType",
    },
)
class ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs:
    def __init__(
        self,
        *,
        enforce_on_key_name: typing.Optional[builtins.str] = None,
        enforce_on_key_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enforce_on_key_name: Rate limit key name applicable only for the following key types: HTTP_HEADER -- Name of the HTTP header whose value is taken as the key value. HTTP_COOKIE -- Name of the HTTP cookie whose value is taken as the key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_name ComputeSecurityPolicyRuleA#enforce_on_key_name}
        :param enforce_on_key_type: Determines the key to enforce the rateLimitThreshold on. Possible values are: - ALL: A single rate limit threshold is applied to all the requests matching this rule. This is the default value if "enforceOnKeyConfigs" is not configured. - IP: The source IP address of the request is the key. Each IP has this limit enforced separately. - HTTP_HEADER: The value of the HTTP header whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the header value. If no such header is present in the request, the key type defaults to ALL. - XFF_IP: The first IP address (i.e. the originating client IP address) specified in the list of IPs under X-Forwarded-For HTTP header. If no such header is present or the value is not a valid IP, the key defaults to the source IP address of the request i.e. key type IP. - HTTP_COOKIE: The value of the HTTP cookie whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the cookie value. If no such cookie is present in the request, the key type defaults to ALL. - HTTP_PATH: The URL path of the HTTP request. The key value is truncated to the first 128 bytes. - SNI: Server name indication in the TLS session of the HTTPS request. The key value is truncated to the first 128 bytes. The key type defaults to ALL on a HTTP session. - REGION_CODE: The country/region from which the request originates. - TLS_JA3_FINGERPRINT: JA3 TLS/SSL fingerprint if the client connects using HTTPS, HTTP/2 or HTTP/3. If not available, the key type defaults to ALL. - USER_IP: The IP address of the originating client, which is resolved based on "userIpRequestHeaders" configured with the security policy. If there is no "userIpRequestHeaders" configuration or an IP address cannot be resolved from it, the key type defaults to IP. Possible values: ["ALL", "IP", "HTTP_HEADER", "XFF_IP", "HTTP_COOKIE", "HTTP_PATH", "SNI", "REGION_CODE", "TLS_JA3_FINGERPRINT", "USER_IP"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_type ComputeSecurityPolicyRuleA#enforce_on_key_type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02854d3ae5bd19f36ba590451fb451418cebcd6f9572505654838a43f3caa443)
            check_type(argname="argument enforce_on_key_name", value=enforce_on_key_name, expected_type=type_hints["enforce_on_key_name"])
            check_type(argname="argument enforce_on_key_type", value=enforce_on_key_type, expected_type=type_hints["enforce_on_key_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enforce_on_key_name is not None:
            self._values["enforce_on_key_name"] = enforce_on_key_name
        if enforce_on_key_type is not None:
            self._values["enforce_on_key_type"] = enforce_on_key_type

    @builtins.property
    def enforce_on_key_name(self) -> typing.Optional[builtins.str]:
        '''Rate limit key name applicable only for the following key types: HTTP_HEADER -- Name of the HTTP header whose value is taken as the key value.

        HTTP_COOKIE -- Name of the HTTP cookie whose value is taken as the key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_name ComputeSecurityPolicyRuleA#enforce_on_key_name}
        '''
        result = self._values.get("enforce_on_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enforce_on_key_type(self) -> typing.Optional[builtins.str]:
        '''Determines the key to enforce the rateLimitThreshold on.

        Possible values are:

        - ALL: A single rate limit threshold is applied to all the requests matching this rule. This is the default value if "enforceOnKeyConfigs" is not configured.
        - IP: The source IP address of the request is the key. Each IP has this limit enforced separately.
        - HTTP_HEADER: The value of the HTTP header whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the header value. If no such header is present in the request, the key type defaults to ALL.
        - XFF_IP: The first IP address (i.e. the originating client IP address) specified in the list of IPs under X-Forwarded-For HTTP header. If no such header is present or the value is not a valid IP, the key defaults to the source IP address of the request i.e. key type IP.
        - HTTP_COOKIE: The value of the HTTP cookie whose name is configured under "enforceOnKeyName". The key value is truncated to the first 128 bytes of the cookie value. If no such cookie is present in the request, the key type defaults to ALL.
        - HTTP_PATH: The URL path of the HTTP request. The key value is truncated to the first 128 bytes.
        - SNI: Server name indication in the TLS session of the HTTPS request. The key value is truncated to the first 128 bytes. The key type defaults to ALL on a HTTP session.
        - REGION_CODE: The country/region from which the request originates.
        - TLS_JA3_FINGERPRINT: JA3 TLS/SSL fingerprint if the client connects using HTTPS, HTTP/2 or HTTP/3. If not available, the key type defaults to ALL.
        - USER_IP: The IP address of the originating client, which is resolved based on "userIpRequestHeaders" configured with the security policy. If there is no "userIpRequestHeaders" configuration or an IP address cannot be resolved from it, the key type defaults to IP. Possible values: ["ALL", "IP", "HTTP_HEADER", "XFF_IP", "HTTP_COOKIE", "HTTP_PATH", "SNI", "REGION_CODE", "TLS_JA3_FINGERPRINT", "USER_IP"]

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#enforce_on_key_type ComputeSecurityPolicyRuleA#enforce_on_key_type}
        '''
        result = self._values.get("enforce_on_key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98f49042b2b1eb7c982742419fd39980c440b00a155487f8ddc0e1fa7549012f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__640790d972476073dce5e9910e56b5ac71eb4e7a39ebaa7a98769eaf15146427)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7348bdca496cd1c1a4f92169830cbccb048978578b183f6acb2f056db89f0f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73779f01821b3370c1826db0c9a7ab2d93fd95e230d4923929f1ff7d6fe71322)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87a84523455940e90a8f65d70126ecae4bc44db7bd5b39c7d93349fe974e9342)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca230e0dfd9ee0da7f1b54d002c2a4c8c152d5fa653cfe37db263a81880d70db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__746455ef404792b942c89437b19d211ed836a65754795bc69fca43af990bfc47)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEnforceOnKeyName")
    def reset_enforce_on_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceOnKeyName", []))

    @jsii.member(jsii_name="resetEnforceOnKeyType")
    def reset_enforce_on_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceOnKeyType", []))

    @builtins.property
    @jsii.member(jsii_name="enforceOnKeyNameInput")
    def enforce_on_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enforceOnKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="enforceOnKeyTypeInput")
    def enforce_on_key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enforceOnKeyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="enforceOnKeyName")
    def enforce_on_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enforceOnKeyName"))

    @enforce_on_key_name.setter
    def enforce_on_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__508dcb28a6b004617dbeb142f9d253c4bf42408609c337d417944541f0e82d12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforceOnKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="enforceOnKeyType")
    def enforce_on_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enforceOnKeyType"))

    @enforce_on_key_type.setter
    def enforce_on_key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f52e4cc500ab69c4845310f85d5c6fd9429da7b029bee0a83032021793d80dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforceOnKeyType", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de46aa5871ddd4412ee91695f01683521d78b620a69b7ae888c59dff5a61de87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA",
    jsii_struct_bases=[],
    name_mapping={"target": "target", "type": "type"},
)
class ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA:
    def __init__(
        self,
        *,
        target: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target: Target for the redirect action. This is required if the type is EXTERNAL_302 and cannot be specified for GOOGLE_RECAPTCHA. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#target ComputeSecurityPolicyRuleA#target}
        :param type: Type of the redirect action. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#type ComputeSecurityPolicyRuleA#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1690255bcbfb56dcafbb0c19ccb150c61ee20fd8755313a606a6c2f1ebfeaaca)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if target is not None:
            self._values["target"] = target
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Target for the redirect action. This is required if the type is EXTERNAL_302 and cannot be specified for GOOGLE_RECAPTCHA.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#target ComputeSecurityPolicyRuleA#target}
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Type of the redirect action.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#type ComputeSecurityPolicyRuleA#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5403c904cb982f3903081d1481c881cea599d93600d5e510982783f68fb00883)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfba1caa7be9054d2a44a745e5880b54640f7f479eb5efe566ecd455b9e08cca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8afa41225184bf503392e5306ebf89b8d20f04377ae47aa62f4fa2defd356c01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5a67d7405370de76e8190a0249fb37b6267cbbd5009498f439340edbca99fa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA",
    jsii_struct_bases=[],
    name_mapping={"count": "count", "interval_sec": "intervalSec"},
)
class ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA:
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        interval_sec: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: Number of HTTP(S) requests for calculating the threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#count ComputeSecurityPolicyRuleA#count}
        :param interval_sec: Interval over which the threshold is computed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#interval_sec ComputeSecurityPolicyRuleA#interval_sec}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52aeb2c5edf02c0882bb6d3d7862522981a2abc162aebd87cc462699b0cf4a98)
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument interval_sec", value=interval_sec, expected_type=type_hints["interval_sec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if interval_sec is not None:
            self._values["interval_sec"] = interval_sec

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''Number of HTTP(S) requests for calculating the threshold.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#count ComputeSecurityPolicyRuleA#count}
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval_sec(self) -> typing.Optional[jsii.Number]:
        '''Interval over which the threshold is computed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#interval_sec ComputeSecurityPolicyRuleA#interval_sec}
        '''
        result = self._values.get("interval_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3610558c12f590f37a281c96014316b816ea4ecaee6f280522887c8ed991e29)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCount")
    def reset_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCount", []))

    @jsii.member(jsii_name="resetIntervalSec")
    def reset_interval_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalSec", []))

    @builtins.property
    @jsii.member(jsii_name="countInput")
    def count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalSecInput")
    def interval_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalSecInput"))

    @builtins.property
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16f8227e521b0a5f7c389cb2dbd59baf93b99cc61f8f4575c1d169d482e5beed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "count", value)

    @builtins.property
    @jsii.member(jsii_name="intervalSec")
    def interval_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "intervalSec"))

    @interval_sec.setter
    def interval_sec(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f1f84769e3fabb1050a5f222d5574eed1997d8a2cb2c2021e2d2db5e9e8e671)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalSec", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA]:
        return typing.cast(typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edb6d9685b51ca85dff9cfc54a548096c74cb988df9270a7b93df8f0c462c137)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class ComputeSecurityPolicyRuleTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#create ComputeSecurityPolicyRuleA#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#delete ComputeSecurityPolicyRuleA#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#update ComputeSecurityPolicyRuleA#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1451b3be5e8eb523da1c8fa8732c563b6d6965b83437a91328a7d4afa212590c)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#create ComputeSecurityPolicyRuleA#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#delete ComputeSecurityPolicyRuleA#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/5.38.0/docs/resources/compute_security_policy_rule#update ComputeSecurityPolicyRuleA#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeSecurityPolicyRuleTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeSecurityPolicyRuleTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeSecurityPolicyRule.ComputeSecurityPolicyRuleTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__467e9ddd2bf1ce7c180d84633a87d37313a6d142846a6ccb0f9bb0573ea0839f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82a0c250ae1627bec651aa94658b8e7f5677456ea10292ffbc23c9b53e4cc219)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf53ee5c247b3610d52ff7d8dd0c8266bb9f50e0fdca4b0f286fb787bac87c5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa0410ee830d131ed6cb7da46da729b0516e7ad812b870a1bdd93d49a76b05a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRuleTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRuleTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRuleTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71ced097535d29ae8f817736f3ee232479bb26acf36adc4f5559599ba5402655)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "ComputeSecurityPolicyRuleA",
    "ComputeSecurityPolicyRuleAConfig",
    "ComputeSecurityPolicyRuleMatchA",
    "ComputeSecurityPolicyRuleMatchAOutputReference",
    "ComputeSecurityPolicyRuleMatchConfigA",
    "ComputeSecurityPolicyRuleMatchConfigAOutputReference",
    "ComputeSecurityPolicyRuleMatchExprA",
    "ComputeSecurityPolicyRuleMatchExprAOutputReference",
    "ComputeSecurityPolicyRuleMatchExprOptionsA",
    "ComputeSecurityPolicyRuleMatchExprOptionsAOutputReference",
    "ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA",
    "ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsAOutputReference",
    "ComputeSecurityPolicyRulePreconfiguredWafConfig",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionList",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionOutputReference",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieList",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookieOutputReference",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderList",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeaderOutputReference",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamList",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParamOutputReference",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriList",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUriOutputReference",
    "ComputeSecurityPolicyRulePreconfiguredWafConfigOutputReference",
    "ComputeSecurityPolicyRuleRateLimitOptionsA",
    "ComputeSecurityPolicyRuleRateLimitOptionsAOutputReference",
    "ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA",
    "ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdAOutputReference",
    "ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs",
    "ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsList",
    "ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigsOutputReference",
    "ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA",
    "ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsAOutputReference",
    "ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA",
    "ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdAOutputReference",
    "ComputeSecurityPolicyRuleTimeouts",
    "ComputeSecurityPolicyRuleTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__691f7fcc7d22a9e12d0f0baadf49d6abcd3ba135731c4245351c0262fa8b3fde(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    action: builtins.str,
    priority: jsii.Number,
    security_policy: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    match: typing.Optional[typing.Union[ComputeSecurityPolicyRuleMatchA, typing.Dict[builtins.str, typing.Any]]] = None,
    preconfigured_waf_config: typing.Optional[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    preview: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    project: typing.Optional[builtins.str] = None,
    rate_limit_options: typing.Optional[typing.Union[ComputeSecurityPolicyRuleRateLimitOptionsA, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[ComputeSecurityPolicyRuleTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa84346c8250fe4aa3cb3a595f9ecdb997e3fad4998ab8605aeb2a892f236b36(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0494db04cb5b1f1caeb403ab3d889b55e48eea59cc56416223ae312cb5fcf73d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1184b3c648b0898eac47d0b8ffa6df9229cb50e4cedb33f6077418976f6bb1fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56b173ad9c43ba279beb002ec1b70ce9afcbb424915397ae9333f1c56cb5f566(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb1a6ca95315f3d93af6a43694e4312cb281fba62b4105a59d6949d2c1651b1b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6b83a45982f4dd220ccf728ccf32e3283d2530568395a232756338e0f720026(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2708c45644fe79b7c84f86b351ed589155d2586c6e08c2ac87c83bb009e7a665(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9357b6cb3d30ccbe9167f3e9a51317c20986025ffea9c25383185ddda1defbe1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4262c59dde9bd7ab66c95d422d2fce00e6ef6259eff20144ed8cd410969c5f6(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    action: builtins.str,
    priority: jsii.Number,
    security_policy: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    match: typing.Optional[typing.Union[ComputeSecurityPolicyRuleMatchA, typing.Dict[builtins.str, typing.Any]]] = None,
    preconfigured_waf_config: typing.Optional[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    preview: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    project: typing.Optional[builtins.str] = None,
    rate_limit_options: typing.Optional[typing.Union[ComputeSecurityPolicyRuleRateLimitOptionsA, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[ComputeSecurityPolicyRuleTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65174d8f91f150dcac58e1d728372be3b0633231ede5bdd54ea57b7f7df2165c(
    *,
    config: typing.Optional[typing.Union[ComputeSecurityPolicyRuleMatchConfigA, typing.Dict[builtins.str, typing.Any]]] = None,
    expr: typing.Optional[typing.Union[ComputeSecurityPolicyRuleMatchExprA, typing.Dict[builtins.str, typing.Any]]] = None,
    expr_options: typing.Optional[typing.Union[ComputeSecurityPolicyRuleMatchExprOptionsA, typing.Dict[builtins.str, typing.Any]]] = None,
    versioned_expr: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3cf7ec571d9282573fd4c4c528c1177fc318faeee54c39fb28eedd1b34acacc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59647a7baa9c1256980a903143cc704b556bc779dc5a6b64ccf48afe0903b676(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__840439d5051bc274b962eb072c1e27b16c24f61551a3a4c618ac5808980e27e4(
    value: typing.Optional[ComputeSecurityPolicyRuleMatchA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5b6ab2577b3c54368655c6d34d83d27c17c78d97c419cb239e85ca822397f13(
    *,
    src_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b04cc9efd64a083969f0780ec78860ce7e37eb4fa1fb1c0f601a36bc49884d0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36b67d93a953c4a841fee0257bd3fc80202e01d42b4ae546e1dc41981a4314b6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86b50d2d9301f0976b51e0501aa539e2fbe9b29772586a12f66c8fe7e0ebf4e4(
    value: typing.Optional[ComputeSecurityPolicyRuleMatchConfigA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4e1bab806a7c61d681ea6878e985e466a1c79c4e8c7af3d0664434a0ae4256(
    *,
    expression: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc9ceda20ac2988a4e62cebf98e9148fda21535ad47e8d8a0398f4809f2212bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2740bf3d2a484c57d599f7f9bbc0728459f8d871bb93ab3f48e6e4de9862b6ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40b9e433e9c35e26a16d8b5b438d8575cf8e1424bff1cb1c8f02e80bfc57a96a(
    value: typing.Optional[ComputeSecurityPolicyRuleMatchExprA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__055bf2d0d71f440aa828c41c8a4b4e22a07285e5d79ca34e7394305233e5b60d(
    *,
    recaptcha_options: typing.Union[ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca8858b9b4ebb3761b6ef83756ff82ecfe5bb019170a0ec7c422451c940d1e95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4a45ed025a064552c9bd4755e6ce04a1f882ff85380f62c326969858a43cc2d(
    value: typing.Optional[ComputeSecurityPolicyRuleMatchExprOptionsA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a7abf57ca54b23bd0ffd27b075c465845cf1994307e7a784fab7f68c2e30c8a(
    *,
    action_token_site_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    session_token_site_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__432bcd1f8ad5cce52f6af6803e9e39dc45e0447d3078d93f6ae264c77b9fe1df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a516228e6148beff957229ec7bb2533c546e034098e6b2e40bce5a8d6350ef31(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b062e24842185c2638e781f43a43d6d839772c897a5812513a70fdad9632037d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1932c30d6536ac49bb7dd8c62fbeb21b6767c86a490bda27f190faac015cf494(
    value: typing.Optional[ComputeSecurityPolicyRuleMatchExprOptionsRecaptchaOptionsA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb562d2528ffa364f09b9608349f7fab272682025bec7f690f3a56e24f924d78(
    *,
    exclusion: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40391ae7f179dc8c8655c6f1aad63d715bc493b602da818c8a3458e66d1d407b(
    *,
    target_rule_set: builtins.str,
    request_cookie: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie, typing.Dict[builtins.str, typing.Any]]]]] = None,
    request_header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader, typing.Dict[builtins.str, typing.Any]]]]] = None,
    request_query_param: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam, typing.Dict[builtins.str, typing.Any]]]]] = None,
    request_uri: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri, typing.Dict[builtins.str, typing.Any]]]]] = None,
    target_rule_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ac700cbfcb16216c732003c8012a027e5aad9619e178f123590fbb0eaf0f438(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6dfa535097047ffc24fa47b7d750816a570dda2b7b1b4170a8aca87d3032814(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c9d9c51b433afaa250a40f4861164ef24d2163685944c0a767fc2e56ae7038(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc8654751fc217c791de50e44b8faeb0d07d360e8e1f178d0f97fd2febec5f0a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7b5c1953898e19c481009e46e3a7719c3972f7a167f5b0414b8125c5fbe7164(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59c69a78645843d9f7c12f5a294a34d9eededa8cf829d270efa1f44658247812(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1718f83a7a1d17d6da0da6c3e1c9e86d25abcf62f137f302e02db86c8141d699(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88c14ab69049b111694c252ba388d4d3145c513bae1ce6c815f88a6c1740fd1e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4a861e98aff9d249bae8d0ea3b695c94ffa6126e83e50298627afe7d7fc90f9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__205fda1952a03d8a90abf17e97dc24fcd76667832e8ce4e9d2b2f14ef142f1eb(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__613da6435808f70e4879826987f764d3c2857c73035eb66761e1253273e5967e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b60eb767561d77488b3bcb67308a0fcfc91711ed4c2449025c92db058cbebffb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66c1b34badb23eaf30a2bfaf34257b552ed7bc320617cf0cdf0ce0b3cfc257bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__143df5906f4f127e92edd0ce325a19b6239abe3e59e5f1f30919065b785af787(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f8581d0132a7305f57a2761184c4afaf9083c303e169ec7a5ee824116a5fd3e(
    *,
    operator: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64632fb88e32222927132e713a68270889fc6b59cf5ee45e726b9ce38b7843d3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6eca32181723581b910d50cd854e698ab3bead16a98859cfb6bccc6cfdbc70cd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a3465c60df45faf83b74436f1b7b2c85f3e883b1a75fe5249947082b751523d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e77d64bebcbc875fdd3655a1b9301dfe0bb34881221f18d532a22396971b96b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd26a1772e6616811d315754fe258fafc8fd351abe829741036f85a78a691178(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef3cd6b85ad8b742725f7b83db3e3b0c98b615811b392a4eda90e27af61ee9cb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d06f9b82028a4cfb60a4bf3b59423c4cd42fad910b2507c6e68bdfeced4b0a6d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b09bb3a4bc03a2c49f4ed0656a6a3456f3f2b1ac9f93ded380d54942ef9a53a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41b94c8978368c0a2cd34ab78d16587e7ef2b523511e550447a61eb27b4d5826(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b09b7cdf2de337ce850900cdec51589377d6692280c6b7dedfede19c5fbc01b2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestCookie]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f577bfeeb81cba99ce321886c45146ce788c259aac52dc13f6bfd27e7f3944ed(
    *,
    operator: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07f6a13b7ba20db39bf5d9f0b16b1ac3b747f6f06274f7191f42e21367a6e761(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bc95de1036940b474f30c5e7f33b2c8a2a00ad324be5a6f8f01c94ed360060b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8db69ece1ae0d43f08b86082ed041514da204d6340b9a9ecbdcb5476195038e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80de57514d7f1918030bc22b3c23dbda6089aa64c55d1eb6efaf83d4c295e323(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48f79d3b034a543796a187b8e43ff8349a2f9f126bb976b1b6d27d1a8e7cc98c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc3c0f7e94beb6ad4b0e11ac7cfe26839e89417fbd55376b8a11451ed3271c7c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d896c717fe5677579db1b89b336efdf4a0cdba7c41b6991af3171ddc20dc2992(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94958fa9405db5a495f38b29d5141e311321c065f987842d924166b435fcb774(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fc6a3287614c8a0d042e2919b15adcacf1f10db6869f64340768d5da0297f48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10ad779a65b439118268f63cfcff5fe19f74aa9d82206c1893db9dd90f4f6bd8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestHeader]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__902683da211adef53a8b75b82cf7eda73eecffb8b7270b6d864ee1987972ca73(
    *,
    operator: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7071b66a460117ef92ec687e938fb9bd190aabb94d067c63a88ba72a5a8ec19(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2df9801c44cee2b3d653f8f741e37d4a04c9ecf18db9c83ddac240f76c133471(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5f7fa5a7b3170dd962f7581858a700064231bf010fb000e497f899dc2003273(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d91899abf35cc8a8debca80c628fedd06364dc2e9c8b5d9d57ff4525d3c8a5fb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbf3c3910672460decd917dc59896304dc4ad12e5b0ad2999fbc3bdb7a2b4702(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c74ef870f5fc34a7478458441a7e0cbf79976fe4a5cd280a4a0453d59686b8b0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a0eca5b148867fb5a3cef20f414ee52fa01649234bd2801e02c49551438059a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fc29dfcc505dd38d65027aa21bb919b4ef322c2ec195ffacd7577cc8355d972(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24b6db40080c91213cec914a56a72e7c6a2e9f444a615db688ebea08b1bc4dbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f32f9ca3978e5f26cd5c35e3818941e759f7637a0321793e712670c60306f31b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestQueryParam]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e61d7ee259265062db01f4f84e317cefc8e947048206499073f0e68038993e0(
    *,
    operator: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7ae78febfeb43d9c5eaf3e9dca168ebfd295ba97149f0683dae93df981b2b60(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a370fb5336bc7e326df26752e7deb8b71ec1c159ee444d6101a99798c3ad69c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8481a2c963472547cae7375fd47fc112eca9d574e1b7649bd41a175384b5a48b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caba8a1efbd9c2af1ddafe181a3664c3aa1036a1ba590df461372c72e6dc4d84(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0420df8557688a9f0d5c692c87dcb26bc09b564ba63441236b74de13b51ad401(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c68a2a1e4e10632ed6f77e0b5cccff74e2bc474fdb687934d97bb8aac10886ff(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd4cd4248d2871da30887d952113c9169570d62964ffe09c99c9df5f0dcd0549(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8da09d0e6eeb43cac700ab4dfd684eaf166e8d9632857019e6641b2c9e1f293f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f66e96384fcfef4a006891518f38bd49e7dd6696219d4002981e2e7ce20eaeed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f207a85cd235fdc4408f176a1c5048e9d428be8ab62f12e566be769b36ffd41b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRulePreconfiguredWafConfigExclusionRequestUri]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3e5a4947578043377decb97b3169615f64eabb0c1c4bf939c2f2bf0ed0c106(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2f050fec3d00dba590cb85e41bedad411a005db418976d62692ec8d1155cb64(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRulePreconfiguredWafConfigExclusion, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4b26c87f96de4a5861435bc0fec0ad2993d0bc034d07c6b198c986c4242595b(
    value: typing.Optional[ComputeSecurityPolicyRulePreconfiguredWafConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c79ab185097daf9e58182b59b3b5ca352314fb25cf6100f6cc5e721e8b36aeec(
    *,
    ban_duration_sec: typing.Optional[jsii.Number] = None,
    ban_threshold: typing.Optional[typing.Union[ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA, typing.Dict[builtins.str, typing.Any]]] = None,
    conform_action: typing.Optional[builtins.str] = None,
    enforce_on_key: typing.Optional[builtins.str] = None,
    enforce_on_key_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    enforce_on_key_name: typing.Optional[builtins.str] = None,
    exceed_action: typing.Optional[builtins.str] = None,
    exceed_redirect_options: typing.Optional[typing.Union[ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA, typing.Dict[builtins.str, typing.Any]]] = None,
    rate_limit_threshold: typing.Optional[typing.Union[ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__517ae0201347d559419b0411a9fa4bc30393568baababa6677bc101a8b27b6d8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a60ef09f264e420642506263511c03c94a81b27f34905622199600b9333b0572(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ea0ea8fb31a1663b259eb973e0e174b8c5a7c42004d5341710c8a22201d8e60(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbe3e1e41a57d010983287acc5c589deab6859c491f3eac4ac76228d7863a9d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58b3d1c7bb4db0cceced61f1fb35abc046ed389d78c49b2fa944d431f9f2b67f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46f214f36c68191382a49aa64f6ac157e0d00c8e73b9732e6d67239d742e5e07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d93b183f633ce88a627fd176f913c47b44595eed0227c75bbf1c5a9ec37a23d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c275f8a1d0a807eeead27b982e986ed198276b771c6d3a40a0b4f8145a542738(
    value: typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1e8f33aef11460c1cd6d3f46ca83d615ed19ed15806843a10527b0fc4683c31(
    *,
    count: typing.Optional[jsii.Number] = None,
    interval_sec: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28b7be881b50a12ec335a13ed247f11526bbf671bd5e40e1aebdb64c70220c6b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3c0351b3d9145548c9bb6167e227c11dde4138177a3b87efe88bc0673268dac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f193cc4b031313cb6f921a37efad1b3a86f9b862e5c725e6200599bfe2d65c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab8c3b4dd0fb0b4b5a17800b68f58866f14a969306891457c854523ccd02a53d(
    value: typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsBanThresholdA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02854d3ae5bd19f36ba590451fb451418cebcd6f9572505654838a43f3caa443(
    *,
    enforce_on_key_name: typing.Optional[builtins.str] = None,
    enforce_on_key_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98f49042b2b1eb7c982742419fd39980c440b00a155487f8ddc0e1fa7549012f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__640790d972476073dce5e9910e56b5ac71eb4e7a39ebaa7a98769eaf15146427(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7348bdca496cd1c1a4f92169830cbccb048978578b183f6acb2f056db89f0f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73779f01821b3370c1826db0c9a7ab2d93fd95e230d4923929f1ff7d6fe71322(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87a84523455940e90a8f65d70126ecae4bc44db7bd5b39c7d93349fe974e9342(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca230e0dfd9ee0da7f1b54d002c2a4c8c152d5fa653cfe37db263a81880d70db(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__746455ef404792b942c89437b19d211ed836a65754795bc69fca43af990bfc47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__508dcb28a6b004617dbeb142f9d253c4bf42408609c337d417944541f0e82d12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f52e4cc500ab69c4845310f85d5c6fd9429da7b029bee0a83032021793d80dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de46aa5871ddd4412ee91695f01683521d78b620a69b7ae888c59dff5a61de87(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRuleRateLimitOptionsEnforceOnKeyConfigs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1690255bcbfb56dcafbb0c19ccb150c61ee20fd8755313a606a6c2f1ebfeaaca(
    *,
    target: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5403c904cb982f3903081d1481c881cea599d93600d5e510982783f68fb00883(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfba1caa7be9054d2a44a745e5880b54640f7f479eb5efe566ecd455b9e08cca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8afa41225184bf503392e5306ebf89b8d20f04377ae47aa62f4fa2defd356c01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5a67d7405370de76e8190a0249fb37b6267cbbd5009498f439340edbca99fa8(
    value: typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsExceedRedirectOptionsA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52aeb2c5edf02c0882bb6d3d7862522981a2abc162aebd87cc462699b0cf4a98(
    *,
    count: typing.Optional[jsii.Number] = None,
    interval_sec: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3610558c12f590f37a281c96014316b816ea4ecaee6f280522887c8ed991e29(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16f8227e521b0a5f7c389cb2dbd59baf93b99cc61f8f4575c1d169d482e5beed(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f1f84769e3fabb1050a5f222d5574eed1997d8a2cb2c2021e2d2db5e9e8e671(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edb6d9685b51ca85dff9cfc54a548096c74cb988df9270a7b93df8f0c462c137(
    value: typing.Optional[ComputeSecurityPolicyRuleRateLimitOptionsRateLimitThresholdA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1451b3be5e8eb523da1c8fa8732c563b6d6965b83437a91328a7d4afa212590c(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__467e9ddd2bf1ce7c180d84633a87d37313a6d142846a6ccb0f9bb0573ea0839f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82a0c250ae1627bec651aa94658b8e7f5677456ea10292ffbc23c9b53e4cc219(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf53ee5c247b3610d52ff7d8dd0c8266bb9f50e0fdca4b0f286fb787bac87c5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa0410ee830d131ed6cb7da46da729b0516e7ad812b870a1bdd93d49a76b05a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71ced097535d29ae8f817736f3ee232479bb26acf36adc4f5559599ba5402655(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeSecurityPolicyRuleTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
