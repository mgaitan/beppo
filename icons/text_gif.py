#Done with imageEmbedder 1.0 utility img2pytk.py from
#  http://www.3dartist.com/WP/python/pycode.htm#img2pytk

import Tkinter as tk
root = tk.Tk()

img00 = tk.PhotoImage(format='gif',data=
             'R0lGODlhJgAYAOf/AB4aGR8bGh4fHSIeHR8gHicdGSYdHSobHSMfHiocHiAh'
            +'HywcGiceHiUgGigeHy4dGyEjICUhICUhIC4eHCAkJiYiISogISMkIjMdHS4f'
            +'ISwhHSElJzQeHisiIiImKCQmJDQfHyUnJCklJB8pKiEpJTMiIComJS4lJSkn'
            +'KysnJjsgITQkIjwgIiwoJyIsLTwhIzEnKCUtKSMuLiAxMDcnKicvKz8kJSUw'
            +'MCEyMTkoJjsnKiEzMj0nJkUjJyIzM0ImKCM0NEMnKCQ1NSkzNEcmKUQoKUgn'
            +'KiY3NkooLE4mLCQ5PUspLU8nLUgrLVEoKVAoLik6OiA+QE0rLiU9O1EpL1As'
            +'K1gpLSNAQylCQCZDRidER1gwNSlGSSNJSiNJS2MtM14vN2QtM2UuNCtISyVL'
            +'TSxJTC1KTSdNT2gxNylOUG0wOSVQVmkzPSZRV2U2PW8yOidTWSxSUy1TVG43'
            +'PSlVWyNZXipWXHg0PylZWXk1QHY4QCZcYXw3PX03PiddYihdY4I2P4M2QCle'
            +'ZCpfZCtgZSxhZoI8Ry1iZ4g7RCZmai5jaIU+RC9kaShobIo9SzBlapA8SIs+'
            +'TCpqbow/TTJnbJI9SY1ATiZtdo5BTjRpbidud5Q/Si5tcShveC9ucilweZVB'
            +'USpxephCTp1BTyxzfJlET55CUC50fZ9DUSZ5gS91fqFEUqJFTjB2f6hDUDF3'
            +'gKdEVTN4galFVjR5gix+hqtHWC1/h7JFVK5IVC+AiLRHVjCBibVIVzGCirdK'
            +'WTOEjLxIWrlLWjWFjb5JWy+JljaHjsBLXTCKly+NkzKLmDmJkcdKYMJNXymR'
            +'nTSNmspMYsVPYSuSnsdQXMtNY8ZQYiyTn81OXjePnM5PXy+Voc9QYDmRntRO'
            +'YjCWos5RZtBRYTKXo9dQYzOYpNhRZDWZpdpSZjabpi+er9tUZ+JSaTmdqSan'
            +'tzufqzGkryiouDOlsD6hrTSmsT+iri2ruzqmuC+svEKlsTynuTGtvT2oujKu'
            +'vjSvvzWwwDexwTmywjqzxCH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAsAAAA'
            +'ACYAGAAACP4A/QkcSLAguWrbtp0ryLChQ4bqFHDgMIFEvH38HjL8x7Gjx47+'
            +'rvBBl26cFSyziuX7yJKjv5YsX7HgNgzduGEW0jBC9hImSI0C41GQBQsENW/c'
            +'AHkQ5Ake0H9AX5oJo+3BCDbTvEELAmWQradQNV574O2NkD8IUE2ztoqBnJ0a'
            +'wz6MN6PSrQGN8GThEWwZMzQyBs2yF/fhP0pPvNmIowjPoRtomBnTVUKLomKG'
            +'5TLc5iBYHxmUCA0KpazCqmC+HEHAw0me4YdZ+BgzIIiQoEfR/D0qwusWLylA'
            +'BM2K51AzQU8spjnh8kjQoFzx+unzoYdXrVUasDzaVrxhvhC4Kv6NuCRIUCZ2'
            +'/lYmi7AKV605MfB4IryxYRo1zA5AuEDCg4whQxwxhBAIVLGKLKsUocQhmNVX'
            +'kDIZWNMHFVQwUcUTUmTYRBVFNCHFIqussogGcjzCU0FQyRWPDJWwEsEQN9ww'
            +'www74ICDDzMAcYMLOpRSiilbeHDIYCgSdFgV3uiARyJ/CFLIk08mQoiUgtQA'
            +'RimgYJKDFowog6Jc2zAAzBs3POLHIJ8kc001yCBzDTLOINOMLQ0Ysgkoc4hQ'
            +'RybmuCTQP/bYYw4UefgygB1wxPFINX+myJE92YCTBg+IOLKIEUPIQYky9AHa'
            +'wAIP9PCNFRgccIAAqdijT08vvURKA6IdWNABG44Y4kYKIrTQgjP+ELcOAEEU'
            +'IWywRfDQgCe0FGNPiq2+ygMNOeRAA7QtoIBCC4+kpE4+ueTSyhpcdBFuF10M'
            +'ggclTrUq0DnE7JLJGmOU0YUXZZhhRhpyDPLHib2mksklmlySSSafdPKKawWt'
            +'5E81n3gycCadeKJJJ51okkk1ctGzjjzyaLwOPfIQVyRH8byzzjrurNNOOxxz'
            +'7E4+AQEAOw==')

newButton = tk.Button(root,image=img00)
t = str(img00.width()) + ' wide x ' + str(img00.height()) + ' high'
newButton.pack()
tk.Label(root,text='The image is\n'+t).pack()
root.mainloop()    #comment this out to run from IDLE
