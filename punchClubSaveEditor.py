#coding: utf-8
from Crypto.Cipher import AES
from datetime import datetime
from getpass import getuser
from sys import platform
from os import path as PATH

# FILES PATHS
if platform.startswith('win'):
    path = "C:\Users\%s\AppData\LocalLow\Lazy Bear Games\Punch Club\\" %getuser()
elif platform.startswith('linux'):
    path = '~/.config/unity3d/Lazy Bear Games/Punch Club/'
elif platform.startswith('darwin'):
    path =  '~/Library/Application Support/unity.Lazy Bear Games.Punch Club'
else:
    raise RuntimeError('Operation is not supported in this platform')

# AUX FUNCITONS
def getList(data,searchString):
    searchStringIndex = data.find(searchString)
    startIndex = data[searchStringIndex:].find('[') + searchStringIndex
    endIndex = data[startIndex:].find(']') + searchStringIndex + len(searchString)
    rawList = data[startIndex+1:endIndex+2]
    return (filter(lambda x: x not in ['\x00','\\','"'],rawList).split(','),startIndex+1,endIndex+2)

def getDict(data):
    keys,keysStart,keysEnd = getList(data, '\x00'.join(list('"_res_type\\\\\\"')))
    values,valuesStart,valuesEnd = getList(data, '\x00'.join(list('"_res_v\\\\\\"')))
    return keys,values,valuesStart,valuesEnd

# KEY AND IV OF THE AES
key = bytearray([0x7b, 0xd9, 0x4f, 0x0b, 0x18, 0x02, 0x55, 0x2d, 0x72, 0xb8, 0x1b, 0x70, 0x25, 0x70, 0xde, 0xd1,0xf1, 0x18, 0xaf, 0x90, 0xad, 0x35, 0xc4, 0x13, 0x18, 0x1a, 0x11, 0xda, 0x83, 0xec, 0x35, 0xd1])
IV = bytearray([0x92, 0x40, 0xab, 0xa1, 0x02, 0x03, 0x71, 0x77, 0xe7, 0x79, 0xdd, 0x70, 0x4f, 0x20, 0x72, 0x10])

# INSTANTIATION OF AES OBJECTS
decryptor = AES.new(bytes(key), AES.MODE_CBC, bytes(IV))
encryptor = AES.new(bytes(key), AES.MODE_CBC, bytes(IV))

# OPENS AND READ THE INPUT FILE
saveNumber = 0
while(saveNumber not in ['1','2','3']): saveNumber = raw_input("Select the save file that will be edited (1,2 or 3): ")
path += 'save_%s.dat' %saveNumber
if not PATH.isfile(path): raise RuntimeError("This file save_%s doesn't exists" %saveNumber)
inp = open(path,'rb')
content = inp.read()
inp.close()

# ATTRIBUTE LEVELS/POINTS DICT
levelsPoint = [0,100,200,350,500,750,1000,1300,1600,1900,2200,2500,2800,3200,3700,4200,4700,5200,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,30000,50000,70000,100000,200000]
attLevel = {(lvl+1):point for lvl,point in enumerate(levelsPoint)}; attLevel[0],attLevel[-1] = 0,-777

# USER INPUT
print('IF YOU DO NOT WANT TO MODIFY THE ATTRIBUTE JUST PUT A "-1" (WITHOUT QUOTES)')
inputs = { 0 : '_money', 1 : '_sp', 2 : '_str', 3 : '_agl', 4 : '_stm'}
newValues = [str(min(int(raw_input("Money: ")),99999)), str(min(int(raw_input("Skill points: ")),3000)), int(raw_input("Strength (1-32): ")), int(raw_input("Agility (1-32): ")), int(raw_input("Stamina (1-32): "))]
for i in xrange(2,5):
    if newValues[i] == 0: newValues[i] = '50'
    elif newValues[i] > 0: newValues[i] = str((attLevel[newValues[i]] + attLevel[newValues[i]+1])/2)
    else: newValues[i] = str(newValues[i])

# DECRYPTS THE CONTENT AND FILTER THE RELEVANT INFORMATION
decryptedText = decryptor.decrypt(content)
keys,values,valuesStart,valuesEnd = getDict(decryptedText)
indexes = {value : keys.index(value) for value in inputs.values()}

# MODIFY THE ATTRIBUTES
for index,newValue in enumerate(newValues):
    if newValue.isdigit() and int(newValue) >= 0: values[indexes[inputs[index]]] = newValue
    elif newValue.strip(): print "%s will not change" %inputs[index][1:]

# GENERATE THE NEW CONTENT
newDecryptedText = decryptedText[:valuesStart] + '\x00' + '\x00'.join(list(','.join(values))) + decryptedText[valuesEnd:]

# CHECK IF THE NEW CONTENT HAS A NUMBER OF BITS THAT IS MULTIPLE OF 16, DUE TO AES CBC RESTRICTION
mod16 = len(newDecryptedText) & 15
if mod16: newDecryptedText = newDecryptedText + '\n'*(16-mod16)

# ENCRYPTS THE NEW CONTENT AND WRITE IN THE OUTPUT FILE
encryptedText = encryptor.encrypt(newDecryptedText)
out = open(path,'wb')
out.write(encryptedText)
out.close()

# STORES THE FORMER SAVE AS A "TIME_STAMP".OLD
timestamp = datetime.now().strftime('%Y-%b-%d_%H-%M-%S')
oldSave = open(path[:-4] + '_' + timestamp + '.old','a+')
oldSave.write(content)
oldSave.close()

raw_input('Press any key to exit')