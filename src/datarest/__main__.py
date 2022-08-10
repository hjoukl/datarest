import sys


def main():
    from . import cli
    return cli.cli()


if __name__ == '__main__':
    sys.exit(main())
