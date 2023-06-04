import pygame, sys
from pygame.locals import *
import time
import random
import copy
 
# game parameters
pygame.init()
win_width, win_height = 930, 700
displaysurf = pygame.display.set_mode((win_width, win_height), 0, 32)
pygame.display.set_caption('Connect_4')
 
# color parameters
backgroundcolor_chess = (244, 171, 102)
color_white = (255, 255, 255)
color_black = (0, 0, 0)
color_tip_white = (225, 225, 225)
color_tip_black = (25, 25, 25)
color_green = (0, 255, 0)
 
# chess parameters
chess_grid_row, chess_grid_col = 6, 8
chess_list = []
for i in range(chess_grid_row):
    new_line = [0 for j in range(chess_grid_col)]
    chess_list.append(new_line)
player = True
play_flag = False
 
# draw chessboard
def draw_chessboard():
    displaysurf.fill(color_white)
    fontobj = pygame.font.SysFont('SimHei',70)
    text = fontobj.render("重力四子棋", True, color_black, color_white)
    textrect = text.get_rect()
    textrect.center = (430, 70)
    displaysurf.blit(text, textrect)
    pygame.draw.rect(displaysurf, backgroundcolor_chess, (50, 170, 640, 480))
    for pix_row in range(7):
        pygame.draw.line(displaysurf, color_black, (50, 170 + pix_row * 80), (690, 170 + pix_row * 80))
    for pix_col in range(9):
        pygame.draw.line(displaysurf, color_black, (50 + pix_col * 80, 170), (50 + pix_col * 80, 650))
 
def draw_tip_chess(mousex, mousey, type):
    for row in range(chess_grid_row):
        for col in range(chess_grid_col):
            if chess_list[row][col] in [3, 4]:
                chess_list[row][col] = 0
    col = int((mousex - 50) / 80)
    row = int((mousey - 170) / 80)
    if row == chess_grid_row:
        row -= 1
    if col == chess_grid_col:
        col -= 1
    if row < chess_grid_row - 1:
        if chess_list[row + 1][col] == 0:
            return
    if chess_list[row][col] == 0:
        chess_list[row][col] = type
 
def clear_tip_chess():
    for row in range(chess_grid_row):
        for col in range(chess_grid_col):
            if chess_list[row][col] in [3, 4]:
                chess_list[row][col] = 0
 
def draw_check_chess(mousex, mousey, type):
    for row in range(chess_grid_row):
        for col in range(chess_grid_col):
            if chess_list[row][col] in [3, 4]:
                chess_list[row][col] = 0
    col = int((mousex - 50) / 80)
    row = int((mousey - 170) / 80)
    if row == chess_grid_row:
        row -= 1
    if col == chess_grid_col:
        col -= 1
    if row < chess_grid_row - 1:
        if chess_list[row + 1][col] == 0:
            return
    if chess_list[row][col] in [1, 2]:
        return False
    else:
        chess_list[row][col] = type
        return True
 
def draw_chess():
    for row in range(chess_grid_row):
        for col in range(chess_grid_col):
            if chess_list[row][col] == 0:
                pygame.draw.circle(displaysurf, backgroundcolor_chess, (90 + col * 80, 210 + row * 80), 38)
            elif chess_list[row][col] == 1:
                pygame.draw.circle(displaysurf, color_black, (90 + col * 80, 210 + row * 80), 38)
            elif chess_list[row][col] == 2:
                pygame.draw.circle(displaysurf, color_white, (90 + col * 80, 210 + row * 80), 38)
            elif chess_list[row][col] == 3:
                pygame.draw.circle(displaysurf, color_tip_black, (90 + col * 80, 210 + row * 80), 38)
            elif chess_list[row][col] == 4:
                pygame.draw.circle(displaysurf, color_tip_white, (90 + col * 80, 210 + row * 80), 38)
 
