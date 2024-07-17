from datetime import datetime, timedelta, timezone
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

import dateutil

from wallaroo.assay import AssayAnalysis, AssayAnalysisList
from wallaroo.object import Object, RequiredAttributeMissing
from wallaroo.assay_config import (
    Aggregation as V1Aggregation,
    CalculatedBaseline as V1CalculatedBaseline,
    FixedBaseline as V1FixedBaseline,
    StaticBaseline as V1StaticBaseline,
    UnivariateContinousSummarizerConfig as V1Summarizer,
    BinMode as V1BinMode,
    Metric as V1Metric,
    AssayConfig as V1AssayConfig,
)
from wallaroo.workspace import Workspace
from wallaroo.unwrap import unwrap
from wallaroo.wallaroo_ml_ops_api_client.models.aggregation import Aggregation
from wallaroo.wallaroo_ml_ops_api_client.models.bin_mode_type_0 import BinModeType0
from wallaroo.wallaroo_ml_ops_api_client.models.bin_mode_type_1 import BinModeType1
from wallaroo.wallaroo_ml_ops_api_client.models.bin_mode_type_2 import BinModeType2
from wallaroo.wallaroo_ml_ops_api_client.models.bin_mode_type_3 import BinModeType3
from wallaroo.wallaroo_ml_ops_api_client.models.bin_mode_type_4 import BinModeType4
from wallaroo.wallaroo_ml_ops_api_client.models.bins import Bins
from wallaroo.wallaroo_ml_ops_api_client.models.data_origin import DataOrigin
from wallaroo.wallaroo_ml_ops_api_client.models.data_path import DataPath
from wallaroo.wallaroo_ml_ops_api_client.models.field_tagged_summaries import (
    FieldTaggedSummaries,
)
from wallaroo.wallaroo_ml_ops_api_client.models.interval_unit import IntervalUnit
from wallaroo.wallaroo_ml_ops_api_client.models.metric import Metric
from wallaroo.wallaroo_ml_ops_api_client.models.pg_interval import PGInterval
from wallaroo.wallaroo_ml_ops_api_client.models.preview_result import (
    PreviewResult as MLOpsPreviewResult,
)
from wallaroo.wallaroo_ml_ops_api_client.models.run_frequency_type_1 import (
    RunFrequencyType1 as MLOpsSimpleRunFrequency,
)
from wallaroo.wallaroo_ml_ops_api_client.models.series_summary import SeriesSummary
from wallaroo.wallaroo_ml_ops_api_client.models.series_summary_statistics import (
    SeriesSummaryStatistics,
)
from wallaroo.wallaroo_ml_ops_api_client.models.thresholds import Thresholds
from wallaroo.wallaroo_ml_ops_api_client.models.univariate_continuous import (
    UnivariateContinuous,
)
from wallaroo.wallaroo_ml_ops_api_client.models.window_width_duration import (
    WindowWidthDuration,
)
from wallaroo.wallaroo_ml_ops_api_client.types import Unset
from .wallaroo_ml_ops_api_client.models.assay_v2 import AssayV2 as MLOpsAssayV2
from .wallaroo_ml_ops_api_client.models import BaselineType1 as MLOpsStaticBaseline
from .wallaroo_ml_ops_api_client.models import BaselineType0 as MLOpsSummaryBaseline
from .wallaroo_ml_ops_api_client.models.targeting import Targeting as MLOpsTargeting
from .wallaroo_ml_ops_api_client.models.summarizer_type_0 import (
    SummarizerType0 as UnivariateSummarizer,
)
from .wallaroo_ml_ops_api_client.models.scheduling import (
    Scheduling as MLOpsScheduling,
)
from .wallaroo_ml_ops_api_client.models.rolling_window import (
    RollingWindow as MLOpsRollingWindow,
)
from .wallaroo_ml_ops_api_client.models.assay_result_v2 import (
    AssayResultV2 as MLOPsAssayResultV2,
)
import pandas as pd
from .wallaroo_ml_ops_api_client.api.assays.preview import (
    sync_detailed as sync_detailed_preview,
    PreviewBody,
)
from .wallaroo_ml_ops_api_client.api.assays.get_by_id import (
    sync as sync_get_by_id,
    GetByIdBody,
)
from .wallaroo_ml_ops_api_client.api.assays.get_results import (
    sync_detailed as sync_detailed_results,
    GetResultsBody,
)
from .wallaroo_ml_ops_api_client.api.assays.set_active import (
    SetActiveBody,
    sync_detailed as sync_detailed_set_active,
)
from .wallaroo_ml_ops_api_client.api.assays.schedule import (
    sync_detailed as sync_detailed_schedule,
    ScheduleBody,
)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


if TYPE_CHECKING:
    # Imports that happen below in methods to fix circular import dependency
    # issues need to also be specified here to satisfy mypy type checking.
    from wallaroo.client import Client


class RollingWindow(MLOpsRollingWindow):
    @classmethod
    def _from_v1_config(cls, v1_config: V1AssayConfig):
        dur = None
        [count, unit] = v1_config.window.width.split()
        if unit == "minutes" or unit == "minute":
            dur = int(count) * 60
        elif unit == "hours" or unit == "hour":
            dur = int(count) * 60 * 60
        elif unit == "days" or unit == "day":
            dur = int(count) * 60 * 60 * 24
        elif unit == "weeks" or unit == "week":
            dur = int(count) * 60 * 60 * 24 * 7

        return RollingWindow(width=WindowWidthDuration(seconds=unwrap(dur)))

    def _get_display_row(self):
        return f"""
        <tr><td>Window Width</td><td>{self.width.seconds} seconds</td></tr>
        """


class StaticBaseline(MLOpsStaticBaseline):
    """A Baseline from the server will always come in the form of a set of Summaries."""

    def summarize(self):
        # TODO: Expose summarize function like v1 to convert between baseline types.
        pass

    def _get_baseline_end(self):
        return self[1]

    def _get_display_row(self):
        return f"""
        <tr><td>Baseline</td><td>TODO</td></tr>
        """


