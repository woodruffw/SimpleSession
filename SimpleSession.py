from glob import glob
import json
from os import path
import sublime
import sublime_plugin

def error_message(*args):
	sublime.error_message(' '.join(args))

def get_path():
	return path.join(sublime.packages_path(), 'User', 'simplesession')

def get_sessions():
	pathnames = glob(path.join(get_path(), '*'))
	names = [path.basename(p) for p in pathnames]
	return names

class SaveSession(sublime_plugin.WindowCommand):
	def run(self):
		self.get_session_name_and_save()

	def get_session_name_and_save(self):
		self.window.show_input_panel(
			"Session name:",
			"",
			on_done=self.save_session,
			on_change=None,
			on_cancel=None
		)

	def save_session(self, name):
		session = path.join(get_path(), name)

		try:
			os.makedirs(get_path(), exist_ok=True)
			open(session, 'w').close()
			os.unlink(session)
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
					file_list.append("buffer:" + view.substr(sublime.Region(0, view.size())))
				file_groups[i] = file_list

		data = {
			'groups': file_groups,
			'layout': self.window.get_layout()
		}

		with open(session, 'w') as sess_file:
			json.dump(data, sess_file, indent=4)

class SaveAndCloseSession(SaveSession, sublime_plugin.WindowCommand):
	def run(self):
		self.window.show_input_panel(
			"Session name:",
			"",
			on_done=self.save_and_close_session,
			on_change=None,
			on_cancel=None
		)

	def save_and_close_session(self, name):
		super(SaveAndCloseSession, self).save_session(name)

		for view in self.window.views():
			view.set_status('ss', '')
			view.close()

class LoadSession(sublime_plugin.WindowCommand):
	def run(self):
		pathnames = glob(path.join(get_path(), '*'))
		sessions = [path.basename(p) for p in pathnames]

		if not sessions:
			sublime.message_dialog("No sessions available to load.")
			return

		sublime.active_window().show_quick_panel(
			sessions,
			self.handle_selection
		)

	def handle_selection(self, idx):
		if idx >= 0:
			self.load(path.join(get_path(), get_sessions()[idx]))

	def load(self, session):
		with open(session) as sess_file:
			data = json.load(sess_file)

		groups = data['groups']
		layout = data['layout']

		window = self.window
		open_files = [view.file_name() for view in window.views() if view.file_name()]

		# if the current window has open files, load the session in a new one
		if open_files:
			sublime.run_command('new_window')
			window = sublime.active_window()

		window.set_layout(layout)

		for group, files in groups.items():
			window.focus_group(int(group))

			for file in files:
				# if the string starts with buffer, it's an inline buffer and not a filename
				if file.startswith('buffer:'):
					window.new_file().run_command('insert', {'characters': file[7:]})
				else:
					window.open_file(file)

			for view in window.views():
				view.set_status('ss', path.basename(session))

class DeleteSession(sublime_plugin.WindowCommand):
	def run(self):
		sessions = get_sessions()

		if not sessions:
			sublime.message_dialog("No sessions available to delete.")
			return

		sublime.active_window().show_quick_panel(
			sessions,
			self.handle_selection
		)

	def handle_selection(self, idx):
		if idx >= 0:
			os.unlink(path.join(get_path(), get_sessions()[idx]))
