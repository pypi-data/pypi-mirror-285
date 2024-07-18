import pygame as pg
import os
from pygame.locals import *
game_window=pg.display.set_mode((1000,600))#窗口大小
pg.init()

try:
    system_fond='fangsong'
    check_system=os.popen('uname')
    read_system=str(check_system.read())
    if read_system=='Darwin\n':
        system_fond='pingfang'
    elif read_system=='Linux\n':
        system_fond='Noto Serif CJK SC'
except:
    system_fond='fangsong'

def set_display(long,high):
    global game_window
    game_window=pg.display.set_mode((long,high))#窗口大小

def window_jump(txt,art):
    '''
    import pygame as pg
    import os
    game_window=pg.display.set_mode((1000,600))#窗口大小
    pg.init()

    try:
        system_fond='fangsong'
        check_system=os.popen('uname')
        read_system=str(check_system.read())
        if read_system=='Darwin\n':
            system_fond='pingfang'
        elif read_system=='Linux\n':
            system_fond='Noto Serif CJK SC'
    except:
        system_fond='fangsong'
    '''
    
    while True:
        game_window.fill("black")
        try:
            if 'background' in art:
                img=pg.image.load(str(art[0]))
                game_window.blit(img,(0,0))
        except:
            pass

        mouse_x,mouse_y=pg.mouse.get_pos()#鼠标位置
        mouse_presses=pg.mouse.get_pressed()

        if 'NOui' in art:
            pass
        else:
            pg.draw.rect(game_window,("white"),(300,200,400,200))
            pg.draw.rect(game_window,("gray"),(300,350,199,50))
            pg.draw.rect(game_window,("gray"),(501,350,199,50))
        if 'NOblackword' in art:
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,30)
            game_font=font.render(str(txt),True,("white"))
            game_window.blit(game_font,(305,205))
        else:
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,30)
            game_font=font.render(str(txt),True,("black"))
            game_window.blit(game_font,(305,205))

        if mouse_x>=300 and mouse_x<=500 and mouse_y>=350 and mouse_y<=400:
            pg.draw.rect(game_window,("orange"),(300,350,199,50))
            if mouse_presses[0]:
                print('n')
                return 'n'
        elif mouse_x>=500 and mouse_x<=700 and mouse_y>=350 and mouse_y<=400:
            pg.draw.rect(game_window,("orange"),(501,350,199,50))
            if mouse_presses[0]:
                print('y')
                return 'y'

        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,40)
        game_font=font.render(str("取消"),True,("white"))
        game_window.blit(game_font,(360,350))

        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,40)
        game_font=font.render(str("确定"),True,("white"))
        game_window.blit(game_font,(555,350))


        if 'Extend' in art:
            art[1]
        if 'Exec' in art:
            for i in art[1]:
                exec(str(i))

        for event in pg.event.get():
            if event.type==pg.QUIT:
                exit()#使用sys退出

        pg.display.update()

