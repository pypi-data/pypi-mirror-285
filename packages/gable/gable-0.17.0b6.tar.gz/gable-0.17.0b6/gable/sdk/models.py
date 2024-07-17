from datetime import datetime
from typing import List, Optional
from uuid import UUID

from gable.openapi import ContractSpec, EnforcementLevel, Status
from pydantic import BaseModel


class GitMetadata(BaseModel):
    gitHash: str
    gitRepo: str
    gitUser: str
    mergedAt: datetime
    filePath: str
    reviewers: List[str]


class ExternalContractInput(BaseModel):
    version: Optional[str]
    status: Status
    enforcementLevel: Optional[EnforcementLevel]
    contractSpec: ContractSpec
    gitMetadata: Optional[GitMetadata]


class ContractPublishResponse(BaseModel):
    id: UUID
    message: Optional[str]
    success: bool
