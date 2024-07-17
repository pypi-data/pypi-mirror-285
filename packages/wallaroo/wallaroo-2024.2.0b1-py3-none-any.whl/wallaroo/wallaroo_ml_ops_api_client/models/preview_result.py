import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.preview_result_summaries import PreviewResultSummaries
    from ..models.scores import Scores


T = TypeVar("T", bound="PreviewResult")


@_attrs_define
class PreviewResult:
    """
    Attributes:
        scores (Scores):
        summaries (PreviewResultSummaries):
        window_end (datetime.datetime):
    """

    scores: "Scores"
    summaries: "PreviewResultSummaries"
    window_end: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        scores = self.scores.to_dict()

        summaries = self.summaries.to_dict()

        window_end = self.window_end.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "scores": scores,
                "summaries": summaries,
                "window_end": window_end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.preview_result_summaries import PreviewResultSummaries
        from ..models.scores import Scores

        d = src_dict.copy()
        scores = Scores.from_dict(d.pop("scores"))

        summaries = PreviewResultSummaries.from_dict(d.pop("summaries"))

        window_end = isoparse(d.pop("window_end"))

        preview_result = cls(
            scores=scores,
            summaries=summaries,
            window_end=window_end,
        )

        preview_result.additional_properties = d
        return preview_result

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
