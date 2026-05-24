"""Pydantic v2 models for the gshell-memory workspace.

This module is the canonical source of truth for the workspace schema.
The gshell-memory engine package re-exports from here to avoid duplication.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

HexFingerprint = Annotated[
    str,
    StringConstraints(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"),
]


EpisodeType = Literal[
    "decision",
    "failure",
    "milestone",
    "insight",
    "pitfall",
    "lesson",
    "bugfix",
    "setup",
    "integration",
    "refactor",
    "knowledge_digest",
    "discovery",
    "architecture",
    "deployment",
    "security",
    "agent_write",
    "maintenance",
]

DecayStatus = Literal["active", "fading", "archived"]

AssociationType = Literal[
    "supports",
    "contradicts",
    "elaborates",
    "references",
    "caused-by",
]

NodeKind = Literal["episode", "fact", "file", "skill"]


class NodeRef(BaseModel):
    kind: NodeKind
    id: str


class Quality(BaseModel):
    duplicate_suspect: bool = False
    exclusive: bool = True
    predictive: bool = False
    recurrence: int = 0
    score: float = 0.65


class RetrievalState(BaseModel):
    count: int = 0
    last_accessed: str | None = None
    strength: float = 0.7


class Links(BaseModel):
    facts: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)


class FactIdentity(BaseModel):
    name: str
    call_as: str
    language: str
    timezone: str
    last_updated: str


class FactPreferences(BaseModel):
    communication: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    forbidden_words: list[str] = Field(default_factory=list)


class FactDocument(BaseModel):
    schema_version: int = 1
    identity: FactIdentity
    preferences: FactPreferences
    rules: list[str] = Field(default_factory=list)
    tools: dict[str, dict] = Field(default_factory=dict)
    archive: dict = Field(default_factory=dict)


class EpisodicEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    ts: str
    type: EpisodeType
    title: str = Field(max_length=200)
    content: str
    tags: list[str]
    importance: int = Field(ge=1, le=10)
    source: str | None = None
    fingerprint: HexFingerprint
    links: Links | None = None
    decay_status: DecayStatus
    quality: Quality | None = None
    retrieval: RetrievalState | dict
    date: str | None = None
    linked_to: list[str] = Field(default_factory=list)


class ConsolidationTrigger(BaseModel):
    type: Literal["count", "calendar"] = "count"
    threshold: int = 20
    last_count: int = 0


class MemoryManifest(BaseModel):
    schema_version: int = 1
    last_consolidation: str | None = None
    last_decay_run: str | None = None
    last_audit_run: str | None = None
    last_health_run: str | None = None
    stats: dict = Field(default_factory=dict)
    next_consolidation_trigger: ConsolidationTrigger = Field(default_factory=ConsolidationTrigger)
    consolidation_history: list[dict] = Field(default_factory=list)
    quality_history: list[dict] = Field(default_factory=list)


class AssociationEntry(BaseModel):
    ts: str
    src: NodeRef
    dst: NodeRef
    type: AssociationType
    weight: float = Field(ge=0.0, le=1.0)
    evidence: str
    created_by: str


REQUIRED_REGIONS: frozenset[str] = frozenset(
    {
        "hippocampus",
        "prefrontal",
        "limbic",
        "cerebellum",
        "default",
    }
)


class RegionFile(BaseModel):
    path: str


class RegionDef(BaseModel):
    display: str
    core_files: list[RegionFile]
    on_demand_files: list[RegionFile]


class BrainRegionManifest(BaseModel):
    schema_version: int = 1
    generated_at: str
    regions: dict[str, RegionDef]

    @field_validator("regions")
    @classmethod
    def _exactly_five_fixed_regions(cls, v: dict[str, RegionDef]) -> dict[str, RegionDef]:
        if set(v.keys()) != REQUIRED_REGIONS:
            raise ValueError(
                f"brain_region_manifest must have exactly these regions: {sorted(REQUIRED_REGIONS)}"
            )
        return v


SanctumTier = Literal["public", "private", "sacred"]
SanctumAction = Literal["read", "write", "delete"]


class SanctumEntry(BaseModel):
    path: str
    tier: SanctumTier
    reason: str
    enforced_actions: list[SanctumAction]


class SanctumRegistry(BaseModel):
    schema_version: int = 1
    entries: list[SanctumEntry] = Field(default_factory=list)


class ExecutorProfile(BaseModel):
    label: str
    binary: str
    args: list[str]
    timeout: int = 600
    output_mode: Literal["text", "json"] = "text"
    max_turns: int = 10


class RuntimeProfile(BaseModel):
    label: str
    source: str
    tags: list[str]


class LauncherProfile(BaseModel):
    label: str
    binary: str
    args: list[str]
    runtime: str
    executor: str


class RuntimeProfiles(BaseModel):
    version: str = "1.0"
    default_executor: str
    default_runtime: str
    default_launcher: str
    executors: dict[str, ExecutorProfile]
    runtimes: dict[str, RuntimeProfile]
    launchers: dict[str, LauncherProfile]


# Canonical aliases for the spec's planned naming. The current v5 codebase uses
# the legacy class names (FactDocument, AssociationEntry); the M6 plan promotes
# Workspace / FactStore / Association as the public-facing identifiers. Until
# the engine code is renamed end-to-end, expose both.
Workspace = FactDocument
FactStore = FactDocument
Association = AssociationEntry


class SOPRoute(BaseModel):
    """A standard-operating-procedure routing entry.

    When the agent detects any string in `triggers` in the user's request,
    it must read every file in `must_read` before proceeding, optionally
    pulls `also_read` later, and may chain `skills_pipeline` for execution.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    triggers: list[str] = Field(min_length=1)
    must_read: list[str] = Field(min_length=1)
    also_read: list[str] = Field(default_factory=list)
    skills_pipeline: list[str] = Field(default_factory=list)
    note: str | None = None
    inline_sop: str | None = None
