from prompt_toolkit import PromptSession
from ..dao import InstDao
from rich.console import Console
from prompt_toolkit.styles import Style as prompt_style
import os
from ..logic import InstCompleter, PrintHelp, Bindings, Execute

# 终端
class Terminal:
    style = prompt_style.from_dict({
        'name':   '#00FFFF',
        'prompt': '#FFFF00',
        'char':   '#ff0066',
        '':       '#FFF',
    })

    def __init__(self):
        self.insts = InstDao().SelectAllExist()
        self.session = PromptSession(completer=InstCompleter(self.insts), key_bindings=Bindings, style=self.style)
        self.console = Console()

    # 启动终端
    def Run(self):
        self.console.clear()
        self.console.print(
        """[#00FFFF]
      ____  ____________  ____________  ___ 
     / __ \/ __/_  __/ / / /_  __/ __ \/ _ \\
    / /_/ _\ \  / / / /_/ / / / / /_/ / , _/
    \____/___/ /_/  \____/ /_/  \____/_/|_| - OpenEuler Assistant. 
            [/#00FFFF]""")
        while True:
            curpath = os.getcwd()
            try:
                message = [
                    ('class:name', '[OSTutor] '),
                    ('class:prompt', f'{curpath}'),
                    ('class:char', ' > ')
                ]
                user_input = self.session.prompt(message=message)
                Execute(self, user_input)

            except KeyboardInterrupt:
                # Ctrl+C 捕获
                self.console.print('[green]Goodbye![/green]')
                break
            except EOFError:
                # 错误捕获，退出程序
                break
            