class SummaryBaseline(MLOpsSummaryBaseline):
    """A Baseline from the server will always come in the form of a set of Summaries."""

    def _get_display_row(self):
        # TODO: Check dates
        return f"""
        <tr><td>Monitoring</td><td>{list(self.summary.to_dict().keys())}</td></tr>
        """

    def _get_baseline_end(self):
        return self.summary[list(self.summary.to_dict())[0]].end

    @classmethod
    def _from_v1_config(cls, v1_config: V1AssayConfig):
        config_baseline = v1_config.baseline
        if isinstance(config_baseline, V1CalculatedBaseline) or isinstance(
            config_baseline, V1FixedBaseline
        ):
            start = cast(str, config_baseline.calculated["fixed_window"].get("start"))
            baseline_start_at = dateutil.parser.parse(start)
            end = cast(str, config_baseline.calculated["fixed_window"].get("end"))
            baseline_end_at = dateutil.parser.parse(end)
            return StaticBaseline([baseline_start_at, baseline_end_at]).summarize()
        elif isinstance(config_baseline, V1StaticBaseline):
            config_summarizer = cast(V1Summarizer, v1_config.summarizer)
            parsed_path = unwrap(v1_config.window.path).split()
            prefix = "in" if parsed_path[0] == "input" else "out"
            iopath = f"{prefix}.{parsed_path[1]}.{parsed_path[2]}"

            start = cast(str, config_baseline.static.get("start"))
            baseline_start_at = dateutil.parser.parse(start)
            end = cast(str, config_baseline.static.get("end"))
            baseline_end_at = dateutil.parser.parse(end)
            return SummaryBaseline.from_v1_summary(
                config_baseline, config_summarizer, iopath
            )
        else:
            raise Exception(
                "Could not parse baseline, unknown V1 type.",
                isinstance(config_baseline, V1StaticBaseline),
                config_baseline.__dict__,
            )

    @classmethod
    def from_v1_summary(
        cls, baseline: V1StaticBaseline, summarizer: V1Summarizer, iopath: str
    ):
        """A v1 summary is guaranteed to only contain one observed path."""

        aggregation = Aggregation(baseline.static["aggregation"].value)  # type: ignore # mypy can't handle complex dicts
        # TODO: Move baseline calculation to assays v2, this is relying on v1.
        v1_edges = cast(List[Union[float, str]], baseline.static.get("edges"))
        # TODO: Handle infinity, make sure edge cases are clean.
        if v1_edges[-1] == None:
            # We could convert None instead of a str to INF if this is weird.
            v1_edges[-1] = "INFINITY"
        v1_labels = cast(List[str], baseline.static.get("edge_names"))
        v1_mode = summarizer.bin_mode
        v1_bin_count = summarizer.num_bins

        # OpenAPI doesn't know that "INFINITY" is allowed. This is manually deserialized into a float::INF by serde
        # In practice we never construct these manually, but we're converting v1 Baselines into the v2 Baseline, which is
        # not really a public interface.
        v1_edges_hack = cast(List[float], list(v1_edges))

        # TODO: Handle add_explicit_edges
        v2_mode = cast(
            Union[BinModeType0, BinModeType1, BinModeType2, BinModeType4],
            BinModeType0.NONE,
        )
        if v1_mode == V1BinMode.NONE:
            v2_mode = BinModeType0.NONE
        elif v1_mode == V1BinMode.EQUAL:
            v2_mode = BinModeType1(v1_bin_count)
        elif v1_mode == V1BinMode.QUANTILE:
            v2_mode = BinModeType2(v1_bin_count)
        elif v1_mode == V1BinMode.PROVIDED:
            v2_mode = BinModeType4(v1_edges_hack)

        v2_bins = Bins(edges=v1_edges_hack, labels=v1_labels, mode=v2_mode)
        summ = SeriesSummary(
            aggregated_values=cast(
                List[float], baseline.static.get("aggregated_values")
            ),
            aggregation=aggregation,
            bins=v2_bins,
            name=iopath,
            statistics=SeriesSummaryStatistics(
                count=cast(int, baseline.static.get("count")),
                max_=cast(float, baseline.static.get("max")),
                mean=cast(float, baseline.static.get("mean")),
                median=cast(float, baseline.static.get("median")),
                min_=cast(float, baseline.static.get("min")),
                std=cast(float, baseline.static.get("std")),
            ),
            start=cast(Union[None, datetime], baseline.static.get("start", None)),
            end=cast(Union[None, datetime], baseline.static.get("end", None)),
        )
        summary = FieldTaggedSummaries.from_dict({iopath: summ.to_dict()})
        return SummaryBaseline(summary=summary)


# TODO: Pull in client fmt
fmt: str = "%Y-%d-%b %H:%M:%S"


class Scheduling(MLOpsScheduling):
    @classmethod
    def _from_v1_config(
        cls, v1_config: V1AssayConfig, baseline_end_at: Optional[datetime]
    ):
        interval = (
            v1_config.window.interval
            if v1_config.window.interval
            else v1_config.window.width
        )

        first_run = (
            v1_config.window.start
            if v1_config.window.start
            else (baseline_end_at if baseline_end_at else datetime.now(timezone.utc))
        )

        run_frequency = cast(Optional[PGInterval], None)
        [count, unit] = interval.split()
        if unit == "minutes" or unit == "minute":
            run_frequency = PGInterval(quantity=int(count), unit=IntervalUnit.MINUTE)
        elif unit == "hours" or unit == "hour":
            run_frequency = PGInterval(quantity=int(count), unit=IntervalUnit.HOUR)
        elif unit == "days" or unit == "day":
            run_frequency = PGInterval(quantity=int(count), unit=IntervalUnit.DAY)
        elif unit == "weeks" or unit == "week":
            run_frequency = PGInterval(quantity=int(count), unit=IntervalUnit.WEEK)

        if run_frequency is None:
            raise Exception(
                "Failed to parse the run frequency for this assay.", interval
            )

        return Scheduling(
            first_run=first_run,
            run_frequency=MLOpsSimpleRunFrequency(simple_run_frequency=run_frequency),
            # Run Until from a product persp. is only used for previews.
            # end=v1_config.run_until,
        )

    def _get_display_row(self):
        return f"""
        <tr><td>First Run</td><td>{self.first_run.strftime(fmt)}</td></tr>
        {f"<tr><td>End Run</td><td>{self.end.strftime(fmt)}</td></tr>" if self.end else ""}
        {f"<tr><td>Run Frequency</td><td>{self.run_frequency.simple_run_frequency.quantity} {self.run_frequency.simple_run_frequency.unit}</td></tr>"}
        """


