"""Spatial Holdout Cross-Validator using H3 Spatial Cell Block Stratification."""

import random
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class SpatialHoldoutSplit:
    """Disjoint spatial block split containing training and holdout test rows."""

    training_rows: tuple[dict, ...]
    test_rows: tuple[dict, ...]
    training_block_ids: tuple[str, ...]
    test_block_ids: tuple[str, ...]


class SpatialHoldoutCrossValidator:
    """Validator for creating spatial cross-validation holdouts based on H3 spatial cell blocks."""

    def __init__(self, test_ratio: float = 0.3, random_seed: int = 42) -> None:
        self.test_ratio = test_ratio
        self.random_seed = random_seed

    def split_rows(self, rows: Sequence[dict]) -> SpatialHoldoutSplit:
        """Partition analytical rows into disjoint spatial block train and test sets."""
        if not rows:
            return SpatialHoldoutSplit((), (), (), ())

        # Group rows by spatial block ID
        blocks: dict[str, list[dict]] = {}
        for r in rows:
            b_id = r.get("spatial_block_id", "default_block")
            blocks.setdefault(b_id, []).append(r)

        unique_blocks = sorted(list(blocks.keys()))
        rng = random.Random(self.random_seed)
        rng.shuffle(unique_blocks)

        n_test = max(1, int(len(unique_blocks) * self.test_ratio)) if len(unique_blocks) > 1 else 0
        test_block_ids = set(unique_blocks[:n_test]) if n_test > 0 else set()
        train_block_ids = set(unique_blocks) - test_block_ids

        train_rows: list[dict] = []
        test_rows: list[dict] = []

        for b_id, b_rows in blocks.items():
            if b_id in test_block_ids:
                test_rows.extend(b_rows)
            else:
                train_rows.extend(b_rows)

        return SpatialHoldoutSplit(
            training_rows=tuple(train_rows),
            test_rows=tuple(test_rows),
            training_block_ids=tuple(sorted(list(train_block_ids))),
            test_block_ids=tuple(sorted(list(test_block_ids))),
        )
