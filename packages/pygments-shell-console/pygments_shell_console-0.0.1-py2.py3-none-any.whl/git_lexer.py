"""An example plugin lexer for Pygments."""

from pygments.lexer import Lexer
from pygments.lexer import RegexLexer, ExtendedRegexLexer, include, bygroups, \
    default, using, line_re, do_insertions
from pygments.token import Token, Punctuation, Whitespace, \
    Text, Comment, Operator, Keyword, Name, String, Number, Generic
from pygments.lexers.diff import DiffLexer
from pygments.token import STANDARD_TYPES

import re

__all__ = ['GitLexer']

STANDARD_TYPES.update({
    Token.Git: 'git',
    Token.Git.BranchLine: 'git-bl',
    Token.Git.CommitHash: 'git-ch',
    Token.Git.CommitDate: 'git-cd',
    Token.Git.CommitMessage: 'git-cm',
    Token.Git.CommitAuthor: 'git-ca',
    Token.Git.Refs: 'git-r',
})

class GitLexer(Lexer):
    name = "Git"
    aliases = ["git"]
    filenames = ['*.git']
    version_added = '1.0'

    _branch_line_rgx = r'([\|\\\/ ]*)'
    _logrgx_groups = [
      _branch_line_rgx,     # Branch line
      r'(\*)',          # Commit asterisk
      _branch_line_rgx,     # Branch line
      r'( +)',          # Space
      r'([a-f0-9]+)',   # Commit hash
      r'( +- +)',       # Commit separator
      r'(\([0-9A-Za-zÀ-ÖØ-öø-ÿ ]+\))', # Date
      r'(\s+[0-9A-Za-zÀ-ÖØ-öø-ÿ \.\:\_\'\"\!\?\(\)\\\/\-]+ +- +)', # Commit message
      r'([0-9A-Za-zÀ-ÖØ-öø-ÿ ]+)', # Author
      r'((\([\w ->,:]+\))?)', # Refs
      r'$', # End
    ]

    # Combine the regex patterns into a single pattern
    _logrgx = re.compile(r''.join(_logrgx_groups))

    _log_tokens = {
      1: Token.Git.BranchLine,
      3: Token.Git.BranchLine,
      4: Whitespace,
      5: Token.Git.CommitHash,
      7: Token.Git.CommitDate,
      8: Token.Git.CommitMessage,
      9: Token.Git.CommitAuthor,
      10: Token.Git.Refs,
    }

    def get_tokens_unprocessed(self, text):
        pos = 0

        for match in line_re.finditer(text):
            line = match.group()

            match_log = self._logrgx.match(line)
            match_branch_line = re.match(r'^' + self._branch_line_rgx + r'$', line)

            ## Line is log
            if match_log:
                for i in range(1, len(match_log.groups())):
                    if match_log.group(i):
                        if self._log_tokens.get(i):
                            yield match_log.start(i), self._log_tokens[i], match_log.group(i)
                        else:
                            yield match_log.start(i), Generic.Output, match_log.group(i)
                yield match.end(), Whitespace, '\n'
            elif match_branch_line:
                yield match.start(), Token.Git.BranchLine, line

            else:
                yield match.start(), Generic.Output, line