class Targeting(MLOpsTargeting):
    @classmethod
    def _from_v1_config(cls, v1_config: V1AssayConfig):
        parsed_path = unwrap(v1_config.window.path).split()
        prefix = "in" if parsed_path[0] == "input" else "out"

        model_name = v1_config.window.model_name
        thresh = Thresholds(
            alert=v1_config.alert_threshold, warning=v1_config.warning_threshold
        )
        do = DataOrigin(
            v1_config.pipeline_name, unwrap(v1_config.workspace_id), model_id=model_name
        )
        dp = DataPath(
            field=f"{prefix}.{parsed_path[1]}",
            indexes=[int(parsed_path[2])],
            thresholds=thresh,
        )
        return cls(do, [dp])

    def _get_iopath(self) -> str:
        """Returns the legacy iopath"""
        index = (
            0
            if self.iopath[0].indexes == None
            or isinstance(self.iopath[0].indexes, Unset)
            else unwrap(self.iopath[0].indexes)[0]
        )
        return f"{self.iopath[0].field}.{index}"

    def _get_display_row(self):
        return f"""
        <tr><td>Pipeline</td><td>{self.data_origin.pipeline_name}</td></tr>
        {f"<tr><td>Model ID</td><td>{self.data_origin.model_id}</td></tr>" if self.data_origin.model_id else ""}
        <tr><td>Workspace ID</td><td>{self.data_origin.workspace_id}</td></tr>
        """


class Summarizer(UnivariateSummarizer):
    def _get_display_row(self):
        bin_mode_str = None
        if isinstance(self.univariate_continuous.bin_mode, BinModeType0):
            bin_mode_str = self.univariate_continuous.bin_mode.name
        elif isinstance(self.univariate_continuous.bin_mode, BinModeType1):
            bin_mode_str = f"{self.univariate_continuous.bin_mode.equal} Equal bins"
        elif isinstance(self.univariate_continuous.bin_mode, BinModeType2):
            bin_mode_str = (
                f"{self.univariate_continuous.bin_mode.quantile} Quantile bins"
            )
        elif isinstance(self.univariate_continuous.bin_mode, BinModeType3):
            bin_mode_str = f"{self.univariate_continuous.bin_mode.quantile_with_explicit_outliers} Quantile bins"
        elif isinstance(self.univariate_continuous.bin_mode, BinModeType4):
            bin_mode_str = f"{self.univariate_continuous.bin_mode.provided}"

        # TODO: Would be nice to wrap this in a <summary> and show the actual bins underneath.
        return f"""
        <tr><td>Bin Mode</td><td>{bin_mode_str}</td></tr>
        {f"<tr><td>Bin Weights</td><td>{self.univariate_continuous.bin_weights}</td></tr>" if self.univariate_continuous.bin_weights else ""}
        <tr><td>Aggregation</td><td>{self.univariate_continuous.aggregation.value}</td></tr>
        <tr><td>Metric</td><td>{self.univariate_continuous.metric.value}</td></tr>
        """

    @classmethod
    def _from_v1_config(cls, v1_config: V1AssayConfig):
        config_summarizer = cast(V1Summarizer, v1_config.summarizer)
        return Summarizer.from_v1_summarizer(config_summarizer)

    @classmethod
    def from_v1_summarizer(cls, summarizer: V1Summarizer):
        agg = summarizer.aggregation
        v1_mode = summarizer.bin_mode
        v1_bin_count = summarizer.num_bins
        v1_edges = summarizer.provided_edges
        v1_weights = summarizer.bin_weights

        # TODO: Handle add_explicit_edges
        v2_mode = cast(
            Union[BinModeType0, BinModeType1, BinModeType2, BinModeType4],
            BinModeType0.NONE,
        )
        if v1_mode == V1BinMode.NONE:
            v2_mode = BinModeType0.NONE
        elif v1_mode == V1BinMode.EQUAL:
            v2_mode = BinModeType1(v1_bin_count)
        elif v1_mode == V1BinMode.QUANTILE:
            v2_mode = BinModeType2(v1_bin_count)
        elif v1_mode == V1BinMode.PROVIDED:
            v2_mode = BinModeType4(unwrap(v1_edges))

        metric = V1Metric[summarizer.metric.name]

        return cls(
            univariate_continuous=UnivariateContinuous(
                Aggregation[agg.name], v2_mode, Metric[metric.name], v1_weights
            )
        )


