"""Planner Application Service."""

from typing import Sequence

from packages.ovon_core.domain import LoopRequest, RouteOption
from packages.ovon_core.fixtures import ROUTE_BIRDY, ROUTE_EASY, ROUTE_WEIRD


class PlanLoopPreview:
    """Application Service for evaluating LoopRequest and returning available RouteOptions."""

    def execute(self, request: LoopRequest) -> Sequence[RouteOption]:
        """Return distinct route options for the request."""
        # Returns distinct Easy, Birdy, and Weird persona route options
        return (ROUTE_EASY, ROUTE_BIRDY, ROUTE_WEIRD)
