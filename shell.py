from kivy.event import EventDispatcher
from kivy.properties import StringProperty

import os
import shutil
import subprocess as sp
from os.path import isfile, join, normpath
from shell_code import ShellLexer, split_list
from pygments.token import Token, Name

class Shell(EventDispatcher):

	path = StringProperty("")
	
	def __init__(self, app, **kwargs):
		super(Shell, self).__init__(**kwargs)

		self.bind(path=app.setter('path'))
		app.bind(path=self.setter('path'))
		self.path = app.path
		self.register_event_type('on_update')

	def command(self, instance):
		lexer = ShellLexer()
		lexed = [{'token':t, 'value':v} for t,v in lexer.get_tokens(instance.text)]
		lex_seqs = [seq for seq in split_list(lexed, Token.Text.Whitespace, lambda l : l['token']) if seq]

		args = []
		for seq in lex_seqs:
			value = ''.join(lex['value'] for lex in seq)
			token = seq[0]['token']
			if token == Token.Punctuation:
				token = Token.Text
			args.append({'token':token, 'value':value})
		print(args)

		if args[0]['token'] == Name.Builtin:
			self.builtin(args)
		else:
			self.run(instance.text.split())

		self.dispatch('on_update')

	def builtin(self, args):
		cmd, n_args = args[0]['value'], len(args)

		is_path = [False for i in range(max(n_args, 4))]
		for i, arg in enumerate(args):
			if arg['token'] == Token.Text:
				arg['value'] = normpath(join(self.path, arg['value']))
				is_path[i] = True

		if cmd == 'touch' and n_args == 2 and is_path[1]:
			self.touch(args[1]['value'])
		elif cmd == 'rm':
			if n_args == 3 and args[1]['token'] == Name.Attribute and is_path[2]:
				if args[1]['value'] == '-d':
					self.rmdir(args[2]['value'])
				elif args[1]['value'] == '-r':
					self.rmtree(args[2]['value'])
			elif n_args == 2 and is_path[1]:
				self.rm(args[1]['value'])
		elif cmd == 'rmdir' and n_args == 2 and is_path[1]:
			self.rmdir(args[1]['value'])
		elif cmd == 'mkdir' and n_args == 2 and is_path[1]:
			self.mkdir(args[1]['value'])
		elif cmd == 'cp':
			if n_args == 4 and args[1]['token'] == Name.Attribute and \
					args[1]['value'] == '-r' and is_path[2] and is_path[3]:
				self.cptree(args[2]['value'], args[3]['value'])
			elif n_args == 3 and is_path[1] and is_path[2]:
				self.cp(args[1]['value'], args[2]['value'])
		elif cmd == 'mv' and n_args == 3 and is_path[1] and is_path[2]:
			self.mv(args[1]['value'], args[2]['value'])
		elif cmd == 'cd' and n_args == 2 and is_path[1]:
			self.cd(args[1]['value'])
		else:
			self.run(instance.text.split())

	def list_dir(path):
		contents = os.listdir(path)
		return {file : not isfile(join(path, file)) for file in contents}
		
	def run(self, args):
		try:
			sp.run(args, cwd=self.path, timeout = 3)
		except FileNotFoundError:
			pass
		except FileExistsError:
			pass
		except NotADirectoryError:
			pass
		except IsADirectoryError:
			pass

	def on_update(shell):
		pass

	def touch(self, path):
		f = open(path,"w+")
		f.close()

	def rm(self, path):
		try:
			os.remove(path)
		except FileNotFoundError:
			pass
		except IsADirectoryError:
			pass

	def rmdir(self, path):
		try:
			os.rmdir(path)
		except FileNotFoundError:
			pass
		except OSError:
			pass

	def rmtree(self, path):
		try:
			shutil.rmtree(path)
		except FileNotFoundError:
			pass
		except NotADirectoryError:
			pass
	
	def mkdir(self, path):
		try:
			os.mkdir(path)
		except FileExistsError:
			pass
			
	def cp(self, path_src, path_tgt):
		try:
			shutil.copy2(path_src, path_tgt)
		except FileNotFoundError:
			pass
		except IsADirectoryError:
			pass
	
	def cptree(path_src, path_tgt):
		try:
			shutil.copytree(path_src, path_tgt)
		except FileNotFoundError:
			pass
		except NotADirectoryError:
			pass
	
	def mv(self, path_src, path_tgt):
		try:
			shutil.move(path_src, path_tgt)
		except FileNotFoundError:
			pass
		except FileExistsError:
			pass
	
	def cd(self, arg):
		prev_path = self.path
		try:
			self.path = normpath(join(self.path, arg))
		except FileNotFoundError:
			self.path = prev_path
		except NotADirectoryError:
			self.path = prev_path

	def cd(self, new_path):
		prev_path = self.path
		try:
			self.path = new_path
		except FileNotFoundError:
			self.path = prev_path
		except NotADirectoryError:
			self.path = prev_path