class AssayV2(Object):
    def __init__(self, client: Optional["Client"], id: str) -> None:
        assert client is not None
        self._client = client
        self.id = id
        super().__init__(gql_client=client._gql_client, data={}, fetch_first=True)

    def _fill(self, data) -> None:
        # Can't violate the Liskov principle, so we can rehydrate the typings here.
        data = MLOpsAssayV2.from_dict(data)
        self.id = data.id
        self.name = data.name
        self.active = data.active

        if hasattr(data, "window"):
            self.window = RollingWindow.from_dict(data.window.to_dict())

        if hasattr(data, "baseline"):
            if isinstance(data.baseline, MLOpsStaticBaseline):
                self.baseline = cast(
                    Union[StaticBaseline, SummaryBaseline],
                    StaticBaseline.from_dict(data.baseline.to_dict()),
                )

            elif isinstance(data.baseline, MLOpsSummaryBaseline):
                self.baseline = SummaryBaseline.from_dict(data.baseline.to_dict())

        if hasattr(data, "scheduling"):
            if isinstance(data.scheduling, MLOpsScheduling):
                self.scheduling = Scheduling.from_dict(data.scheduling.to_dict())

        if hasattr(data, "summarizer"):
            if isinstance(data.summarizer, UnivariateSummarizer):
                self.summarizer = Summarizer.from_dict(data.summarizer.to_dict())

        if hasattr(data, "targeting"):
            if isinstance(data.targeting, MLOpsTargeting):
                self.targeting = Targeting.from_dict(data.targeting.to_dict())

        self.created_at = data.created_at
        self.updated_at = data.updated_at

    def _fetch_attributes(self) -> Dict[str, Any]:
        ret = sync_get_by_id(client=self._client.mlops(), body=GetByIdBody(self.id))
        if ret is None:
            raise Exception(f"Failed to fetch assay {self.id}")
        return ret.to_dict()

    def results(self, start=None, end=None, include_failures=False, workspace_id=None):
        ret = sync_detailed_results(
            client=self._client.mlops(),
            body=GetResultsBody(
                id=self.id, start=start, end=end, workspace_id=workspace_id
            ),
        )
        if ret.parsed is None:
            raise Exception("Failed to get results", ret)

        return AssayResultsList(
            [
                AssayResultV2(self, x)
                for x in ret.parsed
                if include_failures or len(x.summaries.additional_properties) > 0
            ],
            self,
        )

    def set_active(self, active: bool):
        """
        @param active bool True if you want to resume the assay, False if you want to pause it.
        """
        ret = sync_detailed_set_active(
            client=self._client.mlops(),
            body=SetActiveBody(active, self.id),
        )

        if ret.status_code != 200:
            verb = "resume" if active else "pause"
            raise Exception(f"Failed to {verb} assay. ", ret.content)

        self._rehydrate()
        return self

    def pause(self):
        """Pauses an assay. Note that this only pauses future scheduled runs- historical calculations will still be computed."""
        self.set_active(False)
        self._rehydrate()
        return self

    def resume(self):
        """Resumes a previously-paused assay."""
        self.set_active(True)
        self._rehydrate()
        return self

    @staticmethod
    def builder(client, pipeline_name: str, workspace_id: int):
        return AssayV2Builder(client, pipeline_name, workspace_id)

    def _next_run(self):
        from .wallaroo_ml_ops_api_client.api.assays.get_next_run import (
            sync_detailed,
            GetNextRunBody,
        )

        ret = sync_detailed(client=self._client.mlops(), body=GetNextRunBody(self.id))

        if ret.parsed == None:
            raise Exception(ret.content)

        return ret.parsed

    def _get_iopath(self):
        return self.targeting._get_iopath()

    def _repr_html_(self):
        self._rehydrate()
        fmt = self._client._time_format
        next_run_data = self._next_run()
        workspace_name = Workspace(
            self._client, {"id": self.targeting.data_origin.workspace_id}
        ).name()
        return f"""<table>
          <tr><th>Field</th><th>Value</th></tr>
          <tr><td>ID</td><td>{self.id}</td></tr>
          <tr><td>Name</td><td>{self.name}</td></tr>
          <tr><td>Active</td><td>{self.active}</td></tr>
          {self.targeting._get_display_row()}
          <tr><td>Workspace Name</td><td>{workspace_name}</td></tr>
          {self.baseline._get_display_row()}
          {self.window._get_display_row()}
          {self.scheduling._get_display_row()}
          {self.summarizer._get_display_row()}
          <tr><td>Last Run</td><td>{next_run_data.last_run.strftime(fmt) if next_run_data.last_run else None}</td></tr>
          <tr><td>Next Run</td><td>{next_run_data.next_run.strftime(fmt)}</td></tr>
          <tr><td>Created At</td><td>{self.created_at.strftime(fmt)}</td></tr>
          <tr><td>Updated At</td><td>{self.updated_at.strftime(fmt)}</td></tr>
        </table>"""


class AssayV2List(List[AssayV2]):
    def _repr_html_(self):
        def row(assay: AssayV2):
            next_run_data = assay._next_run()
            fmt = assay._client._time_format
            monitored_fields = None
            workspace_name = Workspace(
                assay._client, {"id": assay.targeting.data_origin.workspace_id}
            ).name()
            if isinstance(assay.baseline, SummaryBaseline):
                monitored_fields = list(assay.baseline.summary.to_dict().keys())
            return f"""
            <tr>
              <td>{assay.id}</td>
              <td>{assay.targeting.data_origin.pipeline_name}</td>
              <td>{assay.targeting.data_origin.workspace_id}</td>
              <td>{workspace_name}</td>
              <td>{monitored_fields}</td>
              <td>{next_run_data.last_run.strftime(fmt)}</td>
              <td>{next_run_data.next_run.strftime(fmt)}</td>
              <td>{assay.created_at.strftime(fmt)}</td>
              <td>{assay.updated_at.strftime(fmt)}</td>
            </tr>
            """

        fields = [
            "id",
            "pipeline",
            "workspace id",
            "workspace name",
            "monitored fields",
            "last_run",
            "next_run",
            "created_at",
            "updated_at",
        ]

        if not self:
            return "(no assays)"
        else:
            return (
                "<table>"
                + "<tr><th>"
                + "</th><th>".join(fields)
                + "</th></tr>"
                + ("".join([row(p) for p in self]))
                + "</table>"
            )


