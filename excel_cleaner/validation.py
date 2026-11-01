"""Checks reported verbatim in exported audit metadata."""
import pandas as pd


def integrity_checks(original: pd.DataFrame, cleaned: pd.DataFrame, removed: int, allow_removal: bool) -> dict[str, bool]:
    expected = original.iloc[~original.duplicated(keep="first").to_numpy()] if removed else original
    return {
        "row_accounting": len(original) == len(cleaned) + removed,
        "column_count_preserved": len(original.columns) == len(cleaned.columns),
        "unique_headers": cleaned.columns.is_unique,
        "deletion_authorized": removed == 0 or allow_removal,
        "source_order_preserved": cleaned.index.equals(expected.index),
        "missing_values_preserved": expected.shape == cleaned.shape and (expected.isna().to_numpy() == cleaned.isna().to_numpy()).all().item(),
    }