def input_word(txt,art):
    '''
    import pygame as pg
    import os
    from pygame.locals import KEYDOWN,K_1,K_2,K_3,K_4,K_5,K_6,K_7,K_8,K_9,K_9,K_0,K_BACKSPACE,K_RETURN,K_q,K_w,K_e,K_r,K_t,K_y,K_u,K_i,K_o,K_p,K_a,K_s,K_d,K_f,K_g,K_h,K_j,K_k,K_l,K_z,K_x,K_c,K_v,K_b,K_n,K_m,K_LSHIFT,KEYUP,K_RSHIFT,K_SPACE
    
    game_window=pg.display.set_mode((1000,600))#窗口大小
    pg.init()

    try:
        system_fond='fangsong'
        check_system=os.popen('uname')
        read_system=str(check_system.read())
        if read_system=='Darwin\n':
            system_fond='pingfang'
        elif read_system=='Linux\n':
            system_fond='Noto Serif CJK SC'
    except:
        system_fond='fangsong'
    '''

    word=''
    shift=0
    #light=False

    while True:
        light=False
        
        game_window.fill("black")
        try:
            if 'background' in art:
                img=pg.image.load(str(art[0]))
                game_window.blit(img,(0,0))
        except:
            pass

        mouse_x,mouse_y=pg.mouse.get_pos()#鼠标位置
        mouse_presses=pg.mouse.get_pressed()

        if 'NOui' in art:
            pass
        else:
            pg.draw.rect(game_window,("white"),(300,200,400,200))
            pg.draw.rect(game_window,("gray"),(300,350,199,50))
            pg.draw.rect(game_window,("gray"),(501,350,199,50))

            pg.draw.rect(game_window,("black"),(305,250,390,40))
            pg.draw.rect(game_window,("white"),(307,252,386,36))

        if 'NOblackword' in art:
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,30)
            game_font=font.render(str(txt),True,("white"))
            game_window.blit(game_font,(305,205))
        else:
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,30)
            game_font=font.render(str(txt),True,("black"))
            game_window.blit(game_font,(305,205))

        if 'NOhide' in art:
            light=True

        for event in pg.event.get():
            if event.type==KEYDOWN:
                try:
                    if event.key==K_1:
                        word+='1'
                    elif event.key==K_2:
                        word+='2'
                    elif event.key==K_3:
                        word+='3'
                    elif event.key==K_4:
                        word+='4'
                    elif event.key==K_5:
                        word+='5'
                    elif event.key==K_6:
                        word+='6'
                    elif event.key==K_7:
                        word+='7'
                    elif event.key==K_8:
                        word+='8'
                    elif event.key==K_9:
                        word+='9'
                    elif event.key==K_0:
                        word+='0'
                        
                    if shift==1:
                        if event.key==K_q:
                            word+='Q'
                    else:
                        if event.key==K_q:
                            word+='q'
                    if shift==1:
                        if event.key==K_w:
                            word+='W'
                    else:
                        if event.key==K_w:
                            word+='w'
                    if shift==1:
                        if event.key==K_e:
                            word+='E'
                    else:
                        if event.key==K_e:
                            word+='e'
                    if shift==1:
                        if event.key==K_r:
                            word+='R'
                    else:
                        if event.key==K_r:
                            word+='r'
                    if shift==1:
                        if event.key==K_t:
                            word+='T'
                    else:
                        if event.key==K_t:
                            word+='t'
                    if shift==1:
                        if event.key==K_y:
                            word+='Y'
                    else:
                        if event.key==K_y:
                            word+='y'
                    if shift==1:
                        if event.key==K_u:
                            word+='U'
                    else:
                        if event.key==K_u:
                            word+='u'
                    if shift==1:
                        if event.key==K_i:
                            word+='I'
                    else:
                        if event.key==K_i:
                            word+='i'
                    if shift==1:
                        if event.key==K_o:
                            word+='O'
                    else:
                        if event.key==K_o:
                            word+='o'
                    if shift==1:
                        if event.key==K_p:
                            word+='P'
                    else:
                        if event.key==K_p:
                            word+='p'
                    if shift==1:
                        if event.key==K_a:
                            word+='A'
                    else:
                        if event.key==K_a:
                            word+='a'
                    if shift==1:
                        if event.key==K_s:
                            word+='S'
                    else:
                        if event.key==K_s:
                            word+='s'
                    if shift==1:
                        if event.key==K_d:
                            word+='D'
                    else:
                        if event.key==K_d:
                            word+='d'
                    if shift==1:
                        if event.key==K_f:
                            word+='F'
                    else:
                        if event.key==K_f:
                            word+='f'
                    if shift==1:
                        if event.key==K_g:
                            word+='G'
                    else:
                        if event.key==K_g:
                            word+='g'
                    if shift==1:
                        if event.key==K_h:
                            word+='H'
                    else:
                        if event.key==K_h:
                            word+='h'
                    if shift==1:
                        if event.key==K_j:
                            word+='J'
                    else:
                        if event.key==K_j:
                            word+='j'
                    if shift==1:
                        if event.key==K_k:
                            word+='K'
                    else:
                        if event.key==K_k:
                            word+='k'
                    if shift==1:
                        if event.key==K_l:
                            word+='L'
                    else:
                        if event.key==K_l:
                            word+='l'
                    if shift==1:
                        if event.key==K_z:
                            word+='Z'
                    else:
                        if event.key==K_z:
                            word+='z'
                    if shift==1:
                        if event.key==K_x:
                            word+='X'
                    else:
                        if event.key==K_x:
                            word+='x'
                    if shift==1:
                        if event.key==K_c:
                            word+='C'
                    else:
                        if event.key==K_c:
                            word+='c'
                    if shift==1:
                        if event.key==K_v:
                            word+='V'
                    else:
                        if event.key==K_v:
                            word+='v'
                    if shift==1:
                        if event.key==K_b:
                            word+='B'
                    else:
                        if event.key==K_b:
                            word+='b'
                    if shift==1:
                        if event.key==K_n:
                            word+='N'
                    else:
                        if event.key==K_n:
                            word+='n'
                    if shift==1:
                        if event.key==K_m:
                            word+='M'
                    else:
                        if event.key==K_m:
                            word+='m'

                    if event.key==K_LSHIFT or event.key==K_RSHIFT:
                        shift=1

                    elif event.key==K_SPACE:
                        word+=' '
                        
                    elif event.key==K_BACKSPACE:
                        delete=list(word)
                        delete.pop(-1)
                        word=''
                        for i in delete:
                            word+=i
                    elif event.key==K_RETURN:
                        print(word)
                        return word
                        
                except:
                    print('未指定')
            if event.type==pg.QUIT:
                exit()#使用sys退出
            if event.type==KEYUP:
                if event.key==K_LSHIFT or event.key==K_RSHIFT:
                    shift=0
                
        if mouse_x>=300 and mouse_x<=500 and mouse_y>=350 and mouse_y<=400:
            pg.draw.rect(game_window,("orange"),(300,350,199,50))
            if mouse_presses[0]:
                print('n')
                return 'n'
        elif mouse_x>=500 and mouse_x<=700 and mouse_y>=350 and mouse_y<=400:
            pg.draw.rect(game_window,("orange"),(501,350,199,50))
            if mouse_presses[0]:
                print(word)
                return word

        if mouse_x>=305 and mouse_x<=405 and mouse_y>=285 and mouse_y<=330:
            pg.draw.rect(game_window,('orange'),(305,290,95,40))
            if mouse_presses[0]:
                light=True

        hidden=''
        for i in range(len(word)):
            hidden+='*'
        if light==False:
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,55)
            game_font=font.render(str(hidden),True,("black"))
            game_window.blit(game_font,(310,240))
        else:
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,40)
            game_font=font.render(str(word),True,("black"))
            game_window.blit(game_font,(310,248))

        if 'NOhide' not in art:
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,23)
            game_font=font.render(str('显示明文'),True,("black"))
            game_window.blit(game_font,(308,295))

        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,40)
        game_font=font.render(str("取消"),True,("white"))
        game_window.blit(game_font,(360,350))

        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,40)
        game_font=font.render(str("确定"),True,("white"))
        game_window.blit(game_font,(555,350))

        if 'Extend' in art:
            art[1]
        if 'Exec' in art:
            for i in art[1]:
                exec(str(i))

        pg.display.update()

