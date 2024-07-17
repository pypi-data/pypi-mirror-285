from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.series_summary_statistics import SeriesSummaryStatistics


T = TypeVar("T", bound="MinimalSummary")


@_attrs_define
class MinimalSummary:
    """A MinimalSummary is a stripped down version of the [`SeriesSummary`] that omits data that could be looked up from
    the [`crate::assays::univariate::baseline::Baseline`]

        Attributes:
            aggregated_values (List[float]): The output of aggregating data across bins.
            statistics (SeriesSummaryStatistics): Statistics that may be useful for advanced users but are not directly used
                in calculating assays.
    """

    aggregated_values: List[float]
    statistics: "SeriesSummaryStatistics"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        aggregated_values = self.aggregated_values

        statistics = self.statistics.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aggregated_values": aggregated_values,
                "statistics": statistics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.series_summary_statistics import SeriesSummaryStatistics

        d = src_dict.copy()
        aggregated_values = cast(List[float], d.pop("aggregated_values"))

        statistics = SeriesSummaryStatistics.from_dict(d.pop("statistics"))

        minimal_summary = cls(
            aggregated_values=aggregated_values,
            statistics=statistics,
        )

        minimal_summary.additional_properties = d
        return minimal_summary

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