def is_win(temp_chess_list):
    not_null_sum = 0
    for row in range(chess_grid_row):
        for col in range(chess_grid_col):
            if temp_chess_list[row][col] in [3, 4]:
                temp_chess_list[row][col] = 0
            if temp_chess_list[row][col] != 0:
                not_null_sum += 1
 
            # horizontal
            if col < chess_grid_col - 3:
                if temp_chess_list[row][col] == temp_chess_list[row][col + 1] == temp_chess_list[row][col + 2] == \
                        temp_chess_list[row][col + 3] and temp_chess_list[row][col] != 0:
                    return temp_chess_list[row][col]
            # vertical
            if row < chess_grid_row - 3:
                if temp_chess_list[row][col] == temp_chess_list[row + 1][col] == temp_chess_list[row + 2][col] == \
                        temp_chess_list[row + 3][col] and temp_chess_list[row][col] != 0:
                    return temp_chess_list[row][col]
            # right slant
            if col < chess_grid_col - 3 and row < chess_grid_row - 3:
                if temp_chess_list[row][col] == temp_chess_list[row + 1][col + 1] == temp_chess_list[row + 2][
                    col + 2] == \
                        temp_chess_list[row + 3][col + 3] and temp_chess_list[row][col] != 0:
                    return temp_chess_list[row][col]
            # left slant
            if col >= 3 and row < chess_grid_row - 3:
                if temp_chess_list[row][col] == temp_chess_list[row + 1][col - 1] == temp_chess_list[row + 2][
                    col - 2] == \
                        temp_chess_list[row + 3][col - 3] and temp_chess_list[row][col] != 0:
                    return temp_chess_list[row][col]
    if not_null_sum == chess_grid_row*chess_grid_col:
        return 3
    return 0
 
 
def AI(chess_list, type):
    node_list = []
    chess_null_sum = 0
    for col in range(chess_grid_col):
        for row in range(chess_grid_row):
            if chess_list[row][col] == 0:
                chess_null_sum += 1
                if row == chess_grid_row -1:
                    temp_chess_list = copy.deepcopy(chess_list)
                    temp_chess_list[row][col] = type
                    node_list.append([row, col])
                    flag = is_win(temp_chess_list)
                    if flag != 0:
                        chess_list[row][col] = type
                        return row, col
                elif chess_list[row+1][col] != 0:
                    temp_chess_list = copy.deepcopy(chess_list)
                    temp_chess_list[row][col] = type
                    node_list.append([row, col])
                    flag = is_win(temp_chess_list)
                    if flag != 0:
                        chess_list[row][col] = type
                        return row, col
    print(node_list)
    range_sum = 500 + int((chess_grid_row*chess_grid_col-chess_null_sum)/(chess_grid_row*chess_grid_col)*100)
    print(range_sum)
    win_list = [0 for j in range(chess_grid_col)]
    tip_list = [0 for j in range(chess_grid_col)]
    start = time.perf_counter()
    for i in range(len(node_list)):
        for j in range(100):
            temp_type = type
            temp_chess_list = copy.deepcopy(chess_list)
            temp_node_list = copy.deepcopy(node_list)
            temp_chess_list[temp_node_list[i][0]][temp_node_list[i][1]] = temp_type
            flag_win = is_win(temp_chess_list)
            if flag_win != 0:
                if flag_win == type:
                    win_list[i] += 1
                continue
            elif flag_win == 3:
                tip_list[i] += 1
            if temp_node_list[i][0] == 0:
                del temp_node_list[i]
            else:
                temp_node_list[i][0] -= 1
            while True:
                if temp_type == 1:
                    temp_type = 2
                else:
                    temp_type = 1
                try:
                    temp_index = random.randint(0, len(temp_node_list)-1)
                except:
                    break
                temp_chess_list[temp_node_list[temp_index][0]][temp_node_list[temp_index][1]] = temp_type
                flag_win = is_win(temp_chess_list)
                if flag_win != 0:
                    if flag_win == type:
                        win_list[i] += 1
                    elif flag_win == 3:
                        tip_list[i] += 1
                    break
                if temp_node_list[temp_index][0] == 0:
                    del temp_node_list[temp_index]
                else:
                    temp_node_list[temp_index][0] -= 1
    end = time.perf_counter()
    print(end - start)
    if max(win_list) > range_sum*0.1:
        print(win_list)
        check = win_list.index(max(win_list))
        print(node_list)
        print(check)
    else:
        check = tip_list.index(max(tip_list))
        print("选择平局")
    chess_list[node_list[check][0]][node_list[check][1]] = type
 
def draw_player(player):
    fontobj = pygame.font.SysFont('SimHei', 25)
    if player:
        text = fontobj.render("先手： 电脑    棋色： 黑色", True, color_black, color_white)
    else:
        text = fontobj.render("先手： 玩家    棋色： 黑色", True, color_black, color_white)
    textrect = text.get_rect()
    textrect.center = (260, 140)
    displaysurf.blit(text, textrect)
 
