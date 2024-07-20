import argparse
from .analyser import calculate_contributions, create_contributions_md, create_report, is_github_url
from .hooks import install_hooks, uninstall_hooks

def main():
    parser = argparse.ArgumentParser(description="Kreeck - A tool to track Git contributions and generate reports.")
    subparsers = parser.add_subparsers(dest='command')

    contribute_parser = subparsers.add_parser('contribute', help='Generate contributions report')
    contribute_parser.add_argument('repo_path', type=str, nargs='?', default='.', help='Path to the Git repository or GitHub URL')

    report_parser = subparsers.add_parser('report', help='Generate detailed contributions report')
    report_parser.add_argument('repo_path', type=str, nargs='?', default='.', help='Path to the Git repository or GitHub URL')

    install_parser = subparsers.add_parser('install-hooks', help='Install Git hooks to automatically update contributions report on commit')
    install_parser.add_argument('repo_path', type=str, nargs='?', default='.', help='Path to the Git repository')

    uninstall_parser = subparsers.add_parser('uninstall-hooks', help='Uninstall Git hooks')
    uninstall_parser.add_argument('repo_path', type=str, nargs='?', default='.', help='Path to the Git repository')

    info_parser = subparsers.add_parser('info', help='Show information about Kreeck commands')

    args = parser.parse_args()

    if args.command == 'contribute':
        contributions, percentages = calculate_contributions(args.repo_path)
        if not is_github_url(args.repo_path):
            create_contributions_md(contributions, percentages, args.repo_path)
        print_contributions(contributions, percentages)
    elif args.command == 'report':
        create_report(args.repo_path)
    elif args.command == 'install-hooks':
        install_hooks(args.repo_path)
    elif args.command == 'uninstall-hooks':
        uninstall_hooks(args.repo_path)
    elif args.command == 'info':
        show_info()
    else:
        parser.print_help()

def print_contributions(contributions, percentages):
    sorted_contributions = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
    print("# Contributions\n")
    print("| Rank | Contributor | Percentage | Lines Added |")
    print("|------|-------------|------------|-------------|")
    
    for rank, (author, percentage) in enumerate(sorted_contributions, start=1):
        print(f"| {rank} | {author} | {percentage:.2f}% | {contributions[author]} |")

def show_info():
    info_text = """
    Kreeck - A tool to track Git contributions and generate reports.

    Commands:
    contribute <repo_path>            Generate contributions report for the specified repository.
                                       If no path is provided, the current directory is used.

    report <repo_path>                Generate a detailed contributions report for the specified repository.

    install-hooks <repo_path>         Install Git hooks to automatically update contributions report on commit.
                                       If no path is provided, the current directory is used.

    uninstall-hooks <repo_path>       Uninstall Git hooks.
                                       If no path is provided, the current directory is used.

    info                              Show information about Kreeck commands and usage.

    Examples:
    kreeck contribute .               Generate contributions report for the current directory.
    kreeck report https://github.com/yourusername/your-repo
                                      Generate a detailed report for a GitHub repository.
    """
    print(info_text)

if __name__ == '__main__':
    main()
