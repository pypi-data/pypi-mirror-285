This is a gui program.You can use it to make gui program.

You can get it on http//pypi.org
If you find some problem,you can send problem to 'Toy142hjkl@hotmail.com'

These are some help and usage for you:

'''
import yuui as yu
yu.window_jump(str(word),art)
'''

art is a tuple,you can join word such as:
'background' it allow you add a picture on the program,but path must at first,for example:

'''
yu.window_jump('example',('C:/users/...',background)
'''

if you picture is beautiful,you can remove many ui,'NOui' can do it

'''
yu.window_jump('example',('NOui'))
'''

if you picture is black,but words are black too.you can add 'NOblackword'

All 'Art' options on it 




You also can use 'input_word' to input some numbers:
'''
yu.input_word('example',art)
'''

You also can use 'password' to set password:
'''
yu.password('information','password',art)
'''

You also can use 'choose_disk' to show some WINDOWS drives:
'''
yu.choose_disk('information',art)
'''

You also can use 'passage' to write passage:
'''
yu.passage([list],art)#everyone in [list] is a line.
'''


Options mode is like 'menu' or 'menus' and 'easyui'

'menu' can let you to choose options,'menus' can let you choose more
'easyui' can show double menu!

'''
import yuui
yuui.menu([list],art)
yuui.menus([list],art)
yuui.easyui([list],[list],art)
'''

2024.6.23 version fix a bug about font,More system can display more language
2024.6.27 allow users display file such as '.txt',you can use it following:
        '''
        yuui.display_file('path',art)
        '''
2024.7.1 version fix a bug about display file.and you can make a progress program
   for example:
        '''
        yuui.progress('word',int(done),int(all_work))
        '''
2024.7.5 version add a new mode ,you can add code in art,code must in a list or tuple and in second in art,the first must be 'Exec'

for example:
        '''
        code=['a=0','print(a)']
        yuui.window_jump('txt',('Exec',code))
        '''

Thank you to read it!

writer:yuzijiang