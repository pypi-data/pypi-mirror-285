import math
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Callable, Union, Any

import numpy as np
import pandas as pd

from player_performance_ratings.consts import PredictColumnNames


class Operator(Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUALS = ">="
    LESS_THAN_OR_EQUALS = "<="
    IN = "in"
    NOT_IN = "not in"


@dataclass
class Filter:
    column_name: str
    value: Union[Any, list[Any]]
    operator: Operator


def apply_filters(df: pd.DataFrame, filters: list[Filter]) -> pd.DataFrame:
    df = df.copy()
    for filter in filters:
        if filter.operator == Operator.EQUALS:
            df = df[df[filter.column_name] == filter.value]
        elif filter.operator == Operator.NOT_EQUALS:
            df = df[df[filter.column_name] != filter.value]
        elif filter.operator == Operator.GREATER_THAN:
            df = df[df[filter.column_name] > filter.value]
        elif filter.operator == Operator.LESS_THAN:
            df = df[df[filter.column_name] < filter.value]
        elif filter.operator == Operator.GREATER_THAN_OR_EQUALS:
            df = df[df[filter.column_name] >= filter.value]
        elif filter.operator == Operator.LESS_THAN_OR_EQUALS:
            df = df[df[filter.column_name] <= filter.value]
        elif filter.operator == Operator.IN:
            df = df[df[filter.column_name].isin(filter.value)]
        elif filter.operator == Operator.NOT_IN:
            df = df[~df[filter.column_name].isin(filter.value)]

    return df


class BaseScorer(ABC):

    def __init__(
        self,
        target: str,
        pred_column: str,
        filters: Optional[list[Filter]] = None,
        granularity: Optional[list[str]] = None,
    ):
        self.target = target
        self.pred_column = pred_column
        self.filters = filters or []
        self.granularity = granularity

    @abstractmethod
    def score(self, df: pd.DataFrame) -> float:
        pass


class SklearnScorer(BaseScorer):

    def __init__(
        self,
        pred_column: str,
        scorer_function: Callable,
        target: Optional[str] = PredictColumnNames.TARGET,
        granularity: Optional[list[str]] = None,
        filters: Optional[list[Filter]] = None,
    ):
        self.pred_column_name = pred_column
        self.scorer_function = scorer_function
        super().__init__(
            target=target,
            pred_column=pred_column,
            granularity=granularity,
            filters=filters,
        )

    def score(self, df: pd.DataFrame) -> float:
        df = df.copy()
        df = apply_filters(df, self.filters)
        if self.granularity:
            grouped = (
                df.groupby(self.granularity)[self.pred_column_name, self.target]
                .mean()
                .reset_index()
            )
        else:
            grouped = df
        if isinstance(df[self.pred_column_name].iloc[0], list):
            return self.scorer_function(
                grouped[self.target],
                np.asarray(grouped[self.pred_column_name]).tolist(),
            )
        return self.scorer_function(
            grouped[self.target], grouped[self.pred_column_name]
        )


class OrdinalLossScorer(BaseScorer):

    def __init__(
        self,
        pred_column: str,
        targets_to_measure: Optional[list[int]] = None,
        target: Optional[str] = PredictColumnNames.TARGET,
        granularity: Optional[list[str]] = None,
        filters: Optional[list[Filter]] = None,
    ):

        self.pred_column_name = pred_column
        self.targets_to_measure = targets_to_measure
        self.granularity = granularity
        super().__init__(
            target=target,
            pred_column=pred_column,
            filters=filters,
            granularity=granularity,
        )

    def score(self, df: pd.DataFrame) -> float:
        df = df.copy()
        df = apply_filters(df, self.filters)
        df.reset_index(drop=True, inplace=True)

        distinct_classes_variations = df.drop_duplicates(subset=["classes"])[
            "classes"
        ].tolist()

        sum_lrs = [0 for _ in range(len(distinct_classes_variations))]
        sum_lr = 0
        for variation_idx, distinct_class_variation in enumerate(
            distinct_classes_variations
        ):

            if not isinstance(distinct_class_variation, list):
                if math.isnan(distinct_class_variation):
                    continue

            rows_target_group = df[
                df["classes"].apply(lambda x: x == distinct_class_variation)
            ]
            probs = rows_target_group[self.pred_column_name]
            last_column_name = f"prob_under_{distinct_class_variation[0] - 0.5}"
            rows_target_group[last_column_name] = probs.apply(lambda x: x[0])

            for idx, class_ in enumerate(distinct_class_variation[1:]):

                p_c = "prob_under_" + str(class_ + 0.5)
                rows_target_group[p_c] = (
                    probs.apply(lambda x: x[idx + 1])
                    + rows_target_group[last_column_name]
                )

                count_exact = len(
                    rows_target_group[rows_target_group["__target"] == class_]
                )
                weight_class = count_exact / len(rows_target_group)

                if self.granularity:
                    grouped = (
                        rows_target_group.groupby(self.granularity + ["__target"])[p_c]
                        .mean()
                        .reset_index()
                    )
                else:
                    grouped = rows_target_group

                grouped["min"] = 0.0001
                grouped["max"] = 0.9999
                grouped[p_c] = np.minimum(grouped["max"], grouped[p_c])
                grouped[p_c] = np.maximum(grouped["min"], grouped[p_c])
                grouped["log_loss"] = 0
                grouped.loc[grouped["__target"] <= class_, "log_loss"] = np.log(
                    grouped[p_c]
                )
                grouped.loc[grouped["__target"] > class_, "log_loss"] = np.log(
                    1 - grouped[p_c]
                )
                log_loss = grouped["log_loss"].mean()
                sum_lrs[variation_idx] -= log_loss * weight_class

                last_column_name = p_c
            sum_lr += sum_lrs[variation_idx] * len(rows_target_group) / len(df)
        return sum_lr
