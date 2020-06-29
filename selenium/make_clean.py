import os
import shutil


def remove_dirs(path,index=1,parent=0):
    newindex=index+1
    filepath,tempfilename = os.path.split(path)
    if os.path.exists(path):
        if index==1:
            print('│ '*parent+"[{}]".format(tempfilename))
        else:
            print(' '+'│ '*(parent-1)+'├─'+"[{}]".format(tempfilename))
        if os.path.isdir(path):
            for filename in os.listdir(path):
                remove_dirs(os.path.join(path,filename),newindex,index)
            os.rmdir(path)
        else:
            os.remove(path)
    else:
        pass

def copy_file(src_path, dist_path):
    if os.path.exists(src_path):
        if os.path.exists(dist_path):
            print('[copy_file] '+dist_path + ' is exists,delete it')
            os.remove(dist_path)  
        shutil.copyfile(src_path, dist_path)
        print('[copy_file] Copy {} to {} success'.format(src_path, dist_path))
    else:
        print('[copy_file] {} :No such file or directory'.format(src_path))



if __name__ == '__main__':
    copy_file('dist/testsuit.exe','exe/testsuit.exe')

    copy_file('language.json','exe/language.json')

    if os.path.exists('build'):
        remove_dirs('build')

    if os.path.exists('dist'):
        remove_dirs('dist')

    if os.path.exists('testsuit.spec'):
        remove_dirs('testsuit.spec')

