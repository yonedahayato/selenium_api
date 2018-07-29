import argparse
import sys

import log

logger = log.logger

class ArgumentParser_edit(argparse.ArgumentParser):
    def _get_action_from_name(self, name):
        """Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is
        passed as it's first arg...
        """

        container = self._action
        if name is None:
            return None

        for action in container:
            if "/".join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        super(ArgumentParser_edit, self).error(message)

class ArgParse:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
                    prog="monex_api",
                    usage="please read README",
                    description="I can not help you.",
                    epilog="end",
                    add_help=True
        )

        self.parser.add_argument("-at", "--argument_test", help="argument test", action="store_true")
        self.parser.add_argument("-d", "--debug", help="debug mode", action="store_true")
        self.parser.add_argument("ps_wd", help="pass word: [string]", action="store", type=str)
        self.parser.add_argument("Id", help="Id: [string]", action="store", type=str)
        self.parser.add_argument("BuySell", help="action: [string]", action="store", type=str, choices=["buy", "sell", "result", "buysell", "auto"])

    def parse_args(self):
        try:
             return self.parser.parse_args()
        except BaseException as e:
            print("error!!")
            logger.error("fail to read argument")
            logger.exception("fail to read argument")
            raise Exception(e)
        else:
            logger.info("success to read argument")

def main(ps_wd, Id, BuySell, debug):
    print("[main]: ps_wd:{}, Id:{}, BuySell:{}, debug:{}".format(ps_wd, Id, BuySell, debug))

if __name__ == "__main__":
    ap = ArgParse()
    args = ap.parse_args()

    if args.argument_test:
        print("argument_test is True")
    else:
        print("argument_test is False")

    if args.debug:
        print("debug mode")

    main(ps_wd=args.ps_wd, Id=args.Id, BuySell=args.BuySell, debug=args.debug)
# python args_parser.py -h
