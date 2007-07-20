# This file is part of Beppo.
#
# Beppo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Beppo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Beppo; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from Tkinter import *
from beppo.Constants import EMOTIC, SYMBOL, MATH

eq = ('R0lGODlhEQAHAIABAAAAAP///yH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAh'
            +'+QQBCgABACwAAAAAEQAHAAACDYSPqavhD6OctEqG8yoAOw==')

less = ('R0lGODlhEQAOAKU1AAAAAAICAgMDAwYGBgcHBwgICA0NDQ4ODhUVFRYWFigo'
            +'KCwsLDU1NTY2Njg4ODk5OUJCQkNDQ0VFRU9PT1BQUFFRUVJSUlxcXF1dXV9f'
            +'X2pqamxsbIGBgYKCgoWFhYaGho6Ojo+Pj5KSkpycnJ2dnZ6enp+fn6mpqaqq'
            +'qqurq6ysrLa2tre3t7m5ucPDw8bGxtvb29zc3N7e3ubm5ujo6P//////////'
            +'/////////////////////////////////yH+FUNyZWF0ZWQgd2l0aCBUaGUg'
            +'R0lNUAAh+QQBCgA/ACwAAAAAEQAOAAAGX8CfcEgkyj6LopImegCeymFJInga'
            +'LitlqkJ4DiYnJQtjeAYgI6VLg3gCGKBZ9OdWcGDzYb0TywtfGwluDSFyfi0Z'
            +'B2YRJH5CKhYFTwQUKI4/JlRWGCyOTA5ul0IyHgtBADs=')

great = ('R0lGODlhEQAOAKUwAAAAAAICAgMDAwYGBgcHBwgICA0NDQ4ODhUVFRcXFyYm'
            +'JiwsLC0tLTMzMzg4ODk5OUFBQUVFRU9PT1FRUVJSUl1dXV5eXl9fX2pqamxs'
            +'bH9/f4WFhYaGho2NjZKSkpubm56enp+fn6mpqaqqqqurq6ysrLa2tre3t7m5'
            +'ucPDw8bGxtnZ2d/f3+Xl5ejo6Onp6f//////////////////////////////'
            +'/////////////////////////////////yH+FUNyZWF0ZWQgd2l0aCBUaGUg'
            +'R0lNUAAh+QQBCgA/ACwAAAAAEQAOAAAGYMAFh/UrGo9HgPLhcSGfpopBKYiE'
            +'ns/RhKAkUEhYJCgiUBosp7DR5XEoAQhMSl1kcRhv+m+lUeSxLR0NbwkZKk8f'
            +'EAFKBxcoTyISA0oFFCVPJ1JUVmpvDh4vegsbRHpFQQA7')

