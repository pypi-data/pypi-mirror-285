from __future__ import annotations

from chalk._validation.validation import Validation
from chalk._version import __version__
from chalk.features import (
    Cron,
    DataFrame,
    Environments,
    FeatureTime,
    Primary,
    Tags,
    after,
    before,
    description,
    embed,
    feature,
    has_many,
    has_one,
    is_primary,
    op,
    owner,
    tags,
)
from chalk.features._document import Document
from chalk.features._last import Last
from chalk.features.filter import freeze_time
from chalk.features.pseudofeatures import Distance, Now
from chalk.features.resolver import OfflineResolver, OnlineResolver, Resolver, offline, online
from chalk.features.scheduled_query import ScheduledQuery
from chalk.features.tag import BranchId, EnvironmentId
from chalk.features.underscore import _, underscore
from chalk.importer import get_resolver
from chalk.logging import chalk_logger
from chalk.state import State
from chalk.streams import Windowed, stream, windowed
from chalk.utils import AnyDataclass
from chalk.utils.duration import CronTab, Duration, ScheduleOptions

batch = offline
realtime = online
embedding = embed

__all__ = [
    "AnyDataclass",
    "BranchId",
    "Cron",
    "CronTab",
    "DataFrame",
    "Distance",
    "Document",
    "Duration",
    "EnvironmentId",
    "Environments",
    "FeatureTime",
    "Last",
    "Now",
    "OfflineResolver",
    "OnlineResolver",
    "Primary",
    "Resolver",
    "ScheduleOptions",
    "ScheduledQuery",
    "State",
    "Tags",
    "Validation",
    "Windowed",
    "_",
    "__version__",
    "after",
    "batch",
    "before",
    "chalk_logger",
    "description",
    "embed",
    "embedding",
    "feature",
    "freeze_time",
    "get_resolver",
    "has_many",
    "has_one",
    "is_primary",
    "offline",
    "online",
    "op",
    "owner",
    "realtime",
    "stream",
    "tags",
    "underscore",
    "windowed",
]
