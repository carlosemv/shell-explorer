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
		sublists = [seq for seq in split_list(lexed, Token.Text.Whitespace, lambda l : l['token']) if seq]
		if sublists[0][0]['token'] == Token.Text and sublists[0][0]['value'] == "sudo":
			print("Erro: Tentativa de comando sudo")
			return
		args = [tok['value'] for sublist in sublists for tok in sublist]
		if sublists[0][0]['token'] == Name.Builtin:
			cmd, n_args = args[0], len(args)
			if cmd == 'touch' and n_args == 2:
				self.touch(args[1])
			elif cmd == 'rm' and n_args == 2:
				self.rm(args[1])
			elif (cmd == 'rm' and n_args == 3 and args[1] == '-d') or \
					(cmd == 'rmdir' and n_args == 2):
				self.rmdir(args[-1])
			elif cmd == 'rm' and n_args == 3 and args[1] == '-r':
				self.rmtree(args[2])
			elif cmd == 'mkdir' and n_args == 2:
				self.mkdir(args[1])
			elif cmd == 'cp' and n_args == 3:
				self.cp(args[1], args[2])
			elif cmd == 'cp' and n_args == 4 and args[1] == '-r':
				self.cptree(args[2], args[3])
			elif cmd == 'mv' and n_args == 3:
				self.mv(args[1], args[2])
			elif cmd == 'cd' and n_args > 1:
				prev_pont = True
				arg = ""
				bad = False
				for tok in [tmp for sublist in sublists for tmp in sublist][1:]:
					if tok['token'] == Token.Punctuation:
						arg = arg + tok['value']
						prev_pont = True
					elif prev_pont:
						arg = arg + tok['value']
						prev_pont = False
					else:
						bad = True
						break
				if not bad:
					self.cd(arg)
				else:
					self.run(instance.text.split())
			else:
				self.run(instance.text.split())
		else:
			self.run(instance.text.split())
		self.dispath('on_update')
	
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

	def touch(self, name):
		f = open(join(self.path, name),"w+")
		f.close()

	def rm(self, name):
		try:
			os.remove(join(self.path,name))
		except FileNotFoundError:
			pass
		except IsADirectoryError:
			pass

	def rmdir(self, name):
		try:
			os.rmdir(join(self.path,name))
		except FileNotFoundError:
			pass
		except OSError:
			pass

	def rmtree(self, name):
		try:
			shutil.rmtree(join(self.path,name))
		except FileNotFoundError:
			pass
		except NotADirectoryError:
			pass
	
	def mkdir(self, name):
		try:
			os.mkdir(join(self.path,name))
		except FileExistsError:
			pass
			
	def cp(self, a, b):
		try:
			shutil.copy2(join(self.path,a), join(self.path,b))
		except FileNotFoundError:
			pass
		except IsADirectoryError:
			pass
	
	def cptree(self, a, b):
		try:
			shutil.copytree(join(self.path,a), join(self.path,b))
		except FileNotFoundError:
			pass
		except NotADirectoryError:
			pass
	
	def mv(self, a, b):
		try:
			shutil.move(join(self.path,a), join(self.path,b))
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

