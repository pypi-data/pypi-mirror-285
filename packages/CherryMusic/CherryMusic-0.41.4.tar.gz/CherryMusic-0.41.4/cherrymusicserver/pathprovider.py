#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# CherryMusic - a standalone music server
# Copyright (c) 2012 - 2016 Tom Wallroth & Tilman Boerner
#
# Project page:
#   http://fomori.org/cherrymusic/
# Sources on github:
#   http://github.com/devsnd/cherrymusic/
#
# CherryMusic is based on
#   jPlayer (GPL/MIT license) http://www.jplayer.org/
#   CherryPy (BSD license) http://www.cherrypy.org/
#
# licensed under GNU GPL version 3 (or later)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

import codecs
import hashlib
import os
import sys

userDataFolderName = 'cherrymusic'  # $XDG_DATA_HOME/userDataFolderName
pidFileName = 'cherrymusic.pid'     # $XDG_DATA_HOME/userDataFolderName/cherrymusic.pid
configFolderName = 'cherrymusic'    # $XDG_CONFIG_HOME/configFolderName
configFileName = 'cherrymusic.conf' # $XDG_CONFIG_HOME/configFolderName/cherrymusic.conf
sharedFolderName = 'cherrymusic'    # /usr/share/sharedFolderName

def isWindows():
    return sys.platform.startswith('win')

def isLinux():
    return sys.platform.startswith('linux')

def isOSX():
    return sys.platform.startswith('darwin')

fallbackPath = os.path.join(os.path.expanduser('~'), '.cherrymusic')

def get_base_path(type_='data'):
    if isLinux():
        if type_ == 'data':
            return os.environ['XDG_DATA_HOME'] or os.path.join(os.path.expanduser('~'), '.local', 'share')
        if type_ == 'config':
            return os.environ['XDG_CONFIG_HOME'] or os.path.join(os.path.expanduser('~'), '.config')
    elif isWindows():
        return os.environ['APPDATA']
    elif isOSX():
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    return fallbackPath

def getUserDataPath():
    userdata = os.path.join(get_base_path('data'), userDataFolderName)
    assureFolderExists(userdata, ['db', 'albumart', 'sessions'])
    return userdata

def get_cli_arg(arg, default=None):
    try:
        return sys.argv[sys.argv.index(arg) + 1]
    except ValueError:
        return default

def getConfigPath():
    if config_path := get_cli_arg('-c') or get_cli_arg('--config-path'):
        return config_path
    configpath = os.path.join(get_base_path('config'), configFolderName)
    assureFolderExists(configpath)
    return configpath

def fallbackPathInUse():
    for _, _, files in os.walk(fallbackPath):
        if files:
            return True
    return False

def pidFile():
    return os.path.join(getUserDataPath(), pidFileName)

def pidFileExists():
    return os.path.exists(pidFile())

def licenseFile():
    owndir = os.path.dirname(__file__)
    basedir = os.path.split(owndir)[0] or '.'
    basedir = os.path.abspath(basedir)
    return os.path.join(basedir, 'COPYING')

def configurationFile():
    return os.path.join(getConfigPath(), configFileName)

def configurationFileExists():
    return os.path.exists(configurationFile())

def absOrConfigPath(filepath):
    if os.path.isabs(filepath):
        path = filepath
    else:
        path = os.path.join(getConfigPath(), filepath)
    return os.path.normpath(path)

def databaseFilePath(filename):
    configdir = os.path.join(getUserDataPath(), 'db')
    os.makedirs(configdir, exist_ok=True)
    return os.path.join(configdir, filename)

def albumArtFilePath(directorypath):
    albumartcachepath = os.path.join(getUserDataPath(), 'albumart')
    os.makedirs(albumartcachepath, exist_ok=True)
    if directorypath:
        filename = _md5_hash(directorypath) + '.thumb'
        albumartcachepath = os.path.join(albumartcachepath, filename)
    return albumartcachepath

def assureFolderExists(folder,subfolders=['']):
    for subfolder in subfolders:
        dirpath = os.path.join(folder, subfolder)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

def readRes(path):
    with codecs.open(getResourcePath(path), encoding="utf-8") as f:
        return f.read()

def getResourcePath(path):
    RESOURCE_PATHS = []
    if isLinux():
        # check share first
        RESOURCE_PATHS.append(os.path.join(sys.prefix, 'share', sharedFolderName))
        # otherwise check local/share
        RESOURCE_PATHS.append(os.path.join(sys.prefix, 'local', 'share', sharedFolderName))
    # otherwise check local install
    RESOURCE_PATHS.append(os.path.dirname(os.path.dirname(__file__)))
    # lastly check homedir
    RESOURCE_PATHS.append(getUserDataPath())

    for prefixpath in RESOURCE_PATHS:
        respath = os.path.join(prefixpath, path)
        if os.path.exists(respath):
            return respath
    raise ResourceNotFound(
        "Couldn't locate {path!r} in any {res!r}!".format(path=path, res=RESOURCE_PATHS)
    )

class ResourceNotFound(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

def filename(path, pathtofile=False):
    if pathtofile:
        return os.path.split(path)[0]
    else:
        return os.path.split(path)[1]

def stripext(filename):
    if '.' in filename:
        return filename[:filename.rindex('.')]
    return filename

def _md5_hash(s):
    utf8_bytestr = codecs.encode(s, 'UTF-8')
    return hashlib.md5(utf8_bytestr).hexdigest()
