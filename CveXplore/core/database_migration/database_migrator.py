import argparse
import logging
import os
import sys
from collections import namedtuple
from subprocess import run, PIPE, STDOUT, CompletedProcess

from CveXplore.core.logging.logger_class import AppLogger

logging.setLoggerClass(AppLogger)


class DatabaseMigrator(object):
    def __init__(self, cwd: str = None):
        self.logger = logging.getLogger(__name__)

        self.current_dir = (
            cwd
            if cwd is not None
            else os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            )
        )

        self._commands = namedtuple(
            "commands", "INIT REVISION UPGRADE CURRENT HISTORY REV_UP REV_DOWN"
        )(1, 2, 3, 4, 5, 6, 7)

    @property
    def commands(self) -> namedtuple:
        return self._commands

    def db_init(self) -> None:
        res = self.__cli_runner(self.commands.INIT)
        self.__parse_command_output(res)

    def db_revision(self, message: str) -> None:
        res = self.__cli_runner(self.commands.REVISION, message=message)
        self.__parse_command_output(res)

    def db_upgrade(self) -> None:
        res = self.__cli_runner(self.commands.UPGRADE)
        self.__parse_command_output(res)

    def db_current(self) -> None:
        res = self.__cli_runner(self.commands.CURRENT)
        self.__parse_command_output(res)

    def db_history(self) -> None:
        res = self.__cli_runner(self.commands.HISTORY)
        self.__parse_command_output(res)

    def db_up(self, count: int) -> None:
        res = self.__cli_runner(self.commands.REV_UP, message=count)
        self.__parse_command_output(res)

    def db_down(self, count: int) -> None:
        res = self.__cli_runner(self.commands.REV_DOWN, message=count)
        self.__parse_command_output(res)

    def __parse_command_output(self, cmd_output: CompletedProcess) -> None:
        if cmd_output.returncode != 0:
            self.logger.error(cmd_output.stdout)
        else:
            output_list = cmd_output.stdout.split("\n")

            for m in output_list:
                if m != "":
                    self.logger.info(m)

    def __cli_runner(self, command: int, message: str | int = None) -> CompletedProcess:
        if command == 2 and message is None:
            raise ValueError("Missing message for revision command")
        elif command == 6 and message is None:
            raise ValueError(
                "You must specify a positive number when submitting a upgrade command"
            )
        elif command == 7 and message is None:
            raise ValueError(
                "You must specify a negative number when submitting a downgrade command"
            )

        command_mapping = {
            1: f"alembic init alembic",
            2: f'alembic revision --autogenerate -m "{message}"',
            3: f"alembic upgrade head",
            4: f"alembic current",
            5: f"alembic history --verbose",
            6: f"alembic upgrade {message}",
            7: f"alembic downgrade {message}",
        }
        try:
            result = run(
                command_mapping[command],  # nosec
                stdout=PIPE,
                stderr=STDOUT,
                universal_newlines=True,
                shell=True,
                cwd=self.current_dir,
            )
            return result
        except KeyError:  # pragma: no cover
            self.logger.error(f"Unknown command number received....")

    def __repr__(self) -> str:
        return f"<< {self.__class__.__name__} >>"


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="migrate/update the database schema"
    )

    argparser.add_argument(
        "-i", action="store_true", help="Setup new alembic environment"
    )
    argparser.add_argument(
        "-r", action="store_true", help="Create new revision the database"
    )
    argparser.add_argument(
        "-u", action="store_true", help="Update the database to latest head"
    )

    argparser.add_argument(
        "-up", action="store_true", help="Upgrade the database x revisions"
    )
    argparser.add_argument(
        "-down", action="store_true", help="Downgrade the database x revisions"
    )

    argparser.add_argument("-cs", action="store_true", help="Print current state")
    argparser.add_argument("-hist", action="store_true", help="Print history")

    args = argparser.parse_args()

    fsm = DatabaseMigrator()

    if (args_count := len(sys.argv)) < 2 and args.r:
        print("You must specify a message when submitting a new revision")
        raise SystemExit(2)
    elif args_count < 2 and args.up:
        print("You must specify a positive number when submitting a upgrade command")
        raise SystemExit(2)
    elif args_count < 2 and args.down:
        print("You must specify a negative number when submitting a downgrade command")
        raise SystemExit(2)

    if args.i:
        fsm.db_init()

    if args.r:
        fsm.db_revision(sys.argv[1])

    if args.u:
        fsm.db_upgrade()

    if args.up:
        fsm.db_up(int(sys.argv[1]))

    if args.down:
        fsm.db_down(int(sys.argv[1]))

    if args.cs:
        fsm.db_current()

    if args.hist:
        fsm.db_history()
