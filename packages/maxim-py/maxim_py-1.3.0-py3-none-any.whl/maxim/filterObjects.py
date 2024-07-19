from typing import List, Optional

from .models.prompt import RuleGroupType, RuleType


class IncomingQuery():
    def __init__(self, query: str, operator: str, exactMatch: bool):
        self.query = query
        self.operator = operator
        self.exactMatch = exactMatch


class QueryObject():
    def __init__(self, id: str, query: RuleGroupType):
        self.id = id
        self.query = query


def parseIncomingQuery(incomingQuery: str) -> List[RuleType]:
    if not incomingQuery.strip():
        return []
    operators = ["!=", ">=", "<=", ">", "<",
                 "includes", "does not include", "="]
    result = []
    for condition in incomingQuery.split(","):
        noOperatorFound = False
        for op in operators:
            if op in condition:
                no_operator_found = True
                field, value = map(str.strip, condition.split(op))
                exactMatch = False
                if field.startswith("!!"):
                    exactMatch = True
                    field = field[2:]
                # converting 'True'/'False':str to True/False:bool
                if value == 'True' or value == 'False':
                    value = bool(value)
                try:
                    value = int(value)
                except ValueError:
                    pass
                result.append(RuleType(field=field, value=value,
                              operator=op, exactMatch=exactMatch))
        if noOperatorFound:
            raise ValueError(
                f"Unsupported operator found in condition \"{condition}\"")
    return result


def evaluateRuleGroup(ruleGroup: RuleGroupType, incomingQueryRules: List[RuleType]) -> bool:
    matchedRules = []
    matchResults = []
    for rule in ruleGroup.rules:
        if isinstance(rule, RuleGroupType):
            matchResults.append(evaluateRuleGroup(rule, incomingQueryRules))
        else:
            match = False
            for incomingRule in incomingQueryRules:
                if rule.field == incomingRule.field and conditionMet(rule, incomingRule):
                    match = match or True
                    matchedRules.append(incomingRule)
            matchResults.append(match)
            if match:
                matchedRules.append(rule)
    exactMatches = all(
        rule.exactMatch == False or rule in matchedRules for rule in incomingQueryRules)
    if not exactMatches:
        return False
    if ruleGroup.combinator == "AND":
        return all(matchResults)
    else:
        return any(matchResults)

# Had to write this extensive logic in python since type support in python isn't as extensive as typescript


