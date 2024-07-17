import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.arbex_status import ArbexStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_tagged_summaries import FieldTaggedSummaries
    from ..models.scores import Scores


T = TypeVar("T", bound="AssayResultV2")


@_attrs_define
class AssayResultV2:
    """
    Attributes:
        assay_id (str):
        created_at (datetime.datetime):
        status (ArbexStatus):
        updated_at (datetime.datetime):
        window_end (datetime.datetime):
        window_start (datetime.datetime):
        workspace_id (int):
        scores (Union['Scores', None, Unset]):
        summaries (Union['FieldTaggedSummaries', None, Unset]):
    """

    assay_id: str
    created_at: datetime.datetime
    status: ArbexStatus
    updated_at: datetime.datetime
    window_end: datetime.datetime
    window_start: datetime.datetime
    workspace_id: int
    scores: Union["Scores", None, Unset] = UNSET
    summaries: Union["FieldTaggedSummaries", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.field_tagged_summaries import FieldTaggedSummaries
        from ..models.scores import Scores

        assay_id = self.assay_id

        created_at = self.created_at.isoformat()

        status = self.status.value

        updated_at = self.updated_at.isoformat()

        window_end = self.window_end.isoformat()

        window_start = self.window_start.isoformat()

        workspace_id = self.workspace_id

        scores: Union[Dict[str, Any], None, Unset]
        if isinstance(self.scores, Unset):
            scores = UNSET
        elif isinstance(self.scores, Scores):
            scores = self.scores.to_dict()
        else:
            scores = self.scores

        summaries: Union[Dict[str, Any], None, Unset]
        if isinstance(self.summaries, Unset):
            summaries = UNSET
        elif isinstance(self.summaries, FieldTaggedSummaries):
            summaries = self.summaries.to_dict()
        else:
            summaries = self.summaries

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assay_id": assay_id,
                "created_at": created_at,
                "status": status,
                "updated_at": updated_at,
                "window_end": window_end,
                "window_start": window_start,
                "workspace_id": workspace_id,
            }
        )
        if scores is not UNSET:
            field_dict["scores"] = scores
        if summaries is not UNSET:
            field_dict["summaries"] = summaries

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.field_tagged_summaries import FieldTaggedSummaries
        from ..models.scores import Scores

        d = src_dict.copy()
        assay_id = d.pop("assay_id")

        created_at = isoparse(d.pop("created_at"))

        status = ArbexStatus(d.pop("status"))

        updated_at = isoparse(d.pop("updated_at"))

        window_end = isoparse(d.pop("window_end"))

        window_start = isoparse(d.pop("window_start"))

        workspace_id = d.pop("workspace_id")

        def _parse_scores(data: object) -> Union["Scores", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scores_type_1 = Scores.from_dict(data)

                return scores_type_1
            except:  # noqa: E722
                pass
            return cast(Union["Scores", None, Unset], data)

        scores = _parse_scores(d.pop("scores", UNSET))

        def _parse_summaries(
            data: object,
        ) -> Union["FieldTaggedSummaries", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                summaries_type_1 = FieldTaggedSummaries.from_dict(data)

                return summaries_type_1
            except:  # noqa: E722
                pass
            return cast(Union["FieldTaggedSummaries", None, Unset], data)

        summaries = _parse_summaries(d.pop("summaries", UNSET))

        assay_result_v2 = cls(
            assay_id=assay_id,
            created_at=created_at,
            status=status,
            updated_at=updated_at,
            window_end=window_end,
            window_start=window_start,
            workspace_id=workspace_id,
            scores=scores,
            summaries=summaries,
        )

        assay_result_v2.additional_properties = d
        return assay_result_v2

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
