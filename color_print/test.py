RED = '91m'
YELLOW = '93m'
BLUE = '94m'
GREEN = '92m'


def color_print(msg, color=RED, **kw):
    print('\033[0{}{}\033[0m'.format(color, msg), **kw)

if __name__ == '__main__':
    color_print('hello world red', color=RED)
    color_print('hello world green', color=GREEN)
    color_print('hello world blue', color=BLUE)
    color_print('hello world yellow', color=YELLOW)
    
    for i in range(108):
        print('\033[0{}m{}\033[0m'.format(i, i))
