"""Scientific Calibration Gate enforcing Brier Score <= 0.15 and ECE <= 0.08 thresholds."""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class CalibrationMetrics:
    """Scientific calibration metric evaluation results."""

    brier_score: float
    ece: float
    sample_count: int
    is_calibrated: bool
    status: str  # "calibrated_promoted" or "provisional_heuristic"
    rejection_reasons: tuple[str, ...]


class CalibrationGate:
    """Scientific gate evaluating model predictions against empirical holdout outcomes."""

    def __init__(
        self,
        max_brier_score: float = 0.15,
        max_ece: float = 0.08,
        num_bins: int = 10,
    ) -> None:
        self.max_brier_score = max_brier_score
        self.max_ece = max_ece
        self.num_bins = num_bins

    def evaluate(
        self,
        predictions: Sequence[float],
        outcomes: Sequence[int],
    ) -> CalibrationMetrics:
        """Evaluate out-of-fold predictions against empirical test outcomes."""
        if not predictions or len(predictions) != len(outcomes):
            return CalibrationMetrics(
                brier_score=1.0,
                ece=1.0,
                sample_count=0,
                is_calibrated=False,
                status="provisional_heuristic",
                rejection_reasons=("Empty or mismatched validation samples",),
            )

        n = len(predictions)

        # 1. Compute Brier Score: (1/N) * sum((p_hat - y)^2)
        brier_sum = sum((p - y) ** 2 for p, y in zip(predictions, outcomes))
        brier_score = round(brier_sum / float(n), 4)

        # 2. Compute Expected Calibration Error (ECE) across 10 equal-width bins
        bins: list[list[tuple[float, int]]] = [[] for _ in range(self.num_bins)]
        for p, y in zip(predictions, outcomes):
            bin_idx = min(int(p * self.num_bins), self.num_bins - 1)
            bins[bin_idx].append((p, y))

        ece_sum = 0.0
        for bin_items in bins:
            if not bin_items:
                continue
            bin_size = len(bin_items)
            avg_confidence = sum(p for p, _ in bin_items) / float(bin_size)
            avg_accuracy = sum(y for _, y in bin_items) / float(bin_size)
            ece_sum += (bin_size / float(n)) * abs(avg_accuracy - avg_confidence)

        ece = round(ece_sum, 4)

        rejection_reasons: list[str] = []
        if brier_score > self.max_brier_score:
            rejection_reasons.append(
                f"Brier score {brier_score:.3f} exceeds threshold {self.max_brier_score:.3f}"
            )
        if ece > self.max_ece:
            rejection_reasons.append(
                f"Expected Calibration Error (ECE) {ece:.3f} exceeds threshold {self.max_ece:.3f}"
            )

        is_calibrated = len(rejection_reasons) == 0
        status = "calibrated_promoted" if is_calibrated else "provisional_heuristic"

        return CalibrationMetrics(
            brier_score=brier_score,
            ece=ece,
            sample_count=n,
            is_calibrated=is_calibrated,
            status=status,
            rejection_reasons=tuple(rejection_reasons),
        )
