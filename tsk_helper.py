import sys


def get_fsstat_output(f):
    """
    Returns assignment-defined output (for unit tests) from `fsstat` output.


    :param f: open file-like object containing `fsstat` output
    :return: list of strings representing unit-testable output
    """
    result = []
    for line in f:
        result.append(line)
    return result


def strip_all(lines):
    """Returns a copy of the list of lines where all lines have been strip()ped."""
    return [line.strip() for line in lines]


if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        for line in get_fsstat_output(f):
            print(line)
