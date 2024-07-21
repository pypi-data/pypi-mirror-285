from chalk._gen.chalk.auth.v1 import permissions_pb2 as _permissions_pb2
from chalk._gen.chalk.pubsub.v1 import node_status_pb2 as _node_status_pb2
from chalk._gen.chalk.pubsub.v1 import pod_status_pb2 as _pod_status_pb2
from chalk._gen.chalk.server.v1 import chart_pb2 as _chart_pb2
from chalk._gen.chalk.usage.v1 import rate_pb2 as _rate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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

class UsageChartPeriod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USAGE_CHART_PERIOD_UNSPECIFIED: _ClassVar[UsageChartPeriod]
    USAGE_CHART_PERIOD_DAILY: _ClassVar[UsageChartPeriod]
    USAGE_CHART_PERIOD_MONTHLY: _ClassVar[UsageChartPeriod]

class UsageChartGrouping(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USAGE_CHART_GROUPING_UNSPECIFIED: _ClassVar[UsageChartGrouping]
    USAGE_CHART_GROUPING_INSTANCE_TYPE: _ClassVar[UsageChartGrouping]
    USAGE_CHART_GROUPING_CLUSTER: _ClassVar[UsageChartGrouping]

USAGE_CHART_PERIOD_UNSPECIFIED: UsageChartPeriod
USAGE_CHART_PERIOD_DAILY: UsageChartPeriod
USAGE_CHART_PERIOD_MONTHLY: UsageChartPeriod
USAGE_CHART_GROUPING_UNSPECIFIED: UsageChartGrouping
USAGE_CHART_GROUPING_INSTANCE_TYPE: UsageChartGrouping
USAGE_CHART_GROUPING_CLUSTER: UsageChartGrouping

class GetNodesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNodesResponse(_message.Message):
    __slots__ = ("node_statuses", "pod_statuses")
    NODE_STATUSES_FIELD_NUMBER: _ClassVar[int]
    POD_STATUSES_FIELD_NUMBER: _ClassVar[int]
    node_statuses: _containers.RepeatedCompositeFieldContainer[
        _node_status_pb2.NodeStatusPubSub
    ]
    pod_statuses: _containers.RepeatedCompositeFieldContainer[
        _pod_status_pb2.PodStatusPubSub
    ]
    def __init__(
        self,
        node_statuses: _Optional[
            _Iterable[_Union[_node_status_pb2.NodeStatusPubSub, _Mapping]]
        ] = ...,
        pod_statuses: _Optional[
            _Iterable[_Union[_pod_status_pb2.PodStatusPubSub, _Mapping]]
        ] = ...,
    ) -> None: ...

class GetUsageChartRequest(_message.Message):
    __slots__ = ("start_ms", "end_ms", "period", "grouping")
    START_MS_FIELD_NUMBER: _ClassVar[int]
    END_MS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    GROUPING_FIELD_NUMBER: _ClassVar[int]
    start_ms: int
    end_ms: int
    period: UsageChartPeriod
    grouping: UsageChartGrouping
    def __init__(
        self,
        start_ms: _Optional[int] = ...,
        end_ms: _Optional[int] = ...,
        period: _Optional[_Union[UsageChartPeriod, str]] = ...,
        grouping: _Optional[_Union[UsageChartGrouping, str]] = ...,
    ) -> None: ...

class GetUsageChartResponse(_message.Message):
    __slots__ = ("chart",)
    CHART_FIELD_NUMBER: _ClassVar[int]
    chart: _chart_pb2.Chart
    def __init__(
        self, chart: _Optional[_Union[_chart_pb2.Chart, _Mapping]] = ...
    ) -> None: ...

class GetUtilizationRatesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetUtilizationRatesResponse(_message.Message):
    __slots__ = ("rates",)
    RATES_FIELD_NUMBER: _ClassVar[int]
    rates: _containers.RepeatedCompositeFieldContainer[_rate_pb2.MachineRate]
    def __init__(
        self, rates: _Optional[_Iterable[_Union[_rate_pb2.MachineRate, _Mapping]]] = ...
    ) -> None: ...
