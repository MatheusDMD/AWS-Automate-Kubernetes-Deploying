import argparse
from json import dumps, load
import requests
import pprint

op_list=[
  "ceil",
  "copysign",
  "fabs",
  "factorial",
  "floor",
  "fmod",
  "frexp",
  "isinf",
  "isnan",
  "ldexp",
  "modf",
  "trunc",
  "exp",
  "expm1",
  "log",
  "log1p",
  "log10",
  "pow",
  "sqrt",
  "acos",
  "asin",
  "atan",
  "atan2",
  "cos",
  "hypot",
  "sin",
  "tan",
  "degrees",
  "radians",
  "acosh",
  "asinh",
  "atanh",
  "cosh",
  "sinh",
  "tanh",
  "erf",
  "erfc",
  "gamma",
  "lgamma",
  "pi",
  "e"
]

two_args = [
    "ldexp",
    "copysign",
    "fmod",
    "ldexp",
    "log",
    "pow",
    "atan2",
    "hypot"
]

zero_args = [
    "pi",
    "e"
]
def calculate(args):
    print()
    # Error cases
    if not args.a and args.operation not in zero_args:
        if args.operation in two_args:
            print("{0} requires 2 arguments and 0 given".format(args.operation))
        else:
            print("{0} requires 1 arguments and 0 given".format(args.operation))
    elif args and args.operation in zero_args:
        print("{0} takes no arguments".format(args.operation))
    elif not args.b and args.operation in two_args:
        print("{0} takes 2 arguments and only 1 given".format(args.operation))
    elif args.b and args.operation not in two_args:
        print("{0} takes 1 argument and 2 given".format(args.operation))
    # Success cases
    else:
        number_of_params = 0
        if args.a:
            number_of_params += 1
        else:
            args.a = 0
        if args.b:
            number_of_params += 1
        else:
            args.b = 0
        data = {"operation": args.operation, "a": args.a, "b":args.b, "params": number_of_params}
        r = requests.post(url = "http://" + args.domain + "/calculate", data = data)
        print(r.text)
    print()

    


parser = argparse.ArgumentParser(description='Client for myCluster')

parser.add_argument('operation',choices=op_list, help='Python Math Operation to be executed')

parser.add_argument('a', help='first argument', type=float, nargs='?')

parser.add_argument('b', help='second argument', type=float, nargs='?')

parser.add_argument('--domain', help='Domain for client request', required=True)

args = parser.parse_args()
calculate(args)