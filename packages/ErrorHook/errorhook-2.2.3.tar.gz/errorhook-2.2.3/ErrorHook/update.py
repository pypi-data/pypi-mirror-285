import requests,sys,os
def check():
    print('正在检查更新')
    new_hash=requests.get('https://gitee.com/cc1287/error-hook/raw/master/ErrorHook/hash.file').text
    with open(os.path.dirname(sys.executable)+'\\Lib\\site-packages\\ErrorHook\\hash.file') as f:
        old_hash=f.read()
    print('检查完成')
    if old_hash!=new_hash:
        print('正在更新')
        os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade ErrorHook')
    else:
        print('无更新')
    os.system('pause')