confused = ('R0lGODlhGAAYAOf/ABkQBhMTCRIUERQTFxcTERsSEhkSGBYZCiASFxwWEBsY'
            +'CyQTDh4THxkZEigUBSIXBjMQARwYFyMXDjATASIXEyAZDhkbGSEYGR8aFSgZ'
            +'AywXAyUbBCAZHRwbHiAdCx8bGh8aIx8gCB4eFyAeEx4gDiYZHhwgFCQZJTAa'
            +'ASkeASMdGCwdASUgCiYeFCgeDyMjAy4bECcdGR8hHi0bGCMfHjwYACAgJDka'
            +'ASkiAiUeIyceHjEgADUeAC4iACMjHCUjGCciHC4jEEAeACUlKTsiADAoACUn'
            +'JCklJDYmAC0lHyskKi8iLC4kJSorIkglAD8rAEQpADsuAC8tLD0vFFIpAjgx'
            +'Kjg2NTk5LlE2AFc1AE46AEM2PlhCAF5AAE9GJkdGPUdFRWRFBE9DUF9KCWlO'
            +'AG1NAGZSAFZUUVtRV21aFndfDYBcBnthAHtnAGRiYmZkXHJkQHxpKJBpGItw'
            +'Fo5xDYtwI4Z0JHJxbpF3BHpwdZ15Bp98JqN/IZ6CIYh8gZqCMoKBfp2DKqKF'
            +'FKiGAaiDEpmEQq2MDKmOD7GKEKyRAK2NG7OQAauOKbmQBaqQO7aOLLiVC76U'
            +'D5OSj72ZAMGXAJmQl7iXIr2VJLaYM8abCMSfDMidDcehAMygANScAMihINGk'
            +'CL2iT82nCqOimcKkPcGnMMikMtWnAMSpJKSiodGqANiqAL6oYbupctytBdmw'
            +'B9uyALarjOCwAOmtANayI+SzAOG4AOuzArOwrtmzQOi3BdS0Tte4N9a3Qt22'
            +'N+O5Gu27APK5AOq5Huu/AOG/H+m5Lua4POi/Eu68EuHDEea8LOG/LN+/NeW9'
            +'NvPAAvy8Bfi/BezGBffDAP+/AOzCJ/LFCfzCAPTHAPnFAOvHHffEDfXCHubD'
            +'Q/HKAPzCD/HFHurHKvvHAP/FAOjDTtnFfv7KAOvKPP/MAPfMGPPJPf3PB//R'
            +'AN/Nl9LPzeLeyvjqsOjq5P/ovvrvq/3zvv7w3/73yvrx+v341f/53f749vz8'
            +'6fz6//f9//z98/r9+v///yH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAh+QQB'
            +'CgD/ACwAAAAAGAAYAAAI/gD/CRwo8A4HCRYiUCiBi6BDhzQsqNHmzBs2Z+Gw'
            +'5Ajw0GGHXtasSQtpDdszac/6COj4D42EcBe1YaPoDFpJZ9aCyej4QRw0Z86w'
            +'CRWHDZpMbBa9jXAIwts0ikOtAcVGVKY2mSwGzvjlTY1Rbd5wVmNmLiZQZ+L4'
            +'EBCoQpwwf/5+AtUmrt++oxexSbt14Z+kMtjk0AAxVWo0Hf6OYSOJDZguFP8k'
            +'yIxWwULNqxhJ9BNZUaouV5ouVNBbU1zQkdquqZNpWlowXbZWbbLxQVpRa5il'
            +'1QyK01vIYa5UgcoUIQJpmdAu4pSKurGuVaI2NdLBAedRqTh16ybqrJYr2ZEW'
            +'xEVooE1q8svlF3Ov5X14pEMRKpGxBi0BAwnVZga1Jq7CsFnQZQKJISuwVQ04'
            +'PDiDTgTolBQWCjvo8goomkQCCSEgCGQCM9XYhM0xFjjgCAoj8PAZhZNYMkga'
            +'Ogx0QTDO6FaSNrZQBMwrE1p4iCI7EVTCNiUpd40zwAjjiiiZhDeIEg/d8cEz'
            +'QsVoDTC1TKjJJIsscgRL/0SwyzXeDOmdKp5MgogXSXApUAMGmKHLLa6c0okm'
            +'UXRAg5oESdIBBsWp0GNHAQEAOw==')

embarrased = ('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'
            +'DaEgwQgaWFAAnwEBADs=')

