from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional, Tuple

import economic_complexity as ec
import pandas as pd

if TYPE_CHECKING:
    from logiclayer_complexity.rca import RcaParameters, RcaSubnationalParameters


@dataclass
class RelatednessParameters:
    rca_params: "RcaParameters"
    cutoff: float = 1
    iterations: int = 20
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self):
        return f"{self.rca_params.measure} Relatedness"

    def _calculate(self, rca: pd.Series) -> pd.Series:
        df_rca = rca.unstack()
        df_relatd = ec.relatedness(df_rca, cutoff=self.cutoff)
        relatd = df_relatd.stack()
        assert isinstance(relatd, pd.Series), "Calculation did not yield a pandas.Series"
        return relatd.rename(self.column_name)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        sort_ascending = self.sort_ascending
        name = self.column_name
        measure = self.rca_params.measure

        df_pivot = self.rca_params.pivot(df)
        columns = df_pivot.index.name, df_pivot.columns.name

        rca = self.rca_params._calculate(df_pivot)
        relatd = self._calculate(rca)

        ds = pd.concat([rca, relatd], axis=1).reset_index()

        if sort_ascending is not None:
            ds.sort_values(by=name, ascending=sort_ascending, inplace=True)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = (
                ds[name].rank(ascending=False, method="max").astype(int)
            )

        df_index = df[
            [df_pivot.index.name, df_pivot.index.name.replace(" ID", "")]
        ].drop_duplicates()
        df_column = df[
            [df_pivot.columns.name, df_pivot.columns.name.replace(" ID", "")]
        ].drop_duplicates()

        df_index = df_index.merge(ds, how="right", on=df_pivot.index.name)
        df_column = df_column.merge(df_index, how="right", on=df_pivot.columns.name)
        df_final = df_column.merge(
            df[[df_pivot.columns.name, df_pivot.index.name, measure]],
            how="left",
            on=columns,
        )

        return df_final


@dataclass
class RelatednessSubnationalParameters:
    rca_params: "RcaSubnationalParameters"
    cutoff: float = 1
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self):
        return f"{self.rca_params.subnat_params.measure} Relatedness"

    def _calculate(self, df_subnat: pd.DataFrame, df_global: pd.DataFrame):
        name = self.column_name
        params = self.rca_params.subnat_params

        location_id = params.location_id
        activity_id = params.activity_id

        df, tbl_global, tbl_rca_subnat = self.rca_params._calculate_subnat(
            df_subnat, df_global
        )
        df_country = ec.rca(tbl_global)

        proximity = ec.proximity(df_country)
        output = ec.relatedness(
            tbl_rca_subnat.reindex(columns=list(proximity)).fillna(0),
            proximities=proximity,
        )
        output = pd.melt(output.reset_index(), id_vars=[location_id], value_name=name)
        output = output.merge(df, on=[location_id, activity_id], how="inner")

        return output

    def calculate(
        self,
        df_subnat: pd.DataFrame,
        df_global: pd.DataFrame,
    ) -> pd.DataFrame:
        name = self.column_name
        sort_ascending = self.sort_ascending
        params = self.rca_params.subnat_params

        location_id = params.location_id
        activity_id = params.activity_id

        ds = self._calculate(df_subnat, df_global)

        if sort_ascending is not None:
            ds.sort_values(by=name, ascending=sort_ascending, inplace=True)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = (
                ds[name].rank(ascending=False, method="max").astype(int)
            )

        df_relatedness = ds.merge(
            df_subnat[[activity_id, params.activity]].drop_duplicates(),
            on=activity_id,
            how="left",
        )
        df_relatedness = df_relatedness.merge(
            df_subnat[[location_id, params.location]].drop_duplicates(),
            on=location_id,
            how="left",
        )

        df_relatedness = df_relatedness.merge(
            df_subnat,
            on=[location_id, params.location, activity_id, params.activity],
            how="left",
        )
        df_relatedness[params.measure] = df_relatedness[params.measure].fillna(0)

        return df_relatedness


