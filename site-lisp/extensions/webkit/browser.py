#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2014 Andy Stewart
# 
# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from PyQt5 import QtCore
from PyQt5.QtCore import QCoreApplication, QEvent
if os.name == 'posix':
    QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads, True)
    
from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtWebKit import  QWebSettings
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl, Qt
from PyQt5 import QtGui
import time
import os
from epc.server import ThreadingEPCServer
import threading
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QImage
import functools

def get_parent_dir(filepath, level=1):
    '''
    Get parent directory with given return level.
    
    @param filepath: Filepath.
    @param level: Return level, default is 1
    @return: Return parent directory with given return level. 
    '''
    parent_dir = os.path.realpath(filepath)
    
    while(level > 0):
        parent_dir = os.path.dirname(parent_dir)
        level -= 1
    
    return parent_dir

class postGui(QtCore.QObject):
    
    throughThread = QtCore.pyqtSignal(object, object)    
    
    def __init__(self, inclass=True):
        super(postGui, self).__init__()
        self.throughThread.connect(self.onSignalReceived)
        self.inclass = inclass
        
    def __call__(self, func):
        self._func = func
        
        @functools.wraps(func)
        def objCall(*args, **kwargs):
            self.emitSignal(args, kwargs)
        return objCall
        
    def emitSignal(self, args, kwargs):
        self.throughThread.emit(args, kwargs)
                
    def onSignalReceived(self, args, kwargs):
        if self.inclass:
            obj, args = args[0], args[1:]
            self._func(obj, *args, **kwargs)
        else:    
            self._func(*args, **kwargs)
            
class BrowserBuffer(QWebView):

    redrawScreenshot = QtCore.pyqtSignal(object)
    
    def __init__(self, buffer_id, buffer_width, buffer_height):
        super(BrowserBuffer, self).__init__()
        
        self.buffer_id = buffer_id
        self.buffer_width = buffer_width
        self.buffer_height = buffer_height
        
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.page().linkClicked.connect(self.link_clicked)
        self.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self.settings().setUserStyleSheetUrl(QUrl.fromLocalFile(os.path.join(get_parent_dir(__file__), "scrollbar.css")))
        self.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        
        self.view_list = []
        self.resize(self.buffer_width, self.buffer_height)
        
    def eventFilter(self, obj, event):
        if event.type() in [QEvent.KeyPress, QEvent.KeyRelease,
                            QEvent.MouseButtonPress, QEvent.MouseButtonRelease,
                            QEvent.MouseMove, QEvent.MouseButtonDblClick, QEvent.Wheel,
                            QEvent.InputMethod, QEvent.InputMethodQuery, QEvent.ShortcutOverride,
                            QEvent.ActivationChange, QEvent.Enter, QEvent.WindowActivate,
                            ]:
            QApplication.sendEvent(self, event)
        else:
            if event.type() not in [12, 77]:
                print event.type(), event
        
        return False
        
    @postGui()
    def redraw(self):
        qimage = QImage(self.buffer_width, self.buffer_height, QImage.Format_ARGB32)
        self.render(qimage)
        
        self.redrawScreenshot.emit(qimage)
        
    def add_view(self, view):
        if view not in self.view_list:
            self.view_list.append(view)
            
    def remove_view(self, view):
        if view in self.view_list:
            self.view_list.remove(view)
            
    @postGui()    
    def open_url(self, url):    
        self.load(QUrl(url))
        
    def link_clicked(self, url):
        self.load(url)
        
class BrowserView(QWidget):
    def __init__(self, browser_buffer):
        super(BrowserView, self).__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self.setContentsMargins(0, 0, 0, 0)
        
        browser_buffer.add_view(self)
        browser_buffer.redrawScreenshot.connect(self.updateView)
        
        self.qimage = None
        
        self.installEventFilter(browser_buffer)
        
    def paintEvent(self, event):    
        if self.qimage:
            painter = QPainter(self)
            painter.drawImage(QtCore.QRect(0, 0, self.width(), self.height()), self.qimage)
            painter.end()
        else:
            painter = QPainter(self)
            painter.setBrush(QtGui.QColor(255, 255, 255, 255))
            painter.drawRect(0, 0, self.width(), self.height())
            painter.end()
        
    @postGui()
    def updateView(self, qimage):
        self.qimage = qimage
        self.update()
        
    @postGui()    
    def moveresize(self, emacs_xid, x, y, w, h):
        self.resize(w, h)
        self.reparent(emacs_xid, x, y)
        
    def reparent(self, emacs_xid, x, y):
        from Xlib import display
        xlib_display = display.Display()
        
        browser_xid = self.winId().__int__()
        browser_xwindow = xlib_display.create_resource_object("window", int(browser_xid))
        emacs_xwindow = xlib_display.create_resource_object("window", int(emacs_xid))
        
        browser_xwindow.reparent(emacs_xwindow, x, y)
        xlib_display.sync()
        
if __name__ == '__main__':
    import sys
    import signal
    
    app = QApplication(sys.argv)
    
    server = ThreadingEPCServer(('localhost', 0), log_traceback=True)
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.allow_reuse_address = True
    
    buffer_dict = {}
    
    # NOTE: every epc method must should wrap with postGui.
    # Because epc server is running in sub-thread.
    @postGui(False)        
    def create_buffer(buffer_id, buffer_url, buffer_width, buffer_height):
        if not buffer_dict.has_key(buffer_id):
            buffer = BrowserBuffer(buffer_id, buffer_width, buffer_height)
            buffer.open_url(buffer_url)
            buffer_dict[buffer_id] = buffer
            
    @postGui(False)        
    def create_view(buffer_id, emacs_xid, x, y, w, h):
        if buffer_dict.has_key(buffer_id):
            view = BrowserView(buffer_dict[buffer_id])
            view.moveresize(emacs_xid, x, y, w, h)
            view.show()
    
    def update_buffer():
        while True:
            for buffer in list(buffer_dict.values()):
                buffer.redraw()
            
            time.sleep(0.05)
            
    server_thread.start()
    server.print_port()
    
    server.register_function(create_buffer)
    server.register_function(create_view)
    
    # test_create_buffer()
    # test_create_view("83886167")
    
    # create_buffer("1", "http://www.google.com", 600, 400)
    # create_view("1", "83886167", 0, 0, 600, 400)
    
    threading.Thread(target=update_buffer).start()            
        
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())
