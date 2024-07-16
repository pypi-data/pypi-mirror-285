# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""

import grpc

from chalk._gen.chalk.server.v1 import (
    graph_pb2 as chalk_dot_server_dot_v1_dot_graph__pb2,
)


class GraphServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetFeatureSQL = channel.unary_unary(
            "/chalk.server.v1.GraphService/GetFeatureSQL",
            request_serializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetFeatureSQLRequest.SerializeToString,
            response_deserializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetFeatureSQLResponse.FromString,
        )
        self.GetFeaturesMetadata = channel.unary_unary(
            "/chalk.server.v1.GraphService/GetFeaturesMetadata",
            request_serializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetFeaturesMetadataRequest.SerializeToString,
            response_deserializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetFeaturesMetadataResponse.FromString,
        )
        self.GetGraph = channel.unary_unary(
            "/chalk.server.v1.GraphService/GetGraph",
            request_serializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetGraphRequest.SerializeToString,
            response_deserializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetGraphResponse.FromString,
        )
        self.UpdateGraph = channel.unary_unary(
            "/chalk.server.v1.GraphService/UpdateGraph",
            request_serializer=chalk_dot_server_dot_v1_dot_graph__pb2.UpdateGraphRequest.SerializeToString,
            response_deserializer=chalk_dot_server_dot_v1_dot_graph__pb2.UpdateGraphResponse.FromString,
        )


class GraphServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetFeatureSQL(self, request, context):
        """GetFeatureSQL returns the feature SQLs for a given deployment."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetFeaturesMetadata(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetGraph(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def UpdateGraph(self, request, context):
        """UpdateGraph uploads the protobuf graph for a given deployment."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_GraphServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetFeatureSQL": grpc.unary_unary_rpc_method_handler(
            servicer.GetFeatureSQL,
            request_deserializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetFeatureSQLRequest.FromString,
            response_serializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetFeatureSQLResponse.SerializeToString,
        ),
        "GetFeaturesMetadata": grpc.unary_unary_rpc_method_handler(
            servicer.GetFeaturesMetadata,
            request_deserializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetFeaturesMetadataRequest.FromString,
            response_serializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetFeaturesMetadataResponse.SerializeToString,
        ),
        "GetGraph": grpc.unary_unary_rpc_method_handler(
            servicer.GetGraph,
            request_deserializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetGraphRequest.FromString,
            response_serializer=chalk_dot_server_dot_v1_dot_graph__pb2.GetGraphResponse.SerializeToString,
        ),
        "UpdateGraph": grpc.unary_unary_rpc_method_handler(
            servicer.UpdateGraph,
            request_deserializer=chalk_dot_server_dot_v1_dot_graph__pb2.UpdateGraphRequest.FromString,
            response_serializer=chalk_dot_server_dot_v1_dot_graph__pb2.UpdateGraphResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "chalk.server.v1.GraphService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class GraphService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetFeatureSQL(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chalk.server.v1.GraphService/GetFeatureSQL",
            chalk_dot_server_dot_v1_dot_graph__pb2.GetFeatureSQLRequest.SerializeToString,
            chalk_dot_server_dot_v1_dot_graph__pb2.GetFeatureSQLResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetFeaturesMetadata(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chalk.server.v1.GraphService/GetFeaturesMetadata",
            chalk_dot_server_dot_v1_dot_graph__pb2.GetFeaturesMetadataRequest.SerializeToString,
            chalk_dot_server_dot_v1_dot_graph__pb2.GetFeaturesMetadataResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetGraph(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chalk.server.v1.GraphService/GetGraph",
            chalk_dot_server_dot_v1_dot_graph__pb2.GetGraphRequest.SerializeToString,
            chalk_dot_server_dot_v1_dot_graph__pb2.GetGraphResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def UpdateGraph(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chalk.server.v1.GraphService/UpdateGraph",
            chalk_dot_server_dot_v1_dot_graph__pb2.UpdateGraphRequest.SerializeToString,
            chalk_dot_server_dot_v1_dot_graph__pb2.UpdateGraphResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
