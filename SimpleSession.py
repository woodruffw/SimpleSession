import sublime, sublime_plugin
import os
import glob
import json

def error_message(*args):
	sublime.error_message(' '.join(list(args)))

def get_path():
	return os.path.join(sublime.packages_path(), 'User', 'simplesession')

def get_sessions():
	pathnames = glob.glob(os.path.join(get_path(), '*'))
	names = [os.path.basename(path) for path in pathnames]
	return names

try:
	os.makedirs(get_path())
except Exception:
	pass

class SaveSession(sublime_plugin.WindowCommand):
	def run(self):
		self.window.show_input_panel(
			"Session name:",
			"",
			on_done=self.save_session,
			on_change=None,
			on_cancel=None
		)

	def save_session(self, name):
		session = os.path.join(get_path(), name)

		try:
			open(session, 'w').close()
			os.unlink(session)
		except OSError:
			error_message("Invalid Session Name:", session)
			return

		self.save(session, self.window)

	def save(self, session, window):
		file_groups = {}

		for i in range(window.num_groups()):
			file_groups[i] = [view.file_name() for view in window.views_in_group(i) if view.file_name() != None]

		data = {
			'groups': file_groups,
			'layout': window.get_layout()
		}

		sess_file = open(session, 'w')

		json.dump(data, sess_file, indent=4)

		sess_file.close()

class LoadSession(sublime_plugin.WindowCommand):
	def run(self):
		pathnames = glob.glob(os.path.join(get_path(), '*'))
		sessions = [os.path.basename(path) for path in pathnames]
		print(sessions)

		if not sessions:
			sublime.message_dialog("No sessions available to load.")
			return

		sublime.active_window().show_quick_panel(
			sessions,
			self.handle_selection
		)

	def handle_selection(self, idx):
		if idx < 0:
			return

		self.load(os.path.join(get_path(), get_sessions()[idx]))

	def load(self, session):
		with open(session) as sess_file:
			data = json.load(sess_file)

		groups = data['groups']
		layout = data['layout']

		window = self.window
		open_files = [view.file_name() for view in window.views() if view.file_name() != None]

		# if the current window has open files, load the session in a new one
		if open_files:
			sublime.run_command('new_window')
			window = sublime.active_window()

		window.set_layout(layout)

		for group, filenames in groups.items():
			window.focus_group(int(group))

			for filename in filenames:
				window.open_file(filename)

class DeleteSession(sublime_plugin.WindowCommand):
	def run(self):
		sessions = get_sessions()

		if not sessions:
			sublime.message_dialog("No sessions available to load.")
			return

		sublime.active_window().show_quick_panel(
			sessions,
			self.handle_selection
		)

	def handle_selection(self, idx):
		if idx < 0:
			return

		os.unlink(os.path.join(get_path(), get_sessions()[idx]))

