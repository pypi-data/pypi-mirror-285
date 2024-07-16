import os, subprocess, json, getpass, typing
from pathlib import Path
from argparse import ArgumentParser, Namespace

####################################
exit()


def reverse_string(s: str):
    return s[::-1]


ENCODING = "utf-8"
KEY_API_KEY = reverse_string("_apI_kEy")
KEY_APP_ID = reverse_string("_aPp_iD")
KEY_NAME = reverse_string("_naME")
KEY_ADDED_ON = reverse_string("_AdDed@oN")

dir_path = Path(os.path.expanduser("~")) / "Documents"


####################################

import logging

logger = logging.getLogger("ReverieCLI")
logger.setLevel(logging.INFO)
log_file_handler = logging.FileHandler(dir_path / ".reverie-cli.logs")
log_file_handler.setFormatter(
    logging.Formatter(
        fmt="[%(asctime)s] | %(levelname)5s | %(message)s",
    )
)
logger.addHandler(log_file_handler)

####################################


def obscure_partial(s: str, len_right: int = 4):
    return "XXXXX" + s[-4:]


def get_parser() -> ArgumentParser:
    parser = ArgumentParser("reverie-sdk")

    parser_data = dict(
        subparsers=dict(
            configure=dict(
                help="Handle configurations",
                set_defaults=dict(command="print_help"),
                subparsers=dict(
                    add=dict(
                        help="Set a named configuration for APP-ID and API-KEY",
                        set_defaults=dict(
                            handler=handle_configure_new,
                        ),
                    ),
                    list=dict(
                        help="List all registered configurations",
                        args={
                            "--date": {
                                "type": bool,
                            }
                        },
                    ),
                ),
            )
        )
    )

    def _add_subparsers(_parser: ArgumentParser, _parser_data: typing.Dict):
        subparsers: typing.Dict = _parser_data.get("subparsers", {})
        if len(subparsers) > 0:
            help_ = _parser_data.get("help", None)
            subparser_action = _parser.add_subparsers(
                title="commands", dest="command", help=help_
            )
            for name, subparser_data in subparsers.items():
                help_ = subparser_data.get("help", None)
                subparser = subparser_action.add_parser(name, help=help_)
                _add_subparsers(subparser, subparser_data)

        set_defaults_ = _parser_data.get("set_defaults", {})
        _parser.set_defaults(**set_defaults_)

        return _parser

    _add_subparsers(parser, parser_data)

    return parser


def handle_configure_new(**kwargs):
    cred_map = {}

    try:
        config_fp = dir_path / ".reverie-cli.creds"

        if os.path.exists(config_fp) and os.stat(config_fp).st_size > 0:
            with open(config_fp, "rb") as f:
                creds: typing.List[typing.Dict[str, str]] = json.loads(
                    f.read().decode(ENCODING)
                )

            for c in creds:
                cred_map[(c[KEY_APP_ID], c[KEY_API_KEY])] = c[KEY_NAME]

        app_id = input("Enter APP-ID: ")
        api_key = getpass.getpass("Enter API-KEY: ")
        key = (app_id, api_key)

        if key in cred_map:
            logger.error(
                f"user entered app_id='{app_id}' and api_key='{api_key}'; "
                f"but cred exists with name='{cred_map[key]}"
            )
            print(f"The configuration exists with the name: '{cred_map[key]}'!")
            exit()

        name_attempt = 0
        while True:
            name = input("Enter a name for this configuration [default]: ")

            if len(name) == 0:
                name = "default"

            if name in cred_map.values():
                logger.error(
                    f"name attempt {name_attempt} failed; "
                    f"name exists; "
                    f"name entered: '{name}"
                )
                print(
                    f"Configuration name '{name}' is already assigned to another configuration!"
                )
                name_attempt += 1

                if name_attempt == 3:
                    print(
                        "Max attempts to name configuration exhausted! Please try again"
                    )
                    exit()

                continue

            break

        cred_map[key] = name

        with open(config_fp, "wb") as f:
            creds = [
                {
                    KEY_APP_ID: k[0],
                    KEY_API_KEY: k[1],
                    KEY_NAME: v,
                }
                for k, v in cred_map.items()
            ]
            s: str = json.dumps(creds, indent=4, ensure_ascii=False)
            f.write(s.encode(ENCODING))

        msg = f"Configuration '{name}' saved successfully!"
        logger.info(msg)
        print(msg)
    except KeyboardInterrupt:
        print("\b\nAborting!")
        exit()

    except Exception as e:
        print("Something went wrong!")
        print(e)


def main():
    parser = get_parser()
    args: Namespace = parser.parse_args()
    print(args)
    if args.command:
        kwargs = dict(args._get_kwargs())
        args.handler(**kwargs)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