def password(txt,passwd,art):
    import time,os
    while True:
        word=input_word(txt,art)
        time.sleep(0.1)
        if str(word)!=str(passwd) and str(word)!='n':
            window_jump('密码错误！请重试！',art)
            time.sleep(0.1)
        else:
            return str(word)

def choose_disk(txt,art):
    '''
    import pygame as pg
    import os
    game_window=pg.display.set_mode((1000,600))#窗口大小
    pg.init()

    try:
        system_fond='fangsong'
        check_system=os.popen('uname')
        read_system=str(check_system.read())
        if read_system=='Darwin\n':
            system_fond='pingfang'
        elif read_system=='Linux\n':
            system_fond='Noto Serif CJK SC'
    except:
        system_fond='fangsong'
    '''

    car=0
    choose=100

    list_check=['C:/','D:/','E:/','F:/','G:/','H:/','I:/','J:/','K:/']

    def icon(add_x,add_y,txt,car):
        
        for i in range(50):
            pg.draw.rect(game_window,('white'),(50-0.4*i+add_x,100+i+add_y,50+0.8*i,10))
        pg.draw.rect(game_window,('gray'),(50-0.4*50+add_x,100+50+add_y,50+0.8*50,15))
        pg.draw.rect(game_window,('white'),(50-0.4*44+add_x,100+52+add_y,50+0.8*45,11))
        if car<40:
            pg.draw.circle(game_window,('gray'),(41+add_x,158+add_y),4)
        else:
            pg.draw.circle(game_window,('green'),(41+add_x,158+add_y),5)

        if txt=='C:/ 驱动器':
            for i in range(50):
                pg.draw.rect(game_window,('blue'),(30+add_x+i,100+add_y-i*0.25,2,30+0.5*i))
            pg.draw.rect(game_window,('white'),(51+add_x,100+add_y,3,50))
            pg.draw.rect(game_window,('black'),(51+add_x,90+add_y,3,10))
            pg.draw.rect(game_window,('white'),(40+add_x,115+add_y,50,3))
            pg.draw.rect(game_window,('black'),(30+add_x,115+add_y,14,2))
            pg.draw.rect(game_window,('black'),(30+add_x,116+add_y,13,2))

        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,20)
        game_font=font.render(str(txt),True,("white"))
        game_window.blit(game_font,(48-0.4*i+add_x,164+add_y))

    while True:
        game_window.fill("black")
        try:
            if 'background' in art:
                img=pg.image.load(str(art[0]))
                game_window.blit(img,(0,0))
        except:
            pass

        mouse_x,mouse_y=pg.mouse.get_pos()#鼠标位置
        mouse_presses=pg.mouse.get_pressed()
        
        #defind & change
        car+=1
        if car>79:
            car=0

        list_menu=[]
            
        #end
            
        '''main'''
        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,40)
        game_font=font.render(str(txt),True,("white"))
        game_window.blit(game_font,(10,10))

        for i in list_check:
            try:
                os.listdir(i)
                list_menu.append(i)
            except:
                pass

        if mouse_x>=420-len(list_menu)*40 and mouse_x<419-len(list_menu)*40+120*(len(list_menu)) and mouse_y>=100 and mouse_y<=200:
            choose=(mouse_x-(420-len(list_menu)*40))//120

            pg.draw.rect(game_window,('orange'),(435-len(list_menu)*40+choose*120,100,120,100))

            #print(choose)
            
            if mouse_presses[0]:
                ask=window_jump('是否选择这个驱动器?',art)
                if ask=='y':
                    #print(list_menu[choose])
                    return list_menu[choose]
                else:
                    pass
        else:
            choose=100
            
        for i in list_menu:
            icon(420-len(list_menu)*40+120*int(list_menu.index(i)),10,i+' 驱动器',car)

        if choose==0:
            pg.draw.rect(game_window,('orange'),(51+420-len(list_menu)*40+120*0,90+10,3,10))
            pg.draw.rect(game_window,('orange'),(30+420-len(list_menu)*40+120*0,115+10,14,2))
            pg.draw.rect(game_window,('orange'),(30+420-len(list_menu)*40+120*0,116+10,13,2))
            
        '''end'''

        if 'Extend' in art:
            art[1]
        if 'Exec' in art:
            for i in art[1]:
                exec(str(i))

        for event in pg.event.get():
            if event.type==pg.QUIT:
                exit()#使用sys退出

        pg.display.update()


