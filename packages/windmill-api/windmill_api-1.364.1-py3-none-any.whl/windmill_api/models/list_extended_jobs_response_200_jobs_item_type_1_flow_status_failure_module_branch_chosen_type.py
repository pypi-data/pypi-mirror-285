from enum import Enum


class ListExtendedJobsResponse200JobsItemType1FlowStatusFailureModuleBranchChosenType(str, Enum):
    BRANCH = "branch"
    DEFAULT = "default"

    def __str__(self) -> str:
        return str(self.value)
