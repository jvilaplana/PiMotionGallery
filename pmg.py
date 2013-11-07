#!/usr/bin/env python

import logging # http://docs.python.org/2/howto/logging.html#logging-basic-tutorial
import pysftp # https://code.google.com/p/pysftp/
from configobj import ConfigObj # http://www.voidspace.org.uk/python/configobj.html
import os
import sys
import time
import curses
import Image
import ImageTk
import Tkinter

from gallery import Gallery

logging.basicConfig(level=logging.WARNING)

class PiMotionGallery():
    def __init__(self):
        print "\n--- PiMotionGallery v0.1 ---\n"
        self.config = None
        self.current = 0
        self.image_list = ['1.jpg', '2.jpg', '5.jpg']
        self.text_list = ['apple', 'bird', 'cat']
        self.root = Tkinter.Tk()
        self.label = Tkinter.Label(self.root, compound=Tkinter.TOP)

        self.tmp_host = ''
        self.tmp_port = ''
        self.tmp_user = ''
        self.tmp_pass = ''
        self.tmp_base = ''
        self.tmp_loca = ''

        if(self.loadExistingConfig()):
            print "Existing configuration successfully loaded."
            #fetchImages()
        else:
            self.askParameters()
            self.loadFromRemote()
            self.reviewConfig()
            self.saveConfig()

    def gallery2(self):
        gallery = Gallery(self)
        gallery.master.title('PiMotionGallery v0.1')
        #gallery.master.maxsize(1024, 750)
        #gallery.master.minsize(1024, 750)
        gallery.mainloop()

    # Try to load existing configuration file.
    def loadExistingConfig(self):
            logging.info("loadExistingConfig()")
            self.config = ConfigObj('pmg.conf')
            return self.config != {}

    def fetchImages(self):
            print "Connecting to remote server to fetch new images ..."
            srv = pysftp.Connection(host=self.config['host'], username=self.config['username'], password=self.config['password'], port=int(self.config['port']))
            #base_list = srv.execute('ls -al ' + config['motion_base'])
            for item in srv.listdir(path=self.config['motion_base']):
    #                lstatout=str(srv.lstat(i)).split()[0]
    #                if 'd' in lstatout:
    #                        print i, 'is a directory'
                    # Verify it is a directory
                    if len(item) == 8:
                            self.fetchImagesFromDir(srv, item)
            srv.close()

    def fetchImagesFromDir(self, srv, directory):
            remote = self.config['motion_base'] + directory
            local = self.config['motion_local'] + directory

            print "\nChecking " + directory + " directory ..."

            if not os.path.exists(local):
                    os.makedirs(local)

            dir_list = srv.listdir(path=remote)
            i = 0
            total = len(dir_list)

            # All files are copied to the local directory
            for item in dir_list:
                    if (not 'm' in item) and (not os.path.exists(local + '/' + item)):
                            srv.get(remotepath=remote+'/'+item, localpath=local+'/'+item)
                    i += 1
                    current = int(i * 100 / total)
                    if(current % 5 == 0):
                            sys.stdout.write("\r[%-20s] %d%% - this can take a while, grab a coffee!" % ('=' * (current / 5), current))
                            sys.stdout.flush()

            # Remote directory is deleted
            sys.stdout.write("\n\nDeleting remote directory " + directory + " ...")
            srv.execute('rm -rf ' + remote)
            sys.stdout.write(" [OK]\n")
            sys.stdout.flush()

    def askParameters(self):
            logging.info("askParameters()")
            global tmp_host
            global tmp_port
            global tmp_user
            global tmp_pass
            global tmp_base
            global tmp_loca
            tmp_host = raw_input('host [] : ') or ''
            tmp_port = raw_input('port [22] : ') or 22
            tmp_user = raw_input('username [pi] : ') or 'pi'
            tmp_pass = raw_input('password [raspberry] : ') or 'raspberry'
            tmp_base = raw_input('motion base [/home/pi/motion/] : ') or '/home/pi/motion/'
            tmp_loca = raw_input('local directory [] : ')
            print "\n\nconfig parameters set to:\n\thost: " + tmp_host + "\n\tport: " + str(tmp_port) + "\n\tusername: " + tmp_user + "\n\tpassword: " + tmp_pass + "\n\n"

            if(self.representsInt(tmp_port)):
                    tmp_port = int(tmp_port)

    def loadFromRemote(self):
            logging.info("loadFromRemote()")
            print tmp_host
            print tmp_user
            print tmp_base
            print tmp_port

            if(self.checkConnection()):
                    print "Successfully connected to the remote host."
            else:
                    keep = ''
                    while (keep != 'y') and (keep != 'n'):
                            keep = raw_input("\nDo you want to keep your current connection parameters? [y/N] : ").lower() or 'n'

                            if(keep == 'no'):
                                    keep = 'n'
                            elif(keep == 'yes'):
                                    keep = 'y'
                    if(keep == 'n'):
                            self.askParameters()
                            self.loadFromRemote()

            #srv.get('thefile.txt')
            #srv.put('anotherfile.txt')


    def checkConnection(self):
            success = True
            try:
                    srv = pysftp.Connection(host=tmp_host, username=tmp_user, password=tmp_pass, port=tmp_port)
    ##              test = srv.execute('ls -al ' + tmp_base)
    ##              print test
                    srv.close()
            except:
                    logging.warning("Could not connect to remote host.")
                    print "[WARNING] Could not connect to remote host, please check your connection parameters."
                    success = False
            if(os.path.isdir(tmp_loca)):
                    return success
            else:
                    logging.warning("Local directory does not exist.")
                    print "[WARNING] Local directory does not exist."
                    return False

    def reviewConfig(self):
            logging.info("reviewConfig()")
            pass

    def saveConfig(self):
            logging.info("saveConfig()")
            config = ConfigObj('pmg.conf')
            config['host'] = tmp_host
            config['port'] = tmp_port
            config['username'] = tmp_user
            config['password'] = tmp_pass
            config['motion_base'] = tmp_base
            config['motion_local'] = tmp_loca
            config.write()
            self.loadExistingConfig()

            print "Configuration parameters successfully saved."

    def playVideo(filename):
        os.system("open " + filename)

    def gallery():
            label.pack()

            frame = Tkinter.Frame(root)
            frame.pack()

            Tkinter.Button(frame, text='Previous picture', command=lambda: move(-1)).pack(side=Tkinter.LEFT)
            Tkinter.Button(frame, text='Next picture', command=lambda: move(+1)).pack(side=Tkinter.LEFT)
            Tkinter.Button(frame, text='Quit', command=root.quit).pack(side=Tkinter.LEFT)

            move(0)

            root.mainloop()

    def move(delta):
        global current, image_list
        if not (0 <= current + delta < len(image_list)):
            tkMessageBox.showinfo('End', 'No more image.')
            return
        current += delta
        image = Image.open(image_list[current])
        photo = ImageTk.PhotoImage(image)
        label['text'] = text_list[current]
        label['image'] = photo
        label.photo = photo

    def representsInt(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

def main():
    pmg = PiMotionGallery()
    pmg.gallery2()

if __name__ == "__main__":
        main()
