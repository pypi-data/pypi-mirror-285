import time,os,pygame,urllib.request,threading,random
pygame.init()
def meow():
    if not os.path.exists("meow.mp3"): urllib.request.urlretrieve("https://github.com/NumbersTada/ScratchTomfoolery/raw/main/Ko%C4%8Dkov...%20M%C5%87AU!!!!!.mp3","meow.mp3")
    pygame.mixer.Sound("meow.mp3").play()
    print("uaua");time.sleep(1)
    print("uaua");time.sleep(1)
    for i in range(20) :print("UAUA"+"".join(chr(random.randint(1,1000)) for i in range(10)),end="",flush=True);time.sleep(0.05)
for i in range(3): threading.Thread(target=meow).start();time.sleep(1)