def checkOperatorMatch(fieldRule: RuleType, fieldIncomingRule: RuleType) -> bool:
    operator = fieldRule.operator

    if operator == "=":
        return fieldRule.value == fieldIncomingRule.value

    elif operator == "!=":
        return fieldRule.value != fieldIncomingRule.value

    elif operator == ">":
        if isinstance(fieldRule.value, int) and isinstance(fieldIncomingRule.value, int):
            return fieldRule.value > fieldIncomingRule.value
        elif isinstance(fieldRule.value, str) and isinstance(fieldIncomingRule.value, str):
            return fieldRule.value > fieldIncomingRule.value
        raise ValueError(
            f"Cannot operate {operator} on types {fieldRule} and {fieldIncomingRule}")

    elif operator == "<":
        if isinstance(fieldRule.value, int) and isinstance(fieldIncomingRule.value, int):
            return fieldRule.value < fieldIncomingRule.value
        elif isinstance(fieldRule.value, str) and isinstance(fieldIncomingRule.value, str):
            return fieldRule.value < fieldIncomingRule.value
        raise ValueError(
            f"Cannot operate {operator} on types {fieldRule} and {fieldIncomingRule}")

    elif operator == ">=":
        if isinstance(fieldRule.value, int) and isinstance(fieldIncomingRule.value, int):
            return fieldRule.value >= fieldIncomingRule.value
        elif isinstance(fieldRule.value, str) and isinstance(fieldIncomingRule.value, str):
            return fieldRule.value >= fieldIncomingRule.value

        raise ValueError(
            f"Cannot operate {operator} on types {fieldRule} and {fieldIncomingRule}")

    elif operator == "<=":
        if isinstance(fieldRule.value, int) and isinstance(fieldIncomingRule.value, int):
            return fieldRule.value <= fieldIncomingRule.value
        elif isinstance(fieldRule.value, str) and isinstance(fieldIncomingRule.value, str):
            return fieldRule.value <= fieldIncomingRule.value

        raise ValueError(
            f"Cannot operate {operator} on types {fieldRule} and {fieldIncomingRule}")

    elif operator == "includes":
        if isinstance(fieldRule.value, str) and isinstance(fieldIncomingRule.value, str):
            return fieldIncomingRule.value in fieldRule.value
        elif isinstance(fieldRule.value, list) and isinstance(fieldIncomingRule.value, list):
            return fieldIncomingRule.value in fieldRule.value
        elif isinstance(fieldRule.value, list) and isinstance(fieldIncomingRule.value, str):
            return fieldIncomingRule.value in fieldRule.value
        elif isinstance(fieldRule.value, str) and isinstance(fieldIncomingRule.value, list):
            return fieldRule.value in fieldIncomingRule.value
        raise ValueError(
            f"Cannot operate {operator} on types {fieldRule} and {fieldIncomingRule}")

    elif operator == "does not include":
        if isinstance(fieldRule.value, str) and isinstance(fieldIncomingRule.value, str):
            return fieldIncomingRule.value not in fieldRule.value
        elif isinstance(fieldRule.value, list) and isinstance(fieldIncomingRule.value, list):
            return fieldIncomingRule.value not in fieldRule.value
        elif isinstance(fieldRule.value, list) and isinstance(fieldIncomingRule.value, str):
            return fieldIncomingRule.value not in fieldRule.value
        elif isinstance(fieldRule.value, str) and isinstance(fieldIncomingRule.value, list):
            return fieldRule.value not in fieldIncomingRule.value
        raise ValueError(
            f"Cannot operate {operator} on types {fieldRule} and {fieldIncomingRule}")

    else:
        return False


def conditionMet(fieldRule: RuleType, fieldIncomingRule: RuleType) -> bool:
    if type(fieldRule.value) != type(fieldIncomingRule.value):
        if isinstance(fieldRule.value, int):
            if isinstance(fieldIncomingRule.value, int) or isinstance(fieldIncomingRule.value, bool):
                fieldIncomingRule.value = int(fieldIncomingRule.value)

        # revisit : possible error : everything will be true with bool(fieldIncomingRule.value)
        elif isinstance(fieldRule.value, bool):
            fieldIncomingRule.value = bool(fieldIncomingRule.value)
        elif isinstance(fieldRule.value, str):
            fieldIncomingRule.value = str(fieldIncomingRule.value)

    match = checkOperatorMatch(fieldRule, fieldIncomingRule)
    return match


def findBestMatch(objects: List[QueryObject], incomingQuery: IncomingQuery) -> Optional[QueryObject]:
    bestMatch = None
    maxMatchCount = 0
    incomingQueryRules = parseIncomingQuery(incomingQuery.query)
    for obj in objects:
        if evaluateRuleGroup(obj.query, incomingQueryRules):
            if incomingQuery.exactMatch and len(incomingQueryRules) != len(obj.query.rules):
                continue
            matchCount = len(obj.query.rules)
            if matchCount > maxMatchCount:
                maxMatchCount = matchCount
                bestMatch = obj
    return bestMatch


def findAllMatches(objects: List[QueryObject], incomingQuery: IncomingQuery) -> List[QueryObject]:
    matches: List[QueryObject] = []
    incomingQueryRules = parseIncomingQuery(incomingQuery.query)
    for object in objects:
        if evaluateRuleGroup(object.query, incomingQueryRules):
            if incomingQuery.exactMatch and len(incomingQueryRules) != len(object.query.rules):
                continue
            matches.append(object)
    return matches
