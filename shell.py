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

	def on_update(shell):
		pass

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

		succeed = False
		if args[0]['token'] == Name.Builtin:
			succeed = self.builtin(args)
		else:
			succeed = self.run(instance.text.split())
		
		self.dispatch('on_update')
		return succeed

	def builtin(self, args):
		cmd, n_args = args[0]['value'], len(args)

		is_path = [False for i in range(max(n_args, 4))]
		for i, arg in enumerate(args):
			if arg['token'] in (Token.Literal.String.Single,
					Token.Literal.String.Double):
				arg['value'] = arg['value'].strip('\"\'')
				arg['token'] = Token.Text

			if arg['token'] == Token.Text:
				arg['value'] = arg['value'].replace("\\ ", " ")
				arg['value'] = normpath(join(self.path, arg['value']))
				is_path[i] = True

		if cmd == 'touch' and n_args == 2 and is_path[1]:
			r = self.touch(args[1]['value'])
		elif cmd == 'rm':
			if n_args == 3 and args[1]['token'] == Name.Attribute and is_path[2]:
				if args[1]['value'] == '-d':
					r = self.rmdir(args[2]['value'])
				elif args[1]['value'] == '-r':
					r = self.rmtree(args[2]['value'])
			elif n_args == 2 and is_path[1]:
				r = self.rm(args[1]['value'])
			else:
				return False
		elif cmd == 'rmdir' and n_args == 2 and is_path[1]:
			r = self.rmdir(args[1]['value'])
		elif cmd == 'mkdir' and n_args == 2 and is_path[1]:
			r = self.mkdir(args[1]['value'])
		elif cmd == 'cp':
			if n_args == 4 and args[1]['token'] == Name.Attribute and \
					args[1]['value'] == '-r' and is_path[2] and is_path[3]:
				r = self.cptree(args[2]['value'], args[3]['value'])
			elif n_args == 3 and is_path[1] and is_path[2]:
				r = self.cp(args[1]['value'], args[2]['value'])
			else:
				return False
		elif cmd == 'mv' and n_args == 3 and is_path[1] and is_path[2]:
			r = self.mv(args[1]['value'], args[2]['value'])
		elif cmd == 'cd' and n_args == 2 and is_path[1]:
			r = self.cd(args[1]['value'])
		else:
			return False
		return r

	def list_dir(path):
		contents = os.listdir(path)
		return {file : not isfile(join(path, file)) for file in contents}
		
	def run(self, args):
		try:
			sp.run(args, cwd=self.path, timeout=3)
		except OSError as e:
			print("Shell.run:", e)
			return False
		else:
			return True

	def touch(self, path):
		try:
			file = open(path,"w+")
		except OSError as e:
			print(e)
			return False
		else:
			file.close()
			return True

	def rm(self, path):
		try:
			os.remove(path)
		except OSError as e:
			print(e)
			return False
		else:
			return True

	def rmdir(self, path):
		try:
			os.rmdir(path)
		except OSError as e:
			print(e)
			return False
		else:
			return True

	def rmtree(self, path):
		try:
			shutil.rmtree(path)
		except OSError as e:
			print(e)
			return False
		else:
			return True
	
	def mkdir(self, path):
		try:
			os.mkdir(path)
		except OSError as e:
			print(e)
			return False
		else:
			return True
					
	def cp(self, path_src, path_tgt):
		try:
			shutil.copy2(path_src, path_tgt)
		except (shutil.SameFileError,
				OSError) as e:
			print("Shell.cp:", e)
			return False
		else:
			return True
	
	def cptree(self, path_src, path_tgt):
		try:
			shutil.copytree(path_src, path_tgt)
		except (shutil.SameFileError,
				OSError) as e:
			print(e)
			return False
		else:
			return True

	def mv(self, path_src, path_tgt):
		try:
			shutil.move(path_src, path_tgt)
		except (shutil.SameFileError,
				OSError) as e:
			print(e)
			return False
		else:
			return True

	def cd(self, new_path):
		prev_path = self.path
		try:
			self.path = new_path
		except OSError as e:
			print(e)
			return False
		else:
			return True