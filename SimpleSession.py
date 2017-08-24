from glob import glob
import json
from os import path, makedirs, unlink, rename
from datetime import datetime

import sublime
import sublime_plugin
import os
import re

file_extension = '.simplesession'
default_filename_format = '%Y%m%d-%H.%M.%S'


def plugin_loaded():
    update_old_session_files()


def update_old_session_files():
    paths = glob(path.join(get_path(), '*'))

    for entry in paths:
        if not entry.endswith('.simplesession'):
            rename(entry, entry + '.simplesession')


def error_message(*args):
    sublime.error_message(' '.join(args))


def get_path():
    return path.join(sublime.packages_path(), 'User', 'simplesession')


def getSessionFilePaths():
    paths = glob(path.join(get_path(), '*' + file_extension))
    exp = re.compile('(\d{8}-\d{2}\.\d{2}\.\d{2}\.simplesession)$')
    autoSessions = []
    namedSessions = []

    for entry in paths:
        if exp.search(entry) is not None:
            autoSessions.append(entry)
        else:
            namedSessions.append(entry)

    autoSessions = sorted(autoSessions, key=lambda x: os.path.getmtime(x),
                          reverse=True)
    namedSessions = sorted(namedSessions, key=lambda x: os.path.getmtime(x),
                           reverse=True)
    sortedpaths = namedSessions + autoSessions
    return sortedpaths


def getSessionFileNames():
    return [path.basename(p).rsplit(file_extension, 1)[0]
            for p in getSessionFilePaths()]


def generate_name():
    return datetime.now().strftime(default_filename_format)


def prompt_get_session_name(them, ondone):
    them.window.show_input_panel(
        "Session name:",
        generate_name(),
        on_done=ondone,
        on_change=None,
        on_cancel=None
    )


class SaveSession(sublime_plugin.WindowCommand):
    def run(self):
        prompt_get_session_name(self, self.save_session)

    def save_session(self, name):
        session = path.join(get_path(), name + file_extension)

        try:
            makedirs(get_path(), exist_ok=True)
            open(session, 'w').close()
            unlink(session)
        except OSError:
            error_message("Invalid Session Name:", session)
            return

        self.save(session)

    def save(self, session):
        file_groups = {}

        for i in range(self.window.num_groups()):
            file_list = []
            for view in self.window.views_in_group(i):
                if view.file_name():
                    file_list.append(view.file_name())
                else:
                    file_list.append("buffer:" + view.substr(sublime.Region(0,
                                     view.size())))
                file_groups[i] = file_list

        data = {
            'groups': file_groups,
            'layout': self.window.get_layout()
        }

        with open(session, 'w') as sess_file:
            json.dump(data, sess_file, indent=4)


class SaveAndCloseSession(SaveSession, sublime_plugin.WindowCommand):
    def run(self):
        prompt_get_session_name(self, self.save_and_close_session)

    def save_and_close_session(self, name):
        super(SaveAndCloseSession, self).save_session(name)

        for view in self.window.views():
            view.set_status('ss', '')
            view.close()


class LoadSession(sublime_plugin.WindowCommand):
    def run(self):
        sessions = getSessionFileNames()

        if not sessions:
            sublime.message_dialog("No sessions available to load.")
            return

        sublime.active_window().show_quick_panel(
            sessions,
            self.handle_selection
        )

    def handle_selection(self, idx):
        if idx >= 0:
            self.load(getSessionFilePaths()[idx])

    def load(self, session):
        with open(session) as sess_file:
            data = json.load(sess_file)

        groups = data['groups']
        layout = data['layout']

        window = self.window
        open_files = [view.file_name() for view in window.views()
                      if view.file_name()]

        # if the current window has open files, load the session in a new one
        if open_files:
            sublime.run_command('new_window')
            window = sublime.active_window()

        window.set_layout(layout)

        for group, files in groups.items():
            window.focus_group(int(group))

            for file in files:
                # if the string starts with buffer, it's an inline buffer
                # and not a filename
                if file.startswith('buffer:'):
                    window.new_file().run_command('insert',
                                                  {'characters': file[7:]})
                else:
                    window.open_file(file)

            for view in window.views():
                view.set_status('ss', path.basename(session))


class DeleteSession(sublime_plugin.WindowCommand):
    def run(self):
        sessions = getSessionFileNames()

        if not sessions:
            sublime.message_dialog("No sessions available to delete.")
            return

        sublime.active_window().show_quick_panel(
            sessions,
            self.handle_selection
        )

    def handle_selection(self, idx):
        if idx >= 0:
            unlink(getSessionFilePaths()[idx])
