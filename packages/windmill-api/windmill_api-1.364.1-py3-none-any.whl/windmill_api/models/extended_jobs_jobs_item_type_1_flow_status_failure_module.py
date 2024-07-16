from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.extended_jobs_jobs_item_type_1_flow_status_failure_module_type import (
    ExtendedJobsJobsItemType1FlowStatusFailureModuleType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.extended_jobs_jobs_item_type_1_flow_status_failure_module_approvers_item import (
        ExtendedJobsJobsItemType1FlowStatusFailureModuleApproversItem,
    )
    from ..models.extended_jobs_jobs_item_type_1_flow_status_failure_module_branch_chosen import (
        ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchChosen,
    )
    from ..models.extended_jobs_jobs_item_type_1_flow_status_failure_module_branchall import (
        ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchall,
    )
    from ..models.extended_jobs_jobs_item_type_1_flow_status_failure_module_iterator import (
        ExtendedJobsJobsItemType1FlowStatusFailureModuleIterator,
    )


T = TypeVar("T", bound="ExtendedJobsJobsItemType1FlowStatusFailureModule")


@_attrs_define
class ExtendedJobsJobsItemType1FlowStatusFailureModule:
    """
    Attributes:
        type (ExtendedJobsJobsItemType1FlowStatusFailureModuleType):
        id (Union[Unset, str]):
        job (Union[Unset, str]):
        count (Union[Unset, int]):
        iterator (Union[Unset, ExtendedJobsJobsItemType1FlowStatusFailureModuleIterator]):
        flow_jobs (Union[Unset, List[str]]):
        flow_jobs_success (Union[Unset, List[bool]]):
        branch_chosen (Union[Unset, ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchChosen]):
        branchall (Union[Unset, ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchall]):
        approvers (Union[Unset, List['ExtendedJobsJobsItemType1FlowStatusFailureModuleApproversItem']]):
        failed_retries (Union[Unset, List[str]]):
        parent_module (Union[Unset, str]):
    """

    type: ExtendedJobsJobsItemType1FlowStatusFailureModuleType
    id: Union[Unset, str] = UNSET
    job: Union[Unset, str] = UNSET
    count: Union[Unset, int] = UNSET
    iterator: Union[Unset, "ExtendedJobsJobsItemType1FlowStatusFailureModuleIterator"] = UNSET
    flow_jobs: Union[Unset, List[str]] = UNSET
    flow_jobs_success: Union[Unset, List[bool]] = UNSET
    branch_chosen: Union[Unset, "ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchChosen"] = UNSET
    branchall: Union[Unset, "ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchall"] = UNSET
    approvers: Union[Unset, List["ExtendedJobsJobsItemType1FlowStatusFailureModuleApproversItem"]] = UNSET
    failed_retries: Union[Unset, List[str]] = UNSET
    parent_module: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        id = self.id
        job = self.job
        count = self.count
        iterator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.iterator, Unset):
            iterator = self.iterator.to_dict()

        flow_jobs: Union[Unset, List[str]] = UNSET
        if not isinstance(self.flow_jobs, Unset):
            flow_jobs = self.flow_jobs

        flow_jobs_success: Union[Unset, List[bool]] = UNSET
        if not isinstance(self.flow_jobs_success, Unset):
            flow_jobs_success = self.flow_jobs_success

        branch_chosen: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.branch_chosen, Unset):
            branch_chosen = self.branch_chosen.to_dict()

        branchall: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.branchall, Unset):
            branchall = self.branchall.to_dict()

        approvers: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.approvers, Unset):
            approvers = []
            for approvers_item_data in self.approvers:
                approvers_item = approvers_item_data.to_dict()

                approvers.append(approvers_item)

        failed_retries: Union[Unset, List[str]] = UNSET
        if not isinstance(self.failed_retries, Unset):
            failed_retries = self.failed_retries

        parent_module = self.parent_module

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if job is not UNSET:
            field_dict["job"] = job
        if count is not UNSET:
            field_dict["count"] = count
        if iterator is not UNSET:
            field_dict["iterator"] = iterator
        if flow_jobs is not UNSET:
            field_dict["flow_jobs"] = flow_jobs
        if flow_jobs_success is not UNSET:
            field_dict["flow_jobs_success"] = flow_jobs_success
        if branch_chosen is not UNSET:
            field_dict["branch_chosen"] = branch_chosen
        if branchall is not UNSET:
            field_dict["branchall"] = branchall
        if approvers is not UNSET:
            field_dict["approvers"] = approvers
        if failed_retries is not UNSET:
            field_dict["failed_retries"] = failed_retries
        if parent_module is not UNSET:
            field_dict["parent_module"] = parent_module

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.extended_jobs_jobs_item_type_1_flow_status_failure_module_approvers_item import (
            ExtendedJobsJobsItemType1FlowStatusFailureModuleApproversItem,
        )
        from ..models.extended_jobs_jobs_item_type_1_flow_status_failure_module_branch_chosen import (
            ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchChosen,
        )
        from ..models.extended_jobs_jobs_item_type_1_flow_status_failure_module_branchall import (
            ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchall,
        )
        from ..models.extended_jobs_jobs_item_type_1_flow_status_failure_module_iterator import (
            ExtendedJobsJobsItemType1FlowStatusFailureModuleIterator,
        )

        d = src_dict.copy()
        type = ExtendedJobsJobsItemType1FlowStatusFailureModuleType(d.pop("type"))

        id = d.pop("id", UNSET)

        job = d.pop("job", UNSET)

        count = d.pop("count", UNSET)

        _iterator = d.pop("iterator", UNSET)
        iterator: Union[Unset, ExtendedJobsJobsItemType1FlowStatusFailureModuleIterator]
        if isinstance(_iterator, Unset):
            iterator = UNSET
        else:
            iterator = ExtendedJobsJobsItemType1FlowStatusFailureModuleIterator.from_dict(_iterator)

        flow_jobs = cast(List[str], d.pop("flow_jobs", UNSET))

        flow_jobs_success = cast(List[bool], d.pop("flow_jobs_success", UNSET))

        _branch_chosen = d.pop("branch_chosen", UNSET)
        branch_chosen: Union[Unset, ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchChosen]
        if isinstance(_branch_chosen, Unset):
            branch_chosen = UNSET
        else:
            branch_chosen = ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchChosen.from_dict(_branch_chosen)

        _branchall = d.pop("branchall", UNSET)
        branchall: Union[Unset, ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchall]
        if isinstance(_branchall, Unset):
            branchall = UNSET
        else:
            branchall = ExtendedJobsJobsItemType1FlowStatusFailureModuleBranchall.from_dict(_branchall)

        approvers = []
        _approvers = d.pop("approvers", UNSET)
        for approvers_item_data in _approvers or []:
            approvers_item = ExtendedJobsJobsItemType1FlowStatusFailureModuleApproversItem.from_dict(
                approvers_item_data
            )

            approvers.append(approvers_item)

        failed_retries = cast(List[str], d.pop("failed_retries", UNSET))

        parent_module = d.pop("parent_module", UNSET)

        extended_jobs_jobs_item_type_1_flow_status_failure_module = cls(
            type=type,
            id=id,
            job=job,
            count=count,
            iterator=iterator,
            flow_jobs=flow_jobs,
            flow_jobs_success=flow_jobs_success,
            branch_chosen=branch_chosen,
            branchall=branchall,
            approvers=approvers,
            failed_retries=failed_retries,
            parent_module=parent_module,
        )

        extended_jobs_jobs_item_type_1_flow_status_failure_module.additional_properties = d
        return extended_jobs_jobs_item_type_1_flow_status_failure_module

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
