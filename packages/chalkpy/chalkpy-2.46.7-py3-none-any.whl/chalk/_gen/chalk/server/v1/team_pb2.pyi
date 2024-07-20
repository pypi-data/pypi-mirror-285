from chalk._gen.chalk.auth.v1 import agent_pb2 as _agent_pb2
from chalk._gen.chalk.auth.v1 import audit_pb2 as _audit_pb2
from chalk._gen.chalk.auth.v1 import displayagent_pb2 as _displayagent_pb2
from chalk._gen.chalk.auth.v1 import featurepermission_pb2 as _featurepermission_pb2
from chalk._gen.chalk.auth.v1 import permissions_pb2 as _permissions_pb2
from chalk._gen.chalk.server.v1 import environment_pb2 as _environment_pb2
from chalk._gen.chalk.utils.v1 import sensitive_pb2 as _sensitive_pb2
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class GetEnvRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetEnvResponse(_message.Message):
    __slots__ = ("environment",)
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    environment: _environment_pb2.Environment
    def __init__(
        self,
        environment: _Optional[_Union[_environment_pb2.Environment, _Mapping]] = ...,
    ) -> None: ...

class GetEnvironmentsRequest(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: str
    def __init__(self, project: _Optional[str] = ...) -> None: ...

class GetEnvironmentsResponse(_message.Message):
    __slots__ = ("environments",)
    ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    environments: _containers.RepeatedCompositeFieldContainer[
        _environment_pb2.Environment
    ]
    def __init__(
        self,
        environments: _Optional[
            _Iterable[_Union[_environment_pb2.Environment, _Mapping]]
        ] = ...,
    ) -> None: ...

class GetAgentRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAgentResponse(_message.Message):
    __slots__ = ("agent",)
    AGENT_FIELD_NUMBER: _ClassVar[int]
    agent: _agent_pb2.Agent
    def __init__(
        self, agent: _Optional[_Union[_agent_pb2.Agent, _Mapping]] = ...
    ) -> None: ...

class GetDisplayAgentRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetDisplayAgentResponse(_message.Message):
    __slots__ = ("agent",)
    AGENT_FIELD_NUMBER: _ClassVar[int]
    agent: _displayagent_pb2.DisplayAgent
    def __init__(
        self, agent: _Optional[_Union[_displayagent_pb2.DisplayAgent, _Mapping]] = ...
    ) -> None: ...

class Team(_message.Message):
    __slots__ = ("id", "name", "slug", "logo", "projects")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    LOGO_FIELD_NUMBER: _ClassVar[int]
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    slug: str
    logo: str
    projects: _containers.RepeatedCompositeFieldContainer[Project]
    def __init__(
        self,
        id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        slug: _Optional[str] = ...,
        logo: _Optional[str] = ...,
        projects: _Optional[_Iterable[_Union[Project, _Mapping]]] = ...,
    ) -> None: ...

class Project(_message.Message):
    __slots__ = ("id", "team_id", "name", "environments")
    ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    team_id: str
    name: str
    environments: _containers.RepeatedCompositeFieldContainer[
        _environment_pb2.Environment
    ]
    def __init__(
        self,
        id: _Optional[str] = ...,
        team_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        environments: _Optional[
            _Iterable[_Union[_environment_pb2.Environment, _Mapping]]
        ] = ...,
    ) -> None: ...

class CreateTeamRequest(_message.Message):
    __slots__ = ("name", "slug", "logo")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    LOGO_FIELD_NUMBER: _ClassVar[int]
    name: str
    slug: str
    logo: str
    def __init__(
        self,
        name: _Optional[str] = ...,
        slug: _Optional[str] = ...,
        logo: _Optional[str] = ...,
    ) -> None: ...

class CreateTeamResponse(_message.Message):
    __slots__ = ("team",)
    TEAM_FIELD_NUMBER: _ClassVar[int]
    team: Team
    def __init__(self, team: _Optional[_Union[Team, _Mapping]] = ...) -> None: ...

class CreateProjectRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class CreateProjectResponse(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: Project
    def __init__(self, project: _Optional[_Union[Project, _Mapping]] = ...) -> None: ...

class CreateEnvironmentRequest(_message.Message):
    __slots__ = ("project_id", "name", "is_default")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    name: str
    is_default: bool
    def __init__(
        self,
        project_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        is_default: bool = ...,
    ) -> None: ...

class CreateEnvironmentResponse(_message.Message):
    __slots__ = ("environment",)
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    environment: _environment_pb2.Environment
    def __init__(
        self,
        environment: _Optional[_Union[_environment_pb2.Environment, _Mapping]] = ...,
    ) -> None: ...

class GetTeamRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetTeamResponse(_message.Message):
    __slots__ = ("team",)
    TEAM_FIELD_NUMBER: _ClassVar[int]
    team: Team
    def __init__(self, team: _Optional[_Union[Team, _Mapping]] = ...) -> None: ...

class CreateServiceTokenRequest(_message.Message):
    __slots__ = (
        "name",
        "permissions",
        "custom_claims",
        "customer_claims",
        "feature_tag_to_permission",
    )
    class FeatureTagToPermissionEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _featurepermission_pb2.FeaturePermission
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[
                _Union[_featurepermission_pb2.FeaturePermission, str]
            ] = ...,
        ) -> None: ...

    NAME_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_CLAIMS_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_CLAIMS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_TAG_TO_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    permissions: _containers.RepeatedScalarFieldContainer[_permissions_pb2.Permission]
    custom_claims: _containers.RepeatedScalarFieldContainer[str]
    customer_claims: _containers.RepeatedCompositeFieldContainer[_agent_pb2.CustomClaim]
    feature_tag_to_permission: _containers.ScalarMap[
        str, _featurepermission_pb2.FeaturePermission
    ]
    def __init__(
        self,
        name: _Optional[str] = ...,
        permissions: _Optional[
            _Iterable[_Union[_permissions_pb2.Permission, str]]
        ] = ...,
        custom_claims: _Optional[_Iterable[str]] = ...,
        customer_claims: _Optional[
            _Iterable[_Union[_agent_pb2.CustomClaim, _Mapping]]
        ] = ...,
        feature_tag_to_permission: _Optional[
            _Mapping[str, _featurepermission_pb2.FeaturePermission]
        ] = ...,
    ) -> None: ...

class CreateServiceTokenResponse(_message.Message):
    __slots__ = ("agent", "client_secret")
    AGENT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    agent: _agent_pb2.ServiceTokenAgent
    client_secret: str
    def __init__(
        self,
        agent: _Optional[_Union[_agent_pb2.ServiceTokenAgent, _Mapping]] = ...,
        client_secret: _Optional[str] = ...,
    ) -> None: ...

class DeleteServiceTokenRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteServiceTokenResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PermissionDescription(_message.Message):
    __slots__ = ("id", "slug", "namespace", "name", "description", "group_description")
    ID_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GROUP_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: _permissions_pb2.Permission
    slug: str
    namespace: str
    name: str
    description: str
    group_description: str
    def __init__(
        self,
        id: _Optional[_Union[_permissions_pb2.Permission, str]] = ...,
        slug: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        group_description: _Optional[str] = ...,
    ) -> None: ...

class RoleDescription(_message.Message):
    __slots__ = (
        "id",
        "name",
        "description",
        "permissions",
        "feature_permissions",
        "is_default",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    permissions: _containers.RepeatedScalarFieldContainer[_permissions_pb2.Permission]
    feature_permissions: _featurepermission_pb2.FeaturePermissions
    is_default: bool
    def __init__(
        self,
        id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        permissions: _Optional[
            _Iterable[_Union[_permissions_pb2.Permission, str]]
        ] = ...,
        feature_permissions: _Optional[
            _Union[_featurepermission_pb2.FeaturePermissions, _Mapping]
        ] = ...,
        is_default: bool = ...,
    ) -> None: ...

class GetAvailablePermissionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAvailablePermissionsResponse(_message.Message):
    __slots__ = ("permissions", "roles", "available_service_token_permissions")
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_SERVICE_TOKEN_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[PermissionDescription]
    roles: _containers.RepeatedCompositeFieldContainer[RoleDescription]
    available_service_token_permissions: _containers.RepeatedScalarFieldContainer[
        _permissions_pb2.Permission
    ]
    def __init__(
        self,
        permissions: _Optional[
            _Iterable[_Union[PermissionDescription, _Mapping]]
        ] = ...,
        roles: _Optional[_Iterable[_Union[RoleDescription, _Mapping]]] = ...,
        available_service_token_permissions: _Optional[
            _Iterable[_Union[_permissions_pb2.Permission, str]]
        ] = ...,
    ) -> None: ...

class UpsertFeaturePermissionsRequest(_message.Message):
    __slots__ = ("role", "permissions")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    role: str
    permissions: _featurepermission_pb2.FeaturePermissions
    def __init__(
        self,
        role: _Optional[str] = ...,
        permissions: _Optional[
            _Union[_featurepermission_pb2.FeaturePermissions, _Mapping]
        ] = ...,
    ) -> None: ...

class UpsertFeaturePermissionsResponse(_message.Message):
    __slots__ = ("role", "permissions")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    role: str
    permissions: _featurepermission_pb2.FeaturePermissions
    def __init__(
        self,
        role: _Optional[str] = ...,
        permissions: _Optional[
            _Union[_featurepermission_pb2.FeaturePermissions, _Mapping]
        ] = ...,
    ) -> None: ...

class ListServiceTokensRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListServiceTokensResponse(_message.Message):
    __slots__ = ("agents",)
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    agents: _containers.RepeatedCompositeFieldContainer[
        _displayagent_pb2.DisplayServiceTokenAgent
    ]
    def __init__(
        self,
        agents: _Optional[
            _Iterable[_Union[_displayagent_pb2.DisplayServiceTokenAgent, _Mapping]]
        ] = ...,
    ) -> None: ...

class UpdateServiceTokenRequest(_message.Message):
    __slots__ = (
        "client_id",
        "name",
        "permissions",
        "customer_claims",
        "feature_tag_to_permission",
    )
    class FeatureTagToPermissionEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _featurepermission_pb2.FeaturePermission
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[
                _Union[_featurepermission_pb2.FeaturePermission, str]
            ] = ...,
        ) -> None: ...

    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_CLAIMS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_TAG_TO_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    name: str
    permissions: _containers.RepeatedScalarFieldContainer[_permissions_pb2.Permission]
    customer_claims: _containers.RepeatedCompositeFieldContainer[_agent_pb2.CustomClaim]
    feature_tag_to_permission: _containers.ScalarMap[
        str, _featurepermission_pb2.FeaturePermission
    ]
    def __init__(
        self,
        client_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        permissions: _Optional[
            _Iterable[_Union[_permissions_pb2.Permission, str]]
        ] = ...,
        customer_claims: _Optional[
            _Iterable[_Union[_agent_pb2.CustomClaim, _Mapping]]
        ] = ...,
        feature_tag_to_permission: _Optional[
            _Mapping[str, _featurepermission_pb2.FeaturePermission]
        ] = ...,
    ) -> None: ...

class UpdateServiceTokenResponse(_message.Message):
    __slots__ = ("agent",)
    AGENT_FIELD_NUMBER: _ClassVar[int]
    agent: _displayagent_pb2.DisplayServiceTokenAgent
    def __init__(
        self,
        agent: _Optional[
            _Union[_displayagent_pb2.DisplayServiceTokenAgent, _Mapping]
        ] = ...,
    ) -> None: ...