def progress(txt,done,long,art):
    '''
    import pygame as pg
    import os
    game_window=pg.display.set_mode((1000,600))#窗口大小
    pg.init()
    '''
    
    game_window.fill('black')

    pg.draw.rect(game_window,("white"),(300,200,400,200))
    
    font_name=pg.font.match_font('fangsong')
    font=pg.font.Font(font_name,30)
    game_font=font.render(str(txt),True,("black"))
    game_window.blit(game_font,(305,205))

    font_name=pg.font.match_font('fangsong')
    font=pg.font.Font(font_name,40)
    game_font=font.render(str('已完成:')+str(done/long*100)+'%',True,("black"))
    game_window.blit(game_font,(305,240))
    
    pg.draw.rect(game_window,(0,170,0),(300,360,(done/long*400),40))

    if 'Extend' in art:
        art[1]
    if 'Exec' in art:
        for i in art[1]:
            exec(str(i))

    pg.display.update()

def passage(txt,art):
    '''
    import pygame as pg
    import os
    game_window=pg.display.set_mode((1000,600))#窗口大小
    pg.init()

    try:
        system_fond='fangsong'
        check_system=os.popen('uname')
        read_system=str(check_system.read())
        if read_system=='Darwin\n':
            system_fond='pingfang'
        elif read_system=='Linux\n':
            system_fond='Noto Serif CJK SC'
    except:
        system_fond='fangsong'
    '''

    while True:
        game_window.fill("white")
        try:
            if 'background' in art:
                img=pg.image.load(str(art[0]))
                game_window.blit(img,(0,0))
        except:
            pass

        mouse_x,mouse_y=pg.mouse.get_pos()#鼠标位置
        mouse_presses=pg.mouse.get_pressed()

        #pg.draw.rect(game_window,("white"),(300,200,400,200))
        pg.draw.rect(game_window,("gray"),(300,550,199,50))
        pg.draw.rect(game_window,("gray"),(501,550,199,50))

        for i in range(len(txt)):
            if 'NOblackword' in art:
                font_name=pg.font.match_font(system_fond)
                font=pg.font.Font(font_name,25)
                game_font=font.render(str(txt[i]),True,("white"))
                game_window.blit(game_font,(10,i*25))
            else:
                font_name=pg.font.match_font(system_fond)
                font=pg.font.Font(font_name,25)
                game_font=font.render(str(txt[i]),True,("black"))
                game_window.blit(game_font,(10,i*25))

        if mouse_x>=300 and mouse_x<=500 and mouse_y>=550 and mouse_y<=600:
            pg.draw.rect(game_window,("orange"),(300,550,199,50))
            if mouse_presses[0]:
                print('n')
                return 'n'
        elif mouse_x>=500 and mouse_x<=700 and mouse_y>=550 and mouse_y<=600:
            pg.draw.rect(game_window,("orange"),(501,550,199,50))
            if mouse_presses[0]:
                print('y')
                return 'y'

        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,40)
        game_font=font.render(str("取消"),True,("white"))
        game_window.blit(game_font,(360,550))

        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,40)
        game_font=font.render(str("确定"),True,("white"))
        game_window.blit(game_font,(555,550))

        if 'Extend' in art:
            art[1]
        if 'Exec' in art:
            for i in art[1]:
                exec(str(i))

        for event in pg.event.get():
            if event.type==pg.QUIT:
                exit()#使用sys退出

        pg.display.update()

