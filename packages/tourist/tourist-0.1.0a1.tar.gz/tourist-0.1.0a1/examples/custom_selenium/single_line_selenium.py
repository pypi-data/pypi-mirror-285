import sys
import json


def to_single_line(script: str, as_json: bool = True) -> str:
    single_line = repr(script)[1:-1]
    single_line = json.dumps(single_line) if as_json else single_line
    return single_line.replace('"', r"\"").replace("'", r"\"")


if __name__ == "__main__":
    with open(sys.argv[1], "r") as script:
        single_line = to_single_line(script.read(), False)
    print(single_line)