sad = ('R0lGODlhGAAYAOf/ABMQDhwPBRUTCBkSCRoQERQYCx8SGRkWFBcZFhoWHxgY'
            +'GyUUDyAWEh0YEjMQASQXBh4XGyAXFyIZByQVGCYSIycYASAZDx0ZGB8bCCkW'
            +'CBsbFB0bDywWAiQYDyAWJRseCiIXIRoeFCUcBSEbFiQYHiQaFjkVAC8aAR8h'
            +'CCEdHB0fHSkeAisaFy0dAiAeIjUaACYfECQdIiYdHSEeJyUfGigiAkIVASMh'
            +'FiseESIhGycgFjQeAC4fDSIkEzEgACofGi4iACIjISElGyweIyYiIUMbACsg'
            +'LDkiAD0gAC0lESokHy8oADYlACcpJywnJisnLC0qIzstAFMhAEgnAEMrAEAt'
            +'ADUzMlczADo6MVE4AEw8AEE9P1xAAGJEA3c8AF9KCXFBCW9HAE5MS25NAWlR'
            +'AFRQSV9dXIRXHH5fBndiC3VhIYtcA39nAGtpZ5VpHpFxCotyGI13C3VzcY53'
            +'Ko54NH9+fM9nH8dxEM1tF9xlGtZrDsN2CtRrGdhpG6SDH6+DCpyGMqODL6WI'
            +'E6CIItRxEK6HC6uLCM97ANxxFa2NALOLAMSADtt3CuB0DbORAo6LivBvFraO'
            +'Fcp+NbmRBrORGOh6Bup2Fud2H+B/Au50F+x4COZ5FK+UG+V9BeN9FdyEBbSY'
            +'DLmWDOp8Ga6UPOeDAM+LGNeEKL2ZALCXL8KYAOCJAMCWE7aWMruUN76bFpqX'
            +'l9iSCsacCsyWHc2aBbqeJ8SfDMehAMufANWYDOaRB9CSR82nCdKlCdWnAO+b'
            +'ANmqANWtAKimpcepQuWlD/CiBMmtN8yuK+CrBt2uCNOrNdOoSdW0CdyzAOGx'
            +'AOWvAO+tANizI+i3BOy1B+O6Bf2tD+27APyxFf+0APe2FuzAAPW8ANy9Qe27'
            +'IvLAAO60TP+5BOe9Meu7Mem/I+LBLuHAN+PGF+XDJPy9B+a9Q+zCGOG+UezH'
            +'BffDAP+/APrACvLFCvzCAPbDC/THAPnFAPXCHvHKAPvHAP/FAPHJIv7KAP/M'
            +'AOnJTf3PB//RAPLRQv///yH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAh+QQB'
            +'CgD/ACwAAAAAGAAYAAAI/gD/CRwo0AWFERBGXIDwiKBDhwdYCIunLd47e/HS'
            +'MCDw0KEHcO7izesGT+Q8d+1a5ej478mDefHYhYQ3j6Y7eN0s4ugIQ568kPOC'
            +'ngRakuIAhxDO1ewms2bQbjmDxoPnzsPAC+aCVsMWT2Q3d+JguoMZ1B2cBgIj'
            +'lL0wRd7XkxFawCuZE162ajr+bRF0Lh6NcHPHUs1XY8fIoOyqIavwj0VMB+Hm'
            +'sdMmtGyEdEHhVZOGbJcCGTXf3ZT8dOy8e2PtaYvWbBcvGRC6jST5zelJnCfZ'
            +'davWDBmvWykgSBYcZ8k6qCRGy4MnbRkvXrFW0VC7dJ6IETQFRYAqL9chacB+'
            +'xUF3JKNAPE1K4W1rMZXfEJqeNiG69DwWJVRP2rCxpCnku3onxeMOO/Fscskl'
            +'iNwRSyiU5PVPA5ZY8sk9I5VUoTuIEIIIH3esEkkhLghkgSmeXCKbbfAQeAkf'
            +'fdgxCyWGLPHEQApUYok8mdE0Emu47DFLJJH8MYRDAlBIjwYIkdAACsz8Ukt0'
            +'MCrxUBsP0IMjXZv5FsspkVBCBEv/bCCMTNoo5tsup1DChJRg/qOBAFd044yW'
            +'lPgwQwptOkSDBhH8MAKeLAUEADs=')
            
