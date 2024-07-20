# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Main CLI
# :Created:   gio 21 apr 2016 18:18:46 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018, 2023 Lele Gaifax
#

from pathlib import Path
from traceback import print_exc
import sys

from ruamel.yaml import YAMLError, dump

from .action import Action
from .state import State


OK, SOFTWARE, USAGE, DATAERR, USERBREAK, CONFIG = 0, 1, 2, 3, 4, 128


def do_apply(args):
    "Execute one or more actions"

    try:
        state = State(args.verbose, args.dry_run, args.overwrite, args.config,
                      args.answers_file)
    except YAMLError as e:
        print("YAML error: %s" % e)
        return CONFIG

    for name in args.action:
        if name not in state.config.actions:
            print('Unrecognized action name: %s' % name)
            return DATAERR

    no_prompt = args.answers_file is not None
    state(prompt_only=args.prompt_only, no_prompt=no_prompt)
    for name in args.action:
        Action(state, name, state.config.actions[name])(prompt_only=args.prompt_only,
                                                        no_prompt=no_prompt)

    if args.prompt_only:
        if args.output_answers:
            with open(args.output_answers, 'w') as output:
                dump(state.answers, output, allow_unicode=True, default_flow_style=False)
        else:
            dump(state.answers, sys.stdout, allow_unicode=True, default_flow_style=False)

    return OK


def do_list(args):
    "List available actions"

    print("Available actions:")
    state = State(args.verbose, args.dry_run, args.overwrite, args.config)
    for name in state.config.actions:
        action = Action(state, name, state.config.actions[name])
        print('\n%s\n\t%s' % (name, action.description))
    return OK


def do_fold(args):
    "Fold the configuration into a self contained single YAML file"

    state = State(args.verbose, args.dry_run, args.overwrite, args.config)
    state.config.write(args.output)
    return OK


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    from importlib import metadata
    import locale

    locale.setlocale(locale.LC_ALL, '')

    version = metadata.version('metapensiero.tool.tinject')
    parser = ArgumentParser(description="Template injecter",
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help="emit traceback on error")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="emit some noise in the process")
    parser.add_argument('-n', '--dry-run', action='store_true', default=False,
                        help="test run, just show what would happed")
    parser.add_argument('-o', '--overwrite', action='store_true', default=False,
                        help="whether existing files shall be overwritten")

    subparsers = parser.add_subparsers()

    subp = subparsers.add_parser('apply', help=do_apply.__doc__)
    subp.add_argument('config', help="YAML configuration", type=Path)
    subp.add_argument('action', nargs='+', help="Action to be performed")
    subp.add_argument('-p', '--prompt-only', action='store_true', default=False,
                        help="just collect answers and print them back")
    subp.add_argument('-o', '--output-answers',
                      help="In prompt-only mode, put answers in a file,"
                      " instead of printing them to stdout", type=Path)
    subp.add_argument('-a', '--answers-file', help="Answers file", type=Path)
    subp.set_defaults(func=do_apply)

    subp = subparsers.add_parser('list', help=do_list.__doc__)
    subp.add_argument('config', help="YAML configuration", type=Path)
    subp.set_defaults(func=do_list)

    subp = subparsers.add_parser('fold', help=do_fold.__doc__)
    subp.add_argument('config', help="YAML configuration", type=Path)
    subp.add_argument('output', help="Output file name", type=Path)
    subp.set_defaults(func=do_fold)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        try:
            return args.func(args)
        except Exception as e:
            if args.debug:
                print_exc()
            else:
                print('Error (add --debug to get full traceback): %s' % e)
            return SOFTWARE
        except KeyboardInterrupt:
            return USERBREAK
    else:
        return OK


if __name__ == '__main__':
    sys.exit(main())
