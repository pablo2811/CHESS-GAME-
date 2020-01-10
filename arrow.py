
import math,os
from PIL import Image

def arr_naImage(D,path):
    if math.ceil(D) - D > D - math.floor(D):
        h = math.floor(D)*60
    else:
        h = math.ceil(D)*60
    arr = Image.new(mode="RGBA",size=(60,h))
    os.chdir("graphics")
    seg = Image.open("segment.png")
    grot = Image.open("grot.png")
    for y in range(0,h,30):
        arr.paste(seg,(24,y))
    arr.paste(grot,(0,0))
    arr = Image.eval(arr,lambda x: x/1.1)
    os.chdir("..")
    os.chdir("ARROW")
    arr.save(path,format='PNG')
    os.chdir("..")










