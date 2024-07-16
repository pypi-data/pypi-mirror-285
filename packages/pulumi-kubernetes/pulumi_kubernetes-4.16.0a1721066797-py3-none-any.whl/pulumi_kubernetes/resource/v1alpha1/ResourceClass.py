# coding=utf-8
# *** WARNING: this file was generated by pulumigen. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import sys
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict, TypeAlias
else:
    from typing_extensions import NotRequired, TypedDict, TypeAlias
from ... import _utilities
from . import outputs
from ... import core as _core
from ... import meta as _meta
from ._inputs import *

__all__ = ['ResourceClassInitArgs', 'ResourceClass']

@pulumi.input_type
class ResourceClassInitArgs:
    def __init__(__self__, *,
                 driver_name: pulumi.Input[str],
                 api_version: Optional[pulumi.Input[str]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 metadata: Optional[pulumi.Input['_meta.v1.ObjectMetaArgs']] = None,
                 parameters_ref: Optional[pulumi.Input['ResourceClassParametersReferenceArgs']] = None,
                 suitable_nodes: Optional[pulumi.Input['_core.v1.NodeSelectorArgs']] = None):
        """
        The set of arguments for constructing a ResourceClass resource.
        :param pulumi.Input[str] driver_name: DriverName defines the name of the dynamic resource driver that is used for allocation of a ResourceClaim that uses this class.
               
               Resource drivers have a unique name in forward domain order (acme.example.com).
        :param pulumi.Input[str] api_version: APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        :param pulumi.Input[str] kind: Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        :param pulumi.Input['_meta.v1.ObjectMetaArgs'] metadata: Standard object metadata
        :param pulumi.Input['ResourceClassParametersReferenceArgs'] parameters_ref: ParametersRef references an arbitrary separate object that may hold parameters that will be used by the driver when allocating a resource that uses this class. A dynamic resource driver can distinguish between parameters stored here and and those stored in ResourceClaimSpec.
        :param pulumi.Input['_core.v1.NodeSelectorArgs'] suitable_nodes: Only nodes matching the selector will be considered by the scheduler when trying to find a Node that fits a Pod when that Pod uses a ResourceClaim that has not been allocated yet.
               
               Setting this field is optional. If null, all nodes are candidates.
        """
        pulumi.set(__self__, "driver_name", driver_name)
        if api_version is not None:
            pulumi.set(__self__, "api_version", 'resource.k8s.io/v1alpha1')
        if kind is not None:
            pulumi.set(__self__, "kind", 'ResourceClass')
        if metadata is not None:
            pulumi.set(__self__, "metadata", metadata)
        if parameters_ref is not None:
            pulumi.set(__self__, "parameters_ref", parameters_ref)
        if suitable_nodes is not None:
            pulumi.set(__self__, "suitable_nodes", suitable_nodes)

    @property
    @pulumi.getter(name="driverName")
    def driver_name(self) -> pulumi.Input[str]:
        """
        DriverName defines the name of the dynamic resource driver that is used for allocation of a ResourceClaim that uses this class.

        Resource drivers have a unique name in forward domain order (acme.example.com).
        """
        return pulumi.get(self, "driver_name")

    @driver_name.setter
    def driver_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "driver_name", value)

    @property
    @pulumi.getter(name="apiVersion")
    def api_version(self) -> Optional[pulumi.Input[str]]:
        """
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        """
        return pulumi.get(self, "api_version")

    @api_version.setter
    def api_version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "api_version", value)

    @property
    @pulumi.getter
    def kind(self) -> Optional[pulumi.Input[str]]:
        """
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        """
        return pulumi.get(self, "kind")

    @kind.setter
    def kind(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kind", value)

    @property
    @pulumi.getter
    def metadata(self) -> Optional[pulumi.Input['_meta.v1.ObjectMetaArgs']]:
        """
        Standard object metadata
        """
        return pulumi.get(self, "metadata")

    @metadata.setter
    def metadata(self, value: Optional[pulumi.Input['_meta.v1.ObjectMetaArgs']]):
        pulumi.set(self, "metadata", value)

    @property
    @pulumi.getter(name="parametersRef")
    def parameters_ref(self) -> Optional[pulumi.Input['ResourceClassParametersReferenceArgs']]:
        """
        ParametersRef references an arbitrary separate object that may hold parameters that will be used by the driver when allocating a resource that uses this class. A dynamic resource driver can distinguish between parameters stored here and and those stored in ResourceClaimSpec.
        """
        return pulumi.get(self, "parameters_ref")

    @parameters_ref.setter
    def parameters_ref(self, value: Optional[pulumi.Input['ResourceClassParametersReferenceArgs']]):
        pulumi.set(self, "parameters_ref", value)

    @property
    @pulumi.getter(name="suitableNodes")
    def suitable_nodes(self) -> Optional[pulumi.Input['_core.v1.NodeSelectorArgs']]:
        """
        Only nodes matching the selector will be considered by the scheduler when trying to find a Node that fits a Pod when that Pod uses a ResourceClaim that has not been allocated yet.

        Setting this field is optional. If null, all nodes are candidates.
        """
        return pulumi.get(self, "suitable_nodes")

    @suitable_nodes.setter
    def suitable_nodes(self, value: Optional[pulumi.Input['_core.v1.NodeSelectorArgs']]):
        pulumi.set(self, "suitable_nodes", value)


class ResourceClass(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 api_version: Optional[pulumi.Input[str]] = None,
                 driver_name: Optional[pulumi.Input[str]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 metadata: Optional[pulumi.Input[Union['_meta.v1.ObjectMetaArgs', '_meta.v1.ObjectMetaArgsDict']]] = None,
                 parameters_ref: Optional[pulumi.Input[Union['ResourceClassParametersReferenceArgs', 'ResourceClassParametersReferenceArgsDict']]] = None,
                 suitable_nodes: Optional[pulumi.Input[Union['_core.v1.NodeSelectorArgs', '_core.v1.NodeSelectorArgsDict']]] = None,
                 __props__=None):
        """
        ResourceClass is used by administrators to influence how resources are allocated.

        This is an alpha type and requires enabling the DynamicResourceAllocation feature gate.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] api_version: APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        :param pulumi.Input[str] driver_name: DriverName defines the name of the dynamic resource driver that is used for allocation of a ResourceClaim that uses this class.
               
               Resource drivers have a unique name in forward domain order (acme.example.com).
        :param pulumi.Input[str] kind: Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        :param pulumi.Input[Union['_meta.v1.ObjectMetaArgs', '_meta.v1.ObjectMetaArgsDict']] metadata: Standard object metadata
        :param pulumi.Input[Union['ResourceClassParametersReferenceArgs', 'ResourceClassParametersReferenceArgsDict']] parameters_ref: ParametersRef references an arbitrary separate object that may hold parameters that will be used by the driver when allocating a resource that uses this class. A dynamic resource driver can distinguish between parameters stored here and and those stored in ResourceClaimSpec.
        :param pulumi.Input[Union['_core.v1.NodeSelectorArgs', '_core.v1.NodeSelectorArgsDict']] suitable_nodes: Only nodes matching the selector will be considered by the scheduler when trying to find a Node that fits a Pod when that Pod uses a ResourceClaim that has not been allocated yet.
               
               Setting this field is optional. If null, all nodes are candidates.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ResourceClassInitArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        ResourceClass is used by administrators to influence how resources are allocated.

        This is an alpha type and requires enabling the DynamicResourceAllocation feature gate.

        :param str resource_name: The name of the resource.
        :param ResourceClassInitArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ResourceClassInitArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 api_version: Optional[pulumi.Input[str]] = None,
                 driver_name: Optional[pulumi.Input[str]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 metadata: Optional[pulumi.Input[Union['_meta.v1.ObjectMetaArgs', '_meta.v1.ObjectMetaArgsDict']]] = None,
                 parameters_ref: Optional[pulumi.Input[Union['ResourceClassParametersReferenceArgs', 'ResourceClassParametersReferenceArgsDict']]] = None,
                 suitable_nodes: Optional[pulumi.Input[Union['_core.v1.NodeSelectorArgs', '_core.v1.NodeSelectorArgsDict']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ResourceClassInitArgs.__new__(ResourceClassInitArgs)

            __props__.__dict__["api_version"] = 'resource.k8s.io/v1alpha1'
            if driver_name is None and not opts.urn:
                raise TypeError("Missing required property 'driver_name'")
            __props__.__dict__["driver_name"] = driver_name
            __props__.__dict__["kind"] = 'ResourceClass'
            __props__.__dict__["metadata"] = metadata
            __props__.__dict__["parameters_ref"] = parameters_ref
            __props__.__dict__["suitable_nodes"] = suitable_nodes
        alias_opts = pulumi.ResourceOptions(aliases=[pulumi.Alias(type_="kubernetes:resource.k8s.io/v1alpha2:ResourceClass")])
        opts = pulumi.ResourceOptions.merge(opts, alias_opts)
        super(ResourceClass, __self__).__init__(
            'kubernetes:resource.k8s.io/v1alpha1:ResourceClass',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'ResourceClass':
        """
        Get an existing ResourceClass resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = ResourceClassInitArgs.__new__(ResourceClassInitArgs)

        __props__.__dict__["api_version"] = None
        __props__.__dict__["driver_name"] = None
        __props__.__dict__["kind"] = None
        __props__.__dict__["metadata"] = None
        __props__.__dict__["parameters_ref"] = None
        __props__.__dict__["suitable_nodes"] = None
        return ResourceClass(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="apiVersion")
    def api_version(self) -> pulumi.Output[str]:
        """
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        """
        return pulumi.get(self, "api_version")

    @property
    @pulumi.getter(name="driverName")
    def driver_name(self) -> pulumi.Output[str]:
        """
        DriverName defines the name of the dynamic resource driver that is used for allocation of a ResourceClaim that uses this class.

        Resource drivers have a unique name in forward domain order (acme.example.com).
        """
        return pulumi.get(self, "driver_name")

    @property
    @pulumi.getter
    def kind(self) -> pulumi.Output[str]:
        """
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter
    def metadata(self) -> pulumi.Output['_meta.v1.outputs.ObjectMeta']:
        """
        Standard object metadata
        """
        return pulumi.get(self, "metadata")

    @property
    @pulumi.getter(name="parametersRef")
    def parameters_ref(self) -> pulumi.Output['outputs.ResourceClassParametersReference']:
        """
        ParametersRef references an arbitrary separate object that may hold parameters that will be used by the driver when allocating a resource that uses this class. A dynamic resource driver can distinguish between parameters stored here and and those stored in ResourceClaimSpec.
        """
        return pulumi.get(self, "parameters_ref")

    @property
    @pulumi.getter(name="suitableNodes")
    def suitable_nodes(self) -> pulumi.Output['_core.v1.outputs.NodeSelector']:
        """
        Only nodes matching the selector will be considered by the scheduler when trying to find a Node that fits a Pod when that Pod uses a ResourceClaim that has not been allocated yet.

        Setting this field is optional. If null, all nodes are candidates.
        """
        return pulumi.get(self, "suitable_nodes")

