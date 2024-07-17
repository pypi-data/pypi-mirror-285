"""An example plugin style for Pygments."""

from pygments.style import Style
from pygments.token import Token, Punctuation, Whitespace, \
    Text, Comment, Operator, Keyword, Name, String, Number, Generic
from pygments.styles.default import DefaultStyle

class ShellConsoleStyle(Style):
    styles = DefaultStyle.styles.copy()
    styles.update({
        Generic.Prompt.UserHost: "#008000",
        Generic.Prompt.Directory: "#19177C",
        Generic.Prompt.GitBranch: "#767600",
        Generic.Prompt.VirtualEnv: "#800000",

        Token.Git.BranchLine: "#f00",
        Token.Git.CommitHash: "#00f",
        Token.Git.CommitDate: "#008000",
        Token.Git.CommitMessage: "#FFFFFF",
        Token.Git.CommitAuthor: "#aaaaaa",
        Token.Git.Refs: "#00ffff",
    })
    del styles[Token.Generic.Prompt]
