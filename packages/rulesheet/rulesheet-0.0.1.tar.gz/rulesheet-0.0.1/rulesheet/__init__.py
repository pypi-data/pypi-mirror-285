import csv
import re


class Ruler:
    def __init__(self, rules):
        self.rules = rules

    def test(self, obj, debug=False):
        for [key, method, expected] in self.rules:
            objkey = find_key(obj, key)

            if objkey is None:
                continue

            expected_cleaned = expected.lower().strip()
            value = str(obj[objkey]).strip()
            value_cleaned = value.lower()
            method_cleaned = method.lower().strip()
            if method_cleaned in [
                "starts with",
                "startswith",
                "begins with",
                "beginswith",
            ]:
                if value_cleaned.startswith(expected_cleaned):
                    if debug:
                        print(
                            f'[rulesheet] "{objkey}" of normalized value "{value_cleaned}" starts with "{expected_cleaned}"'
                        )
                    return True
            elif method_cleaned in ["ends with", "endswith"]:
                if value_cleaned.endswith(expected_cleaned):
                    return True
            elif method_cleaned in ["is", "equals"]:
                if value_cleaned == expected_cleaned:
                    return True
            elif method_cleaned in ["includes", "contains"]:
                if expected_cleaned in value_cleaned:
                    return True
            elif method_cleaned in ["in range", "inrange", "between"]:
                start, end = expected_cleaned.strip().split("...")
                start = float(start.lower().strip())
                end = float(end.lower().strip())
                value_float = float(value_cleaned)
                if start <= value_float <= end:
                    if debug:
                        print(
                            f'[rulesheet] "{objkey}" of normalized value "{value_cleaned}" in range "{expected_cleaned}"'
                        )
                    return True
            elif method_cleaned in ["matches"]:
                pattern = re.compile(expected)
                match = pattern.match(value)
                if match:
                    return True

        # no rules matched so returning false
        return False


def find_key(obj, target):
    target = target.lower().replace(" ", "").replace("_", "").replace("-", "")
    for key in obj.keys():
        if key.lower().replace(" ", "").replace("_", "").replace("-", "") == target:
            return key


def load_ruler_from_csv(filepath):
    with open(filepath) as f:
        reader = csv.reader(f)
        next(reader)  # skip first line header
        rules = []
        for line in reader:
            key, method, expected, *rest = line
            rules.append([key, method, expected])

    ruler = Ruler(rules)

    return ruler
