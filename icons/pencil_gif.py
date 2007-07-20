#Done with imageEmbedder 1.0 utility img2pytk.py from
#  http://www.3dartist.com/WP/python/pycode.htm#img2pytk

import Tkinter as tk
root = tk.Tk()

img00 = tk.PhotoImage(format='gif',data=
             'R0lGODlhIQAYAOf+AB4aGSAaFSEcFyAdHCMfHiAhHywcGikeGygfICEjICch'
            +'HC4eHCIkISwhHR8nIzIhHzYgICAqKigpJyIsLSQsKB4vLzIoKT4jJDgnJUEk'
            +'ITwmJSEyMTUqJjkoJiIzMzEtLCcxMkMmIyM0ND8pKDMvLkgmJUUoJTkuKkon'
            +'JkErKiY3N0cqLCI7OUwpKCY7PyA+QFMpK0MxL08sK0ouLyI/Qk0uK0gxMSVC'
            +'RU8xLj05OFUxMCFHSChFR1swMSlGSSNJSiNJS083N1g0MyRKTCVLTUM/PiZM'
            +'TidNT1w3Nlc5OihOUFQ8O2c1NCNTUypQUV86OElEQytRUidTWSxSVGE8Om42'
            +'NyZWVilUWidXVyNZXipWXGg9Pl9BQnI5Ok5JSCVbYCxYXiZcYSddYlFNSyle'
            +'ZGVGRypfZHNBRFRPToM7PGdISixhZnhEQi5jaCdna1hTUm5JTC9kaY0+Qilp'
            +'bVpVVDFmayRsdVtXVitrbn5JR5BBRF1ZVyhveC9ucoVKSipxepVFSHlSUDFw'
            +'dIhNTZtFSzNydiR4gC10fXxUUmRfXi91fqBHSCd6gjB2fyh7g6JJSjN4gWhj'
            +'YoVXVyt9haVMTTZ7hC6AiGxnZjCBia5NUTGCioxeXjOEjCyHlI5fYDWFjbdP'
            +'VnJubDeHjzGKmJNjYziJkKdbWiiQnLtSWDGPlTSNmiqSniyTn6tfXjePnC6V'
            +'oZ5oaq5iYTCWojOYpM9WXbZiZKJrbTWZpbhkZqhrb9JZYDebpySltjmdqS6i'
            +'rbtnaTqeqjyfq75pa6pzdTOlsD6hrd9dZsFsbeFeYiyqusZqbziltjanskCj'
            +'ry2ruzeosy+svEOlsbR2esltcTGtvTKuvs1vbjSvvzWwwDexwbp7f9FycTmy'
            +'wtN0czqzxDy0xZGTkNl0dZeSkMCBhd13eN95ep2YluF7fON8fel7f+V+f9CI'
            +'iaOenaeiodmQkaulpOOTlrGsqumYm7W3tLq8udHT0NjS0dXX1ODi3+vl5Onr'
            +'6Pj1+vr8+P/8+v/9//7//CH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAsAAAA'
            +'ACEAGAAACP4AuQkcSLAgN2jFgvXaNesVK1eqRnXixGrgN4MYuS0DQcLLGDRv'
            +'6OwJQDIAgErXsHH7xrKlS5fPXgCI569mv37+CAAAEECCKlbBnF3MKPCijyQ5'
            +'/P1butTfSJM/ChU61eylVYFayiACx7TrvQ8BBijBgqfUMqID2yyRVyYUO3Pt'
            +'8DX1l4+OBx9aCrF6hpbbIRvwtGHIk8cPGw72mPr78MMJmUpn0VbqAG9YB2Hp'
            +'1KlLN4jrUnYTfEgRdIov0VIk1knTMG1z5nRn3v1TWoSHjzWVdqnMuEvCuFwd'
            +'tm3WnO4cBn2z6Tn4YcVOKdNFVwqMJkEbLBPTXmdWZyqRUn90VP74ADNJ98Xz'
            +'A6OBsEUqRTfixNMlmTe7noQjUeaYNThUhSdPM3STjnbqHLOFAVBcEokXLhgx'
            +'RSOyRMNSdAL5gAgiMgwIn4EXLGIMKkwYUMAOTtTxiYTSETSFGogI8Z6GxzyR'
            +'wSK66JIGBBG8QIQRWRSySjXRDRVHEnAk4Zo6wiCxAiG6ZMIEARvsQERjYNQx'
            +'SjEWDdRIDFxscY5mvwhhAo16aODACzv44MMUYOBhSCm7QDeUKxgssUU56IS5'
            +'AiWgVIFABTcA8YMUYcTxxySjuOLLNUOluAMCbKATywwrLAJICQWo8IMPRkSB'
            +'RR2HYFJKMMxQSKEHbEwKgx5dLFCBjnVHOIEFGHxUMsorxVBD1IRZIABBFTIQ'
            +'IIJtUjhR5SGVuJLKM7qidd4yYKigQoNGHJGFGHMY0gkrxEBXVKP8aWRJHU5I'
            +'YQUZdVRSSinFRHNNNZH1dRGzu3RiSBtr1KFIJ7f2EowvzSyDTTTPLGMwX9EU'
            +'hE0yAQEAOw==')

newButton = tk.Button(root,image=img00)
t = str(img00.width()) + ' wide x ' + str(img00.height()) + ' high'
newButton.pack()
tk.Label(root,text='The image is\n'+t).pack()
root.mainloop()    #comment this out to run from IDLE