smile = ('R0lGODlhGAAYAOf/ABgRCBoQEy8JCRQUGBcUEhoYCxgYEScUBRwVHyIXBiIW'
            +'DCEWEh8YDR4YEyUVEC4UAiEXGCAXHR4aGS8UCyQVJBocGhweCygVGysYAyAd'
            +'Cy0VEygbBkgLCR4eGB0dIRwgFEAPDScbEyIdFywaDiEfFCcdDyoaFy4cAkUQ'
            +'BiccGDQaACUeFCMcJh8gHiMfHicdHiYdIiUiDDwVEy0hASkjAzMfACchHCMk'
            +'HT8dACYlKT0hADgkACklJCUoJjMoAC4kJS0mHy0kLDMmFCkqHzYlIjQlNEMp'
            +'ADcrHUAsADsvADEtLDkvEkQnJVAmJW4aFToyLFonJUs3ADc5LTo3N2AoIFM1'
            +'AGYlI0I1PXIoJVVBAH0oJENENoYmI0dEQUlDS5QnIpcoHaAlH68kHZUvLGRO'
            +'D29NAGtQAGdTAasuJb8mHVRUUbwoJFdWR1xTWc4lIN4eGrgwJ9gjHuMgFNEo'
            +'G9klGLQ1MHxdAtUsF4BcBHZhCoBlAGRjYGpgY4FsLI1wCo9uGohyHXludHNy'
            +'b5R2BJ2CIZyDKZ+GFKWEE4SCeZqENIKCgamHA4t/hpqGQ6+NEbOLEauQFrKR'
            +'AbqQBreOLauSO7KSLbiWDa6WL5OTiZKTkbyZALeZIsSZBJySmMqYAcOfC8ah'
            +'AMufAMWjIJ+fntGkCMGlMMKkP6mfpaOkm82pEcqlMb6mUaWmltumBbunYdmq'
            +'ANWtANujKqiop7uqdd+wAOC2ALGxoOW1AOu0A7KzqrmutbG0sraystC3Ydm6'
            +'Oe68ANi4Uti7ROC4P+m4Luu6IN6+L+e9IePAIe69FOnAFf+5BP+6AOe9Mvu8'
            +'A/e+BPHEBvXCCffDAP+/APzCAPTHAO7IC8DAve/GH/bDH+fGOcm9vuXHSv7K'
            +'APHJL9fIhP/QAMnJx9HGzd7OmtLS0N3R2tjb2N3Z2+Hk4OXi5PfnpPXmte3i'
            +'6O3t4Ort6u7r7fP18vXz+Pn08v76yv/16/361v364f/1/fv87Pr8+fX/+vz9'
            +'8//7+vn+///8//3//P///yH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAh+QQB'
            +'CgD/ACwAAAAAGAAYAAAI/gD/CRwoMJCECBBKVFDAiqBDhzYi6HHGzRk0aNii'
            +'sFjx0CGCbdC4XYzmrKQzapM6dPzHJwA0ahahRZNJMRo3atVSdGTRrB6yaDO5'
            +'PeMmzxg3kjJ7OLzgrJ+/fUBtPrvnz5/MaRafuRgoQVi2IlWNAZ0G7YK/fnls'
            +'AoW2yoNAGM7MEKgqTCbGAFUbTZsWbdozXC/+8arid8rTY0dJBqkabK/NWs1q'
            +'/BsgEhpVdnzJQqtXtZldXLdapZLQwK7QmXxnRhtGrbKzW8ReiVqxAhpZss72'
            +'yuR2VCbJX7hSkeLkosGzsb6jzrSNtRatV6lAWepgQIggRIoyKUKESJB3QXz2'
            +'2Oxh08VLq1CcLNlYgIPXuHf84letGr9fP3TWZLX6ZAlSC15JtFABDzdQ18KB'
            +'LbggYAUH9sCJJI/QIBADE7wRRxwWvvHGHGmIEcYXWljRRA2bbPKIW/+kAEwd'
            +'LLbI4hhjaIGFiD9IIokjfQQxUA6xjLJLOfDMt88+75SzSyebcPIIJDk4ZAI2'
            +'DZQzz3xVvbNODo5AAokhEDyEyQbcbAJBJk7howgJhXCiySOLoNjRAqUw5wwu'
            +'tET3IBkxrDRQAxVk4cwvz3kiSg0uiKCnQ5hEIIELL3Rg6EoBAQA7')
            
