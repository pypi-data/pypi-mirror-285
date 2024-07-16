# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import dispatcher_pb2 as dispatcher__pb2


class DispatcherStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/Dispatcher/Register',
                request_serializer=dispatcher__pb2.WorkerRegisterRequest.SerializeToString,
                response_deserializer=dispatcher__pb2.WorkerRegisterResponse.FromString,
                )
        self.Listen = channel.unary_stream(
                '/Dispatcher/Listen',
                request_serializer=dispatcher__pb2.WorkerListenRequest.SerializeToString,
                response_deserializer=dispatcher__pb2.AssignedAction.FromString,
                )
        self.ListenV2 = channel.unary_stream(
                '/Dispatcher/ListenV2',
                request_serializer=dispatcher__pb2.WorkerListenRequest.SerializeToString,
                response_deserializer=dispatcher__pb2.AssignedAction.FromString,
                )
        self.Heartbeat = channel.unary_unary(
                '/Dispatcher/Heartbeat',
                request_serializer=dispatcher__pb2.HeartbeatRequest.SerializeToString,
                response_deserializer=dispatcher__pb2.HeartbeatResponse.FromString,
                )
        self.SubscribeToWorkflowEvents = channel.unary_stream(
                '/Dispatcher/SubscribeToWorkflowEvents',
                request_serializer=dispatcher__pb2.SubscribeToWorkflowEventsRequest.SerializeToString,
                response_deserializer=dispatcher__pb2.WorkflowEvent.FromString,
                )
        self.SubscribeToWorkflowRuns = channel.stream_stream(
                '/Dispatcher/SubscribeToWorkflowRuns',
                request_serializer=dispatcher__pb2.SubscribeToWorkflowRunsRequest.SerializeToString,
                response_deserializer=dispatcher__pb2.WorkflowRunEvent.FromString,
                )
        self.SendStepActionEvent = channel.unary_unary(
                '/Dispatcher/SendStepActionEvent',
                request_serializer=dispatcher__pb2.StepActionEvent.SerializeToString,
                response_deserializer=dispatcher__pb2.ActionEventResponse.FromString,
                )
        self.SendGroupKeyActionEvent = channel.unary_unary(
                '/Dispatcher/SendGroupKeyActionEvent',
                request_serializer=dispatcher__pb2.GroupKeyActionEvent.SerializeToString,
                response_deserializer=dispatcher__pb2.ActionEventResponse.FromString,
                )
        self.PutOverridesData = channel.unary_unary(
                '/Dispatcher/PutOverridesData',
                request_serializer=dispatcher__pb2.OverridesData.SerializeToString,
                response_deserializer=dispatcher__pb2.OverridesDataResponse.FromString,
                )
        self.Unsubscribe = channel.unary_unary(
                '/Dispatcher/Unsubscribe',
                request_serializer=dispatcher__pb2.WorkerUnsubscribeRequest.SerializeToString,
                response_deserializer=dispatcher__pb2.WorkerUnsubscribeResponse.FromString,
                )
        self.RefreshTimeout = channel.unary_unary(
                '/Dispatcher/RefreshTimeout',
                request_serializer=dispatcher__pb2.RefreshTimeoutRequest.SerializeToString,
                response_deserializer=dispatcher__pb2.RefreshTimeoutResponse.FromString,
                )
        self.ReleaseSlot = channel.unary_unary(
                '/Dispatcher/ReleaseSlot',
                request_serializer=dispatcher__pb2.ReleaseSlotRequest.SerializeToString,
                response_deserializer=dispatcher__pb2.ReleaseSlotResponse.FromString,
                )


class DispatcherServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Listen(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListenV2(self, request, context):
        """ListenV2 is like listen, but implementation does not include heartbeats. This should only used by SDKs
        against engine version v0.18.1+
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Heartbeat(self, request, context):
        """Heartbeat is a method for workers to send heartbeats to the dispatcher
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SubscribeToWorkflowEvents(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SubscribeToWorkflowRuns(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendStepActionEvent(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendGroupKeyActionEvent(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PutOverridesData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Unsubscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RefreshTimeout(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReleaseSlot(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DispatcherServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=dispatcher__pb2.WorkerRegisterRequest.FromString,
                    response_serializer=dispatcher__pb2.WorkerRegisterResponse.SerializeToString,
            ),
            'Listen': grpc.unary_stream_rpc_method_handler(
                    servicer.Listen,
                    request_deserializer=dispatcher__pb2.WorkerListenRequest.FromString,
                    response_serializer=dispatcher__pb2.AssignedAction.SerializeToString,
            ),
            'ListenV2': grpc.unary_stream_rpc_method_handler(
                    servicer.ListenV2,
                    request_deserializer=dispatcher__pb2.WorkerListenRequest.FromString,
                    response_serializer=dispatcher__pb2.AssignedAction.SerializeToString,
            ),
            'Heartbeat': grpc.unary_unary_rpc_method_handler(
                    servicer.Heartbeat,
                    request_deserializer=dispatcher__pb2.HeartbeatRequest.FromString,
                    response_serializer=dispatcher__pb2.HeartbeatResponse.SerializeToString,
            ),
            'SubscribeToWorkflowEvents': grpc.unary_stream_rpc_method_handler(
                    servicer.SubscribeToWorkflowEvents,
                    request_deserializer=dispatcher__pb2.SubscribeToWorkflowEventsRequest.FromString,
                    response_serializer=dispatcher__pb2.WorkflowEvent.SerializeToString,
            ),
            'SubscribeToWorkflowRuns': grpc.stream_stream_rpc_method_handler(
                    servicer.SubscribeToWorkflowRuns,
                    request_deserializer=dispatcher__pb2.SubscribeToWorkflowRunsRequest.FromString,
                    response_serializer=dispatcher__pb2.WorkflowRunEvent.SerializeToString,
            ),
            'SendStepActionEvent': grpc.unary_unary_rpc_method_handler(
                    servicer.SendStepActionEvent,
                    request_deserializer=dispatcher__pb2.StepActionEvent.FromString,
                    response_serializer=dispatcher__pb2.ActionEventResponse.SerializeToString,
            ),
            'SendGroupKeyActionEvent': grpc.unary_unary_rpc_method_handler(
                    servicer.SendGroupKeyActionEvent,
                    request_deserializer=dispatcher__pb2.GroupKeyActionEvent.FromString,
                    response_serializer=dispatcher__pb2.ActionEventResponse.SerializeToString,
            ),
            'PutOverridesData': grpc.unary_unary_rpc_method_handler(
                    servicer.PutOverridesData,
                    request_deserializer=dispatcher__pb2.OverridesData.FromString,
                    response_serializer=dispatcher__pb2.OverridesDataResponse.SerializeToString,
            ),
            'Unsubscribe': grpc.unary_unary_rpc_method_handler(
                    servicer.Unsubscribe,
                    request_deserializer=dispatcher__pb2.WorkerUnsubscribeRequest.FromString,
                    response_serializer=dispatcher__pb2.WorkerUnsubscribeResponse.SerializeToString,
            ),
            'RefreshTimeout': grpc.unary_unary_rpc_method_handler(
                    servicer.RefreshTimeout,
                    request_deserializer=dispatcher__pb2.RefreshTimeoutRequest.FromString,
                    response_serializer=dispatcher__pb2.RefreshTimeoutResponse.SerializeToString,
            ),
            'ReleaseSlot': grpc.unary_unary_rpc_method_handler(
                    servicer.ReleaseSlot,
                    request_deserializer=dispatcher__pb2.ReleaseSlotRequest.FromString,
                    response_serializer=dispatcher__pb2.ReleaseSlotResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Dispatcher', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Dispatcher(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Dispatcher/Register',
            dispatcher__pb2.WorkerRegisterRequest.SerializeToString,
            dispatcher__pb2.WorkerRegisterResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Listen(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/Dispatcher/Listen',
            dispatcher__pb2.WorkerListenRequest.SerializeToString,
            dispatcher__pb2.AssignedAction.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListenV2(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/Dispatcher/ListenV2',
            dispatcher__pb2.WorkerListenRequest.SerializeToString,
            dispatcher__pb2.AssignedAction.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Heartbeat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Dispatcher/Heartbeat',
            dispatcher__pb2.HeartbeatRequest.SerializeToString,
            dispatcher__pb2.HeartbeatResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SubscribeToWorkflowEvents(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/Dispatcher/SubscribeToWorkflowEvents',
            dispatcher__pb2.SubscribeToWorkflowEventsRequest.SerializeToString,
            dispatcher__pb2.WorkflowEvent.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SubscribeToWorkflowRuns(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/Dispatcher/SubscribeToWorkflowRuns',
            dispatcher__pb2.SubscribeToWorkflowRunsRequest.SerializeToString,
            dispatcher__pb2.WorkflowRunEvent.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendStepActionEvent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Dispatcher/SendStepActionEvent',
            dispatcher__pb2.StepActionEvent.SerializeToString,
            dispatcher__pb2.ActionEventResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendGroupKeyActionEvent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Dispatcher/SendGroupKeyActionEvent',
            dispatcher__pb2.GroupKeyActionEvent.SerializeToString,
            dispatcher__pb2.ActionEventResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PutOverridesData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Dispatcher/PutOverridesData',
            dispatcher__pb2.OverridesData.SerializeToString,
            dispatcher__pb2.OverridesDataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Unsubscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Dispatcher/Unsubscribe',
            dispatcher__pb2.WorkerUnsubscribeRequest.SerializeToString,
            dispatcher__pb2.WorkerUnsubscribeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RefreshTimeout(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Dispatcher/RefreshTimeout',
            dispatcher__pb2.RefreshTimeoutRequest.SerializeToString,
            dispatcher__pb2.RefreshTimeoutResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ReleaseSlot(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Dispatcher/ReleaseSlot',
            dispatcher__pb2.ReleaseSlotRequest.SerializeToString,
            dispatcher__pb2.ReleaseSlotResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
