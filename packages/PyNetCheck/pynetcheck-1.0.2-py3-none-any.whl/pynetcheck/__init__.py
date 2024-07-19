import os
import sys

import pytest


def main():
    pytest.main(
        args=[
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"),
            *sys.argv[1:],
        ]
    )


if __name__ == "__main__":
    main()
