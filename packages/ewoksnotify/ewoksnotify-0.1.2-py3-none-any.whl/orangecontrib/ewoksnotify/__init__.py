import sysconfig

NAME = "Notification"

DESCRIPTION = "Common tasks for notifications"

LONG_DESCRIPTION = "Common tasks for notifications"

ICON = "icons/category.svg"

BACKGROUND = "light-blue"

WIDGET_HELP_PATH = (
    # Development documentation (make htmlhelp in ./doc)
    ("{DEVELOP_ROOT}/doc/_build/htmlhelp/canvas/widgets/widgets.html", None),
    # Documentation included in wheel
    (
        "{}/help/ewoksnotify/canvas/widgets/widgets.html".format(
            sysconfig.get_path("data")
        ),
        None,
    ),
    # Online documentation url
    ("http://ewoksnotify.readthedocs.io/en/latest/canvas/widgets/widgets", ""),
)