wink = ('R0lGODlhGAAYAOf/ACUGABMTCRgRChsPDhkPFRUSEBwUByASBxkWBysPAxoT'
            +'HRcXGxkYESgSDBsXFh8VFh0XEiAYBSQWBSgUBRgbDiUTFiEWEhYcFRkaGDQR'
            +'ACEZDxwdCisXAh4bECkVFCgZAx8YIiYVHyMXHSYYECAcCxwcFiAZHSIdAyYb'
            +'BCAbFjAXAB8bGiMZGiUZFh0cHygdABsdJC8aACYXKSwcACYdDiEgGh8hHiMf'
            +'HiUfGh8jFiMhFicfFigeHyoeGzgcAB4kHDEgAC4iADQfACwfFyYfKickDi0i'
            +'CislASkgJSUmFSQkKDMgFSYlHzMiDiQmIygkIyokHzojADclAC8lF0AiADEq'
            +'ATYoAC4nHT4pACosKC8qKDspDTQoKC4tITQqL0wsAEowAEk0AD01HDoyNjc1'
            +'NEAwODM5LD40LDk3LEI4EEc4A0c0H1Q4AU84E1E8AFs3AEA+PmU7AF5BAF9M'
            +'AF1LD05JS2hLAE1PS1hUVHJYAW9YDnpWA3lfAGBfXWddZXllKohnCYhnG4Vs'
            +'DGxqaINuIZtxAJR5Gnl2dpx5H5x7MaN+D52BEJV/MpyBJIKBf6mJGayLCaWM'
            +'G6WKLKmODLCIG7OLDrWNAKOMO7GQAK+KL4+Mi7ORFLOWCbeUCbuSCbGUJq+T'
            +'NcCWALyZAMSaBb6bFsOZF5qXltCYAMOeC8ecC7ydMMahAMyfAL+fQsulBcKj'
            +'KtCjBcmgN9GpANOmDMmnJdaoAKWjo9yoAMeoO9WuANutBN+vANWvHdytGuGx'
            +'AN+1ANCzNa+urOS0ANiuSOuzAeK4ANSzRue2A+C3FvWxCty2O+u6AOG0PPC4'
            +'AOK5KOm9APq1AOG5MuO/Dd69Key7D+G+Hdu7Pu+9APi5AN69M+m+EOu6IOq6'
            +'Lva9AP+6APPAAerFAPW9GevAJfDEBPfDAP+/AP6+DPbDCvTGAPzCAPrBC+LA'
            +'UuvBN/DJAOnFKfDEHfnFAOvHHfXDHuTFRvvHAP/FAOjHOfnGE+zDR/bJE/7K'
            +'APPNF/zOBP/PAPzUD////yH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAh+QQB'
            +'CgD/ACwAAAAAGAAYAAAI/gD/CRw4sESNBxg0tCDIsOEODFS+qUv3bZw0IRCg'
            +'NGTY4ZG6et6+wZM47mOYBxv/2dLQbVy6kd1ekjs3El63FBsR0BupDt5Ln91o'
            +'kqsHD94Chjq6obt3jubIcyK7TfwmUp1GgQGsnfuprmnXok5jitwjQqCNb+Tg'
            +'nev59Fs9cD6pFu12bMO/PojMRRMDlao6c18gDEjHVt23a7ua/MMxklaZpj7X'
            +'KlKnD93Il9eE6aK1gsHadOG+dfsG1XC6dON8jsysyxWLFOQovhwNT53UuLUP'
            +'7+qVapWLFPReChd+rpvPfbHGUROWC1YqUStspKMtd6TcdKrkXDu2y1UqUpxu'
            +'v9wQWfMbxaKn/W2oR2xX61SeIq3oA0hkdaoix7lDcExXr1mokLLJBwJ1IBJN'
            +'B0KVTjxPYPNLL7CwQgomkCghUA7zwNMOVadN94kL0hSjyyypjNJJJGqQMRAS'
            +'4hjAzlSGbDDBOdQgQ6IonUDyiIUEufANIxF0MMM8/HxDzDa1wIKKJzrasFES'
            +'lqWz02GauTKLgJG4kNI/CCCCHmK6RMgJJlIwsaVZGPjwTTG+zDJLKVtgoMWZ'
            +'DK2ggQM5QOBkSgEBADs=')

