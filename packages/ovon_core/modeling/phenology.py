"""Diurnal Time-of-Day Vocal Phenology Kernel."""

import math


class DiurnalPhenologyKernel:
    """Calculates diurnal time-of-day vocal detectability multiplier based on solar elevation angle."""

    def calculate_vocal_detectability(
        self, sun_altitude_degrees: float, species_group: str = "songbird"
    ) -> float:
        """Calculate diurnal detectability multiplier g(alpha_sun) in [0.1, 1.0]."""
        if species_group == "nocturnal":
            # Owls / Nightjars peak at negative sun angles (below horizon)
            peak_angle = -12.0
            sigma = 18.0
        else:
            # Songbirds peak during early morning dawn chorus
            # Sigma of 18° ensures reasonable detectability even in afternoon/evening
            peak_angle = 8.0  # 8 degrees above horizon (early morning golden hour)
            sigma = 18.0

        diff = sun_altitude_degrees - peak_angle
        multiplier = math.exp(-(diff**2) / (2.0 * (sigma**2)))

        # Birds are still visually and audibly detectable outside peak vocal hours
        return max(0.45, min(1.0, multiplier))

