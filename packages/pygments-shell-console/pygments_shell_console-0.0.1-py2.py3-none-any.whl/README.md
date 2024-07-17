# Pygments Shell Console

This Pygments plugin adds new lexers for shell console output. The lexers are:
- `ShellConsoleLexer`: Based in [`ShellSessionBaseLexer`](https://github.com/pygments/pygments/blob/master/pygments/lexers/shell.py#L151C7-L151C28),
    extends its behavior to recognize the prompt elements and use `DiffLexer` and `GitLexer` for highlighting.
- `GitLexer`: Adds support for highlighting git log output, following the format:
    ```
    log --graph --abbrev-commit --decorate --format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(bold yellow)%d%C(reset)'
    ```
