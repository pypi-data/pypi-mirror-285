import argparse

def main():
    parser = argparse.ArgumentParser(description="Monkey CLI")
    subparsers = parser.add_subparsers(dest='command', help='Subcommands', required=True)
    
    parser_project = subparsers.add_parser('project', help='Create and configure a Monkey project')
    parser_project_subparsers = parser_project.add_subparsers(dest='command', help='Subcommands', required=True)
    parser_project_create = parser_project_subparsers.add_parser('create', help='Create a new Monkey project')
    parser_project_create.add_argument('path', type=str, help='Path to create project at')
    parser_project_create.add_argument('--no-starting-worker', action='store_true', help='Create the project without the starting worker')
    parser_project_configure = parser_project_subparsers.add_parser('configure', help='Configure an existing Monkey project')
    parser_project_configure_subparsers = parser_project_configure.add_subparsers(dest='command', help='Subcommands', required=True)
    parser_project_configure_name = parser_project_configure_subparsers.add_parser('name', help='Change the name of the project')
    parser_project_configure_name.add_argument('name', type=str, help='New name of the project')
    parser_project_configure_description = parser_project_configure_subparsers.add_parser('description', help='Change the description of the project')
    parser_project_configure_description.add_argument('description', type=str, help='New description of the project')
    
    parser_worker = subparsers.add_parser('worker', help='Create, configure, or delete a Monkey worker')
    parser_worker_subparsers = parser_worker.add_subparsers(dest='command', help='Subcommands', required=True)
    parser_worker_create = parser_worker_subparsers.add_parser('create', help='Create a new Monkey worker')
    parser_worker_create.add_argument('name', type=str, help='Name of the new worker')
    parser_worker_configure = parser_worker_subparsers.add_parser('configure', help='Configure an existing Monkey worker')
    parser_worker_configure_subparsers = parser_worker_configure.add_subparsers(dest='command', help='Subcommands', required=True)
    parser_worker_configure_name = parser_worker_configure_subparsers.add_parser('name', help='Change the name of the worker')
    parser_worker_configure_name.add_argument('name', type=str, help='New name of the worker')
    parser_worker_configure_description = parser_worker_configure_subparsers.add_parser('description', help='Change the description of the worker')
    parser_worker_configure_description.add_argument('description', type=str, help='New description of the worker')
    parser_worker_delete = parser_worker_subparsers.add_parser('delete', help='Delete an existing Monkey worker')
    parser_worker_delete.add_argument('--yes', '-y', action='store_true', help='Accept all prompts')
    
    args = parser.parse_args()
    
    print(args)
    
if __name__ == "__main__":
    main()
