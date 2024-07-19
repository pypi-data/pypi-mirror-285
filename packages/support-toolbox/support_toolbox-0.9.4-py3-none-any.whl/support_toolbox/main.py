from support_toolbox.app_handler.app import start_app
from support_toolbox.app_handler.auto_updater import check_for_updates
from support_toolbox.app_handler.app_version import __version__


def main():
    check_for_updates(__version__)
    start_app()


if __name__ == "__main__":
    main()
