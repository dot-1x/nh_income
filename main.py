import asyncio
import argparse
from dailyclaim import autoclaim, skip_income


parser = argparse.ArgumentParser("NH Income Tools")
parser.add_argument("--type", choices=["auto", "skip"], required=True)
parser.add_argument("--amount", required=False, type=int, default=1)


def main():
    namespaces = parser.parse_args()
    if namespaces.type == "auto":
        print("Running auto income")
        asyncio.run(autoclaim())
    elif namespaces.type == "skip":
        print("Running skip income")
        asyncio.run(skip_income(namespaces.amount))


if __name__ == "__main__":
    main()