def display_file(path,art):
    '''
    import pygame as pg
    import os
    game_window=pg.display.set_mode((1000,600))#窗口大小
    pg.init()

    try:
        system_fond='fangsong'
        check_system=os.popen('uname')
        read_system=str(check_system.read())
        if read_system=='Darwin\n':
            system_fond='pingfang'
        elif read_system=='Linux\n':
            system_fond='Noto Serif CJK SC'
    except:
        system_fond='fangsong'
    '''

    while True:
        game_window.fill("white")
        try:
            if 'background' in art:
                img=pg.image.load(str(art[0]))
                game_window.blit(img,(0,0))
        except:
            pass

        mouse_x,mouse_y=pg.mouse.get_pos()#鼠标位置
        mouse_presses=pg.mouse.get_pressed()

        #pg.draw.rect(game_window,("white"),(300,200,400,200))
        pg.draw.rect(game_window,("gray"),(300,550,199,50))
        pg.draw.rect(game_window,("gray"),(501,550,199,50))
        try:
            show_file=open(path,encoding='utf-8')
            read_file=show_file.read()
            show_file.close()
        except:
            show_file.close()
            try:
                show_file=open(path,encoding='ANSI')
                read_file=show_file.read()
                show_file.close()
            except:
                show_file.close()
                show_file=open(path,'r')
                read_file=show_file.read()
                show_file.close()

        file_passage=[[]]
        passage_line=0

        if 'NOblackword' in art:
            for i in read_file:
                if i=='\n':
                    file_passage.append([])
                    passage_line+=1
                
                file_passage[int(passage_line)].append(str(i))

            for k in range(len(file_passage)):
                add_word=''
                for a in file_passage[k]:
                    if a!='\n':
                        add_word+=str(a)
                    
                font_name=pg.font.match_font(system_fond)
                font=pg.font.Font(font_name,25)
                game_font=font.render(str(add_word),True,("white"))
                game_window.blit(game_font,(10,k*25))
        else:
            for i in read_file:
                if i=='\n':
                    file_passage.append([])
                    passage_line+=1
                
                file_passage[int(passage_line)].append(str(i))

            for k in range(len(file_passage)):
                add_word=''
                for a in file_passage[k]:
                    if a!='\n':
                        add_word+=str(a)
                    
                font_name=pg.font.match_font(system_fond)
                font=pg.font.Font(font_name,25)
                game_font=font.render(str(add_word),True,("black"))
                game_window.blit(game_font,(10,k*25))
                    

        if mouse_x>=300 and mouse_x<=500 and mouse_y>=550 and mouse_y<=600:
            pg.draw.rect(game_window,("orange"),(300,550,199,50))
            if mouse_presses[0]:
                print('n')
                return 'n'
        elif mouse_x>=500 and mouse_x<=700 and mouse_y>=550 and mouse_y<=600:
            pg.draw.rect(game_window,("orange"),(501,550,199,50))
            if mouse_presses[0]:
                print('y')
                return 'y'

        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,40)
        game_font=font.render(str("取消"),True,("white"))
        game_window.blit(game_font,(360,550))

        font_name=pg.font.match_font(system_fond)
        font=pg.font.Font(font_name,40)
        game_font=font.render(str("确定"),True,("white"))
        game_window.blit(game_font,(555,550))

        if 'Extend' in art:
            art[1]
        if 'Exec' in art:
            for i in art[1]:
                exec(str(i))

        for event in pg.event.get():
            if event.type==pg.QUIT:
                exit()#使用sys退出

        pg.display.update()

