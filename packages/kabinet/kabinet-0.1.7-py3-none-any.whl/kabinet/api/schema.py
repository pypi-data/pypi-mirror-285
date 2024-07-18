from pydantic import Field, BaseModel
from typing import Tuple, Optional, Literal, List
from kabinet.scalars import UntypedParams, NodeHash
from kabinet.funcs import aexecute, execute
from datetime import datetime
from enum import Enum
from kabinet.rath import KabinetRath
from rath.scalars import ID


class PodStatus(str, Enum):
    """The state of a dask cluster"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    UNKOWN = "UNKOWN"


class ContainerType(str, Enum):
    """The state of a dask cluster"""

    APPTAINER = "APPTAINER"
    DOCKER = "DOCKER"


class EnvironmentInput(BaseModel):
    """Which environment do you want to match against?"""

    features: Optional[Tuple["DeviceFeature", ...]]
    container_type: ContainerType = Field(alias="containerType")

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        use_enum_values = True


class DeviceFeature(BaseModel):
    """The Feature you are trying to match"""

    kind: str
    cpu_count: str = Field(alias="cpuCount")

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        use_enum_values = True


class DeploymentFragment(BaseModel):
    typename: Optional[Literal["Deployment"]] = Field(alias="__typename", exclude=True)
    id: ID
    local_id: ID = Field(alias="localId")

    class Config:
        """A config class"""

        frozen = True


class ListDeploymentFragment(BaseModel):
    typename: Optional[Literal["Deployment"]] = Field(alias="__typename", exclude=True)
    id: ID
    local_id: ID = Field(alias="localId")

    class Config:
        """A config class"""

        frozen = True


class GithubRepoFragmentFlavoursDefinitions(BaseModel):
    """Nodes are abstraction of RPC Tasks. They provide a common API to deal with creating tasks.

    See online Documentation"""

    typename: Optional[Literal["Definition"]] = Field(alias="__typename", exclude=True)
    id: ID
    hash: NodeHash
    "The hash of the Node (completely unique)"

    class Config:
        """A config class"""

        frozen = True


class GithubRepoFragmentFlavours(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Optional[Literal["Flavour"]] = Field(alias="__typename", exclude=True)
    definitions: Tuple[GithubRepoFragmentFlavoursDefinitions, ...]
    "The flavours this Definition belongs to"

    class Config:
        """A config class"""

        frozen = True


class GithubRepoFragment(BaseModel):
    typename: Optional[Literal["GithubRepo"]] = Field(alias="__typename", exclude=True)
    id: ID
    branch: str
    user: str
    repo: str
    flavours: Tuple[GithubRepoFragmentFlavours, ...]

    class Config:
        """A config class"""

        frozen = True


class ReleaseFragmentApp(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Optional[Literal["App"]] = Field(alias="__typename", exclude=True)
    identifier: str

    class Config:
        """A config class"""

        frozen = True


class ReleaseFragmentFlavours(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Optional[Literal["Flavour"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    image: str
    manifest: UntypedParams
    requirements: UntypedParams

    class Config:
        """A config class"""

        frozen = True


class ReleaseFragment(BaseModel):
    typename: Optional[Literal["Release"]] = Field(alias="__typename", exclude=True)
    id: ID
    version: str
    app: ReleaseFragmentApp
    scopes: Tuple[str, ...]
    colour: str
    "Is this release deployed"
    description: str
    "Is this release deployed"
    flavours: Tuple[ReleaseFragmentFlavours, ...]

    class Config:
        """A config class"""

        frozen = True


class ListReleaseFragmentApp(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Optional[Literal["App"]] = Field(alias="__typename", exclude=True)
    identifier: str

    class Config:
        """A config class"""

        frozen = True


class ListReleaseFragment(BaseModel):
    typename: Optional[Literal["Release"]] = Field(alias="__typename", exclude=True)
    id: ID
    version: str
    app: ListReleaseFragmentApp
    installed: bool
    "Is this release deployed"
    scopes: Tuple[str, ...]
    flavours: Tuple["ListFlavourFragment", ...]
    colour: str
    "Is this release deployed"
    description: str
    "Is this release deployed"

    class Config:
        """A config class"""

        frozen = True


class ListPodFragment(BaseModel):
    typename: Optional[Literal["Pod"]] = Field(alias="__typename", exclude=True)
    id: ID
    pod_id: str = Field(alias="podId")

    class Config:
        """A config class"""

        frozen = True


class PodFragmentDeployment(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Optional[Literal["Deployment"]] = Field(alias="__typename", exclude=True)
    flavour: "FlavourFragment"

    class Config:
        """A config class"""

        frozen = True


class PodFragment(BaseModel):
    typename: Optional[Literal["Pod"]] = Field(alias="__typename", exclude=True)
    id: ID
    pod_id: str = Field(alias="podId")
    deployment: PodFragmentDeployment

    class Config:
        """A config class"""

        frozen = True


class ListFlavourFragment(BaseModel):
    typename: Optional[Literal["Flavour"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    manifest: UntypedParams

    class Config:
        """A config class"""

        frozen = True


class FlavourFragment(BaseModel):
    typename: Optional[Literal["Flavour"]] = Field(alias="__typename", exclude=True)
    release: ReleaseFragment
    manifest: UntypedParams

    class Config:
        """A config class"""

        frozen = True


class ListDefinitionFragment(BaseModel):
    typename: Optional[Literal["Definition"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    "The cleartext name of this Node"
    hash: NodeHash
    "The hash of the Node (completely unique)"
    description: Optional[str]
    "A description for the Node"

    class Config:
        """A config class"""

        frozen = True


class DefinitionFragment(BaseModel):
    typename: Optional[Literal["Definition"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    "The cleartext name of this Node"

    class Config:
        """A config class"""

        frozen = True


class CreateDeploymentMutation(BaseModel):
    create_deployment: DeploymentFragment = Field(alias="createDeployment")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        flavour: ID
        instance_id: str = Field(alias="instanceId")
        local_id: ID = Field(alias="localId")
        last_pulled: Optional[datetime] = Field(alias="lastPulled", default=None)
        secret_params: Optional[UntypedParams] = Field(
            alias="secretParams", default=None
        )

    class Meta:
        document = "fragment Deployment on Deployment {\n  id\n  localId\n}\n\nmutation CreateDeployment($flavour: ID!, $instanceId: String!, $localId: ID!, $lastPulled: DateTime, $secretParams: UntypedParams) {\n  createDeployment(\n    input: {flavour: $flavour, lastPulled: $lastPulled, secretParams: $secretParams, instanceId: $instanceId, localId: $localId}\n  ) {\n    ...Deployment\n  }\n}"


class CreatePodMutation(BaseModel):
    create_pod: PodFragment = Field(alias="createPod")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        deployment: ID
        instance_id: str = Field(alias="instanceId")
        local_id: ID = Field(alias="localId")

    class Meta:
        document = "fragment Release on Release {\n  id\n  version\n  app {\n    identifier\n  }\n  scopes\n  colour\n  description\n  flavours {\n    id\n    name\n    image\n    manifest\n    requirements\n  }\n}\n\nfragment Flavour on Flavour {\n  release {\n    ...Release\n  }\n  manifest\n}\n\nfragment Pod on Pod {\n  id\n  podId\n  deployment {\n    flavour {\n      ...Flavour\n    }\n  }\n}\n\nmutation CreatePod($deployment: ID!, $instanceId: String!, $localId: ID!) {\n  createPod(\n    input: {deployment: $deployment, instanceId: $instanceId, localId: $localId}\n  ) {\n    ...Pod\n  }\n}"


class UpdatePodMutation(BaseModel):
    update_pod: PodFragment = Field(alias="updatePod")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        status: PodStatus
        instance_id: str = Field(alias="instanceId")
        pod: Optional[ID] = Field(default=None)
        local_id: Optional[ID] = Field(alias="localId", default=None)

    class Meta:
        document = "fragment Release on Release {\n  id\n  version\n  app {\n    identifier\n  }\n  scopes\n  colour\n  description\n  flavours {\n    id\n    name\n    image\n    manifest\n    requirements\n  }\n}\n\nfragment Flavour on Flavour {\n  release {\n    ...Release\n  }\n  manifest\n}\n\nfragment Pod on Pod {\n  id\n  podId\n  deployment {\n    flavour {\n      ...Flavour\n    }\n  }\n}\n\nmutation UpdatePod($status: PodStatus!, $instanceId: String!, $pod: ID, $localId: ID) {\n  updatePod(\n    input: {pod: $pod, localId: $localId, status: $status, instanceId: $instanceId}\n  ) {\n    ...Pod\n  }\n}"


class DumpLogsMutationDumplogsPod(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Optional[Literal["Pod"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class DumpLogsMutationDumplogs(BaseModel):
    """The logs of a pod"""

    typename: Optional[Literal["LogDump"]] = Field(alias="__typename", exclude=True)
    pod: DumpLogsMutationDumplogsPod
    logs: str

    class Config:
        """A config class"""

        frozen = True


class DumpLogsMutation(BaseModel):
    dump_logs: DumpLogsMutationDumplogs = Field(alias="dumpLogs")
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        pod: ID
        logs: str

    class Meta:
        document = "mutation DumpLogs($pod: ID!, $logs: String!) {\n  dumpLogs(input: {pod: $pod, logs: $logs}) {\n    pod {\n      id\n    }\n    logs\n  }\n}"


class CreateGithubRepoMutation(BaseModel):
    create_github_repo: GithubRepoFragment = Field(alias="createGithubRepo")
    "Create a new Github repository on a bridge server"

    class Arguments(BaseModel):
        user: str
        repo: str
        branch: str
        name: str

    class Meta:
        document = "fragment GithubRepo on GithubRepo {\n  id\n  branch\n  user\n  repo\n  flavours {\n    definitions {\n      id\n      hash\n    }\n  }\n}\n\nmutation CreateGithubRepo($user: String!, $repo: String!, $branch: String!, $name: String!) {\n  createGithubRepo(\n    input: {user: $user, repo: $repo, branch: $branch, name: $name}\n  ) {\n    ...GithubRepo\n  }\n}"


class DeclareBackendMutationDeclarebackend(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Optional[Literal["Backend"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class DeclareBackendMutation(BaseModel):
    declare_backend: DeclareBackendMutationDeclarebackend = Field(
        alias="declareBackend"
    )
    "Create a new dask cluster on a bridge server"

    class Arguments(BaseModel):
        instance_id: str = Field(alias="instanceId")
        kind: str
        name: str

    class Meta:
        document = "mutation DeclareBackend($instanceId: String!, $kind: String!, $name: String!) {\n  declareBackend(input: {kind: $kind, instanceId: $instanceId, name: $name}) {\n    id\n    name\n  }\n}"


class ListReleasesQuery(BaseModel):
    releases: Tuple[ListReleaseFragment, ...]

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ListFlavour on Flavour {\n  id\n  name\n  manifest\n}\n\nfragment ListRelease on Release {\n  id\n  version\n  app {\n    identifier\n  }\n  installed\n  scopes\n  flavours {\n    ...ListFlavour\n  }\n  colour\n  description\n}\n\nquery ListReleases {\n  releases {\n    ...ListRelease\n  }\n}"


class GetReleaseQuery(BaseModel):
    release: ReleaseFragment
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Release on Release {\n  id\n  version\n  app {\n    identifier\n  }\n  scopes\n  colour\n  description\n  flavours {\n    id\n    name\n    image\n    manifest\n    requirements\n  }\n}\n\nquery GetRelease($id: ID!) {\n  release(id: $id) {\n    ...Release\n  }\n}"


class GetDeploymentQuery(BaseModel):
    deployment: DeploymentFragment
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Deployment on Deployment {\n  id\n  localId\n}\n\nquery GetDeployment($id: ID!) {\n  deployment(id: $id) {\n    ...Deployment\n  }\n}"


class ListDeploymentsQuery(BaseModel):
    deployments: Tuple[ListDeploymentFragment, ...]

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ListDeployment on Deployment {\n  id\n  localId\n}\n\nquery ListDeployments {\n  deployments {\n    ...ListDeployment\n  }\n}"


class ListPodQuery(BaseModel):
    pods: Tuple[ListPodFragment, ...]

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ListPod on Pod {\n  id\n  podId\n}\n\nquery ListPod {\n  pods {\n    ...ListPod\n  }\n}"


class GetPodQuery(BaseModel):
    pod: PodFragment
    "Return all dask clusters"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Release on Release {\n  id\n  version\n  app {\n    identifier\n  }\n  scopes\n  colour\n  description\n  flavours {\n    id\n    name\n    image\n    manifest\n    requirements\n  }\n}\n\nfragment Flavour on Flavour {\n  release {\n    ...Release\n  }\n  manifest\n}\n\nfragment Pod on Pod {\n  id\n  podId\n  deployment {\n    flavour {\n      ...Flavour\n    }\n  }\n}\n\nquery GetPod($id: ID!) {\n  pod(id: $id) {\n    ...Pod\n  }\n}"


class ListDefinitionsQuery(BaseModel):
    definitions: Tuple[ListDefinitionFragment, ...]

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ListDefinition on Definition {\n  id\n  name\n  hash\n  description\n}\n\nquery ListDefinitions {\n  definitions {\n    ...ListDefinition\n  }\n}"


class DefinitionQuery(BaseModel):
    definition: DefinitionFragment
    "Return all dask clusters"

    class Arguments(BaseModel):
        hash: Optional[NodeHash] = Field(default=None)

    class Meta:
        document = "fragment Definition on Definition {\n  id\n  name\n}\n\nquery Definition($hash: NodeHash) {\n  definition(hash: $hash) {\n    ...Definition\n  }\n}"


class MatchFlavourQueryMatchflavour(BaseModel):
    """A user of the bridge server. Maps to an authentikate user"""

    typename: Optional[Literal["Flavour"]] = Field(alias="__typename", exclude=True)
    id: ID
    image: str

    class Config:
        """A config class"""

        frozen = True


class MatchFlavourQuery(BaseModel):
    match_flavour: MatchFlavourQueryMatchflavour = Field(alias="matchFlavour")
    "Return the currently logged in user"

    class Arguments(BaseModel):
        nodes: Optional[List[NodeHash]] = Field(default=None)
        environment: Optional[EnvironmentInput] = Field(default=None)

    class Meta:
        document = "query MatchFlavour($nodes: [NodeHash!], $environment: EnvironmentInput) {\n  matchFlavour(input: {nodes: $nodes, environment: $environment}) {\n    id\n    image\n  }\n}"


async def acreate_deployment(
    flavour: ID,
    instance_id: str,
    local_id: ID,
    last_pulled: Optional[datetime] = None,
    secret_params: Optional[UntypedParams] = None,
    rath: Optional[KabinetRath] = None,
) -> DeploymentFragment:
    """CreateDeployment


     createDeployment: A user of the bridge server. Maps to an authentikate user


    Arguments:
        flavour (ID): flavour
        instance_id (str): instanceId
        local_id (ID): localId
        last_pulled (Optional[datetime], optional): lastPulled.
        secret_params (Optional[UntypedParams], optional): secretParams.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DeploymentFragment"""
    return (
        await aexecute(
            CreateDeploymentMutation,
            {
                "flavour": flavour,
                "instanceId": instance_id,
                "localId": local_id,
                "lastPulled": last_pulled,
                "secretParams": secret_params,
            },
            rath=rath,
        )
    ).create_deployment


def create_deployment(
    flavour: ID,
    instance_id: str,
    local_id: ID,
    last_pulled: Optional[datetime] = None,
    secret_params: Optional[UntypedParams] = None,
    rath: Optional[KabinetRath] = None,
) -> DeploymentFragment:
    """CreateDeployment


     createDeployment: A user of the bridge server. Maps to an authentikate user


    Arguments:
        flavour (ID): flavour
        instance_id (str): instanceId
        local_id (ID): localId
        last_pulled (Optional[datetime], optional): lastPulled.
        secret_params (Optional[UntypedParams], optional): secretParams.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DeploymentFragment"""
    return execute(
        CreateDeploymentMutation,
        {
            "flavour": flavour,
            "instanceId": instance_id,
            "localId": local_id,
            "lastPulled": last_pulled,
            "secretParams": secret_params,
        },
        rath=rath,
    ).create_deployment


async def acreate_pod(
    deployment: ID, instance_id: str, local_id: ID, rath: Optional[KabinetRath] = None
) -> PodFragment:
    """CreatePod


     createPod: A user of the bridge server. Maps to an authentikate user


    Arguments:
        deployment (ID): deployment
        instance_id (str): instanceId
        local_id (ID): localId
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        PodFragment"""
    return (
        await aexecute(
            CreatePodMutation,
            {"deployment": deployment, "instanceId": instance_id, "localId": local_id},
            rath=rath,
        )
    ).create_pod


def create_pod(
    deployment: ID, instance_id: str, local_id: ID, rath: Optional[KabinetRath] = None
) -> PodFragment:
    """CreatePod


     createPod: A user of the bridge server. Maps to an authentikate user


    Arguments:
        deployment (ID): deployment
        instance_id (str): instanceId
        local_id (ID): localId
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        PodFragment"""
    return execute(
        CreatePodMutation,
        {"deployment": deployment, "instanceId": instance_id, "localId": local_id},
        rath=rath,
    ).create_pod


async def aupdate_pod(
    status: PodStatus,
    instance_id: str,
    pod: Optional[ID] = None,
    local_id: Optional[ID] = None,
    rath: Optional[KabinetRath] = None,
) -> PodFragment:
    """UpdatePod


     updatePod: A user of the bridge server. Maps to an authentikate user


    Arguments:
        status (PodStatus): status
        instance_id (str): instanceId
        pod (Optional[ID], optional): pod.
        local_id (Optional[ID], optional): localId.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        PodFragment"""
    return (
        await aexecute(
            UpdatePodMutation,
            {
                "status": status,
                "instanceId": instance_id,
                "pod": pod,
                "localId": local_id,
            },
            rath=rath,
        )
    ).update_pod


def update_pod(
    status: PodStatus,
    instance_id: str,
    pod: Optional[ID] = None,
    local_id: Optional[ID] = None,
    rath: Optional[KabinetRath] = None,
) -> PodFragment:
    """UpdatePod


     updatePod: A user of the bridge server. Maps to an authentikate user


    Arguments:
        status (PodStatus): status
        instance_id (str): instanceId
        pod (Optional[ID], optional): pod.
        local_id (Optional[ID], optional): localId.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        PodFragment"""
    return execute(
        UpdatePodMutation,
        {"status": status, "instanceId": instance_id, "pod": pod, "localId": local_id},
        rath=rath,
    ).update_pod


async def adump_logs(
    pod: ID, logs: str, rath: Optional[KabinetRath] = None
) -> DumpLogsMutationDumplogs:
    """DumpLogs


     dumpLogs: The logs of a pod


    Arguments:
        pod (ID): pod
        logs (str): logs
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DumpLogsMutationDumplogs"""
    return (
        await aexecute(DumpLogsMutation, {"pod": pod, "logs": logs}, rath=rath)
    ).dump_logs


def dump_logs(
    pod: ID, logs: str, rath: Optional[KabinetRath] = None
) -> DumpLogsMutationDumplogs:
    """DumpLogs


     dumpLogs: The logs of a pod


    Arguments:
        pod (ID): pod
        logs (str): logs
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DumpLogsMutationDumplogs"""
    return execute(DumpLogsMutation, {"pod": pod, "logs": logs}, rath=rath).dump_logs


async def acreate_github_repo(
    user: str, repo: str, branch: str, name: str, rath: Optional[KabinetRath] = None
) -> GithubRepoFragment:
    """CreateGithubRepo


     createGithubRepo: A user of the bridge server. Maps to an authentikate user


    Arguments:
        user (str): user
        repo (str): repo
        branch (str): branch
        name (str): name
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GithubRepoFragment"""
    return (
        await aexecute(
            CreateGithubRepoMutation,
            {"user": user, "repo": repo, "branch": branch, "name": name},
            rath=rath,
        )
    ).create_github_repo


def create_github_repo(
    user: str, repo: str, branch: str, name: str, rath: Optional[KabinetRath] = None
) -> GithubRepoFragment:
    """CreateGithubRepo


     createGithubRepo: A user of the bridge server. Maps to an authentikate user


    Arguments:
        user (str): user
        repo (str): repo
        branch (str): branch
        name (str): name
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GithubRepoFragment"""
    return execute(
        CreateGithubRepoMutation,
        {"user": user, "repo": repo, "branch": branch, "name": name},
        rath=rath,
    ).create_github_repo


async def adeclare_backend(
    instance_id: str, kind: str, name: str, rath: Optional[KabinetRath] = None
) -> DeclareBackendMutationDeclarebackend:
    """DeclareBackend


     declareBackend: A user of the bridge server. Maps to an authentikate user


    Arguments:
        instance_id (str): instanceId
        kind (str): kind
        name (str): name
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DeclareBackendMutationDeclarebackend"""
    return (
        await aexecute(
            DeclareBackendMutation,
            {"instanceId": instance_id, "kind": kind, "name": name},
            rath=rath,
        )
    ).declare_backend


def declare_backend(
    instance_id: str, kind: str, name: str, rath: Optional[KabinetRath] = None
) -> DeclareBackendMutationDeclarebackend:
    """DeclareBackend


     declareBackend: A user of the bridge server. Maps to an authentikate user


    Arguments:
        instance_id (str): instanceId
        kind (str): kind
        name (str): name
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DeclareBackendMutationDeclarebackend"""
    return execute(
        DeclareBackendMutation,
        {"instanceId": instance_id, "kind": kind, "name": name},
        rath=rath,
    ).declare_backend


async def alist_releases(
    rath: Optional[KabinetRath] = None,
) -> List[ListReleaseFragment]:
    """ListReleases


     releases: A user of the bridge server. Maps to an authentikate user


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListReleaseFragment]"""
    return (await aexecute(ListReleasesQuery, {}, rath=rath)).releases


def list_releases(rath: Optional[KabinetRath] = None) -> List[ListReleaseFragment]:
    """ListReleases


     releases: A user of the bridge server. Maps to an authentikate user


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListReleaseFragment]"""
    return execute(ListReleasesQuery, {}, rath=rath).releases


async def aget_release(id: ID, rath: Optional[KabinetRath] = None) -> ReleaseFragment:
    """GetRelease


     release: A user of the bridge server. Maps to an authentikate user


    Arguments:
        id (ID): id
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ReleaseFragment"""
    return (await aexecute(GetReleaseQuery, {"id": id}, rath=rath)).release


def get_release(id: ID, rath: Optional[KabinetRath] = None) -> ReleaseFragment:
    """GetRelease


     release: A user of the bridge server. Maps to an authentikate user


    Arguments:
        id (ID): id
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ReleaseFragment"""
    return execute(GetReleaseQuery, {"id": id}, rath=rath).release


async def aget_deployment(
    id: ID, rath: Optional[KabinetRath] = None
) -> DeploymentFragment:
    """GetDeployment


     deployment: A user of the bridge server. Maps to an authentikate user


    Arguments:
        id (ID): id
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DeploymentFragment"""
    return (await aexecute(GetDeploymentQuery, {"id": id}, rath=rath)).deployment


def get_deployment(id: ID, rath: Optional[KabinetRath] = None) -> DeploymentFragment:
    """GetDeployment


     deployment: A user of the bridge server. Maps to an authentikate user


    Arguments:
        id (ID): id
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DeploymentFragment"""
    return execute(GetDeploymentQuery, {"id": id}, rath=rath).deployment


async def alist_deployments(
    rath: Optional[KabinetRath] = None,
) -> List[ListDeploymentFragment]:
    """ListDeployments


     deployments: A user of the bridge server. Maps to an authentikate user


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListDeploymentFragment]"""
    return (await aexecute(ListDeploymentsQuery, {}, rath=rath)).deployments


def list_deployments(
    rath: Optional[KabinetRath] = None,
) -> List[ListDeploymentFragment]:
    """ListDeployments


     deployments: A user of the bridge server. Maps to an authentikate user


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListDeploymentFragment]"""
    return execute(ListDeploymentsQuery, {}, rath=rath).deployments


async def alist_pod(rath: Optional[KabinetRath] = None) -> List[ListPodFragment]:
    """ListPod


     pods: A user of the bridge server. Maps to an authentikate user


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListPodFragment]"""
    return (await aexecute(ListPodQuery, {}, rath=rath)).pods


def list_pod(rath: Optional[KabinetRath] = None) -> List[ListPodFragment]:
    """ListPod


     pods: A user of the bridge server. Maps to an authentikate user


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListPodFragment]"""
    return execute(ListPodQuery, {}, rath=rath).pods


async def aget_pod(id: ID, rath: Optional[KabinetRath] = None) -> PodFragment:
    """GetPod


     pod: A user of the bridge server. Maps to an authentikate user


    Arguments:
        id (ID): id
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        PodFragment"""
    return (await aexecute(GetPodQuery, {"id": id}, rath=rath)).pod


def get_pod(id: ID, rath: Optional[KabinetRath] = None) -> PodFragment:
    """GetPod


     pod: A user of the bridge server. Maps to an authentikate user


    Arguments:
        id (ID): id
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        PodFragment"""
    return execute(GetPodQuery, {"id": id}, rath=rath).pod


async def alist_definitions(
    rath: Optional[KabinetRath] = None,
) -> List[ListDefinitionFragment]:
    """ListDefinitions


     definitions: Nodes are abstraction of RPC Tasks. They provide a common API to deal with creating tasks.

    See online Documentation


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListDefinitionFragment]"""
    return (await aexecute(ListDefinitionsQuery, {}, rath=rath)).definitions


def list_definitions(
    rath: Optional[KabinetRath] = None,
) -> List[ListDefinitionFragment]:
    """ListDefinitions


     definitions: Nodes are abstraction of RPC Tasks. They provide a common API to deal with creating tasks.

    See online Documentation


    Arguments:
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListDefinitionFragment]"""
    return execute(ListDefinitionsQuery, {}, rath=rath).definitions


async def adefinition(
    hash: Optional[NodeHash] = None, rath: Optional[KabinetRath] = None
) -> DefinitionFragment:
    """Definition


     definition: Nodes are abstraction of RPC Tasks. They provide a common API to deal with creating tasks.

    See online Documentation


    Arguments:
        hash (Optional[NodeHash], optional): hash.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DefinitionFragment"""
    return (await aexecute(DefinitionQuery, {"hash": hash}, rath=rath)).definition


def definition(
    hash: Optional[NodeHash] = None, rath: Optional[KabinetRath] = None
) -> DefinitionFragment:
    """Definition


     definition: Nodes are abstraction of RPC Tasks. They provide a common API to deal with creating tasks.

    See online Documentation


    Arguments:
        hash (Optional[NodeHash], optional): hash.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DefinitionFragment"""
    return execute(DefinitionQuery, {"hash": hash}, rath=rath).definition


async def amatch_flavour(
    nodes: Optional[List[NodeHash]] = None,
    environment: Optional[EnvironmentInput] = None,
    rath: Optional[KabinetRath] = None,
) -> MatchFlavourQueryMatchflavour:
    """MatchFlavour


     matchFlavour: A user of the bridge server. Maps to an authentikate user


    Arguments:
        nodes (Optional[List[NodeHash]], optional): nodes.
        environment (Optional[EnvironmentInput], optional): environment.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        MatchFlavourQueryMatchflavour"""
    return (
        await aexecute(
            MatchFlavourQuery, {"nodes": nodes, "environment": environment}, rath=rath
        )
    ).match_flavour


def match_flavour(
    nodes: Optional[List[NodeHash]] = None,
    environment: Optional[EnvironmentInput] = None,
    rath: Optional[KabinetRath] = None,
) -> MatchFlavourQueryMatchflavour:
    """MatchFlavour


     matchFlavour: A user of the bridge server. Maps to an authentikate user


    Arguments:
        nodes (Optional[List[NodeHash]], optional): nodes.
        environment (Optional[EnvironmentInput], optional): environment.
        rath (kabinet.rath.KabinetRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        MatchFlavourQueryMatchflavour"""
    return execute(
        MatchFlavourQuery, {"nodes": nodes, "environment": environment}, rath=rath
    ).match_flavour


EnvironmentInput.update_forward_refs()
ListReleaseFragment.update_forward_refs()
PodFragmentDeployment.update_forward_refs()
