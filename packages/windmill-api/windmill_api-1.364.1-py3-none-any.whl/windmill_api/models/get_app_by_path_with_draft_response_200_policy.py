from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_app_by_path_with_draft_response_200_policy_execution_mode import (
    GetAppByPathWithDraftResponse200PolicyExecutionMode,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_app_by_path_with_draft_response_200_policy_triggerables import (
        GetAppByPathWithDraftResponse200PolicyTriggerables,
    )
    from ..models.get_app_by_path_with_draft_response_200_policy_triggerables_v2 import (
        GetAppByPathWithDraftResponse200PolicyTriggerablesV2,
    )


T = TypeVar("T", bound="GetAppByPathWithDraftResponse200Policy")


@_attrs_define
class GetAppByPathWithDraftResponse200Policy:
    """
    Attributes:
        triggerables (Union[Unset, GetAppByPathWithDraftResponse200PolicyTriggerables]):
        triggerables_v2 (Union[Unset, GetAppByPathWithDraftResponse200PolicyTriggerablesV2]):
        execution_mode (Union[Unset, GetAppByPathWithDraftResponse200PolicyExecutionMode]):
        on_behalf_of (Union[Unset, str]):
        on_behalf_of_email (Union[Unset, str]):
    """

    triggerables: Union[Unset, "GetAppByPathWithDraftResponse200PolicyTriggerables"] = UNSET
    triggerables_v2: Union[Unset, "GetAppByPathWithDraftResponse200PolicyTriggerablesV2"] = UNSET
    execution_mode: Union[Unset, GetAppByPathWithDraftResponse200PolicyExecutionMode] = UNSET
    on_behalf_of: Union[Unset, str] = UNSET
    on_behalf_of_email: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        triggerables: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.triggerables, Unset):
            triggerables = self.triggerables.to_dict()

        triggerables_v2: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.triggerables_v2, Unset):
            triggerables_v2 = self.triggerables_v2.to_dict()

        execution_mode: Union[Unset, str] = UNSET
        if not isinstance(self.execution_mode, Unset):
            execution_mode = self.execution_mode.value

        on_behalf_of = self.on_behalf_of
        on_behalf_of_email = self.on_behalf_of_email

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if triggerables is not UNSET:
            field_dict["triggerables"] = triggerables
        if triggerables_v2 is not UNSET:
            field_dict["triggerables_v2"] = triggerables_v2
        if execution_mode is not UNSET:
            field_dict["execution_mode"] = execution_mode
        if on_behalf_of is not UNSET:
            field_dict["on_behalf_of"] = on_behalf_of
        if on_behalf_of_email is not UNSET:
            field_dict["on_behalf_of_email"] = on_behalf_of_email

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_app_by_path_with_draft_response_200_policy_triggerables import (
            GetAppByPathWithDraftResponse200PolicyTriggerables,
        )
        from ..models.get_app_by_path_with_draft_response_200_policy_triggerables_v2 import (
            GetAppByPathWithDraftResponse200PolicyTriggerablesV2,
        )

        d = src_dict.copy()
        _triggerables = d.pop("triggerables", UNSET)
        triggerables: Union[Unset, GetAppByPathWithDraftResponse200PolicyTriggerables]
        if isinstance(_triggerables, Unset):
            triggerables = UNSET
        else:
            triggerables = GetAppByPathWithDraftResponse200PolicyTriggerables.from_dict(_triggerables)

        _triggerables_v2 = d.pop("triggerables_v2", UNSET)
        triggerables_v2: Union[Unset, GetAppByPathWithDraftResponse200PolicyTriggerablesV2]
        if isinstance(_triggerables_v2, Unset):
            triggerables_v2 = UNSET
        else:
            triggerables_v2 = GetAppByPathWithDraftResponse200PolicyTriggerablesV2.from_dict(_triggerables_v2)

        _execution_mode = d.pop("execution_mode", UNSET)
        execution_mode: Union[Unset, GetAppByPathWithDraftResponse200PolicyExecutionMode]
        if isinstance(_execution_mode, Unset):
            execution_mode = UNSET
        else:
            execution_mode = GetAppByPathWithDraftResponse200PolicyExecutionMode(_execution_mode)

        on_behalf_of = d.pop("on_behalf_of", UNSET)

        on_behalf_of_email = d.pop("on_behalf_of_email", UNSET)

        get_app_by_path_with_draft_response_200_policy = cls(
            triggerables=triggerables,
            triggerables_v2=triggerables_v2,
            execution_mode=execution_mode,
            on_behalf_of=on_behalf_of,
            on_behalf_of_email=on_behalf_of_email,
        )

        get_app_by_path_with_draft_response_200_policy.additional_properties = d
        return get_app_by_path_with_draft_response_200_policy

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
