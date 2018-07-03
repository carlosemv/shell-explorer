from kivy.uix.codeinput import CodeInput
from pygments.styles.default import DefaultStyle
from pygments.style import Style
from pygments.lexer import RegexLexer
from pygments.lexers.shell import BashLexer
from pygments.lexer import inherit
from pygments.token import Token, Name

class CodeStyle(Style):
	default_style = ""
	styles = DefaultStyle.styles
	styles[Token.Operator] = 'bold #ff0000'
	styles[Token.Punctuation] = "bold #000090"

class ShellLexer(RegexLexer):
	tokens = {
		'root': [
			(r'\s+', Token.Text.Whitespace),
			(r'\'([^\'\\]|\\.)*\'', Token.Literal.String.Single),
			(r'\"([^\"\\]|\\.)*\"', Token.Literal.String.Double),
			(r'(ls|cd|mv|rm|cp|cat|grep|echo|pwd)\r', Name.Builtin),
			(r'-[^\s]+', Name.Attribute),
			(r'\.\.|\.|/', Token.Punctuation),
			(r'\||&&', Token.Operator),
			(r'\w+', Token.Text)
		]
	}

class ShellText(CodeInput):
	def __init__(self, **kwargs):
		kwargs.setdefault('readonly', True)
		kwargs.setdefault('font_size', 12)
		kwargs.setdefault('multiline', False)
		kwargs.setdefault('write_tab', False)
		kwargs.setdefault('lexer', ShellLexer())
		kwargs.setdefault('style', CodeStyle)
		super(ShellText, self).__init__(**kwargs)

class ShellInput(ShellText):
	def __init__(self, **kwargs):
		kwargs.setdefault('readonly', False)
		super(ShellInput, self).__init__(**kwargs)

def split_list(src, sep, key=lambda x:x):
	group = []    
	for num in src:
		if key(num) != sep:
			group.append(num)
		else:
			yield group
			group = []
	yield group

# shell_lexer = ShellLexer()
# test_str = 'mv -rf | & adnsak else && . .. ./dir/../filw \'\\\'\' "aa ..\\ \"a" '

# lexed = [{'token':t, 'value':v} for t,v in shell_lexer.get_tokens(test_str)]
# for seq in split_list(lexed, Token.Text.Whitespace, lambda l : l['token']):
# 	print(''.join(lex['value'] for lex in seq), end=' ')
# 	if not seq:
# 		print()
# 	elif seq[0]['token'] == Token.Punctuation:
# 		print(Token.Text)
# 	else:
# 		print(seq[0]['token'])

