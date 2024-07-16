# LocalStack Resource Provider Scaffolding v2
from __future__ import annotations

import json
import random
import string
from pathlib import Path
from typing import Optional, TypedDict

import localstack.services.cloudformation.provider_utils as util
from localstack.services.cloudformation.resource_provider import (
    OperationStatus,
    ProgressEvent,
    ResourceProvider,
    ResourceRequest,
)


class IAMPolicyProperties(TypedDict):
    PolicyDocument: Optional[dict]
    PolicyName: Optional[str]
    Groups: Optional[list[str]]
    Id: Optional[str]
    Roles: Optional[list[str]]
    Users: Optional[list[str]]


REPEATED_INVOCATION = "repeated_invocation"


class IAMPolicyProvider(ResourceProvider[IAMPolicyProperties]):
    TYPE = "AWS::IAM::Policy"  # Autogenerated. Don't change
    SCHEMA = util.get_schema_path(Path(__file__))  # Autogenerated. Don't change

    def create(
        self,
        request: ResourceRequest[IAMPolicyProperties],
    ) -> ProgressEvent[IAMPolicyProperties]:
        """
        Create a new resource.

        Primary identifier fields:
          - /properties/Id

        Required properties:
          - PolicyDocument
          - PolicyName

        Read-only properties:
          - /properties/Id

        """
        model = request.desired_state
        iam_client = request.aws_client_factory.iam

        policy_doc = json.dumps(util.remove_none_values(model["PolicyDocument"]))
        policy_name = model["PolicyName"]

        if not any([model.get("Roles"), model.get("Users"), model.get("Groups")]):
            return ProgressEvent(
                status=OperationStatus.FAILED,
                resource_model={},
                error_code="InvalidRequest",
                message="At least one of [Groups,Roles,Users] must be non-empty.",
            )

        for role in model.get("Roles", []):
            iam_client.put_role_policy(
                RoleName=role, PolicyName=policy_name, PolicyDocument=policy_doc
            )
        for user in model.get("Users", []):
            iam_client.put_user_policy(
                UserName=user, PolicyName=policy_name, PolicyDocument=policy_doc
            )
        for group in model.get("Groups", []):
            iam_client.put_group_policy(
                GroupName=group, PolicyName=policy_name, PolicyDocument=policy_doc
            )

        # the physical resource ID here has a bit of a weird format
        # e.g. 'stack-fnSe-1OKWZIBB89193' where fnSe are the first 4 characters of the LogicalResourceId (or name?)
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=13))
        model["Id"] = f"stack-{model.get('PolicyName', '')[:4]}-{suffix}"
        return ProgressEvent(status=OperationStatus.SUCCESS, resource_model=model)

    def read(
        self,
        request: ResourceRequest[IAMPolicyProperties],
    ) -> ProgressEvent[IAMPolicyProperties]:
        """
        Fetch resource information
        """
        raise NotImplementedError

    def delete(
        self,
        request: ResourceRequest[IAMPolicyProperties],
    ) -> ProgressEvent[IAMPolicyProperties]:
        """
        Delete a resource
        """
        iam = request.aws_client_factory.iam

        model = request.previous_state
        policy_name = request.previous_state["PolicyName"]
        for role in model.get("Roles", []):
            iam.delete_role_policy(RoleName=role, PolicyName=policy_name)
        for user in model.get("Users", []):
            iam.delete_user_policy(UserName=user, PolicyName=policy_name)
        for group in model.get("Groups", []):
            iam.delete_group_policy(GroupName=group, PolicyName=policy_name)

        return ProgressEvent(status=OperationStatus.SUCCESS, resource_model={})

    def update(
        self,
        request: ResourceRequest[IAMPolicyProperties],
    ) -> ProgressEvent[IAMPolicyProperties]:
        """
        Update a resource
        """
        iam_client = request.aws_client_factory.iam
        model = request.desired_state
        # FIXME: this wasn't properly implemented before as well, still needs to be rewritten
        policy_doc = json.dumps(util.remove_none_values(model["PolicyDocument"]))
        policy_name = model["PolicyName"]

        for role in model.get("Roles", []):
            iam_client.put_role_policy(
                RoleName=role, PolicyName=policy_name, PolicyDocument=policy_doc
            )
        for user in model.get("Users", []):
            iam_client.put_user_policy(
                UserName=user, PolicyName=policy_name, PolicyDocument=policy_doc
            )
        for group in model.get("Groups", []):
            iam_client.put_group_policy(
                GroupName=group, PolicyName=policy_name, PolicyDocument=policy_doc
            )
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resource_model={**request.previous_state, **request.desired_state},
        )
