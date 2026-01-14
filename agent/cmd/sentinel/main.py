from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ServerDispatch agent stub")
    parser.add_argument("--server-ip", required=True, help="Server IP address")
    parser.add_argument("--access-account", required=True, help="SSH access account")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        "ServerSentinel stub started for"
        f" {args.server_ip} with access account {args.access_account}."
    )


if __name__ == "__main__":
    main()
