import os
import shutil
import subprocess as sp
from os.path import isfile, join
from shell_code import ShellLexer, split_list
from pygments.token import Token, Name

path = "/home/victoragnez/"

class Shell():
	
	def __init__(self):
		pass

	def command(instance):
		lexer = ShellLexer()
		lexed = [{'token':t, 'value':v} for t,v in lexer.get_tokens(instance.text)]
		sublists = [seq for seq in split_list(lexed, Token.Text.Whitespace, lambda l : l['token']) if seq]
		if sublists[0][0]['token'] == Token.Text and sublists[0][0]['value'] == "sudo":
			print("Erro: Tentativa de comando sudo")
			return
		args = [tok['value'] for sublist in sublists for tok in sublist]
		if sublists[0][0]['token'] == Name.Builtin:
			if args[0] == 'touch' and len(args) == 2:
				touch(args[1])
			elif args[0] == 'rm' and len(args) == 2:
				remove(args[1])
			elif (args[0] == 'rm' and len(args) == 3 and args[1] == '-d') or (args[0] == 'rmdir' and len(args) == 2):
				rmdir(args[-1])
			elif args[0] == 'rm' and len(args) == 3 and args[1] == '-r':
				rmtree(args[2])
			else:
				run(args)
		else:
			run(args)

	def run(args):
		sp.run(args, cwd=path, timeout = 3)

	def touch(name):
		f = open(join(path, name),"w+")
		f.close()

	def remove(name):
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

	def rmtree(name):
		try:
			shutil.rmtree(join(path,name))
		except FileNotFoundError:
			pass

	def list_dir(path):
		contents = os.listdir(path)
		return {file : not isfile(join(path, file)) for file in contents}