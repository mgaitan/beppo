#Done with imageEmbedder 1.0 utility img2pytk.py from
#  http://www.3dartist.com/WP/python/pycode.htm#img2pytk

import Tkinter as tk
root = tk.Tk()

img00 = tk.PhotoImage(format='gif',data=
             'R0lGODlhIgAYAOf1AB8ZFB0aGR4aGSAaFSAbFh8bGiEcFyAcGyIcFyAdHCEd'
            +'HCQdFCMdGB4fHSUeFCQeGR8gHiEfIiMfHiUfGiUgGiAiICggFyUhICUhICEj'
            +'ISchHCYiIR8mIycjIigkIx4oKS0kFiQmJCUnJC0lGzAmEyomJS8mGCwmISco'
            +'JisnJiErLDIoFSwoJyIsLS8qFiMtLi8pIy0rHzQqFzAqJDUrGCUvLyUwMCEy'
            +'MTYsGDYsHiEzMiIzMycxMiM0NDMwHzovFzMwJTUxIT0wEzwwGDczIyc4Nz4y'
            +'Gjk0Hzo1HyU6PiA+QEM1EiE+QSo7OyU+PCg9QSY/PUE5GSRBREc5FiVCRUI7'
            +'IUQ7HCZDRks7Ekw8EyhGSClGSSNJS0c/H0lAG00+G1A/DyRKTCVLTSxJTCZM'
            +'TlNBElFBGCdNT1JCGChOUFRDFE5EHylPUCVQVlVEFSpQUVJHHCRUVCdSWCdT'
            +'WSxSU1hHGFlIGCdXV1xJFF5KDSNZXipWXCRaXylZWSxXXVlNHCZcYSddYmFO'
            +'GF5QGWNPEileZCpfZGVRFCtgZWpUEC5jaGtVEShobDBlam1XE25YC2xXGyRs'
            +'dW9ZFSxrbyZtdidud3FbFy5tcXVdB3RdESlweSpxendfCjFwdC1zfDNydi50'
            +'fXtiDy91fntjGTF3gCp8hDN4gSt9hSx+hjV6gy1/h4JpFoRqDS+AiIVrDzCB'
            +'iYluBTGCiohtEjKDiyuGkzOEjCyHlDWFjY1xDC6IlTaHjjeIjyaPm5B0EDmJ'
            +'kTOMmSmRnZR3BzSNmiuSnjaOmyyTn5d5CjePnC6UoDiQnTmRnpx9ADCWop1+'
            +'Apt9ETOYpJx+Ep1/FDWZpTebpySltjmdqTCjriantzufqzWisyiouD2grDOl'
            +'sCqpuauKBz+iriyqujanskCjry2ruzeoszqmuEKksC+svEOlsTGtvT2oujqr'
            +'tTKuvrORAjSvv7iPAzWwwLWSBDexwTmywryTDDqzxMCWAMabCtKlCdqsAt6v'
            +'C+q5AO68APC9APi/BvXCCCH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAsAAAA'
            +'ACIAGAAACP4A5wkcSLCgwYMIEypcOM9dvYcQI7pLtikQGy1j3iAShWxexI/1'
            +'5sEDGXLXGAkDHAz5ggbMFBoOEHCg48sjSJEGd/VAIETWu3fGWDlyxEmWs16H'
            +'XDyA4msdwZDwCtI5kCUePkwrBAiAcKNFhQIDcECKNgrHhULr1oUUGHXgFgvG'
            +'+MmakEEPrW7q5qmrl+0VGwkWLDmzg6BNNacG/TyI5w/PAUR5bUIcyO3NgDq9'
            +'BA2gowydQHcCsSnA9S/UgVkDQz70WJDSAUGrjFRo5AtdvbZ+XPDLZyGSZIGr'
            +'V7Oe98YCpDUPtIh65tnjE0f+lgkop7ogyXnKDnwx0sFGn1bb2v7yyLRPFge1'
            +'CSMK/CagCpAJNcZQKoZYSxl9yw5USz85JK0APrAwgQ5jNJILOR418gA995gw'
            +'BkOqrWPDAyykoMATZyCiSzkejROCGfbAshlDekkhwAwpXCBCGGIooks3rNFC'
            +'wR/eZKIBD7skhM4nKDAwAgoRVCDFGGNEgoxtn1EigRWyyCIEAxz48Ykvyijj'
            +'yyd0iFDACETMIEIGTpDBhh+pZDMScOiYgoIGcIySiRkyTPAAAwgMgIAJOFiB'
            +'BAsdiEAFF2zo8Qky65wJETi+kMGBBD58YYcgdtiBBhprdEEECh6EkARGbNBR'
            +'iS/gIPYbOMqQ0gYPIWzgwaoelOAqCoE8KDGGFmzc0UcqtaX22zzrPFPLJorI'
            +'wcUTTzTxxJBhnCHGG3Qgssks07DDWls2DeTONcrQkkojjfRhCB108NFHH41U'
            +'YootymQD2mrUVuvUbetkwwwvusTySir4/rJLMdOQA5q7Ban1kFrruOPOOuhQ'
            +'Y80232SjcDppCbTXu/WsExAAOw==')

newButton = tk.Button(root,image=img00)
t = str(img00.width()) + ' wide x ' + str(img00.height()) + ' high'
newButton.pack()
tk.Label(root,text='The image is\n'+t).pack()
root.mainloop()    #comment this out to run from IDLE
