"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import abc
import collections.abc
import corvic_generated.platform.v1.platform_pb2
import grpc
import grpc.aio
import typing

_T = typing.TypeVar('_T')

class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta):
    ...

class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):  # type: ignore
    ...

class OrgServiceStub:
    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    GetOrg: grpc.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.GetOrgRequest,
        corvic_generated.platform.v1.platform_pb2.GetOrgResponse,
    ]
    CreateOrg: grpc.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.CreateOrgRequest,
        corvic_generated.platform.v1.platform_pb2.CreateOrgResponse,
    ]
    ListOrgs: grpc.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.ListOrgsRequest,
        corvic_generated.platform.v1.platform_pb2.ListOrgsResponse,
    ]
    GetOrgUser: grpc.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.GetOrgUserRequest,
        corvic_generated.platform.v1.platform_pb2.GetOrgUserResponse,
    ]
    AddOrgUser: grpc.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.AddOrgUserRequest,
        corvic_generated.platform.v1.platform_pb2.AddOrgUserResponse,
    ]
    ListOrgUsers: grpc.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.ListOrgUsersRequest,
        corvic_generated.platform.v1.platform_pb2.ListOrgUsersResponse,
    ]

class OrgServiceAsyncStub:
    GetOrg: grpc.aio.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.GetOrgRequest,
        corvic_generated.platform.v1.platform_pb2.GetOrgResponse,
    ]
    CreateOrg: grpc.aio.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.CreateOrgRequest,
        corvic_generated.platform.v1.platform_pb2.CreateOrgResponse,
    ]
    ListOrgs: grpc.aio.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.ListOrgsRequest,
        corvic_generated.platform.v1.platform_pb2.ListOrgsResponse,
    ]
    GetOrgUser: grpc.aio.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.GetOrgUserRequest,
        corvic_generated.platform.v1.platform_pb2.GetOrgUserResponse,
    ]
    AddOrgUser: grpc.aio.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.AddOrgUserRequest,
        corvic_generated.platform.v1.platform_pb2.AddOrgUserResponse,
    ]
    ListOrgUsers: grpc.aio.UnaryUnaryMultiCallable[
        corvic_generated.platform.v1.platform_pb2.ListOrgUsersRequest,
        corvic_generated.platform.v1.platform_pb2.ListOrgUsersResponse,
    ]

class OrgServiceServicer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def GetOrg(
        self,
        request: corvic_generated.platform.v1.platform_pb2.GetOrgRequest,
        context: _ServicerContext,
    ) -> typing.Union[corvic_generated.platform.v1.platform_pb2.GetOrgResponse, collections.abc.Awaitable[corvic_generated.platform.v1.platform_pb2.GetOrgResponse]]: ...
    @abc.abstractmethod
    def CreateOrg(
        self,
        request: corvic_generated.platform.v1.platform_pb2.CreateOrgRequest,
        context: _ServicerContext,
    ) -> typing.Union[corvic_generated.platform.v1.platform_pb2.CreateOrgResponse, collections.abc.Awaitable[corvic_generated.platform.v1.platform_pb2.CreateOrgResponse]]: ...
    @abc.abstractmethod
    def ListOrgs(
        self,
        request: corvic_generated.platform.v1.platform_pb2.ListOrgsRequest,
        context: _ServicerContext,
    ) -> typing.Union[corvic_generated.platform.v1.platform_pb2.ListOrgsResponse, collections.abc.Awaitable[corvic_generated.platform.v1.platform_pb2.ListOrgsResponse]]: ...
    @abc.abstractmethod
    def GetOrgUser(
        self,
        request: corvic_generated.platform.v1.platform_pb2.GetOrgUserRequest,
        context: _ServicerContext,
    ) -> typing.Union[corvic_generated.platform.v1.platform_pb2.GetOrgUserResponse, collections.abc.Awaitable[corvic_generated.platform.v1.platform_pb2.GetOrgUserResponse]]: ...
    @abc.abstractmethod
    def AddOrgUser(
        self,
        request: corvic_generated.platform.v1.platform_pb2.AddOrgUserRequest,
        context: _ServicerContext,
    ) -> typing.Union[corvic_generated.platform.v1.platform_pb2.AddOrgUserResponse, collections.abc.Awaitable[corvic_generated.platform.v1.platform_pb2.AddOrgUserResponse]]: ...
    @abc.abstractmethod
    def ListOrgUsers(
        self,
        request: corvic_generated.platform.v1.platform_pb2.ListOrgUsersRequest,
        context: _ServicerContext,
    ) -> typing.Union[corvic_generated.platform.v1.platform_pb2.ListOrgUsersResponse, collections.abc.Awaitable[corvic_generated.platform.v1.platform_pb2.ListOrgUsersResponse]]: ...

def add_OrgServiceServicer_to_server(servicer: OrgServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]) -> None: ...
