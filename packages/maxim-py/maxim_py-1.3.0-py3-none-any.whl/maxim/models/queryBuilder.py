from dataclasses import dataclass
from typing import Dict, Literal, Union


class QueryRuleType(str):
    DeploymentVar = "deploymentVar"
    Tag = "tag"


@dataclass
class QueryRule():
    query: str
    operator: Literal["AND", "OR"]
    exactMatch: bool
    scopes: Dict[str, str]


class QueryBuilder:
    def __init__(self):
        self.query: str = ""
        self.scopes: Dict[str, str] = {}
        self.operator: Literal["AND", "OR"] = "AND"
        self.isExactMatch: bool = False

    def and_(self) -> 'QueryBuilder':
        self.operator = "AND"
        return self

    def or_(self) -> 'QueryBuilder':
        self.operator = "OR"
        return self

    def folder(self, folderId: str) -> 'QueryBuilder':
        self.scopes["folder"] = folderId
        return self

    def exactMatch(self) -> 'QueryBuilder':
        self.isExactMatch = True
        return self

    def deploymentVar(self, key: str, value: Union[str, int, bool], enforce: bool = True) -> 'QueryBuilder':
        if len(self.query)>0:
            self.query += ","
        self.query += f"{'!!' if enforce else ''}{key}={value}"
        return self

    def tag(self, key: str, value: Union[str, int, bool], enforce: bool = False) -> 'QueryBuilder':
        if len(self.query)>0:
            self.query += ","
        self.query += f"{'!!' if enforce else ''}{key}={value}"
        return self

    def build(self) -> QueryRule:
        if len(self.query.strip())==0:
            raise ValueError("Cannot build an empty query. Please add at least one rule (deploymentVar or tag).")
        return QueryRule(
            query=self.query,
            operator=self.operator,
            exactMatch=self.isExactMatch,
            scopes=self.scopes
        )