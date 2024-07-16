'''## 异常处理
全局捕捉异常，并
- 在控制台打印
- 输出到文件
- 显示错误窗口(使用内置tkinter, 可关闭)
### code by: cc1287'''
import sys,tkinter,tkinter.ttk,base64
import traceback
from datetime import datetime

def exp(exc_type, exc_value, exc_traceback):
    if(exc_type.__name__=='KeyboardInterrupt'):
        return
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Time: [{current_time}]")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

    if log:
        with open(logName, 'a') as file:
            file.write(f"[{current_time}] Unhandled exception occurred:\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=file)

    if gui:
        root=tkinter.Tk()
        #head
        root.title(guiTitle)
        root.attributes('-toolwindow',True,'-topmost',True)
        root.geometry('330x375')
        root.bind('<Return>',lambda event:root.destroy)
        root.resizable(True,False)
        #body
        warning=tkinter.PhotoImage(data=base64.b64decode(
            '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'
        ))
        head=tkinter.Frame(root,height=75)
        tkinter.Label(head,image=warning).place(x=15,y=15)
        tkinter.Label(head,text=guiDescribe).place(x=60,y=25)
        head.pack(fill='x')
        tkinter.ttk.Separator(root,orient=tkinter.HORIZONTAL).pack(padx=6,fill='x')
        info=tkinter.LabelFrame(root,text='详细信息')
        tkinter.Label(info,text='错误堆栈').pack(anchor='w')
        dzf=tkinter.Frame(info)
        scrollbar = tkinter.Scrollbar(dzf, orient='vertical')
        scrollbar.pack(side=tkinter.RIGHT, fill='both')
        dz=tkinter.Text(dzf,height=10,background='#F0F0F0',yscrollcommand=scrollbar.set)
        dz.pack()
        scrollbar.config(command=dz.yview)
        dzf.pack(fill='x',padx=1)
        typ,inf=tkinter.StringVar(),tkinter.StringVar()
        tkinter.Label(info,text='错误类型').pack(anchor='w')
        tkinter.Entry(info,textvariable=typ,state='readonly').pack(fill='x',padx=1)
        tkinter.Label(info,text='错误信息').pack(anchor='w')
        tkinter.Entry(info,textvariable=inf,state='readonly').pack(fill='x',padx=1)
        info.pack(padx=6,fill='x')
        exits=tkinter.ttk.Button(root,text='退出程序',command=root.destroy)
        exits.pack(fill='x',side='right',padx=6)
        exits.focus_set()
        root.update()
        typ.set(exc_type.__name__)
        inf.set(exc_value)
        for line in traceback.TracebackException(
            type(exc_value), exc_value, exc_traceback, limit=None).format(chain=True):
            dz.insert(tkinter.END,line)
        dz.config(state='disabled')
        root.mainloop()
        
def init(setGui=True,setGuiTitle='错误',
         setGuiDescribe='程序遇到错误，给您带来不便，我们深表歉意。',
         setLog=True,setLogName='ErrorLog.txt'):
    '''#### 更改设置
    默认已经初始化，无需再次运行
    '''
    global gui,log,logName,guiTitle,guiDescribe
    gui,log,logName,guiTitle,guiDescribe=setGui,setLog,setLogName,setGuiTitle,setGuiDescribe
    sys.excepthook = exp
    
init()
if __name__ == '__main__':
    1/0