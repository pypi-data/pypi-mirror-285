from electronunitconverter import UnitConverter

from argparse import ArgumentParser

parser = ArgumentParser(description="CLI tool to convert units")
parser.add_argument("input", help="Input string to convert\n e.g. 'B=1.0 T' or 'T 5K'")

def main():
    args = parser.parse_args()
    converter = UnitConverter(args.input)
    print(converter.pprint())

if __name__ == "__main__":
    main()