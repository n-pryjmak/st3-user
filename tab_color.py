import sublime
import sublime_plugin

import re


def plugin_loaded():
    """
    When the plugin loads, set up to monitor the user preferences changing so
    that we can change tab colors on settings change.
    """
    settings = sublime.load_settings("Preferences.sublime-settings")
    settings.add_on_change("tabcolors", check_all_files)

    # if you are using Sublime Text 3, uncomment this line so that when the
    # plugin loads it will check all files and apply color schemes.
    # check_all_files()


def plugin_unloaded():
    """
    When the plugin unloads, remove the settings monitor added at load time.
    """
    settings = sublime.load_settings("Preferences.sublime-settings")
    settings.clear_on_change("tabcolors")


def check_file(view):
    """
    Remove any applied custom color scheme from the file in the provided view,
    and then check the view to see if it has a filename that matches one of the
    configured rules, and if so change it's color scheme.
    """
    # If we previously set a color scheme for this tab, remove it since the
    # settings might now be different.
    if view.settings().has("_tabcolor_set"):
        view.settings().erase("_tabcolor_set")
        view.settings().erase("color_scheme")

    options = view.settings().get("tab_colors", {})
    for regex,color_scheme in options.items():
        if (view.file_name() is not None and re.search(regex, view.file_name())):
            view.settings().set("_tabcolor_set", True)
            view.settings().set("color_scheme", color_scheme)
            return


def check_all_files():
    """
    Check all of the files in all of the windows to see if they need to have a
    custom color scheme applied. This is triggered whenever the user
    preferences change, so that if the rules change the color schemes are
    applied as appropriate.
    """
    for window in sublime.windows():
        for view in window.views():
            check_file(view)


class SyntaxEventListener(sublime_plugin.EventListener):
    """
    Listen for files being loaded and saved and apply color schemes according
    to configured settings
    """
    def on_load(self, view):
        check_file(view)

    def on_save(self, view):
        check_file(view)

    # Sublime Text 4 only; this gets called to tell the event listener about
    # the files that were loaded before the listener was created. If you're
    # using ST3, uncomment the line in plugin_loaded().
    def on_init(self, views):
        for view  in views:
            check_file(view)

    # Sublime Text 4 only; this gets called whenever a project loads so that as
    # you edit the settings in the project, they can be applied. if you're
    # using ST3, you will need to manually close or reopen files (or save them)
    # after you change the project settings.
    def on_load_project(self, window):
        for view in window.views():
            check_file(view)

    # Sublime Text 4 only; this gets called whenever a tab moves between
    # windows so that if you move tabs in and out of a project window, they
    # will take on the appropriate project settings. If you're using ST3, you
    # will need to manually close or reopen files (or save them) after you move
    # them.
    def on_post_move(self, view):
        print('view moved')
        check_file(view)