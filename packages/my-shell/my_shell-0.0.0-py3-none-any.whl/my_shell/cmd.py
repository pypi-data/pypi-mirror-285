import re
import sys
import os
from dataclasses import dataclass
import subprocess


CONFIG_PATH = os.path.join(os.getenv("HOME"), ".config/my-shell/config.cfg")
ALIASES_PATH = os.path.join(os.getenv("HOME"), ".config/my-shell/aliases")


@dataclass
class Alias:
    """
    alias: str - the alias pattern which is used to match the command that user
        has entered in the shell

    command: str - the command that will be executed if the alias pattern
        matches with placeholders that are to be substituted with the values
        from the command entered by the user
    """

    alias: str
    command: str


def matches(alias, pattern):
    if len(pattern) == 0:
        return not len(alias), dict()

    if len(alias) == 0:
        return pattern[0] == "*" and matches(alias, pattern[1:]), dict()

    if pattern[0] == "*":
        result, subs = matches(alias, pattern[1:])
        if result:
            return True, subs

        result, subs = matches(alias[1:], pattern)
        if result:
            return True, subs

        return False, dict()

    if len(alias) == 0:
        return False, dict()

    optional_token_regexp = re.compile(r"\?([a-zA-Z0-9]*)\?\[(.*)]")

    if optional_token_regexp.fullmatch(pattern[0]):
        key = optional_token_regexp.fullmatch(pattern[0]).group(1)
        regexp = re.compile(optional_token_regexp.fullmatch(pattern[0]).group(2))

        if regexp.fullmatch(alias[0]):
            result, subs = matches(alias[1:], pattern[1:])
            if result:
                subs[key] = alias[0]
                return True, subs
            else:
                return False, dict()

        return matches(alias, pattern[1:])

    mandatory_token_regexp = re.compile(r"([a-zA-Z0-9]*)\[(.*)\]")
    if mandatory_token_regexp.fullmatch(pattern[0]):
        key = mandatory_token_regexp.fullmatch(pattern[0]).group(1)
        regexp = re.compile(mandatory_token_regexp.fullmatch(pattern[0]).group(2))

        if regexp.fullmatch(alias[0]):
            result, subs = matches(alias[1:], pattern[1:])
            if result:
                subs[key] = alias[0]
                return True, subs

        return False, dict()


def susbstitute(command, subs):
    """
    FIXME: substitue is not the best name for that
    """
    tokens_after_substitution = []
    for token in command:
        if token[0].startswith("[") and token.endswith("]"):
            tokens_after_substitution.append(subs[token[1:-1]])
        else:
            tokens_after_substitution.append(token)
    return tokens_after_substitution


def read_aliases():
    with open(CONFIG_PATH, "r") as f:
        aliases = f.readlines()

    aliases = [x.split(";;") for x in aliases]
    aliases = [(x.split(), y.split()) for x, y in aliases]
    aliases = [Alias(alias, command) for alias, command in aliases]

    return aliases


def refresh_config():
    """
    FIXME: aliases_path is not the best name for that. In this context it describes
           a file that is supposed to be imported from .zshrc file and includes
           alliases for ms commands in that way, the user does not need to write
           `ms command` in the terminal all the time and can type just `command`
           instead
    """
    with open(ALIASES_PATH, "w") as f:
        for alias in read_aliases():
            alias = alias.alias
            print(alias)
            if len(alias) > 1 and alias[0].startswith("[") and alias[0].endswith("]"):
                f.write(f'alias {alias[0][1:-1]}="ms {alias[0][1:-1]}"\n')


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "refresh":
        refresh_config()
        return

    command = sys.argv[1:]
    aliases = read_aliases()
    for alias in aliases:
        result, subs = matches(command, alias.alias)
        if result:
            subprocess.run(susbstitute(alias.command, subs))
            break
    else:
        subprocess.run(command)


def decorate_with_dev_config():
    """
    Overwrites the config path for the development mode. In the development mode
    the config file is located in the `venv/bin/.config/my-shell/` directory
    where `venv` is the location of the active python virtual environment.
    """
    from pathlib import Path

    global CONFIG_PATH
    global ALIASES_PATH
    CONFIG_PATH = Path(sys.argv[0]).parent.absolute() / ".config/my-shell/config.cfg"
    ALIASES_PATH = Path(sys.argv[0]).parent.absolute() / ".config/my-shell/aliases"


def main_dev():
    decorate_with_dev_config()
    main()


if __name__ == "__main__":
    main()
