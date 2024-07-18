import json
from pathlib import Path
from typing import List

from helix_personmatching.logics.match_score import MatchScore
from helix_personmatching.matchers.matcher import Matcher
from helix_personmatching.models.constants import Attribute
from helix_personmatching.models.rules.RuleWeight import RuleWeight
from helix_personmatching.models.rules.attribute_rule import AttributeRule
from helix_personmatching.models.scoring_option import ScoringOption


def test_labcorp_match_rule_passed_in() -> None:
    print("")
    data_dir: Path = Path(__file__).parent.joinpath("./person_data")

    with open(data_dir.joinpath("bwell_master_person.json")) as file:
        bwell_master_person_json = file.read()

    with open(data_dir.joinpath("hapi_person_name_only.json")) as file:
        hapi_person_json = file.read()

    matcher = Matcher()

    scores: List[MatchScore] = matcher.match(
        source_json=hapi_person_json,
        target_json=bwell_master_person_json,
        only_matches=True,
        verbose=True,
        # pass rule configurations in, for limited demographics - for instance, for HAPI LabCorp
        only_use_passed_in_rules=True,
        options=[
            ScoringOption(
                rule_name="Foo",
                weight=RuleWeight(exact_match=1.0, partial_match=0.95, missing=0.75),
                rule=AttributeRule(
                    name="Foo",  # for Patient/Person name only. for instance, for HAPI LabCorp connection
                    description="first name, last name",
                    number=900,
                    attributes=[
                        Attribute.NAME_GIVEN,
                        Attribute.NAME_FAMILY,
                    ],
                    weight=RuleWeight.get_standard_weight(),
                ),
            ),
        ],
    )

    assert len(scores) == 1
    score = scores[0]

    print(f"\r\nscore.matched: {score.matched}")
    assert score.matched is True

    print(f"\r\nscore.total_score: {score.total_score}")
    assert score.total_score > 0.95

    scores_json = score.to_json(include_rule_scores=True)
    print(scores_json)

    with open(data_dir.joinpath("expected_scores.json")) as file:
        expected_scores = json.loads(file.read())

    assert json.loads(scores_json) == expected_scores
