#Done with imageEmbedder 1.0 utility img2pytk.py from
#  http://www.3dartist.com/WP/python/pycode.htm#img2pytk

import Tkinter as tk
root = tk.Tk()

img00 = tk.PhotoImage(format='gif',data=
             'R0lGODlhIgAYAOfjACEkJiQlIzEhHyUnJCklJC0jJDAiJC0kJSYoJSomJSco'
            +'Ji4lJTAlISErLCgpJyYqLCwoJzgjJyUtKTokIygsLiQuLyktLz8kJTwmJSUw'
            +'MDcoKiYxMScxMj4oKEImKCgyM0cmKUQoKSU2NUgnKkUpKkooLE4mLE8nLSg6'
            +'OU0rLiE+QUgtMyo7OyU+PCg9QSNAQyRBRFQsMiZDRlwsMCdERlcvNShGSClG'
            +'SSNJS1oyNyRKTCVLTSZMTiJNVGcwNi1KTSdNTyhOUGM0PClPUGozOW4xOipQ'
            +'UStRUidTWSxSU3E0PGw2QCZWVi1TVHM1OCdXV3M2PihYWHo1OytXXSlZWSxY'
            +'XnY4QCZcYSddYihdY4I2P4M2QH05QyleZH46RCpfZIU4QStgZSxhZoU6R4I8'
            +'R4g7RCZmai5jaCdnay9kaYs9Roo9SzBlajFmaypqbiRsdTNobSZtdpM+Si1s'
            +'cJQ/SihveJVASy9ucjBvcypxepdCTTFwdJhDTp1BT6RAUqZBTiZ5gaBEUid6'
            +'gih7gzF3gKdEVapEUSp8hDN4galFVit9haxGUix+hq1HU7JFVLNGVTh9hrRH'
            +'VrpFWLVIV7ZJWDKDizOEjLhKWblLWjWFjbpMW79KXDaHjsFMXi+NkziJkDKL'
            +'mMJNXzmKkTOMmchLYcNOYCmRncpMXTSNmspMYiuSnjaOm8tNYyyTnzePnC6U'
            +'oM5PXy+Voc9QYDmRnjCWos5RZtBRYdVPYjOYpNhRZDWZpTabpttUZzecqONT'
            +'ajqeqjCjriantzufq+RVayiouD2grDOlsEecqj6hrSqpuT+iriyqujmlt0Cj'
            +'ry2ruzeos0KksC+svDmptDGtvTKuvjSvvzWwwDexwUmqtjmywjqzxDy0xT21'
            +'xk+wvD63x0O6ylS0wES7y1C9yP//////////////////////////////////'
            +'////////////////////////////////////////////////////////////'
            +'/////////////////////yH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAsAAAA'
            +'ACIAGAAACP4AxYUbSLCgwYMGv4HDdqzbQG/ZIkqcSFHiLEh52FT5wWIDgQIC'
            +'JCSrlg1ixZMT4UwYQ8cPpVOsZIWaUWWWsGXguOncybPnTmoVJA0bmuvWJj0P'
            +'8jDyBA1ct6dQo0p9GnEQCF7DcpW6lCgFiyZ5Pi3zSbZnxFkA/tQKFSmQlQFD'
            +'xOzphY0bSpR2GUFYU0pTID5rVqA4MsfUsmx271YM1uOEpFKUrPAhkwNAjyuI'
            +'cJH8VpYsJAdgSm2SEwFAjSUaWiRx8wma4orSmpTABOsSkQc0dEBYIeFHFki9'
            +'EJd8ne1TBimyNvHpkAHIkCo0Etho4gYVM+E5y3qTdiWEpFqYoP4AgNGjCZU8'
            +'iG6EEaNoVzeJ4LK9ny8/mysLXEiFChSCw4/nbSz1iymEIGJKMnYlKJyC1Xxx'
            +'gSO3aGIFATAAkUQXeYDySzTdIIOLKL9Y001i4mQT34mefJBfKYWUUIEOQ0SB'
            +'hiKtUWNNNtVEg4003ryX2ETWpBFBI7B0wgUBLVhYRR2c9BLNRO9JpFNECtIi'
            +'ghKs1NJIChLc0MMUaEDiijLUSJlYYj4ixo01b0yQiC2kkEEAC0OYdwcnukhj'
            +'ppQLntlNCz7AwkojMzSAw2VtIOIKMGVW9KNdaXLzygm1kCIHAyIMcQQVc1ii'
            +'yzNUTakmlXsixswCasTwQA88MJGoKUnBPAnpqFSOKFyk4HxiAw08PAdHJbpA'
            +'g81Es5LKja20RmSMJ2900cYgqxTTqLEJHhvfmfXZ5Q03zODCySGgzMIMSYpF'
            +'GZG5EwUEADs=')

newButton = tk.Button(root,image=img00)
t = str(img00.width()) + ' wide x ' + str(img00.height()) + ' high'
newButton.pack()
tk.Label(root,text='The image is\n'+t).pack()
root.mainloop()    #comment this out to run from IDLE
