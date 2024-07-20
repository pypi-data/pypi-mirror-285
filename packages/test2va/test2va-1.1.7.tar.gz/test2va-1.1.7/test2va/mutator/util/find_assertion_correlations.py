from typing import List, TypedDict

from ...parser.types.LibTypes import ParsedData, CriteriaData, NestedCriteria


class Correlation(TypedDict):
    event: int
    corresponding_criteria: CriteriaData


text_manipulation_actions = ["typeText", "replaceText"]


def traverse_criteria(criteria: List[CriteriaData | NestedCriteria], out: List[CriteriaData]):
    for c in criteria:
        if c["nested"]:
            nc: NestedCriteria = c
            traverse_criteria(nc["args"], out)
        else:
            out.append(c)


def get_inner_with_text_arg(wt: CriteriaData | NestedCriteria):
    if wt["nested"]:
        nc: NestedCriteria = wt
        return get_inner_with_text_arg(nc["args"][0])
    else:
        for arg in wt["args"]:
            if arg["type"] == "string":
                return wt["args"][0]["content"]
        return None


def find_correlations(data: ParsedData):
    assertions = data["assertion"]
    selectors = data["selectors"]

    correlation_map: List[Correlation | None] = [None] * len(assertions)

    for a in range(len(assertions)):
        assertion = assertions[a]
        assertion_criteria = []

        traverse_criteria(assertion["selector"]["criteria"], assertion_criteria)

        for a_criteria in assertion_criteria:
            for s in range(len(selectors)):
                selector = selectors[s]
                selector_criteria = []
                traverse_criteria(selector["criteria"], selector_criteria)

                # If one of the selectors has the same criteria name and an argument that matches exactly,
                # then there is a correspondence between the assertion and the selector.
                for s_criteria in selector_criteria:
                    if a_criteria["name"] == s_criteria["name"]:
                        for arg in s_criteria["args"]:
                            if arg in a_criteria["args"]:
                                correlation_map[a] = {"event": s, "corresponding_criteria": a_criteria}
                                break

        if correlation_map[a] is not None:
            continue

        # Next, we are going to take a look at the action. If the assertion action has the withText criteria, then
        # we should also check the selector's actions for a text manipulation action that may also match the
        # argument of the assertion's withText criteria.
        for a_criteria in assertion["selector"]["criteria"]:
            if not a_criteria["name"] == "withText":
                continue

            to_match = get_inner_with_text_arg(a_criteria)
            # print(to_match)

            if to_match is None:
                continue

            for s in range(len(selectors)):
                selector = selectors[s]
                if selector["action"]["action"] not in text_manipulation_actions:
                    continue

                for sa_arg in selector["action"]["args"]:
                    if sa_arg["content"] == to_match:
                        correlation_map[a] = {"event": s, "corresponding_criteria": a_criteria}
                        break

    return correlation_map
