"""CLI entry point: ``python -m fantasy_sidekick``."""

from __future__ import annotations

import argparse
import sys

from fantasy_sidekick import __version__
from fantasy_sidekick.config import Settings
from fantasy_sidekick.db.session import session_scope
from fantasy_sidekick.sms.client import TwilioSmsClient
from fantasy_sidekick.sync.league import sync_league
from fantasy_sidekick.sync.players import sync_players


def _cmd_version(_: argparse.Namespace) -> int:
    settings = Settings.from_env()
    print(f"fantasy-sidekick {__version__} ({settings.app_env})")
    return 0


def _cmd_sync_league(args: argparse.Namespace) -> int:
    with session_scope() as session:
        result = sync_league(session, args.league_id)
    print(
        f"Synced league {result.league_id}: "
        f"{result.users_upserted} users, "
        f"{result.league_users_upserted} league_users, "
        f"{result.rosters_upserted} rosters"
    )
    return 0


def _cmd_sync_players(args: argparse.Namespace) -> int:
    with session_scope() as session:
        result = sync_players(session, sport=args.sport)
    print(f"Synced {result.players_upserted} players ({result.sport})")
    return 0


def _cmd_send_sms(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    try:
        account_sid, auth_token, from_number = settings.require_twilio()
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    client = TwilioSmsClient(account_sid, auth_token, from_number)
    try:
        sid = client.send(to=args.to, body=args.message)
    except Exception as exc:
        print(f"Error sending SMS: {exc}", file=sys.stderr)
        return 1

    print(f"Sent SMS; Twilio SID: {sid}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fantasy-sidekick",
        description="SMS coach for fantasy football beginners (backend-only).",
    )
    parser.set_defaults(func=_cmd_version)
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("version", help="Print version and environment")

    league_parser = sub.add_parser(
        "sync-league",
        help="Fetch a Sleeper league and upsert leagues/users/rosters",
    )
    league_parser.add_argument(
        "--league-id",
        required=True,
        help="Sleeper league id (e.g. 1392647678189395968)",
    )
    league_parser.set_defaults(func=_cmd_sync_league)

    players_parser = sub.add_parser(
        "sync-players",
        help="Fetch the Sleeper players catalog and upsert into players",
    )
    players_parser.add_argument(
        "--sport",
        default="nfl",
        help="Sport slug for /players/{sport} (default: nfl)",
    )
    players_parser.set_defaults(func=_cmd_sync_players)

    sms_parser = sub.add_parser(
        "send-sms",
        help="Send one plain-text SMS via Twilio (temporary test command)",
    )
    sms_parser.add_argument(
        "--to",
        required=True,
        help="Destination phone number in E.164 format (e.g. +15551234567)",
    )
    sms_parser.add_argument(
        "--message",
        required=True,
        help="Plain-text SMS body (GSM-7 friendly; no media)",
    )
    sms_parser.set_defaults(func=_cmd_send_sms)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main(sys.argv[1:])
