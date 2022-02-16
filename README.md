Shell Explorer is a shell that combines a command line interface (CLI) with a graphical user interface (GUI).

That is, it's essentially a combined unix shell + file explorer. Its intended use is as a tool for people learning basic unix command line, especially navigation and file/directory manipulation.

![interface](/resources/example.png)

As shown above, each command made either through the GUI or the CLI is simultaneously mirrored (or translated) to the other interface.

Built in Python (>= 3.7) with [Kivy](https://github.com/kivy/kivy). Packages `xclip` and `xsel` are also dependencies for Linux.

Run with `python shell_explorer.py`.

**Shell features**:
* [x] Basic commands
    * [x] ls, cd
    * [x] cp, mv
    * [x] touch, mkdir
    * [x] rm, rmdir
    * [ ] cat
* [x] History navigation (up/down arrows)
* [x] Handling dot (.) and double dot (..) in paths
* [x] Handling tilde (~) home shortcut in paths
* [ ] I/O Redirection
* [ ] Pipes