wink2 = ('R0lGODlhGAAYAOf/ABkRCBUSERsQEx4TDhsUHhgYESYUBBoZDCMYByMXDhgb'
            +'GSAZDhwcCSEXGCYWEiIYFBsaHR0aGR8aFCAYHTAVBSgVHCwYBCUWJCcbBDgR'
            +'DzMTE0wJBjIVDS4WFD8PDB4eGCAeExwgFCEbJS0cAVMJACMgCR0eJiAeIR4g'
            +'HkURCCIfHikeESsgATUbASUdIigdGicdHiIiESUfGigiAicfFjIfAC4dGSMj'
            +'HSUjGD0cAC4iECQmJCYlKTgkACklJD4iASokLjQoAS4kJyoqIDMqDjAoITkr'
            +'AD8pADokLGUWDi4tLDIwGkQnJTovHEgoHEsvAEYzAFAnJkQwGFclKD0zLGMi'
            +'ITQ3NTY4LTk1NT0zN1wnI0E4GFY5AFE+AmYuJW8rJ3gpIHYpJ2cxLYUkIoAp'
            +'HkhDNH8qJownHUdFRFxIAE1DSGJGAJcmJZ0lIJErKKcoILQkHWRRFrQoJqMw'
            +'LMQlH1VUUllVQ3dUA94dGXBYCWNXNa4zK84lIF5UWd4eIL8uJdckHtEoG9kl'
            +'GHlcAOkeHGddX2RhWmNjY2VlVX1oLYhrDIFsH4lpHH5xS3Jxbpp7H5V9MJyA'
            +'DaN9C5aAIoJ/hoSCf6yLDbGJD5uJW6qPE7GPAKaNN66OKqmRK7qRCL6PCbaU'
            +'CLSSG7yYAMGXAJWTj5WSmcuZAcKeA8abCcOZHMCeGribR8ufAL+gKrOfXr6g'
            +'O6WaoNCjBqCfn8ynDqOkmtunAtSsANmqAKinp96vAN+1AOOzAOiyALCvrNe1'
            +'Ne+yBNO0Rt2xQ7Oytte3P+S4Guq4Cse1e9W2XO27ALa4qLi4tPW7AOe/Ed++'
            +'Lua7L+PAIcm9hf+7AP+6Bu/DAvXCCPfDAP+/APrAC/zCAPTBHO/CKPTHAOTC'
            +'TL/AvcC/w+/GHufDRPvHAOfHO/TJEf7KAMPHvMrBzP/QAP7QDMfKx8zIytDT'
            +'0NTWy9nU09jU2tjb2eLj4OLi5+Xm2urs6u/r7fTq8PP18vzx+Pf09vr8+f/7'
            +'+v799Pn+///8//3//P///yH+FUNyZWF0ZWQgd2l0aCBUaGUgR0lNUAAh+QQB'
            +'CgD/ACwAAAAAGAAYAAAI/gD/CRwosI6EBggbBHBEsGFDGjIUhbt2Ddu1cXcU'
            +'KHDYsAA4ateoVaOGrRo2kMACcPxnCAC1cCOpiTRJUyQAjgSuVRtJ8yTJmuE2'
            +'EvygU6TMmSVLmgxHbZqIgQGciUxKcmbVpDuBnRAI4+LOryaNlpxZDVmxAwKN'
            +'UGuGJdxJn+Ne/sRGl1qxH/8ikAQ3xO3UaLy2TNs5FdmuXM1UPCB5kW7PiVix'
            +'LSu26xYrxdi2WQxZk2zhyrFMRVjgGVu0atqgGADRR52sGxiIOYt1SlSEBtGo'
            +'MQNWo0EZffz8CRduD143WLNiiQoVIUCQUr26rYs3r9/w4fbedZM165QnSw3+'
            +'u5UQAQOFCRQoJJg4AUGBChcQXKA4gWoUqBkCF/wBJAiQf0GCBPLHG224MUYV'
            +'TARxSiaWyCAQChP0B2AgFNJBoBtmiBHFC6l8l4iDAoXwAC3KsDOPP/xY5w8+'
            +'7nhTSiuqWCIJDA0FgEM665x4nT3uKLGKKJpYQqNDADwBxIn59NOPPgJYcIoq'
            +'oUjywEr/fNDJNc2sscYrtthiynJxbEXlP0I08MQ01NgSCyqqjCDDBGM2BIMI'
            +'DTwggwpUBgQAOw==')
            
