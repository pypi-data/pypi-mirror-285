import zipfile
import os
import base64
from  pathlib import Path
from mtlibs.github_helper import Ghrepo
repo = Ghrepo(url='https://xbintor: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@github.com/xbintor/p')
IMGTAG='cli'
def on_command(args):
    """构建"""   
    # GHOWNER='xbintor'
    # GHTOKEN='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'
    

    # ghurl = "https://xbintor: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@github.com/xbintor/p"

    def ToBase64(file):
        with open(file, 'rb') as fileObj:
            image_data = fileObj.read()
            base64_data = base64.b64encode(image_data)
            fout = open(txt, 'w')
            fout.write(base64_data.decode())
            fout.close()
            


    print('构建压缩文件')
    zfName = './dist/mydata.zip'
    Path(zfName).parent.mkdir(exist_ok=True)
    
    foo = zipfile.ZipFile(zfName, 'w')
    for root, dirs, files in os.walk('data'):
        for f in files:
            foo.write(os.path.join(root, f))
    foo.close()

    print("生成base64py文件")

    with open(zfName, 'rb') as f:
        bin = f.read()
        base64Str = base64.b64encode(bin)
        pySrcCode = f'''def getZipBase64():
        return '{base64Str.decode()}'
    '''
    
    # with open('datazipSrc.py','w') as f:
    #     f.write(pySrcCode)

    # os.system('pyinstaller -F main.py -n main -i favicon.ico')
    # with open('./dist/main','rb') as f:
    #     repo.write_content('main',f.read())
    # os.system(f'echo {repo.token} | docker login ghcr.io -u USERNAME --password-stdin')    
    # os.system(f'docker build -t ghcr.io/{repo.owner}/{IMGTAG} .')
    # os.system(f'docker push ghcr.io/{repo.owner}/{IMGTAG}')


def pubgitrepo():
    """将编译好的发布到github仓库文件中（单个文件）"""
    with open('./dist/main','rb') as f:
        repo.write_content('main',f.read())

    # pyinstaller -F main.py -n main -i favicon.ico
    