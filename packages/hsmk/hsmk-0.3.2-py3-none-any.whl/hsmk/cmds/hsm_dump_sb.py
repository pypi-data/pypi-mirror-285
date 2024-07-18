import argparse

from chik_base.cbincode import from_bytes
from chik_base.core import SpendBundle

from hsmk.debug.debug_spend_bundle import debug_spend_bundle


def file_or_string(p) -> str:
    try:
        with open(p) as f:
            text = f.read().strip()
    except Exception:
        text = p
    return text


def hsmk_dump_sb(args, parser):
    blob = bytes.fromhex(file_or_string(args.spend_bundle))
    spend_bundle = from_bytes(SpendBundle, blob)
    validates = debug_spend_bundle(spend_bundle)
    assert validates is True


def create_parser():
    parser = argparse.ArgumentParser(description="Dump information about `SpendBundle`")
    parser.add_argument(
        "spend_bundle",
        metavar="hex-encoded-spend-bundle-or-file",
        help="hex-encoded `SpendBundle`",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    return hsmk_dump_sb(args, parser)


if __name__ == "__main__":
    main()
