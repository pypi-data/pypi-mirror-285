"""GH-Issue-exporter CLI"""

import argparse
from .exporter import run_export
from .importer import run_import

def run():
    """CLI for GH Issue Exporter - the easy issue exporter for Github"""
    parser = argparse.ArgumentParser(
        description=(
            "GH Issue Exporter can e used to export issues from Github,"
            " great for backups."
        )
    )

    # General flags
    parser.add_argument(
        '-c', '--ignore-closed',
        help="Don't import/export closed issues",
        action='store_true'
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Show more info, useful for debugging",
        action='store_true'
    )

    # Add subparsers for actions
    subparsers = parser.add_subparsers(
        dest='action', required=True, help='Action to perform'
    )

    # Subparser for the 'import' action
    parser_import = subparsers.add_parser(
        'import', help='Import issues from file to repository'
    )
    parser_import.add_argument(
        'repo', type=str,
        help=('URL or identifier for a Github repository, on form: '
              'https://github.com/<owner>/<repo>')
    )
    parser_import.add_argument(
        'issues_file', type=str,
        help=('Path to json/yml file with issues to import')
    )
    parser_import.add_argument(
        'token', type=str,
        help=('GH token (generate at https://github.com/settings/tokens)')
    )
    parser_import.add_argument(
        '-d', '--delete_issues',
        help=('Delete issues from repository if the issues are not'
              'present in the local issues file.'),
        action='store_true'
    )

    # Subparser for the 'export' action
    parser_export = subparsers.add_parser(
        'export', help='Run Github Issue exporter on a repository'
    )
    parser_export.add_argument(
        'repo', type=str,
        help=('URL or identifier for a Github repository, on form: '
              'https://github.com/<owner>/<repo>')
    )
    parser_export.add_argument(
        '-p', '--pull_requests',
        help="Export PRs from the repository as well",
        action='store_true'
    )
    parser_export.add_argument(
        '-o', '--outfile',
        type=str,
        help=('Name of output file, extension [yml,yaml,json] affect format. '
              'If extension None or unknown, default to yml. '
              'If no file is given, <reponame>-issues.yml will be used.'
        )
    )

    args = parser.parse_args()

    if args.action == "export":
        run_export(
            args.repo,
            export_prs=args.pull_requests,
            verbose=args.verbose,
            outfile=args.outfile
        )
    elif args.action == "import":
        run_import(
            args.repo,
            args.issues_file,
            args.token,
            verbose=args.verbose
        )
    else:
        raise RuntimeError(f"Unknown action {args.action}")

if __name__ == "__main__":
    run()
