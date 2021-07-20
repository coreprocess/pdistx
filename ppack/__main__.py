import argparse


def main():
    parser = argparse.ArgumentParser(prog='ppack')

    parser.add_argument(
        '-r',
        dest='resources',
        metavar='resources',
        action='store_true',
        help='create a resources folder with all non-python files (it will be named <target>_resources)',
    )

    parser.add_argument(
        '-z',
        dest='zip',
        metavar='zip',
        action='store_true',
        help='provide target as zip file',
    )

    parser.add_argument(
        'source',
        help='source folder',
    )

    parser.add_argument(
        'target',
        help='target python or zip file (will be cleared)',
    )

    args = parser.parse_args()

    ...


if __name__ == '__main__':
    main()
