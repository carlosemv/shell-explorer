import os
import shutil
import subprocess as sp
from os.path import isfile, join, abspath
from shell_code import ShellLexer, split_list
from pygments.token import Token, Name

path = "/home/victoragnez/"

class Shell():
	
	def __init__(self):
		pass	

	def command(instance):
		global path
		lexer = ShellLexer()
		lexed = [{'token':t, 'value':v} for t,v in lexer.get_tokens(instance.text)]
		sublists = [seq for seq in split_list(lexed, Token.Text.Whitespace, lambda l : l['token']) if seq]
		if sublists[0][0]['token'] == Token.Text and sublists[0][0]['value'] == "sudo":
			print("Erro: Tentativa de comando sudo")
			return
		args = [tok['value'] for sublist in sublists for tok in sublist]
		if sublists[0][0]['token'] == Name.Builtin:
			if args[0] == 'touch' and len(args) == 2:
				Shell.touch(args[1])
			elif args[0] == 'rm' and len(args) == 2:
				Shell.rm(args[1])
			elif (args[0] == 'rm' and len(args) == 3 and args[1] == '-d') or (args[0] == 'rmdir' and len(args) == 2):
				Shell.rmdir(args[-1])
			elif args[0] == 'rm' and len(args) == 3 and args[1] == '-r':
				Shell.rmtree(args[2])
			elif args[0] == 'mkdir' and len(args) == 2:
				Shell.mkdir(args[1])
			elif args[0] == 'cp' and len(args) == 3:
				Shell.cp(args[1], args[2])
			elif args[0] == 'cp' and len(args) == 4 and args[1] == '-r':
				Shell.cptree(args[2], args[3])
			elif args[0] == 'mv' and len(args) == 3:
				Shell.mv(args[1], args[2])
			elif args[0] == 'cd' and len(args) == 2:
				path = abspath(join(path, args[1]))
				print(path)
			else:
				Shell.run(args)
		else:
			Shell.run(args)
	
	def list_dir(path):
		contents = os.listdir(path)
		return {file : not isfile(join(path, file)) for file in contents}
		
	def run(args):
		sp.run(args, cwd=path, timeout = 3)

	def touch(name):
		f = open(join(path, name),"w+")
		f.close()

	def rm(name):
		try:
			os.remove(join(path,name))
		except FileNotFoundError:
			pass
		except IsADirectoryError:
			pass

	def rmdir(name):
		try:
			os.rmdir(join(path,name))
		except FileNotFoundError:
			pass
		except OSError:
			pass

	def rmtree(name):
		try:
			shutil.rmtree(join(path,name))
		except FileNotFoundError:
			pass
		except NotADirectoryError:
			pass
	
	def mkdir(name):
		try:
			os.mkdir(join(path,name))
		except FileExistsError:
			pass
			
	def cp(a, b):
		try:
			shutil.copy2(join(path,a), join(path,b))
		except FileNotFoundError:
			pass
		except IsADirectoryError:
			pass
	
	def cptree(a, b):
		try:
			shutil.copytree(join(path,a), join(path,b))
		except FileNotFoundError:
			pass
		except NotADirectoryError:
			pass
	
	def mv(a, b):
		try:
			shutil.move(join(path,a), join(path,b))
		except FileNotFoundError:
			pass