class AssayResultV2(MLOPsAssayResultV2):
    def __init__(self, parent_assay: AssayV2, mlops_assay_result: MLOPsAssayResultV2):
        super().__init__(**mlops_assay_result.to_dict())
        self.parent_assay = parent_assay
        self.raw = mlops_assay_result

    def chart(self, show_scores=True):
        """Quickly create a chart showing the bins, values and scores of an assay analysis.
        show_scores will also label each bin with its final weighted (if specified) score.
        """
        iopath = self._v1_iopath()
        bin_mode = self.raw.summaries[iopath].bins.mode
        weighted = isinstance(
            self.parent_assay.summarizer.univariate_continuous.bin_weights, List
        )
        if isinstance(bin_mode, BinModeType0):
            pass
        elif isinstance(bin_mode, BinModeType1):
            num_bins = bin_mode.equal
            bin_mode_str = "Equal"
        elif isinstance(bin_mode, BinModeType2):
            num_bins = bin_mode.quantile
            bin_mode_str = "Quantile"
        elif isinstance(bin_mode, BinModeType3):
            pass
        elif isinstance(bin_mode, BinModeType4):
            num_bins = len(bin_mode.provided)
            bin_mode_str = "Provided"
        agg = self.raw.summaries[iopath].aggregation.value
        baseline_aggregated_values = self.parent_assay.baseline.summary[
            iopath
        ].aggregated_values
        baseline_sample_size = self.parent_assay.baseline.summary[
            iopath
        ].statistics.count
        window_aggregated_values = self.raw.summaries[iopath].aggregated_values
        window_sample_size = self.raw.summaries[iopath].statistics.count
        end = self.raw.window_end
        metric = self.parent_assay.summarizer.univariate_continuous.metric.value
        score = self.raw.scores[iopath]
        edge_names = self.raw.summaries[iopath].bins.labels

        title = f"{num_bins} {bin_mode_str} {agg} {metric}={score:5.3f} Weighted={weighted} {end}"

        fig, ax = plt.subplots()

        if self.raw.summaries[iopath].aggregation == Aggregation.EDGES:
            for n, v in enumerate(baseline_aggregated_values):
                plt.axvline(x=v, color="blue", alpha=0.5)
                plt.text(v, 0, f"e{n}", color="blue")
            for n, v in enumerate(window_aggregated_values):
                plt.axvline(x=v, color="orange", alpha=0.5)
                plt.text(v, 0.1, f"e{n}", color="orange")
        else:
            bar1 = plt.bar(
                edge_names,
                baseline_aggregated_values,
                alpha=0.50,
                label=f"Baseline ({baseline_sample_size})",
            )
            bar2 = plt.bar(
                edge_names,
                window_aggregated_values,
                alpha=0.50,
                label=f"Window ({window_sample_size})",
            )
            if len(edge_names) > 7:
                ax.set_xticklabels(labels=edge_names, rotation=45)

            for i, bar in enumerate(bar1.patches):
                ax.annotate(
                    f"{score:.4f}",
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center",
                    va="center",
                    size=9,
                    xytext=(0, 8),
                    textcoords="offset points",
                )
            plt.legend()
        ax.set_title(title)
        plt.xticks(rotation=45)
        plt.show()

    def _v1_iopath(self):
        return f"{self.parent_assay.targeting.iopath[0].field}.{self.parent_assay.targeting.iopath[0].indexes[0]}"

    def _into_v1(self):
        d = {}

        summary = self.raw.summaries.to_dict().get(self._v1_iopath(), {})
        # v2 assays don't have ids.
        # d.id = self.raw.id
        d["assay_id"] = self.raw.assay_id
        d["assay_name"] = self.parent_assay.name
        # TODO: Pipeline name to ID
        # d.pipeline_id =
        d["pipeline_name"] = self.parent_assay.targeting.data_origin.pipeline_name
        workspace_id = self.parent_assay.targeting.data_origin.workspace_id
        d["workspace_id"] = workspace_id
        d["workspace_name"] = Workspace(
            self.parent_assay._client, {"id": workspace_id}
        ).name()

        d["raw"] = self.raw
        d["iopath"] = self._v1_iopath()
        d["score"] = self.raw.scores[self._v1_iopath()]
        d["status"] = self.raw.status.value
        d["alert_threshold"] = (
            self.parent_assay.targeting.iopath[0].thresholds.alert
            if self.parent_assay.targeting.iopath[0].thresholds
            else None
        )
        d["warning_threshold"] = (
            self.parent_assay.targeting.iopath[0].thresholds.warning
            if self.parent_assay.targeting.iopath[0].thresholds
            else None
        )
        d["window_summary"] = summary
        d["is_baseline_run"] = False
        return AssayAnalysis(d, self.parent_assay._client, d["assay_name"], True)

    def compare_basic_stats(self):
        iopath = self._v1_iopath()
        window_stats = self.raw.summaries[iopath].statistics
        baseline_stats = self.parent_assay.baseline.summary[iopath].statistics
        df = pd.concat(
            [
                pd.DataFrame(baseline_stats.to_dict(), index=["Baseline"]),
                pd.DataFrame(window_stats.to_dict(), index=["Window"]),
            ]
        )
        df.loc["diff"] = df.loc["Window"] - df.loc["Baseline"]
        df.loc["pct_diff"] = df.loc["diff"] / df.loc["Baseline"] * 100.0

        return df.T

    def compare_bins(self):
        iopath = self._v1_iopath()
        window_values = self.raw.summaries[iopath].aggregated_values
        window_edges = self.raw.summaries[iopath].bins.edges
        window_labels = self.raw.summaries[iopath].bins.labels
        baseline_values = self.parent_assay.baseline.summary[iopath].aggregated_values
        baseline_edges = self.parent_assay.baseline.summary[iopath].bins.edges
        baseline_labels = self.parent_assay.baseline.summary[iopath].bins.labels
        aggregation = self.parent_assay.baseline.summary[iopath].aggregation

        window = pd.DataFrame(
            {
                "window_edges": window_edges,
                "window_labels": window_labels,
                "window_values": window_values,
            }
        )
        baseline = pd.DataFrame(
            {
                "baseline_edges": baseline_edges,
                "baseline_labels": baseline_labels,
                "baseline_values": baseline_values,
            }
        )
        df = pd.concat([baseline, window], axis=1)
        df["diff_in_pcts"] = df["window_values"] - df["baseline_values"]

        # print(f"Sum of absolute value of differences as percentage per bin {comparison.diff_in_pcts.abs().sum():5.3f}")
        return df


