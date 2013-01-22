#!/usr/bin/env python

import os
from pyinotify import WatchManager, IN_DELETE, IN_CREATE, IN_CLOSE_WRITE, ProcessEvent, Notifier
import sys

#Source code folder to monitor
source = os.getcwd()
folder = source+'/src' #sys.argv[1]

#plone admin user
user = 'admin' #sys.argv[2] 

#plone admin password
password = 'admin' #sys.argv[3] 

#hostname or ip
host = 'localhost' #sys.argv[4] 

#instance port
port = '8080' #sys.argv[5] 

pastas = os.listdir(folder)
caminho = []

for pasta in pastas:
    if  os.path.islink(folder+'/'+pasta):
        caminho.append(os.path.realpath(folder+'/'+pasta))
        
caminho.append(folder)

def call(arquivo):
    if arquivo.endswith('.zcml'):
        action = 'zcml'
        nome = 'ZCML'
    elif arquivo.endswith('.py'):
        action = 'code'
        nome = 'Python Script'
    else:
        #print 'Nao Precisa recarregar a instancia!! ' + arquivo
        return
    print 'Todos os arquivos \"',nome,'\" foram Recarregados!! - %s' %arquivo.split('/')[-1]
    os.system("wget --user='%s' --password='%s' 'http://%s:%s/@@reload?action=%s' -qO /dev/null " %(user, password, host, port, action))

class Process(ProcessEvent):
    def process_IN_DELETE(self, event):
        arquivo = os.path.join(event.path, event.name)
        if not arquivo.endswith('.pyc'):
            call(arquivo)

    def process_IN_CLOSE_WRITE(self, event):
        arquivo = os.path.join(event.path, event.name)
        if not arquivo.endswith('.pyc'):
            call(arquivo)
        
    def process_IN_CREATE(self, event):
        arquivo = os.path.join(event.path, event.name)
        if not arquivo.endswith('.pyc'):
            call(arquivo)
        

while True:
    wm = WatchManager()
    process = Process()
    notifier = Notifier(wm, process)
    mask = IN_DELETE | IN_CLOSE_WRITE | IN_CREATE
    wdd = wm.add_watch(caminho, mask, rec=True)
    try:
        while True:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        break

