#Done with imageEmbedder 1.0 utility img2pytk.py from
#  http://www.3dartist.com/WP/python/pycode.htm#img2pytk

import Tkinter as tk
root = tk.Tk()

img00 = tk.PhotoImage(format='gif',data=
             'R0lGODlhIAAYAOfgACAaFR8bGiEdHCMdGCggFyQjHSciHCYkGSMlIikjHiAn'
            +'IykmGyklJCEpJSYrIywoJy8qFh4vLy8pJCMuLjEsFy8rKiEyMjQuFCYwMSQy'
            +'LSIzMzEtLDAxIDMvLjQvLiU2NTgyGDAyLy82IzszFDUxMCM4PDgzHis3LS43'
            +'KSc4Nyc5ODczMis5NCg6OTM5ITk3HDI5JiY7Pzw5GCU+PDc7HiNAQ0A8FiVC'
            +'RUI+GCdER0A7OkE8OylGSSNJSyRKTCVLTSZMTkpEGCdNT01GEy5LTihOUEZC'
            +'QSlPUEhDQipQUklFRCdTWSVVVShUWi1TVClVWydXVyNZXk1JSFZOFSRaX09L'
            +'SlBMSihdYlJNTCleZFtXDCtgZVRQTlxYFl1ZDy1iZyZmai5jaChobDBlailp'
            +'bVpVVCpqbiRsdS5pc2VgFzRpbi5tcShveGhiEV9aWTFwdCxye21mC2JdXGxm'
            +'FV9hXmRfXi91fiZ6gjB2fzF3gCp9hWVmZHduCzV6g3lwDmxnZmhqZy+BiXd0'
            +'EGpsaTKDiyuGk3BraTuAiTOEjHx4CHp3FDWFjS+JljeHj29xbn16GCWPmkWD'
            +'hziJkDKLmHVxbyiQnIR+BDmKkYJ9EjSMmSuSnoR/FXV3dDiQnS+VoTCWoouE'
            +'DzKXo3l7eDOYpI2HE3t9ejWZpZCJB4+IFTabppKKCjecqIR/fpSMDTqeqoGD'
            +'gCentz2grJePE5qRBTOmsD6hrSqpuT+iriyqujiltjanspiVCIqFhC2ruy+s'
            +'vDGtvaCWDzKuvjSvv52aEqGdA6WbAzexwaKeBzmywjqzxKWhDT62x1Wutaql'
            +'AK+jAEm2wUG5ya2nBq+pCkW8zLKrD1q5xbevAFTAy7myB16+yruzDGHAzMC4'
            +'AMK5AGTDz8W7BmnH1Me+DcrAAM3DAM/EAdHGCM3JCdXJANbKANTOANbQANfR'
            +'BNvUANrTC97XAODYAOLaAObdAOXdCejfAOngAOviAO3kAPHnB/PpAPfsAPnu'
            +'APrvAPzxA//zAP/0APz2ACH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAsAAAA'
            +'ACAAGAAACP4AwXnbRrCgwYMICzKLZNDbNGgQI0qcSBFiIA5Elj1btizbs4/P'
            +'kIkEOZIkMpK3iMxBNyNXLFrCri0TSbOmTT14VgXTVKIFDGv9/jlAJGmVrms1'
            +'OSalechDGR0YQjy4IK8fv38izuDphCsbNJofa4ZEVggBHV6vdPzBEsBZv7cj'
            +'nKiRdEumTZEzRXZ6wYcOK1FWrBhiQKFe0CA+wDDKlY1jXrAiTblohw2JKEqA'
            +'KgCyIqDLPT4NfHwJREvmWGRKRbpCka5fPhOUMBvRQWdFAAgYiBAJc+hWtqU0'
            +'YZ0Qx+/tJiuA9sipgIRLBQYafDBZUwmW3bu3WGh7my+eORNu6P7QqcJAKoYe'
            +'S7LkSeVrm2OaM2dQ4w4P3bdTD8pUqYKkgoYfRDjxxiW3PHOdUr/wAIxV9bxz'
            +'zjfOKJNGBUrM5kELR0QxBiO3CINMY6jRRIQq/+gzTzrmaKPMMKigMgUCIazw'
            +'QA1AZHHHKL2IdJ1IT1jCzz3vlBMONsrIIssmmzySRgEBINCDgHTlBaJIWfih'
            +'jz3vmPMNNcPIQgqSc+DAwAQ9CMEDFXmsUpNMHKHRxj3ypBOOisB4uUkXICDQ'
            +'gg88/ODEE2tIAktN23z0hhb1yCMkNUWiokgQBWDAgxA/CBFFFmu8IYkpt4SI'
            +'zDQzifAOOuVoQ02dc7ygwAxA+ADEEppOfPFGH5V0kksweInkHjIvoDOOii4u'
            +'EEENRPgghBNZjHEHIZ3U0uFJNl0DzTJPPEKNHzgo0EIPP/xwxBNhqKGHJM36'
            +'cpenIPZyRAMq5ADED0A4cQUaeRSiySq5hBSSUqmJNOUti4yxBKxboKHpJS/1'
            +'4qGHYtlUTUi5rMIIHFtsoVUglWgCSyy56IILLr8g40swwfgCcsjB9BIQADs=')

newButton = tk.Button(root,image=img00)
t = str(img00.width()) + ' wide x ' + str(img00.height()) + ' high'
newButton.pack()
tk.Label(root,text='The image is\n'+t).pack()
root.mainloop()    #comment this out to run from IDLE