class AssayResultsList(List[AssayResultV2]):
    def __init__(self, arr: List[AssayResultV2], parent_assay: AssayV2):
        super().__init__(arr)
        self.parent_assay = parent_assay

    def to_dataframe(self):
        iopath = self.parent_assay._get_iopath()
        alert = self.parent_assay.targeting.iopath[0].thresholds.alert
        warning = self.parent_assay.targeting.iopath[0].thresholds.warning

        if len(self) == 0:
            return pd.DataFrame()

        x = pd.DataFrame([x.raw.to_dict() for x in self])
        x = (
            x.join(pd.json_normalize(x["scores"]))
            # TODO: Can't figure out why .get(iopath, {}) causes the columns to just be missing.
            .join(pd.json_normalize(x["summaries"], errors="ignore"))
            .drop("scores", axis="columns")
            .drop("assay_id", axis="columns")
            .assign(
                warning_threshold=warning,
                alert_threshold=alert,
            )
        )

        # Repeated values as convenience for V1 compatibility/helper
        workspace_id = self.parent_assay.targeting.data_origin.workspace_id
        x["workspace_id"] = workspace_id
        x["workspace_name"] = Workspace(
            self.parent_assay._client, {"id": workspace_id}
        ).name()
        x["iopath"] = iopath

        x["alert_status"] = x[x["iopath"][0]].map(
            lambda score: (
                "Alert"
                if alert != None and score >= alert
                else ("Warn" if warning and score >= warning else "Ok")
            )
        )

        x.insert(
            0, "pipeline_name", self.parent_assay.targeting.data_origin.pipeline_name
        )
        x.insert(0, "assay_name", self.parent_assay.name)
        x.insert(0, "assay_id", self.parent_assay.id)

        x.rename(
            columns={"status": "run_status", "alert_status": "status"}, inplace=True
        )
        return x

    def _into_v1(self):
        return AssayAnalysisList([x._into_v1() for x in self])

    def _repr_html_(self):
        def row(result: AssayResultV2):
            # TODO: Pass in client for this
            # fmt = result.client._time_format
            fmt = "%Y-%d-%b %H:%M:%S"

            summary_html = ""
            if result.raw.summaries:
                summaries = result.raw.summaries.to_dict()
                for key in summaries:
                    summary_html += f"""<details>
                  <summary>{key}</summary>
                  {summaries[key]}
                </details>"""

            score_html = ""
            if result.raw.scores:
                scores = result.raw.scores.to_dict()
                score_html = "<br/>".join(
                    [f"<div>{score}: {scores[score]}</div>" for score in scores]
                )
            workspace_id = result.raw.workspace_id
            workspace_name = Workspace(
                result.parent_assay._client, {"id": workspace_id}
            ).name()
            return (
                "<tr>"
                + f"<td>{result.raw.window_start.strftime(fmt)}</td>"
                + f"<td>{result.raw.window_end.strftime(fmt)}</td>"
                + f"<td>{workspace_id}</td>"
                + f"<td>{workspace_name}</td>"
                # + f"<td>{result.assay_id}</td>"
                + f"<td>{score_html}</td>"
                + f"<td>{result.raw.status}</td>"
                + f"<td>{summary_html}</td>"
                + f"<td>{result.raw.created_at.strftime(fmt)}</td>"
                + f"<td>{result.raw.updated_at.strftime(fmt)}</td>"
                + "</tr>"
            )

        fields = [
            "window_start",
            "window_end",
            "workspace_id",
            "workspace_name",
            # "assay_id",
            "scores",
            "status",
            "summaries",
            "created_at",
            "updated_at",
        ]

        if not self:
            return "(no results)"
        else:
            return (
                "<table>"
                + "<tr><th>"
                + "</th><th>".join(fields)
                + "</th></tr>"
                + ("".join([row(p) for p in self]))
                + "</table>"
            )

    def _color(self, edge=False):
        def _color_row(row: AssayResultV2):
            field = row.parent_assay._get_iopath()
            scores = row.scores
            if scores == None or isinstance(scores, Unset) or not field in scores:  # type: ignore
                return "grey"
            val = unwrap(scores)[field]
            thresh = row.parent_assay.targeting.iopath[0].thresholds
            if thresh is None or isinstance(thresh, Unset):
                return "green" if isinstance(val, float) else "red"
            warning = thresh.warning
            alert = thresh.alert

            # If val errored out, always return red. Most important.
            if not isinstance(val, float):
                return "red" if edge else "white"
            # If no thresholds are configured, always return green.
            elif warning is None and alert is None:
                return "green"
            # If an alert is configured and we're above it, red.
            elif isinstance(alert, float) and val >= alert:
                return "red"
            # If a warning is configured and we're above it, orange.
            elif isinstance(warning, float) and val >= warning:
                return "orange"
            # We are not in error and not above a threshold, but they are configured.
            else:
                return "green"

        return [_color_row(x) for x in self]

    def chart_df(
        self,
        df: Union[pd.DataFrame, pd.Series],
        title: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ):
        """Creates a basic chart of the scores from dataframe created from assay analysis list"""
        float_only_df = df[self.parent_assay._get_iopath()].map(
            lambda x: x if isinstance(x, float) else 0.0
        )

        end_times = df.window_end.map(lambda x: dateutil.parser.parse(x))

        plt.scatter(
            end_times,
            float_only_df,
            color=self._color(),
            edgecolor=self._color(edge=True),
            plotnonfinite=True,
        )
        plt.title(title)
        if start != None and end != None:
            plt.xlim(start, end)

        ax = plt.gca()
        ax.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(ax.xaxis.get_major_locator())
        )
        for label in ax.get_xticklabels(which="major", minor=True):
            label.set(rotation=30, horizontalalignment="right")

        plt.grid()
        plt.show()

    def chart_scores(
        self, start: Optional[datetime] = None, end: Optional[datetime] = None
    ):
        """Creates a basic chart of the scores from an AssayAnalysisList"""
        if len(self) == 0:
            raise ValueError("No data in this AssayResultsList.")
        ardf = self.to_dataframe()
        if ardf.shape == (0, 0):
            raise ValueError("No data in this AssayResultsList.")

        self.chart_df(ardf, "Assays V2 Score", start, end)


