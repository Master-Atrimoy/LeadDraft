from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class RewriteVariant(BaseModel):
    label: str = Field(min_length=1)
    message: str = Field(min_length=1)


class RewriteResponse(BaseModel):
    subject_line: str = Field(default="")
    primary_message: str = Field(min_length=1)
    variants: List[RewriteVariant] = Field(default_factory=list)
    communication_goal: str = Field(min_length=1)
    editing_notes: List[str] = Field(default_factory=list)
