"""Comparative Tradeoff Explanation Generator for Sidetrack Route Options."""

from packages.ovon_core.domain.route import RouteOption, RoutePersona


class TradeoffExplanationGenerator:
    """Generates plain-language human-centric tradeoff text comparing candidate routes to Easy baseline."""

    def generate_tradeoff_description(
        self, candidate: RouteOption, easy_baseline: RouteOption | None
    ) -> str:
        """Return comparative plain-language tradeoff description for a route card."""
        if candidate.persona == RoutePersona.EASY or easy_baseline is None:
            return "Lowest physical effort and simplest navigation path along primary park trails."

        dur_diff = candidate.duration_minutes - easy_baseline.duration_minutes
        dist_diff = candidate.distance_meters - easy_baseline.distance_meters

        if candidate.persona == RoutePersona.BIRDY:
            if dur_diff > 0:
                dist_str = (
                    f"{dist_diff / 1000.0:.1f} km" if dist_diff >= 1000 else f"{int(dist_diff)}m"
                )
                return (
                    f"Adds {dur_diff} min ({dist_str}) over Easy route to cross canopy "
                    "and water edge habitats for higher bird discovery opportunity."
                )
            return "Visits mature canopy and water edge boundaries for highest bird discovery opportunity."

        if candidate.persona == RoutePersona.WEIRD:
            if dur_diff > 0:
                return (
                    f"Adds {dur_diff} min of exploration into secondary trail sectors "
                    "favoring unfamiliar habitat boundaries."
                )
            return "Explores secondary trail sectors favoring unfamiliar habitat boundaries."

        if candidate.persona == RoutePersona.SCENIC:
            return "Offers scenic viewpoint loops and open parkland vistas along alternate trail paths."

        return candidate.tradeoff_description