class AssayV2Builder:
    def __init__(self, client: "Client", pipeline_name: str, workspace_id: int):
        self.client = client
        # Set the defaults
        self.targeting = Targeting(DataOrigin(pipeline_name, workspace_id), [])
        self.scheduling = Scheduling(
            datetime.now().astimezone(),
            MLOpsSimpleRunFrequency(PGInterval(1, IntervalUnit.DAY)),
        )
        self.window: Optional[RollingWindow] = None
        self.name = f"{pipeline_name} assay"
        self.bin_weights: Optional[List[float]] = None

    def _validate(self):
        if self.baseline is None:
            raise Exception("No baseline is configured. See `set_baseline`")

        if len(self.targeting.iopath) <= 0:
            raise Exception("No monitoring paths are configured. See `add_monitoring`")

        if self.metric is None:
            raise Exception("No metric is configured.")

        if self.aggregation is None:
            raise Exception("No aggregation is configured")

        if self.bin_mode is None:
            raise Exception("No binning mode is configured")

    @classmethod
    def _from_v1_config(cls, v1_config: V1AssayConfig):
        builder = cls(
            unwrap(v1_config.client),
            v1_config.pipeline_name,
            unwrap(v1_config.workspace_id),
        )
        builder.targeting = Targeting._from_v1_config(v1_config)
        builder.baseline = SummaryBaseline._from_v1_config(v1_config)
        builder.scheduling = Scheduling._from_v1_config(
            v1_config, builder.baseline._get_baseline_end()
        )
        builder.summarizer = Summarizer._from_v1_config(v1_config)
        builder.window = RollingWindow._from_v1_config(v1_config)

        builder.metric = builder.summarizer.univariate_continuous.metric
        builder.bin_mode = builder.summarizer.univariate_continuous.bin_mode
        builder.aggregation = builder.summarizer.univariate_continuous.aggregation
        builder.bin_weights = builder.summarizer.univariate_continuous.bin_weights

        return builder

    def build(self):
        self._validate()

        self.summarizer = Summarizer(
            UnivariateContinuous(
                self.aggregation, self.bin_mode, self.metric, self.bin_weights
            )
        )
        ret = sync_detailed_schedule(
            client=self.client.mlops(),
            body=ScheduleBody(
                name=self.name,
                baseline=self.baseline,
                scheduling=self.scheduling,
                summarizer=self.summarizer,
                targeting=self.targeting,
                window=self.window,
            ),
        )

        if ret is None:
            raise Exception(f"Failed to schedule assay. {ret.content}")

        return AssayV2(client=self.client, id=ret.parsed)

    def set_name(self, name: str):
        self.name = name
        return self

    # TODO: Make workspace_id optional, warn user and grab current workspace?
    def set_pipeline(self, pipeline_name, workspace_id):
        self.targeting.data_origin.pipeline_name = pipeline_name
        self.targeting.data_origin.workspace_id = workspace_id
        return self

    def set_model(self, model_name: str):
        self.targeting.data_origin.model_id = model_name
        return self

    def add_monitoring(
        self,
        field: str,
        indices: List[int],
        warning: Optional[float] = None,
        alert: Optional[float] = None,
    ):
        thresh = Thresholds(warning=warning, alert=alert)
        dp = DataPath(field, indices, thresh)
        self.targeting.iopath.append(dp)
        return self

    def set_monitoring(
        self,
        field: str,
        indices: List[int],
        warning: Optional[float] = None,
        alert: Optional[float] = None,
    ):
        thresh = Thresholds(warning=warning, alert=alert)
        dp = DataPath(field, indices, thresh)
        self.targeting.iopath = [dp]
        return self

    def set_baseline(self, start: datetime, end: datetime):
        self.baseline = StaticBaseline([start, end])

        if self.window is None:
            self.set_window_width(end - start)

        return self

    def set_window_width(self, width: Union[timedelta, int]):
        """
        @param width int Time span in seconds for the assay window.
        """
        width = width if isinstance(width, int) else int(width.total_seconds())
        self.window = RollingWindow(WindowWidthDuration(width))
        return self

    def set_first_run(self, first_run: datetime):
        self.scheduling.first_run = first_run.astimezone()
        return self

    def daily(self, quantity=1):
        self.scheduling.run_frequency = MLOpsSimpleRunFrequency(
            PGInterval(quantity, IntervalUnit.DAY)
        )
        return self

    def hourly(self, quantity=1):
        self.scheduling.run_frequency = MLOpsSimpleRunFrequency(
            PGInterval(quantity, IntervalUnit.HOUR)
        )
        return self

    def weekly(self):
        self.scheduling.run_frequency = MLOpsSimpleRunFrequency(
            PGInterval(1, IntervalUnit.WEEK)
        )
        return self

    def minutely(self, quantity=1):
        self.scheduling.run_frequency = MLOpsSimpleRunFrequency(
            PGInterval(quantity, IntervalUnit.MINUTE)
        )
        return self

    def days_of_data(self, quantity=1):
        self.set_window_width(quantity * 60 * 60 * 24)
        return self

    def minutes_of_data(self, quantity=1):
        self.set_window_width(quantity * 60)
        return self

    def hours_of_data(self, quantity=1):
        self.set_window_width(quantity * 60 * 60)
        return self

    def weeks_of_data(self, quantity=1):
        self.set_window_width(quantity * 60 * 60 * 24 * 7)
        return self

    def cumulative_aggregation(self):
        self.aggregation = Aggregation.CUMULATIVE
        return self

    def density_aggregation(self):
        self.aggregation = Aggregation.DENSITY
        return self

    def edge_aggregation(self):
        """Edge aggregations look at the calculated bin edges instead of how the data is binned."""
        self.aggregation = Aggregation.EDGES
        return self

    def max_diff_metric(self):
        self.metric = Metric.MAXDIFF
        return self

    def psi_metric(self):
        self.metric = Metric.PSI
        return self

    def sum_diff_metric(self):
        self.metric = Metric.SUMDIFF
        return self

    def no_bins(self):
        self.bin_mode = BinModeType0.NONE
        return self

    def equal_bins(self, num: int):
        self.bin_mode = BinModeType1(equal=num)
        return self

    def quantile_bins(self, num: int):
        self.bin_mode = BinModeType2(num)
        return self

    def set_bin_weights(self, weights: List[float]):
        if self.bin_mode.equal is not None and self.bin_mode.equal != len(weights):
            raise Exception(
                f"Improperly configured bin weights! There are {self.bin_mode.equal} bins but received {len(weights)} weights"
            )
        elif self.bin_mode.quantile is not None and self.bin_mode.quantile != len(
            weights
        ):
            raise Exception(
                f"Improperly configured bin weights! There are {self.bin_mode.equal} bins but received {len(weights)} weights"
            )

        self.bin_weights = weights
        return self

    def set_aggregation(self, aggregation=Union[str, Aggregation, V1Aggregation]):
        if isinstance(aggregation, V1Aggregation):
            aggregation = Aggregation[aggregation.name]
        elif isinstance(aggregation, str):
            aggregation = Aggregation[aggregation]

        self.aggregation = aggregation
        return self

    def set_metric(self, metric=Union[str, Metric, V1Metric]):
        if isinstance(metric, V1Metric):
            metric = Metric[metric.name]
        elif isinstance(metric, str):
            metric = Metric[metric]

        self.metric = metric
        return self

    def set_locations(self, locations=List[str]):
        self.targeting.data_origin.locations = locations
        return self

    def add_locations(self, location: str):
        if self.targeting.data_origin.locations is not None and not isinstance(
            self.targeting.data_origin.locations, Unset
        ):
            self.targeting.data_origin.locations.append(location)
        else:
            self.targeting.data_origin.locations = [location]
        return self

    def preview(self, start: datetime, end: datetime, include_failures=False):
        self._validate()

        if not isinstance(end, datetime):
            raise Exception(
                "Previews require an end time to be set. See builder.add_run_until()."
            )

        self.summarizer = Summarizer(
            UnivariateContinuous(
                self.aggregation, self.bin_mode, self.metric, self.bin_weights
            )
        )

        body = PreviewBody(
            self.baseline,
            preview_start=start,
            preview_end=end,
            scheduling=self.scheduling,
            summarizer=self.summarizer,
            targeting=self.targeting,
            window=unwrap(self.window),
        )
        ret = sync_detailed_preview(client=self.client.mlops(), body=body)

        if ret.parsed is None:
            raise Exception("An exception occurred while previewing assay", ret.content)

        arr = [
            PreviewResult(x, self)
            for x in ret.parsed
            if include_failures or len(x.summaries.additional_properties) > 0
        ]
        return PreviewResultList(arr, self)

    def _get_iopath(self):
        return f"{self.targeting.iopath[0].field}.{self.targeting.iopath[0].indexes[0]}"


