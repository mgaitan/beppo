a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\unpackTK.py'), os.path.join(HOMEPATH,'support\\useTK.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'c:\\svn\\beppo\\beppo\\client\\Login.py', os.path.join(HOMEPATH,'support\\removeTK.py')],
             pathex=['C:\\svn\\beppo', 'C:\\svn\\beppo\\pyinstaller'])
pyz = PYZ(a.pure)
exe = EXE(TkPKG(), pyz,
          a.scripts,
          a.binaries,
          name='beppo.exe',
          debug=False,
          strip=True,
          upx=True,
          console=False )