beta = 'R0lGODlhIAAgAMZUAAAAAAEBAQICAgMDAwQEBAUFBQYGBggICAkJCQoKCgwM' \
        +'DA8PDxAQEBISEhQUFBYWFhcXFxgYGBsbGxwcHCAgICUlJSYmJioqKisrKzY2' \
        +'Njs7Ozw8PEJCQkRERFRUVFVVVV1dXWJiYmVlZWdnZ29vb3BwcHd3d3h4eH9/' \
        +'f4GBgYeHh4iIiIuLi4+Pj5OTk5eXl5iYmJycnJ2dnZ6enp+fn6CgoKGhoaKi' \
        +'oqOjo6Wlpaenp66urrCwsLGxsbKysrm5ubq6ury8vL29vcDAwMfHx8jIyM7O' \
        +'zs/Pz9XV1djY2Nvb29zc3N3d3eDg4OTk5OXl5ebm5ufn5+jo6Orq6v//////' \
        +'////////////////////////////////////////////////////////////' \
        +'////////////////////////////////////////////////////////////' \
        +'/////////////////////////////////////////////////yH+FUNyZWF0' \
        +'ZWQgd2l0aCBUaGUgR0lNUAAh+QQBCgB/ACwAAAAAIAAgAAAH/oB/goOEhYaH' \
        +'iIl/PzI1QIqQhSQIAJUABh9TkYoZlgcPlhNSm4colRQ8gycDAB6khhAAC1CF' \
        +'LAACo6+CSJUgh6w+uoI9lSuHDQA1wn81lTGHBABDyzCVOIbECct/L9aFUhUA' \
        +'JNvdADd/UEdCKhIAHdvclecmlgAf8PEANn/09Qon5CopS1dkRwlkADgsK0fj' \
        +'0IZKLYQxPLSk0gWJlWYgsgAgAEYAMhBpqPREV7mQhzBU+pjikBNWET4yYGJo' \
        +'RCURHwE4cBFFUJIQlQ4o+dgpaAFLA659xJFjQj0AF4IEBKCUSIwWM4zgK6cU' \
        +'XyGuXg2BDUtoLFlBZs8u0aGjybZAADs='

delta = 'R0lGODlhIAAgAMZYAAAAAAEBAQMDAwQEBAcHBwoKCgwMDBAQEBERERISEhQU' \
         +'FBUVFRYWFhgYGBkZGRoaGiIiIiQkJCgoKCoqKi0tLS8vLzIyMjg4OD4+Pj8/' \
         +'P0BAQEFBQUREREVFRUlJSUtLS09PT1VVVVdXV1hYWFlZWV1dXWRkZGlpaW5u' \
         +'bnFxcXNzc3p6en19fX5+foGBgYKCgoiIiIuLi5CQkJKSkpSUlJWVlZiYmJmZ' \
         +'mZ2dnZ6enqCgoKGhoaKioqOjo6urq7Kysra2tre3t7i4uLu7u76+vsHBwcLC' \
         +'wsjIyMnJycrKysvLy8/Pz9DQ0NTU1NXV1dfX19ra2t7e3uPj4+Xl5ebm5urq' \
         +'6uvr6+zs7P//////////////////////////////////////////////////' \
         +'////////////////////////////////////////////////////////////' \
         +'/////////////////////////////////////////////////yH+FUNyZWF0' \
         +'ZWQgd2l0aCBUaGUgR0lNUAAh+QQBCgB/ACwAAAAAIAAgAAAH4IB/goOEhYaH' \
         +'iImKi4yNjo+QkZAlBJWWl5VXkiIAnZ6fnVaSOwSdDzg+qao+koJME50QSK2J' \
         +'J50DMLSIPwqdHFS6hlQdnQtAwYI1GwoJngEuuksRoJ8orVAHnRM3SUo8Gp45' \
         +'khidH4YxnQqRScWIIZ06kCydK4hGnSSQIJ1FiQIAFCBd6DQlEQMADSBZ6FQl' \
         +'US8HkMABaJIoAAAJkEzAQxSkkwdIPTplQDSi04tICDrJMDTEIoAnkWx4CiEk' \
         +'ihQnMwp0GtFKBbVPFXT5mAbKQApkf47QaOGiBhGkUKNKPRQIADs='