def menu(choose,art):
    '''
    import pygame as pg
    import os
    game_window=pg.display.set_mode((1000,600))#窗口大小
    pg.init()

    try:
        system_fond='fangsong'
        check_system=os.popen('uname')
        read_system=str(check_system.read())
        if read_system=='Darwin\n':
            system_fond='pingfang'
        elif read_system=='Linux\n':
            system_fond='Noto Serif CJK SC'
    except:
        system_fond='fangsong'
    '''

    while True:
        game_window.fill('black')
        try:
            if 'background' in art:
                img=pg.image.load(str(art[0]))
                game_window.blit(img,(0,0))
        except:
            pass

        mouse_x,mouse_y=pg.mouse.get_pos()#鼠标位置
        mouse_presses=pg.mouse.get_pressed()

        for i in range(len(choose)):
            pg.draw.rect(game_window,('white'),(5,i*30+5,500,29))
            if mouse_x>=5 and mouse_x<=505 and mouse_y>=5 and mouse_y<=int(len(choose))*30+5:
                pg.draw.rect(game_window,('orange'),(5,(mouse_y-5)//30*30+5,500,29))
                
        for i in range(len(choose)):
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,26)
            game_font=font.render(str(choose[i]),True,("black"))
            game_window.blit(game_font,(10,i*30+6))

        if mouse_x>=5 and mouse_x<=505 and mouse_y>=5 and mouse_y<=int(len(choose))*30+5 and mouse_presses[0]:
            try:
                return (choose[(mouse_y-5)//30])
            except:
                pass

        if 'Extend' in art:
            art[1]
        if 'Exec' in art:
            for i in art[1]:
                exec(str(i))
            
        for event in pg.event.get():
            if event.type==pg.QUIT:
                exit()#使用sys退出

        pg.display.update()

def menus(choose,art):
    '''
    import pygame as pg
    import time,os
    game_window=pg.display.set_mode((1000,600))#窗口大小
    pg.init()

    try:
        system_fond='fangsong'
        check_system=os.popen('uname')
        read_system=str(check_system.read())
        if read_system=='Darwin\n':
            system_fond='pingfang'
        elif read_system=='Linux\n':
            system_fond='Noto Serif CJK SC'
    except:
        system_fond='fangsong'
    '''

    list1=list(choose)
    list1.append('确定')
    list1.append('取消')

    choose_mode=[]

    while True:
        game_window.fill('black')
        try:
            if 'background' in art:
                img=pg.image.load(str(art[0]))
                game_window.blit(img,(0,0))
        except:
            pass

        mouse_x,mouse_y=pg.mouse.get_pos()#鼠标位置
        mouse_presses=pg.mouse.get_pressed()

        for i in range(len(list1)):
            pg.draw.rect(game_window,('white'),(5,i*30+5,500,29))

            if i!=len(list1)-1 and i!=len(list1)-2:
                pg.draw.circle(game_window,('gray'),(485,i*30+20),12)
                pg.draw.circle(game_window,('white'),(485,i*30+20),10)
            #if list1[i] in choose_mode:
                #pg.draw.rect(game_window,('green'),(5,i*30+5,500,29))
            
            if mouse_x>=5 and mouse_x<=505 and mouse_y>=5 and mouse_y<=int(len(list1))*30+5:
                pg.draw.rect(game_window,('orange'),(5,(mouse_y-5)//30*30+5,500,29))
                
        for i in range(len(list1)):
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,26)
            game_font=font.render(str(list1[i]),True,("black"))
            game_window.blit(game_font,(10,i*30+6))

            if list1[i] in choose_mode:
                pg.draw.circle(game_window,('green'),(485,i*30+20),12)
                pg.draw.circle(game_window,('white'),(485,i*30+20),10)
                pg.draw.circle(game_window,('green'),(485,i*30+20),7)

        if mouse_x>=5 and mouse_x<=505 and mouse_y>=5 and mouse_y<=int(len(list1))*30+5 and mouse_presses[0]:
            try:
                if (list1[(mouse_y-5)//30]) not in choose_mode and (list1[(mouse_y-5)//30])!='确定':
                    choose_mode.append(list1[(mouse_y-5)//30])
                    time.sleep(0.1)
                elif (list1[(mouse_y-5)//30]) in choose_mode:
                    choose_mode.pop(choose_mode.index(list1[(mouse_y-5)//30]))

                if (list1[(mouse_y-5)//30])=='确定':
                    return choose_mode
                elif (list1[(mouse_y-5)//30])=='取消':
                    return 'n'
            except:
                pass
            time.sleep(0.1)
            print(choose_mode)

        if 'Extend' in art:
            art[1]
        if 'Exec' in art:
            for i in art[1]:
                exec(str(i))
            
        for event in pg.event.get():
            if event.type==pg.QUIT:
                exit()#使用sys退出

        pg.display.update()

def easyui(mode,choose,art):
    '''
    import pygame as pg
    import os
    game_window=pg.display.set_mode((1000,600))#窗口大小
    pg.init()

    try:
        system_fond='fangsong'
        check_system=os.popen('uname')
        read_system=str(check_system.read())
        if read_system=='Darwin\n':
            system_fond='pingfang'
        elif read_system=='Linux\n':
            system_fond='Noto Serif CJK SC'
    except:
        system_fond='fangsong'
    '''

    move_y=5
    set_move=0

    add_x_add=2

    while True:
        game_window.fill('black')
        try:
            if 'background' in art:
                img=pg.image.load(str(art[0]))
                game_window.blit(img,(0,0))
        except:
            pass

        mouse_x,mouse_y=pg.mouse.get_pos()#鼠标位置
        mouse_presses=pg.mouse.get_pressed()

        for i in range(len(mode)):
            pg.draw.rect(game_window,('white'),(5,i*30+5,200,29))
            if mouse_x>=5 and mouse_x<=205 and mouse_y>=5 and mouse_y<=int(len(mode))*30+5:
                pg.draw.rect(game_window,('orange'),(5,(mouse_y-5)//30*30+5,200,29))
                
        for i in range(len(mode)):
            font_name=pg.font.match_font(system_fond)
            font=pg.font.Font(font_name,26)
            game_font=font.render(str(mode[i]),True,("black"))
            game_window.blit(game_font,(10,i*30+6))

        if mouse_x>=5 and mouse_x<=205 and mouse_y>=5 and mouse_y<=int(len(mode))*30+5 and mouse_presses[0]:
            try:
                return (mode[(mouse_y-5)//30])
            except:
                pass
        ########################
        for i in range(len(choose)):
            pg.draw.rect(game_window,('white'),(215,i*30+move_y,700,29))
            try:
                if mouse_x>=215 and mouse_x<=915 and mouse_y>=move_y and mouse_y<=int(len(choose))*30+move_y and '#' not in (choose[(mouse_y-move_y)//30]):
                    pg.draw.rect(game_window,('orange'),(215,(mouse_y-move_y)//30*30+move_y,700,29))
            except:
                pass
                
        for i in range(len(choose)):
            if '#' in choose[i]:
                font_name=pg.font.match_font(system_fond)
                font=pg.font.Font(font_name,26)
                game_font=font.render(str(choose[i]),True,("gray"))
                game_window.blit(game_font,(220,i*30+1+move_y))
            else:
                font_name=pg.font.match_font(system_fond)
                font=pg.font.Font(font_name,26)
                game_font=font.render(str(choose[i]),True,("black"))
                game_window.blit(game_font,(220,i*30+1+move_y))

        if mouse_x>=5 and mouse_x<=915 and mouse_y>=move_y and mouse_y<=int(len(choose))*30+move_y and mouse_presses[0] and '#' not in (choose[(mouse_y-move_y)//30]):
            try:
                return (choose[(mouse_y-move_y)//30])
            except:
                pass
            
        ########################
        if len(choose)>=20:
            pg.draw.rect(game_window,'gray',(960,0,30,600))
            pg.draw.rect(game_window,'white',(960,set_move,30,90))
            if mouse_x>=960 and mouse_x<=990 and mouse_y>=set_move and mouse_y<=set_move+90:
                pg.draw.rect(game_window,'black',(962,set_move+2,26,86))
                pg.draw.rect(game_window,'white',(965,set_move+5,20,80))
                if mouse_presses[0]:
                    set_move=mouse_y-45
                    move_y=5-set_move*add_x_add
            
            if set_move<0:
                set_move=0
                move_y=5
            elif set_move>510:
                set_move=510
                move_y=-505*add_x_add

        if 'Extend' in art:
            art[1]
        if 'Exec' in art:
            for i in art[1]:
                exec(str(i))
            
        for event in pg.event.get():
            if event.type==pg.QUIT:
                exit()#使用sys退出

        pg.display.update()

def writer_information():
    word=password('开发者密码:','123098',())
    if word=='123098':
        passage(('llllllllllllllll','llllllllllllllll','    llllOOOOllll','    llllOOOOllll','    llllllllllllllll','    llllllllllllllll','','','鱼子酱制作','yuzichen!yyds!','','yuui 基于 pygame，作者承诺永远开源免费！','yuui 2024.6.8 版本'),())
    else:
        pass

def information():
    passage(('YUZIJIANG made (MADE IN CHAIN)','','Based on pygame.','FREE to everyone.','Let pygame begin easily!','','YUUI 2024.6.8'),())

#writer_information()
#print(easyui(('第一页','第二页'),('#第一类','第二项'),()))#,('data/image/1702038319304.jpg','background','NOblackword')))