@dataclass
class RelativeRelatednessParameters:
    rca_params: "RcaParameters"
    cutoff: float = 1
    iterations: int = 20
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self):
        return f"{self.rca_params.measure} Relative Relatedness"

    def _calculate(
        self, rca: pd.Series, filters: Optional[Dict[str, Tuple[str, ...]]] = None,
    ) -> pd.Series:
        """Calculates the Relative Relatedness and returns it as a Series with (location, activity) MultiIndex."""
        df_rca = rca.unstack()

        opp = df_rca.copy()

        if self.cutoff == 0:
            opp = 1
        else:
            opp[opp >= self.cutoff] = pd.NA
            opp[opp < self.cutoff] = 1

        wcp = ec.relatedness(df_rca, cutoff=self.cutoff)
        wcp_opp = opp * wcp

        if filters is None:
            wcp_mean = wcp_opp.mean(axis=1)
            wcp_std = wcp_opp.std(axis=1)

            df_relatd = wcp_opp.transform(lambda x: (x - wcp_mean) / wcp_std)

        else:
            for key, value in filters.items():
                if key == self.rca_params.location:
                    wcp_opp = wcp_opp.loc[wcp_opp.index.isin(value)]

                    wcp_mean = wcp_opp.mean(axis=1)
                    wcp_std = wcp_opp.std(axis=1)

                    df_relatd = wcp_opp.transform(lambda x: (x - wcp_mean) / wcp_std)

                elif key == self.rca_params.activity:
                    wcp_opp = wcp_opp[list(value)]

                    wcp_mean = wcp_opp.mean(axis=0)
                    wcp_std = wcp_opp.std(axis=0)

                    df_relatd = (wcp_opp - wcp_mean) / wcp_std

        relatd = df_relatd.stack()
        assert isinstance(relatd, pd.Series), "Calculation did not yield a pandas.Series"

        return relatd.rename(self.column_name)

    def calculate(
        self, df: pd.DataFrame, filters: Optional[Dict[str, Tuple[str, ...]]] = None
    ) -> pd.DataFrame:
        sort_ascending = self.sort_ascending
        name = self.column_name
        measure = self.rca_params.measure

        df_pivot = self.rca_params.pivot(df)
        columns = df_pivot.index.name, df_pivot.columns.name

        rca = self.rca_params._calculate(df_pivot)
        relatd = self._calculate(rca, filters)

        ds = pd.merge(
            rca,
            relatd,
            on=[f"{self.rca_params.location} ID", f"{self.rca_params.activity} ID"],
        ).reset_index()

        if sort_ascending is not None:
            ds.sort_values(by=name, ascending=sort_ascending, inplace=True)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = (
                ds[name].rank(ascending=False, method="max").astype(int)
            )

        df_index = df[
            [df_pivot.index.name, df_pivot.index.name.replace(" ID", "")]
        ].drop_duplicates()
        df_column = df[
            [df_pivot.columns.name, df_pivot.columns.name.replace(" ID", "")]
        ].drop_duplicates()

        df_index = df_index.merge(ds, how="right", on=df_pivot.index.name)
        df_column = df_column.merge(df_index, how="right", on=df_pivot.columns.name)
        df_final = df_column.merge(
            df[[df_pivot.columns.name, df_pivot.index.name, measure]],
            how="left",
            on=columns,
        )

        return df_final


@dataclass
class RelativeRelatednessSubnationalParameters:
    rca_params: "RcaSubnationalParameters"
    cutoff: float = 1
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self):
        return f"{self.rca_params.subnat_params.measure} Relative Relatedness"

    def _calculate(
        self,
        df_subnat: pd.DataFrame,
        df_global: pd.DataFrame,
        filters: Optional[Dict[str, Tuple[str, ...]]] = None,
    ):
        name = self.column_name
        params = self.rca_params.subnat_params

        location_id = params.location_id
        activity_id = params.activity_id

        df, tbl_global, tbl_rca_subnat = self.rca_params._calculate_subnat(
            df_subnat, df_global
        )
        df_country = ec.rca(tbl_global)

        proximity = ec.proximity(df_country)

        opp = tbl_rca_subnat.copy()

        if self.cutoff == 0:
            opp = 1
        else:
            opp[opp >= self.cutoff] = pd.NA
            opp[opp < self.cutoff] = 1

        wcp = ec.relatedness(
            tbl_rca_subnat.reindex(columns=list(proximity)).fillna(0),
            proximities=proximity,
        )
        wcp_opp = opp * wcp

        if filters is None:
            wcp_mean = wcp_opp.mean(axis=1)
            wcp_std = wcp_opp.std(axis=1)

            output = wcp_opp.transform(lambda x: (x - wcp_mean) / wcp_std)

        else:
            for key, value in filters.items():
                if key == params.location:
                    wcp_opp = wcp_opp.loc[wcp_opp.index.isin(list(value))]

                    wcp_mean = wcp_opp.mean(axis=1)
                    wcp_std = wcp_opp.std(axis=1)

                    output = wcp_opp.transform(lambda x: (x - wcp_mean) / wcp_std)

                elif key == params.activity:
                    wcp_opp = wcp_opp[list(value)]
            
                    wcp_mean = wcp_opp.mean(axis=0)
                    wcp_std = wcp_opp.std(axis=0)

                    output = (wcp_opp - wcp_mean) / wcp_std

        output = pd.melt(output.reset_index(), id_vars=[location_id], value_name=name)
        output = output.merge(df, on=[location_id, activity_id], how="inner")

        return output

    def calculate(
        self,
        df_subnat: pd.DataFrame,
        df_global: pd.DataFrame,
        filters: Optional[Dict[str, Tuple[str, ...]]] = None,
    ) -> pd.DataFrame:
        name = self.column_name
        sort_ascending = self.sort_ascending
        params = self.rca_params.subnat_params

        location_id = params.location_id
        activity_id = params.activity_id

        ds = self._calculate(df_subnat, df_global, filters)

        if sort_ascending is not None:
            ds.sort_values(by=name, ascending=sort_ascending, inplace=True)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = (
                ds[name].rank(ascending=False, method="max").astype(int)
            )

        df_relatedness = ds.merge(
            df_subnat[[activity_id, params.activity]].drop_duplicates(),
            on=activity_id,
            how="left",
        )
        df_relatedness = df_relatedness.merge(
            df_subnat[[location_id, params.location]].drop_duplicates(),
            on=location_id,
            how="left",
        )

        df_relatedness = df_relatedness.merge(
            df_subnat,
            on=[location_id, params.location, activity_id, params.activity],
            how="left",
        )

        return df_relatedness