phi = 'R0lGODlhIAAgAMZTAAAAAAEBAQICAgMDAwQEBAUFBQYGBggICAkJCQwMDA0N' \
       +'DRsbGx8fHyMjIy0tLTExMTMzMzQ0NDU1NTo6Ojs7O0REREVFRUdHR0tLS01N' \
       +'TVNTU1RUVFpaWltbW11dXWFhYWNjY2dnZ2lpaXBwcHNzc3R0dHZ2dnt7e319' \
       +'fX5+foeHh4mJiY2NjZSUlJWVlZaWlpeXl5mZmZqamp6enqOjo6ampqenp6io' \
       +'qKmpqbCwsLGxsbKysrS0tLe3t7i4uLq6uru7u76+vsDAwMLCwsXFxcfHx8nJ' \
       +'yczMzM7Ozs/Pz9DQ0NLS0tTU1NnZ2dra2tzc3OLi4uTk5Orq6v//////////' \
       +'////////////////////////////////////////////////////////////' \
       +'////////////////////////////////////////////////////////////' \
       +'/////////////////////////////////////////////////yH+FUNyZWF0' \
       +'ZWQgd2l0aCBUaGUgR0lNUAAh+QQBCgB/ACwAAAAAIAAgAAAH+IB/goOEhYaH' \
       +'iImKi4yNjo+QkZJEg0MYGBkcKECSf1EUA0mCNgClpgw1kFAMpRejprAAIo8Q' \
       +'pRJRrwAjRzgaAaUojSylD4SkACqDPwkAA0qMCwAGTsalyYM3pR2LRaUfhcfX' \
       +'gw4ACosupTng1oUlpUyKKKVL68iF6ABBiimlSPXiglqU+qFoRika/wqNKPUs' \
       +'UZNSFRISagAAAaMIB6vZGxSj1AZGO0oVeDEo3CAdBwAIONIIhKkHK3acKAXC' \
       +'hwwMplI8ChGrpykTkYBYIOCz1IQenQQZ4UGilAcdQqQklTiVatWS7K5qBKjV' \
       +'pNZBT2DAEPW1rNmzggIBADs='

Sigma = 'R0lGODlhIAAgAKU2AAAAAAICAgUFBQYGBggICAsLCw0NDQ8PDxQUFBUVFRkZ' \
         +'GRwcHCwsLDExMTU1NTY2Nj8/P0dHR0xMTFBQUFhYWFpaWltbW19fX2VlZWdn' \
         +'Z3BwcHV1dYeHh4iIiIuLi4+Pj5WVlZubm6Ojo6Wlpaurq7CwsLOzs7a2trm5' \
         +'ucHBwcTExMnJyc7Ozs/Pz9HR0dXV1dnZ2dvb297e3uHh4eXl5efn5///////' \
         +'/////////////////////////////////yH+FUNyZWF0ZWQgd2l0aCBUaGUg' \
         +'R0lNUAAh+QQBCgA/ACwAAAAAIAAgAAAGmMCfcEgsGo/IpHLJbDqf0KgT9ala' \
         +'r1jS8wLoer9gyBZM/oqdI6+nxW67WzHopmtwSZWS7qJ2TzK6D31IMghdFYJH' \
         +'KQJdHIhGIV0BJY5FGl0FLJRDGHQvmj8gkSafil0dnzMJXRafPw1dDq0UXQo0' \
         +'nx1dBCufJwFdIp8wB10brRNdAxgZy8zNzCpNEWXTXSHR1NPWrdvc3X1BADs='

class Imgs:
    emoticGifs = [confused, embarrased, sad, smile, wink, wink2]
    symbolGifs = [beta, delta, phi, Sigma]
    mathGifs = [eq, less, great]

    def __init__(self):
        global imgs
        imgs = []
        for e in self.emoticGifs:
            img = PhotoImage(format='gif', data=e)
            imgs.append(img)
        for s in self.symbolGifs:
            img = PhotoImage(format='gif', data=s)
            imgs.append(img)
        for s in self.mathGifs:
            img = PhotoImage(format='gif', data=s)
            imgs.append(img)

    def firstKind(self, kind):
        ret = self.getQTotal()
        if kind == EMOTIC:
            ret = 0
        elif kind == SYMBOL:
            ret = self.firstKind(EMOTIC) + self.getQKind(EMOTIC)
        elif kind == MATH:
            ret = self.firstKind(SYMBOL) + self.getQKind(SYMBOL)
        return ret
        
    def getKindImgs(self, kind):
        return imgs[self.firstKind(kind):self.getQKind(kind)]

    def getAllImgs(self):
        return imgs

    def getQKind(self, kind):
        ret = 0
        if kind == EMOTIC:
            ret = len(self.emoticGifs)
        elif kind == SYMBOL:
            ret = len(self.symbolGifs)
        elif kind == MATH:
            ret = len(self.mathGifs)
        return ret

    def getQTotal(self):
        return len(imgs)

    def getImg(self, number):
        return imgs[number]
    
