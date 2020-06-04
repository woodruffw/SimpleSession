SimpleSession
=============

![license](https://raster.shields.io/badge/license-MIT%20with%20restrictions-green.png)

SimpleSession is a tiny session manager for Sublime Text (3).

It was originally based on
[Session Manager](https://github.com/Zeeker/sublime-SessionManager),
which is a lot better than Sublime's default session management but doesn't
allow per-window saving or layout saving.

## Pros
* Saves sessions on a per-window basis, instead of the global Sublime Text
state.
* Saves and restores window layout and file grouping.
* Only opens a new window if your current one is empty.
* Restores unsaved buffers (but *not* unsaved file changes).

## Cons
* Doesn't care about your Sublime Text project files (this might be a 'pro').
* Will probably crash/do something wrong if you try to load a non-session file.
* Probably won't work on Sublime Text 2. I haven't tried it.

## Installation

If you have Package Control installed:
* Open the Command Palette (Ctrl+Shift+P)
* Go to `Package Control: Install Package`
* Search for "SimpleSession" and press Enter to install

If you don't have Package Control or want to install manually for whatever
reason:
* Clone this repository into your packages directory (`Preferences -> Browse
Packages...`).

## Usage

SimpleSession's usage is similar to Session Manager's:

Command Palette (Ctrl+Shift+P) operation:

```
SimpleSession: Delete
SimpleSession: Load
SimpleSession: Save
SimpleSession: Save and Close
SimpleSession: Edit
```

`Delete` and `Load` give you a list of sessions to chose from, and `Save`
prompts you for a filename to save the current session with. `Save and Close`
operates identically to `Save`, but closes all open files in the window after
saving.

Like Session Manager, these commands can be bound:

```
save_session
save_and_close_session
load_session
delete_session
edit_session
```
