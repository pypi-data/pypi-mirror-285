"""An example plugin lexer for Pygments."""

from pygments.lexer import Lexer
from pygments.lexer import RegexLexer, ExtendedRegexLexer, include, bygroups, \
    default, using, line_re, do_insertions
from pygments.token import Token, Punctuation, Whitespace, \
    Text, Comment, Operator, Keyword, Name, String, Number, Generic
from pygments.lexers.diff import DiffLexer
from pygments.lexers.shell import BashLexer
from pygments.lexers.diff import DiffLexer
from git_lexer import GitLexer
from pygments.token import STANDARD_TYPES

import re

__all__ = ['ShellConsoleLexer']

STANDARD_TYPES.update({
    Token.Generic.Prompt.UserHost: 'gp-uh',
    Token.Generic.Prompt.Directory: 'gp-d',
    Token.Generic.Prompt.GitBranch: 'gp-gb',
    Token.Generic.Prompt.VirtualEnv: 'gp-ve',
})

class ShellConsoleLexer(Lexer):
    name = "Shell Console"
    aliases = ["shellconsole", "shell-console", "shell", "console"]
    filenames = ['*.sh-session', '*.shell-session']
    mimetypes = ['application/x-shell-session', 'application/x-sh-session']
    url = 'https://en.wikipedia.org/wiki/Unix_shell'
    version_added = '1.0'

    _bare_continuation = False
    _venv = re.compile(r'^(\([^)]*\))(\s*)')

    _ps1rgx = re.compile(
        r'^\[?(?P<user_host>[^\s@]+@[^\s]+?)(?:\s+|\:)(?P<current_dir>[^\s\]]+)(?:\s+(?P<git_branch>\([^)]+\)))?\]?\s*[$#%]\s*(?P<command>.*\n?)')
    _ps1_groups = [Token.Generic.Prompt.UserHost, Token.Generic.Prompt.Directory, Token.Generic.Prompt.GitBranch]


    _ps2 = '> '
    _innerLexerCls = BashLexer


    def get_tokens_unprocessed(self, text):
        innerlexer = self._innerLexerCls(**self.options)
        difflexer = DiffLexer()
        gitlexer = GitLexer()

        pos = 0
        # Bash command
        curcode = ''
        insertions = []
        backslash_continuation = False
        diff_continuation = False
        git_continuation = False

        for match in line_re.finditer(text):
            line = match.group()

            # Check for virtualenv prompt
            venv_match = self._venv.match(line)
            if venv_match:
                venv = venv_match.group(1)
                venv_whitespace = venv_match.group(2)
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt.VirtualEnv, venv)]))
                if venv_whitespace:
                    insertions.append((len(curcode),
                                       [(0, Text, venv_whitespace)]))
                line = line[venv_match.end():]

            m = self._ps1rgx.match(line)
            ## If line starts with a prompt
            if m:
                # To support output lexers (say diff output), the output
                # needs to be broken by prompts whenever the output lexer
                # changes.
                diff_continuation = False
                git_continuation = False

                if not insertions:
                    pos = match.start()

                prompt_pos = 0
                for i, t in enumerate(self._ps1_groups):
                    if m.group(i + 1):
                        group_pos = m.start(i + 1)
                        before_content = line[prompt_pos:group_pos]
                        insertions.append((len(curcode), [(0, Generic.Prompt, before_content)]))

                        insertions.append((len(curcode), [(0, t, m.group(i + 1))]))
                        prompt_pos += len(before_content) + len(m.group(i+1))

                group_pos = m.start(4)
                before_content = line[prompt_pos:group_pos]
                insertions.append((len(curcode), [(0, Generic.Prompt, before_content)]))

                curcode += m.group(4)
                backslash_continuation = curcode.endswith('\\\n')

            # If line is a continuation of a previous line
            elif backslash_continuation:
                # If there is a continuation prompt, insert it
                if line.startswith(self._ps2):
                    insertions.append((len(curcode),
                                       [(0, Generic.Prompt,
                                         line[:len(self._ps2)])]))
                    curcode += line[len(self._ps2):]
                else:
                    curcode += line
                backslash_continuation = curcode.endswith('\\\n')

            # If line is a continuation of a previous line with bare_continuation
            elif self._bare_continuation and line.startswith(self._ps2):
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt,
                                     line[:len(self._ps2)])]))
                curcode += line[len(self._ps2):]

            # Otherwise, we have a normal line
            else:
                # Add insertions to the current code
                if insertions:
                    toks = innerlexer.get_tokens_unprocessed(curcode)
                    for i, t, v in do_insertions(insertions, toks):
                        # print(f"\n1. yielding pos={pos+i}, t={t}, v={v}")
                        yield pos+i, t, v

                if line.startswith('diff ') or diff_continuation:
                    diff_continuation = True
                    for i, t, v in difflexer.get_tokens_unprocessed(line):
                        # print(f"\n2. yielding pos={match.start()+i}, t={t}, v={v}")
                        yield match.start()+i, t, v
                elif curcode.startswith('git') or git_continuation:
                    git_continuation = True
                    for i, t, v in gitlexer.get_tokens_unprocessed(line):
                        # print(f"\n2. yielding pos={match.start()+i}, t={t}, v={v}")
                        yield match.start()+i, t, v
                else:
                    # print(f"\n3. yielding pos={match.start()}, t={Generic.Output}, v={line}")
                    yield match.start(), Generic.Output, line
                insertions = []
                curcode = ''

        if insertions:
            for i, t, v in do_insertions(insertions,
                                         innerlexer.get_tokens_unprocessed(curcode)):
                # print(f"\n4. yielding pos={pos+i}, t={t}, v={v}")
                yield pos+i, t, v
