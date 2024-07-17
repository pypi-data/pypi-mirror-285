from pydantic import BaseModel
from typing import List, Optional

class Task(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    submissionId: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    duration: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    priority: Optional[str] = None
    escalationToL1Duration: Optional[str] = None
    escalationToL2Duration: Optional[str] = None
    escalationToL3Duration: Optional[str] = None
    activation: Optional[str] = None
    labels: Optional[List] = []
    progressPercent: Optional[int] = None
    assigneeUserIds: Optional[List] = []
    assigneeRoleIds: Optional[List] = []
    escalationL1UserIds: Optional[List] = []
    escalationL1RoleIds: Optional[List] = []
    escalationL2UserIds: Optional[List] = []
    escalationL2RoleIds: Optional[List] = []
    escalationL3UserIds: Optional[List] = []
    escalationL3RoleIds: Optional[List] = []
    onBehalfOf: Optional[int] = None
    workflowId: Optional[int] = None
    workflowTypeId: Optional[int] = None