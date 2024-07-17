from typing import List, Optional

from helix_personmatching.logics.rule_library import RuleLibrary
from helix_personmatching.models.rule import Rule
from helix_personmatching.models.scoring_option import ScoringOption


class RulesGenerator:
    @staticmethod
    def generate_rules(
        *,
        only_use_passed_in_rules: Optional[bool] = None,
        options: Optional[List[ScoringOption]] = None,
    ) -> List[Rule]:
        """
        generate default match rules


        :param only_use_passed_in_rules: if True, only use the rules passed in via the options parameter
        :param options: list of scoring options
        :return: generated rules for matching
        """

        rules: List[Rule] = RuleLibrary.get_standard_rules()

        # IF this is set to True,
        if only_use_passed_in_rules is not None and only_use_passed_in_rules is True:
            # disable all other normal rules first,
            for rule in list(filter(lambda r: r.number < 900, rules)):
                rule.enabled = False

        # then later enable only rules configured/set from the options parameters
        if options and len(options) > 0:
            for option in options:
                if option.rule is not None:
                    if option.weight is not None:
                        option.rule.weight = option.weight
                    rules.append(option.rule)
                elif option.rule_name is not None:
                    # first see if it matches a standard rule
                    matching_rules = [
                        rule for rule in rules if rule.name == option.rule_name
                    ]
                    matching_rule: Optional[Rule]
                    if len(matching_rules) > 0:
                        matching_rule = matching_rules[0]
                        # enable the found/matched rule in the configured options
                        matching_rule.enabled = True
                        if option.weight is not None:
                            matching_rule.weight = option.weight
                    else:  # find in optional rules
                        matching_rule = RuleLibrary.get_optional_rule_by_name(
                            option.rule_name
                        )
                        assert (
                            matching_rule is not None
                        ), f"No matching rule found for name: {option.rule_name}"
                        if option.weight is not None:
                            matching_rule.weight = option.weight
                        rules.append(matching_rule)

        return rules
