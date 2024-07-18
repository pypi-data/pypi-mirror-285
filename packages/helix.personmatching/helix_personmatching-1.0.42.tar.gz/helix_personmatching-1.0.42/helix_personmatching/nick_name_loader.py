from importlib.resources import files

from typing import Set, Dict, List

# noinspection PyProtectedMember
from nicknames import default_lookup, _lookup_from_lines


class NickNameLoader:
    @staticmethod
    def load_nick_names() -> Dict[str, Set[str]]:
        # Open the file using the new files() API
        with files(__package__).joinpath("nick_name_overrides.csv").open() as f:
            contents: str = f.read()
            lines: List[str] = contents.splitlines()
            lines2: List[List[str]] = [
                line.split(",") for line in lines if line.strip()
            ]
            nickname_overrides: Dict[str, Set[str]] = _lookup_from_lines(lines2)
            nickname_lookup: Dict[str, Set[str]] = default_lookup()
            # now add the overrides
            for key, value in nickname_overrides.items():
                if key in nickname_lookup:
                    nickname_lookup[key] = nickname_lookup[key] | value
                else:
                    nickname_lookup[key] = value
            return nickname_lookup
