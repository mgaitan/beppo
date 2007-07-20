#Done with imageEmbedder 1.0 utility img2pytk.py from
#  http://www.3dartist.com/WP/python/pycode.htm#img2pytk

import Tkinter as tk
root = tk.Tk()

img00 = tk.PhotoImage(format='gif',data=
             'R0lGODlhIgAYAOfrAC4mJzEmJi8nKTQmJyorLCsrLCosLCosLSktLSguMDIq'
            +'Kz0mKT8mJz8mKUAmKUEmKTkqLDkrLEQmKSY0NTsrLCgzNS0xMyc1Nic1Nyk1'
            +'Nic2Nyg2Nyg2OCU4OCc4OkorLSc7PCg9P1grMCdBQidBQyZCQydCQydCRVss'
            +'MCdERVcyNypGSFgyNyhHSlkyNydISlkyOFoyNyhISiZJSydJSidJTCxHSl0y'
            +'OCdKTCdKTShKTCZLTSdLTSlKTSdMTidNTidNTydNUCdOUCdOUWczOShPUmsy'
            +'OShQUShQUihQUyhQVChRUyxQVClTVnA1PXY0PHk1Pns1PzFWWng3PzBXWypa'
            +'Xn02PylbXypbXypdYSpdYns6RCpeYn88RTlbX4A8RoA8RyxhZytjaC1iaIM9'
            +'RoM9RyxjaS1lbDBlbCxnbS1nbZM+SS1sczFrdDNscS1vdi5vdS5xeC5yeqBB'
            +'TjByeZpEUC9zei90e55EUaBEUqFEUi92fqJFUjB3fqNFUzB6gjF7hDF8hTZ8'
            +'g7JHVkN4fjJ/h7JHVzGAibJIVrFJWDKBirZIWDKCizKCjLVJWbVJWrZJWrdJ'
            +'WTKEjblKWjOFjzOIkr5MXDOKlDSKlMRNXsVNXzSOlzSOmcdOYMhOYMpOYcpP'
            +'YTSRmzaQm8tQYjWTns9QYs9QYzaTntBRYjaUoDqUnjeVoT2VoDWZpDeZpTab'
            +'qDebqTacqDacqTicqTedqTedqjeeqjieqzegrU6XoDigrjeirzijsTqjsTml'
            +'sjintTmntTmotjmotzqotjqouEOmskOmszmquTqrujqtujqtuzqtvE2msEGr'
            +'uDquvTuuvTuuvjuvvzyvvzuwvzywvzqxwDuxwDuxwTuxwjqywTuywTuywjyy'
            +'wjuzwjuzwzyzw0O2xUO2xkW2xkW3xUa3xk67yFm6xlm7x1i8yFq/zGLDzv//'
            +'////////////////////////////////////////////////////////////'
            +'/////////////////////yH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAsAAAA'
            +'ACIAGAAACP4A1aUbSLCgwYMGzRHykuscOmblwEmcSLGixYnhWGWAMgeAG0Gq'
            +'yHkbSbKkyZPeukEz82DRJz4BZADZIw6lTZSrNEBBNalMBBA4hPypebOot0IL'
            +'Bnnyc8OACRxL7pAiatTmBEuPyFDY8MJHlkvIZFGterIHERYFRuRIEgeXNm1i'
            +'yY78Ri1Vr5HD2qBpEkQLpmQjt8Ul+01UBRQDAHEC1m1aq027tJEUPPbmszAS'
            +'InVy0mGIHWc2KVc9dcFKKUdfFKTAIeZY6ME2ualxgEhTHhgITuBQwqja68om'
            +'G4kAlahLBA41eFyptOymaJvf6Bipo+LA0yJwamUr+twmsRUWQq7Q4FGFErKq'
            +'3b19m/Xn1jaS0y6lkRPrGtnuz8YwiCKgj6Rf6mmjTDRyeUNZN96kgkEUpkDy'
            +'QQk/BCJZgZPJMo40ZzRgSCd6uJBADTvsYQ2FFRrjwROjOAJGBBvMwAMXriBI'
            +'ooGwULFGJnjEQAAJOiDxhi0TzrgNLFJMsQUEF7zAAxaVnDfjZLAUw4QNLexw'
            +'BBy02PckSdi80owwvBzChiK6BCPMmWimqeaaaPoSSkAAOw==')

newButton = tk.Button(root,image=img00)
t = str(img00.width()) + ' wide x ' + str(img00.height()) + ' high'
newButton.pack()
tk.Label(root,text='The image is\n'+t).pack()
root.mainloop()    #comment this out to run from IDLE
