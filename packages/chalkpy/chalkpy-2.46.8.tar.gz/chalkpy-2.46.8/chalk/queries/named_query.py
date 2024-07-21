from __future__ import annotations

from typing import Mapping, Sequence

import pydantic

from chalk.client import FeatureReference


class NamedQuery(pydantic.BaseModel):
    """
    Define a NamedQuery object to:

          - ensure that the query is statically valid and can be executed before `chalk apply` completes
          - document key query patterns for your use-cases
          - aggregate metrics and logs for your queries
          - help define ownership during incidents
    """

    name: str
    """
    The name of the query
    """

    version: str | None = None
    """
    The version of the query
    """

    input: Sequence[FeatureReference] | None = None
    """
    The features which will be provided by callers of this query.
    For example, `[User.id]`. Features can also be expressed as snakecased strings,
    e.g. `["user.id"]`.
    """

    output: Sequence[FeatureReference] | None = None
    """
    Outputs are the features that you'd like to compute from the inputs.
    For example, `[User.age, User.name, User.email]`.

    If an empty sequence, the output will be set to all features on the namespace
    of the query. For example, if you pass as input `{"user.id": 1234}`, then the query
    is defined on the `User` namespace, and all features on the `User` namespace
    (excluding has-one and has-many relationships) will be used as outputs.
    """

    staleness: str | None = None
    """
    Maximum staleness overrides for any output features or intermediate features.
    See https://docs.chalk.ai/docs/query-caching for more information.
    """

    tags: list[str] | None = None
    """
    The tags used to scope the resolvers.
    See https://docs.chalk.ai/docs/resolver-tags for more information.
    """

    meta: dict | None = None
    """
    Additional metadata for the query.
    """

    description: str | None = None
    """
    A description of the query. Rendered in the Chalk UI and used for search indexing.
    """

    owner: str | None = None
    """
    The owner of the query. This should be a Slack username or email address.
    This is used to notify the owner in case of incidents
    """

    planner_options: Mapping[str, str | int | bool] | None = None
    """
    Dictionary of additional options to pass to the Chalk query engine.
    Values may be provided as part of conversations with Chalk support to
    to enable or disable specific functionality.
    """