class PreviewResult:
    def __init__(self, result: MLOpsPreviewResult, builder: AssayV2Builder):
        self.window_end = result.window_end
        self.scores = result.scores
        self.summaries = result.summaries
        self.builder = builder

    def to_df_row(self):
        summaries = {
            f"{k}.summary": v.to_dict()
            for k, v in self.summaries.additional_properties.items()
        }
        return {
            "window_end": self.window_end,
            **self.scores.additional_properties,
            **summaries,
        }

    def chart(self):
        """Quickly create a chart showing the bins, values and scores of an assay analysis.
        show_scores will also label each bin with its final weighted (if specified) score.
        """
        iopath = self.builder._get_iopath()
        bin_mode = self.builder.summarizer.univariate_continuous.bin_mode
        weighted = isinstance(
            self.builder.summarizer.univariate_continuous.bin_weights, List
        )
        if isinstance(bin_mode, BinModeType0):
            pass
        elif isinstance(bin_mode, BinModeType1):
            num_bins = bin_mode.equal
            bin_mode_str = "Equal"
        elif isinstance(bin_mode, BinModeType2):
            num_bins = bin_mode.quantile
            bin_mode_str = "Quantile"
        elif isinstance(bin_mode, BinModeType3):
            pass
        elif isinstance(bin_mode, BinModeType4):
            num_bins = len(bin_mode.provided)
            bin_mode_str = "Provided"
        agg = self.builder.summarizer.univariate_continuous.aggregation.value
        baseline_aggregated_values = self.builder.baseline.summary[
            iopath
        ].aggregated_values
        baseline_sample_size = self.builder.baseline.summary[iopath].statistics.count
        window_aggregated_values = self.summaries[iopath].aggregated_values
        window_sample_size = self.summaries[iopath].statistics.count
        end = self.window_end
        metric = self.builder.summarizer.univariate_continuous.metric.value
        score = self.scores[iopath]
        edge_names = self.builder.baseline.summary[iopath].bins.labels

        title = f"{num_bins} {bin_mode_str} {agg} {metric}={score:5.3f} Weighted={weighted} {end}"

        fig, ax = plt.subplots()

        if agg == Aggregation.EDGES:
            for n, v in enumerate(baseline_aggregated_values):
                plt.axvline(x=v, color="blue", alpha=0.5)
                plt.text(v, 0, f"e{n}", color="blue")
            for n, v in enumerate(window_aggregated_values):
                plt.axvline(x=v, color="orange", alpha=0.5)
                plt.text(v, 0.1, f"e{n}", color="orange")
        else:
            bar1 = plt.bar(
                edge_names,
                baseline_aggregated_values,
                alpha=0.50,
                label=f"Baseline ({baseline_sample_size})",
            )
            bar2 = plt.bar(
                edge_names,
                window_aggregated_values,
                alpha=0.50,
                label=f"Window ({window_sample_size})",
            )
            if len(edge_names) > 7:
                ax.set_xticklabels(labels=edge_names, rotation=45)

            for i, bar in enumerate(bar1.patches):
                ax.annotate(
                    f"{score:.4f}",
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center",
                    va="center",
                    size=9,
                    xytext=(0, 8),
                    textcoords="offset points",
                )
            plt.legend()
        ax.set_title(title)
        plt.xticks(rotation=45)
        plt.show()


class PreviewResultList(List[PreviewResult]):
    def __init__(self, arr: List[PreviewResult], parent_assay: AssayV2Builder):
        super().__init__(arr)
        self.parent_assay = parent_assay

    def to_dataframe(self):
        iopath = self.parent_assay._get_iopath()
        warning = self.parent_assay.targeting.iopath[0].thresholds.warning
        alert = self.parent_assay.targeting.iopath[0].thresholds.alert
        x = pd.DataFrame([x.to_df_row() for x in self]).assign(
            warning_threshold=warning,
            alert_threshold=alert,
        )
        x = x.join(pd.json_normalize(x[f"{iopath}.summary"]))
        # Repeated values as convenience for V1 compatibility/helper
        x["iopath"] = iopath
        x["workspace_id"] = self.parent_assay.targeting.data_origin.workspace_id

        x["status"] = x[iopath].map(
            lambda score: (
                "Alert"
                if alert != None and score >= alert
                else ("Warn" if warning and score >= warning else "Ok")
            )
        )
        x.insert(
            0, "pipeline_name", self.parent_assay.targeting.data_origin.pipeline_name
        )
        x.insert(0, "assay_name", self.parent_assay.name)
        x.insert(0, "assay_id", "Preview")

        return x

    def _color(self, edge=False):
        def _color_row(row: PreviewResult):
            field = self.parent_assay._get_iopath()
            val = row.scores.additional_properties[field]
            thresh = self.parent_assay.targeting.iopath[0].thresholds
            if thresh is None or isinstance(thresh, Unset):
                return "green" if isinstance(val, float) else "red"
            warning = thresh.warning
            alert = thresh.alert

            # If val errored out, always return red. Most important.
            if not isinstance(val, float):
                return "red" if edge else "white"
            # If no thresholds are configured, always return green.
            elif warning is None and alert is None:
                return "green"
            # If an alert is configured and we're above it, red.
            elif isinstance(alert, float) and val >= alert:
                return "red"
            # If a warning is configured and we're above it, orange.
            elif isinstance(warning, float) and val >= warning:
                return "orange"
            # We are not in error and not above a threshold, but they are configured.
            else:
                return "green"

        return [_color_row(x) for x in self]

    def chart_df(self, df: Union[pd.DataFrame, pd.Series], title: str):
        """Creates a basic chart of the scores from dataframe created from assay analysis list"""

        float_only_df = df[self.parent_assay._get_iopath()].map(
            lambda x: x if isinstance(x, float) else 0.0
        )
        plt.scatter(
            df.window_end,
            float_only_df,
            color=self._color(),
            edgecolor=self._color(edge=True),
            plotnonfinite=True,
        )
        plt.title(title)

        ax = plt.gca()
        ax.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(ax.xaxis.get_major_locator())
        )
        for label in ax.get_xticklabels(which="major", minor=True):
            label.set(rotation=30, horizontalalignment="right")

        plt.grid()
        plt.show()

    def chart_scores(self, title: Optional[str] = None):
        """Creates a basic chart of the scores from an AssayAnalysisList"""
        if title is None:
            title = f"Assays V2 Score"
        ardf = self.to_dataframe()
        if ardf.shape == (0, 0):
            raise ValueError("No data in this AssayAnalysisList.")

        self.chart_df(ardf, title)
