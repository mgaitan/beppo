#Done with imageEmbedder 1.0 utility img2pytk.py from
#  http://www.3dartist.com/WP/python/pycode.htm#img2pytk

import Tkinter as tk
root = tk.Tk()

img00 = tk.PhotoImage(format='gif',data=
             'R0lGODlhIwAYAOfiAC0kJTEiJSomJTQjISknKzQkIiYqLCwoJzkjIyspLCcr'
            +'LS0pKDEnKDIoKSUvLzMpKSktLz8kJTcoKiouMCouMCYxMTkqLCM0NCgyM0Yl'
            +'KT4pLSkzNCU2NSo1NSY3Nk4mLEEsMCc5OEYrMUgrLSk6OlIpKiE+QSU+PEou'
            +'L1coLCs8O08tMCNAQ1AuMSVCRVIvMyZDRlwsMCdERlgwNShGSCNJSiNJS1oy'
            +'NyRKTGUuNCVLTSxJTCZMTmIzOyhOUG0wOSlPUGQ1PCpQUSZRVytRUidTWSxS'
            +'U202Oy1TVClVW3czPi5UVXM2PiNZXipWXChYWCRaX3Y4QCtaWyZcYXw3PXc5'
            +'QSddYn44PihdYy9aYX05QyleZCpfZDFcYytgZYA7RSxhZoc6QyVlaS1iZ4M9'
            +'SC5jaCdnay9kaShobIs9RjBlailpbZA8SDFma4w/TSxrbyZtdpM+Si1scJo+'
            +'TC9ucilweZZBTDBvcypxephDTqM/US1zfC50faBEUjB2f6FFUyh7gzF3gKpE'
            +'USp8hDN4galFVit9hTR5gqpGVyx+hjV6g6tHWC1/h7JFVLNGVa1JWbRHVjCB'
            +'ibVIVzGCirZJWDKDizOEjLhKWblLWjWFjS6IlbpMW79KXDaHjrtNXMBLXTeI'
            +'j8FMXjKLmMJNXyiQnDCOlDmKkTOMmcNOYCmRnTSNmjuLkspMYiuSnjaOmyyT'
            +'n81OXi6UoM5PXzmRntROYjCWotBRYdVPYjKXo9dQYzOYpNhRZDWZpdlSZdpT'
            +'ZjabpjecqDmdqS6irTqeqjufqzGkryiouD2grDOlsD6hrSqpuTSmsTektj+i'
            +'riyqujanskCjry2ruzqmuEKksC+svDynuTGtvTKuvjustjSvvzWwwDexwTmy'
            +'wjqzxDy0xT63x0C4yEO6yv//////////////////////////////////////'
            +'////////////////////////////////////////////////////////////'
            +'/////////////////////yH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAsAAAA'
            +'ACMAGAAACP4Aw4EbSLCgwYMIB377NpCbw4cQI0qUOC3LiTvBhj3D5m2ix4/c'
            +'RCn4IglBm06znnHzxrKly5cwvYGrGOFSrksjgKipFAykT4ekKijpxaoPCgVD'
            +'pijiFc5hU25PozqdGm5alwiObHmq0mDDkCV0SkFrio2sWW5l0ZrFpivED1a2'
            +'/ryYUANJmT2ahlkrC46vX4F/v2VrMwCRL09kJIQAUgSOoVnTsqH95o1jZZaW'
            +'M3ubRaIHLVaLZhiQQcTLHU2/nD3sGBMmtzoF9OxC/KADDydtAM1Khg3bw28/'
            +'uQ1TEQPuohsJWAzZUqeTrmkruVF22LolNz4A5hx2Y8E27kOumP5ZexjOd/SP'
            +'0GSkYMVKUIwEJ4xIuVPp+bRwLB2CAy59JXBv/CkigHaepAHCBbepAYgrwvjG'
            +'n1PmeTTNDh+EwsolQSSgghBYwDFJKdB1tJKI0v0nVTiKJOCGL6i4AQIGOjTR'
            +'xh2rJONRR+U5VJY3902DRAac5PLIEQmQsEMWcFjCS2SsuQTRQlDtCAoEWvgy'
            +'ShwiTEADbjTqtdqX0eW4km9ORMCJLZAc8YAKREgBRySxGFMNOOdNB9WTwIVT'
            +'TQdK7DLKHFnSUAQYfIByTDXmsVYejr4x6tA3rpTACiZMNEDCEFCswUgsxZSF'
            +'X3TYfEPWfng6xMwCVbRQQQ2D3gEKMDnRgNofZZV9OmKU1HETixNd1KGGHIrE'
            +'As00/3nz1GqhTgRldNcMs4omqgRTTXQdfcPRiLSOaJ2YAQEAOw==')

newButton = tk.Button(root,image=img00)
t = str(img00.width()) + ' wide x ' + str(img00.height()) + ' high'
newButton.pack()
tk.Label(root,text='The image is\n'+t).pack()
root.mainloop()    #comment this out to run from IDLE