def button():
    pygame.draw.rect(displaysurf, color_green, (730, 200, 160, 80))
    fontobj1 = pygame.font.SysFont('SimHei', 30)
    text1 = fontobj1.render("切换先手", True, color_white, color_green)
    textrect1 = text1.get_rect()
    textrect1.center = (810, 240)
    displaysurf.blit(text1, textrect1)
 
    pygame.draw.rect(displaysurf, color_green, (730, 360, 160, 80))
    fontobj2 = pygame.font.SysFont('SimHei', 30)
    if play_flag == False:
        text2 = fontobj2.render("开始游戏", True, color_white, color_green)
    else:
        text2 = fontobj2.render("暂停游戏", True, color_white, color_green)
    textrect2 = text2.get_rect()
    textrect2.center = (810, 400)
    displaysurf.blit(text2, textrect2)
 
    pygame.draw.rect(displaysurf, color_green, (730, 520, 160, 80))
    fontobj3 = pygame.font.SysFont('SimHei', 30)
    text3 = fontobj3.render("重置游戏", True, color_white, color_green)
    textrect3 = text3.get_rect()
    textrect3.center = (810, 560)
    displaysurf.blit(text3, textrect3)
 
def play_type():
    fontobj = pygame.font.SysFont('SimHei', 25)
    if play_flag == False:
        win_flag = is_win(chess_list)
        pygame.draw.rect(displaysurf, color_white, (400, 120, 300, 45))
        if win_flag == 0:
            text = fontobj.render("状态： 未开始游戏", True, color_black, color_white)
        elif win_flag == 1:
            if player:
                text = fontobj.render("状态： 电脑胜利", True, color_black, color_white)
            else:
                text = fontobj.render("状态： 玩家胜利", True, color_black, color_white)
        elif win_flag == 2:
            if player:
                text = fontobj.render("状态： 玩家胜利", True, color_black, color_white)
            else:
                text = fontobj.render("状态： 电脑胜利", True, color_black, color_white)
        elif win_flag == 3:
            text = fontobj.render("状态： 平局", True, color_black, color_white)
    else:
        null_sum = 0
        for row in range(chess_grid_row):
            for col in range(chess_grid_col):
                if chess_list[row][col] in [0, 3, 4]:
                    null_sum += 1
        if player:
            if (chess_grid_row*chess_grid_col-null_sum) % 2 == 0:
                text = fontobj.render("状态： 请电脑落子", True, color_black, color_white)
            else:
                text = fontobj.render("状态： 请玩家落子", True, color_black, color_white)
        else:
            if (chess_grid_row*chess_grid_col-null_sum) % 2 == 1:
                text = fontobj.render("状态： 请电脑落子", True, color_black, color_white)
            else:
                text = fontobj.render("状态： 请玩家落子", True, color_black, color_white)
    textrect = text.get_rect()
    textrect.center = (570, 140)
    displaysurf.blit(text, textrect)
 
def new_play():
    global player, play_flag
    draw_chessboard()
    # AI(chess_list, 1)
    # main game loop
    while True:
        for event in pygame.event.get():
            # close game
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
                if play_flag:
                    if mousex > 50 and mousex < 690 and mousey > 170 and mousey < 730:
                        if player:
                            draw_tip_chess(mousex, mousey, 4)
                        else:
                            draw_tip_chess(mousex, mousey, 3)
                    else:
                        clear_tip_chess()
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if play_flag:
                    if mousex > 50 and mousex < 690 and mousey > 170 and mousey < 730:
                        if player:
                            flag = draw_check_chess(mousex, mousey, 2)
                            draw_chess()
                            pygame.display.update()
                            if flag:
                                if is_win(chess_list) != 0:
                                    play_flag = False
                                play_type()
                                pygame.display.update()
                                if play_flag:
                                    AI(chess_list, 1)
                            if is_win(chess_list) != 0:
                                play_flag = False
                        else:
                            flag = draw_check_chess(mousex, mousey, 1)
                            draw_chess()
                            pygame.display.update()
                            if flag:
                                if is_win(chess_list) != 0:
                                    play_flag = False
                                play_type()
                                pygame.display.update()
                                if play_flag:
                                    AI(chess_list, 2)
                            if is_win(chess_list) != 0:
                                play_flag = False
                else:
                    if mousex > 730 and mousex < 890 and mousey > 200 and mousey < 280:
                        if is_win(chess_list) == 0:
                            if player:
                                player = False
                            else:
                                player = True
                            draw_player(player)
                if mousex > 730 and mousex < 890 and mousey > 360 and mousey < 440:
                    if play_flag:
                        play_flag = False
                    else:
                        if is_win(chess_list) == 0:
                            play_flag = True
                            play_type()
                            button()
                            pygame.display.update()
                            if player and sum(chess_list[-1]) == 0:
                                AI(chess_list, 1)
                elif mousex > 730 and mousex < 890 and mousey > 520 and mousey < 600:
                    play_flag = False
                    for row in range(chess_grid_row):
                        for col in range(chess_grid_col):
                                chess_list[row][col] = 0
 
        draw_player(player)
        button()
        draw_chess()
        play_type()
        pygame.display.update()
 
def main():
    new_play()
 
 
main()
 