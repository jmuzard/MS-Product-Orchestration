import argparse
from renderjinja2 import renderjinja2

parser = argparse.ArgumentParser(
    description="Generate configuration file from jinja2 template"
)
parser.add_argument('customer', help="customer name")
parser.add_argument('device', help="Device name")
args = parser.parse_args()

renderjinja2(args.customer, args.device, "day0-config")
