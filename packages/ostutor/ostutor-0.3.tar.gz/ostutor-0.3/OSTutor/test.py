
def test_createdatabase():
    from src.dao import BaseDao
    BaseDao().createDatabase()

test_createdatabase()
def test_store():
    from src.data import storage
    storage.Storage().Store('411toppm.txt')

def test_parse_man():
    from src.data import Parse
    file = 'src/assets/man/' + 'cryptsetup.txt'
    data = Parse().parseMan(file)
    print(data)

def test_initdatabase():
    from src.data import Collection
    Collection().initdatabase()
# test_initdatabase()

def test_parsecontent():
    from src.data.parse import Parse
    text = """
       Reads a .411 file, such as from a Sony Mavic camera, and converts it to
       a PPM image as output.

       Output is to Standard Output.

       The originator of this program and decipherer of the .411 format, Steve
       Allen  <sla@alumni.caltech.edu>,  has  this to say about the utility of
       this program: "There's so little image in a 64x48 thumbnail (especially
       when you have the full size JPG file) that the only point in doing this
       was to answer the implicit challenge posed by the manual  stating  that
       only the camera can use these files."
    """
    data = Parse().parseContent(text=text)
    print(data)

def test_connect():
    """
    测试连接以及关闭耗时
    """
    from src.dao.entity import Inst
    from src.dao import InstDao
    import time
    s = time.time()
    d = 1
    i = InstDao()
    for c in range(0, 1000):
        with i.connect() as (conn, cur):
            pass

    end = time.time()
    print(end - s)

def test_collect():
    from src.data import Collection
    Collection().collect()

def test_collectnodata():
    from src.data import Collection
    Collection().collectNoDataInsts()

# 更新模型
def test_tdfidfinit():
    from src.data import Process
    Process().instDesc2csv()
    Process().tdIdfDataInit()
    
def test_tdfidfsearch():
    from src.logic import tfidf
    tfidf.search('edit')

def test_preprocessing():
    from src.data import Process
    text = 'This is an Examlpe sentence, showing off the stop words filtration.'
    print('text:\n' + text + '\n')
    print('new_text:\n' + Process().Preprocessing(text))

# 备份模型
def test_backup_file():
    from src.data import Process
    tvp = 'src/assets/pickle/tfidf_vectorizer.pickle'
    Process().backup_file(tvp)
    
# 创数据表
def test_add_table():
    from src.dao import BaseDao
    BaseDao().add_table()

def test_exportdata():
    from src.data import Export
    Export().exportDatabase()

def test_importdata():
    from src.data import Import
    Import().importDatabase()

def test_prompt_tookit():
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.formatted_text import FormattedText

    from src.dao import InstDao, InstExtraDao, OptDao
    from src.dao.entity import Inst
    from prompt_toolkit.key_binding import KeyBindings

    from src.view import display
    import curses
    

    # 定义按键绑定
    bindings = KeyBindings()

    # 定义一个函数，当按下 ! 时执行
    @bindings.add('?')
    def _(event):
        # 获取当前会话的输入缓冲区
        buffer = event.app.current_buffer
        # 读取当前输入的文本
        text = buffer.text
        curses.wrapper(display.display, [text])
       

    # 创建一个会话
    session = PromptSession(key_bindings=bindings)

    class MyCompleter(Completer):
        def __init__(self, insts):
            self.insts = {i.name:i.id for i in insts}
            self.briefs = {i.name:i.brief for i in insts}
            self.synopsis = {i.name:i.synopsis for i in insts}
        def get_completions(self, document, complete_event):
            text = document.current_line
            words = text.split(' ')

            if len(words) == 1:
                insts = [inst for inst in self.insts.keys() if inst.startswith(words[0])]
                for inst in insts:
                    brief = self.briefs[inst].split('-')[-1]
                    formatted_text = FormattedText([
                        ('fg:black', inst + ' '),  # 补全的实例名称
                        ('fg:grey italic',' - ' + brief)  # 实例的brief信息
                    ])
                    yield Completion(inst, start_position=-len(words[0]), display=formatted_text)

            else:
                if words[0] not in self.insts:
                    return
                
                formatted_text = FormattedText([
                        ('fg:blue italic',self.synopsis[words[0]]) 
                    ])
                yield Completion('', start_position=-len(words[-1]), display=formatted_text) # 显示语法
                
                opts = OptDao().SelectById(self.insts[words[0]])
                opts = {opt.name:opt.content for opt in opts}
                names = [opt for opt in opts.keys() if opt.startswith(words[-1])]
                
                for name in names:
                    formatted_text = FormattedText([
                        ('fg:black', name + ' '),  # 补全的实例名称
                        ('fg:grey italic',f'  {opts[name]}')  # 实例的brief信息
                    ])

                    yield Completion(name, start_position=-len(words[-1]), display=formatted_text)

    insts = InstDao().SelectAllExist()

    session = PromptSession('> ', completer=MyCompleter(insts), key_bindings=bindings)

    while True:
        user_input = session.prompt()
        print(user_input)

# test_tdfidfinit()