import argparse

from test2va.bridge import create_examples
from test2va.commands import gui_command, profile_create, profile_list, profile_delete, profile_java, profile_apk, \
    profile_udid, profile_view, capability_list, capability_add, capability_remove, capability_edit, capability_docs, \
    stats_list_command, stats_view_command, run_command


# TODO: Check ANDROID_HOME nor ANDROID_SDK_ROOT environment variables


def main():
    create_examples()

    parser = argparse.ArgumentParser(description="Test2VA CLI Tool")
    subparsers = parser.add_subparsers(dest='command', help='Subcommands')

    parser.set_defaults(func=lambda _: parser.print_help())

    # test2va gui --------
    gui = subparsers.add_parser('gui', help='Launch the GUI version of the tool')
    gui.set_defaults(func=lambda _: gui_command(_))

    # test2va run [--auto-udid] [--udid <udid>] [--prof <name>] --------
    parser_run = subparsers.add_parser('run', help='Run the tool with the specified profile and parameters')
    parser_run.add_argument('-a', '--auto-udid', action='store_true', help='Automatically detect a device UDID')
    parser_run.add_argument('-u', '--udid', help='The device UDID to use')
    parser_run.add_argument('-p', '--prof', help='The name of the profile to use')
    parser_run.set_defaults(func=lambda a: run_command(a))

    # test2va profile --------
    profile = subparsers.add_parser('profile', help='Create or manage test profiles')
    profile.set_defaults(func=lambda a: profile.print_help())
    profile_subparsers = profile.add_subparsers(dest='profile_command', help='Profile commands')

    # test2va profile create <name>
    profile_create_ = profile_subparsers.add_parser('create', help='Create a new test profile')
    profile_create_.add_argument('name', help='The name of the profile')
    profile_create_.set_defaults(func=lambda a: profile_create(a.name))

    # test2va profile list
    profile_list_ = profile_subparsers.add_parser('list', help='List all test profiles')
    profile_list_.set_defaults(func=lambda _: profile_list())

    # test2va profile delete <name>
    profile_delete_ = profile_subparsers.add_parser('delete', help='Delete a test profile')
    profile_delete_.add_argument('name', help='The name of the profile')
    profile_delete_.set_defaults(func=lambda a: profile_delete(a.name))

    # test2va profile java <name> <path>
    profile_java_ = profile_subparsers.add_parser('java', help='Add Java source code path to a profile')
    profile_java_.add_argument('name', help='The name of the profile')
    profile_java_.add_argument('path', help='The path to the Java source code')
    profile_java_.set_defaults(func=lambda a: profile_java(a.name, a.path))

    # test2va profile apk <name> <path>
    profile_apk_ = profile_subparsers.add_parser('apk', help='Add APK path to a profile')
    profile_apk_.add_argument('name', help='The name of the profile')
    profile_apk_.add_argument('path', help='The path to the APK')
    profile_apk_.set_defaults(func=lambda a: profile_apk(a.name, a.path))

    # test2va profile udid <name>
    profile_udid_ = profile_subparsers.add_parser('udid', help='Add device UDID to a profile')
    profile_udid_.add_argument('name', help='The name of the profile')
    profile_udid_.add_argument('udid', help='The device UDID')
    profile_udid_.set_defaults(func=lambda a: profile_udid(a.name, a.udid))

    # test2va profile view <name>
    profile_view_ = profile_subparsers.add_parser('view', help='View the details of a profile')
    profile_view_.add_argument('name', help='The name of the profile')
    profile_view_.set_defaults(func=lambda a: profile_view(a.name))

    # test2va cap --------
    cap = subparsers.add_parser('cap', help='Manage capabilities')
    cap_subparsers = cap.add_subparsers(dest='cap_command', help='Capability commands')
    cap.set_defaults(func=lambda a: cap.print_help())

    # test2va cap list
    cap_list = cap_subparsers.add_parser('list', help='List all capabilities')
    cap_list.set_defaults(func=lambda a: capability_list())

    # test2va cap add <prof-name> <cap> <value>
    cap_add = cap_subparsers.add_parser('add', help='Add a capability to a profile')
    cap_add.add_argument('prof_name', help='The name of the profile')
    cap_add.add_argument('cap', help='The capability name')
    cap_add.add_argument('value', help='The capability value')
    cap_add.set_defaults(func=lambda a: capability_add(a.prof_name, a.cap, a.value))

    # test2va cap remove <prof-name> <cap>
    cap_remove = cap_subparsers.add_parser('remove', help='Remove a capability from a profile')
    cap_remove.add_argument('prof_name', help='The name of the profile')
    cap_remove.add_argument('cap', help='The capability name')
    cap_remove.set_defaults(func=lambda a: capability_remove(a.prof_name, a.cap))

    # test2va cap edit <prof-name> <cap> <value>
    cap_edit = cap_subparsers.add_parser('edit', help='Edit a capability in a profile')
    cap_edit.add_argument('prof_name', help='The name of the profile')
    cap_edit.add_argument('cap', help='The capability name')
    cap_edit.add_argument('value', help='The new capability value')
    cap_edit.set_defaults(func=lambda a: capability_edit(a.prof_name, a.cap, a.value))

    # test2va cap docs <cap>
    cap_docs = cap_subparsers.add_parser('docs', help='View the documentation for a capability')
    cap_docs.add_argument('cap', help='The capability name')
    cap_docs.set_defaults(func=lambda a: capability_docs(a.cap))

    # test2va stats --------
    stats = subparsers.add_parser('stats', help='View test statistics/results')
    stats_subparsers = stats.add_subparsers(dest='stats_command', help='Stats commands')
    stats.set_defaults(func=lambda a: stats.print_help())

    # test2va stats list
    stats_list = stats_subparsers.add_parser('list', help='List all test statistics/results')
    stats_list.set_defaults(func=lambda a: stats_list_command())

    # test2va stats view <code>
    stats_view = stats_subparsers.add_parser('view', help='View the details of a test statistic/result.')
    stats_view.add_argument('code', help='The code of the test statistic/result (test2va stats list)', type=int)
    stats_view.set_defaults(func=lambda a: stats_view_command(a.code))

    # Parsing arguments
    args = parser.parse_args()

    # Handling the arguments
    args.func(args)


if __name__ == "__main__":
    main()
