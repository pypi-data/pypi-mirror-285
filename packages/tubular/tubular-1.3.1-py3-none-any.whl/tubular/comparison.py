from __future__ import annotations

import pandas as pd  # noqa: TCH002

from tubular.base import BaseTwoColumnTransformer
from tubular.mixins import BaseDropOriginalMixin


class EqualityChecker(BaseDropOriginalMixin, BaseTwoColumnTransformer):
    """Transformer to check if two columns are equal.

    Parameters
    ----------
    columns: list
        List containing names of the two columns to check.

    new_col_name: string
        string containing the name of the new column.

    drop_original: boolean = False
        boolean representing dropping the input columns from X after checks.

    **kwargs:
        Arbitrary keyword arguments passed onto BaseTransformer.init method.

    """

    def __init__(
        self,
        columns: list,
        new_col_name: str,
        drop_original: bool = False,
        **kwargs: dict[str, bool],
    ) -> None:
        super().__init__(columns=columns, new_col_name=new_col_name, **kwargs)

        BaseDropOriginalMixin.set_drop_original_column(self, drop_original)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Create a column which is populated by the boolean
        matching between two columns iterated over rows.

        Parameters
        ----------
        X : pd.DataFrame
            Data to apply mappings to.

        Returns
        -------
        X : pd.DataFrame
            Transformed input X with additional boolean column.

        """
        X = super().transform(X)

        X[self.new_col_name] = X[self.columns[0]] == X[self.columns[1]]

        # Drop original columns if self.drop_original is True
        BaseDropOriginalMixin.drop_original_column(
            self,
            X,
            self.drop_original,
            self.columns,
        )

        return X
