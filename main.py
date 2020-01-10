import copy,os,arcade,time,math
import arrow,engine

HEIGTH = 481
WIDTH  = 581
TITLE = "CHESS"
glowny_projekt = os.getcwd()
figury_sciezka = os.path.abspath("pieces")
grafika = os.path.abspath("graphics")

def setup(save=None): #save - > str zawierajacy nazwe sejwa
    core = engine.Obsluga(-1,-1,2,-1,{}) #wartosci nieosiagane, core odpowiada za inicjalizacje rozgrywki
    if not save:
        for i in range(8):
            core.biale.append(engine.Pionek(i,1,1,0))
        setin = [engine.Wieza(0,0,1,0),engine.Wieza(7,0,1,0),engine.Kon(1,0,1,0),engine.Kon(6,0,1,0),engine.Goniec(2,0,1,0),engine.Goniec(5,0,1,0),engine.Krolowa(3,0,1,0),engine.Krol(4,0,1,0,0,0)]
        for i in setin:
            core.biale.append(i)
        for k in core.biale:
            z = copy.deepcopy(k)
            z.y = 7 - k.y
            z.col = -1
            core.czarne.append(z)
        tura = 1
        return core,1
    else:
        os.chdir(glowny_projekt)
        os.chdir("SAVED_GAMES")
        biale1 = []
        czarne1 = []
        with open(save,"r") as s:
            data = s.readlines()
            i = 0
            if data[0][:-1] == "TIME":
                czasW,czasB = int(data[-2][:-1]),int(data[-1][:-1])
                data.remove("TIME\n")
                data.remove(str(czasW)+"\n")
                data.remove(str(czasB)+"\n")
            else:
                czasW,czasB = None,None
            while i<len(data)-2:
                if data[i][0].isupper() : #linijka mowiaca o nazwie klasy
                    nazwa_klasa = data[i][:-1]
                    i+=1
                    dic = {}
                    while data[i] !=  "-\n": #dopoki nie koniec fragmentu opisujacego dana figure
                        a = data[i].split(":")
                        dic[a[0]] = a[1][:-1]
                        if a[0] == "col":
                            col = int(a[1])
                        i+=1
                    klasa = engine.zmienne()[nazwa_klasa]
                    if col == 1 :
                        new = klasa(dic)
                        biale1.append(new)
                    elif col == -1:
                        new = klasa(dic)
                        czarne1.append(new)
                    i+=1
            tura = int(data[-1][:-1])
        core.biale = biale1
        core.czarne = czarne1
        for fig in core.biale+core.czarne:
            fig.biale = biale1
            fig.czarne = czarne1
        return core,tura,czasW,czasB


def zerowanie(self):
    self.zwiazana_wieza = None
    self.gdzie_wieza = None
    self.punkt_krola = None
    self.pionekbicie = None

def slowczas(i):
    x = {
        0: 900,
        1: 600,
        2: 300,
        3: 180,
        4: 60,
        5: None
    }
    return x[i]

def value(fig):

    maps = {
        "Pionek" : 1,
        "Goniec" : 3,
        "Kon"    : 3,
        "Wieza"  : 5,
        "Krolowa": 9
    }
    return maps[fig]

def jakistartslownika(figury): #funkcja okreslajaca ilosc zbitych figur danego koloru ,potrzebne przy czytaniu z sejwow
    typy = ["Pionek","Goniec","Kon","Wieza","Krolowa"]
    wart =[[0,8],[0,2],[0,2],[0,2],[0,1]]
    for fig in figury:
        if type(fig).__name__!= "Krol":
            co = typy.index(type(fig).__name__)
            wart[co][0] += 1
    dic = {}
    for i in range(5):
        dic[typy[i]] = wart[i][1] - wart[i][0]
    return dic

def pom(tab):
    for fig in tab:
        if type(fig).__name__ == "Krolowa" and fig.col == 1:
            print(f"krolowa na {fig.x} {fig.y} koloru {fig.col}")
    print("------")

class MyGame(arcade.Window):

    def __init__(self,WIDTH,HEIGTH,TITLE,core,tura=1,czasW=None,czasB=None):
        if czasW:
            self.czasy = ["in_korekta", czasW, czasB]
        super().__init__(WIDTH,HEIGTH,TITLE)
        self.plansza = core.biale+core.czarne
        self.Bite = ["in_korekta",jakistartslownika(core.czarne),jakistartslownika(core.biale)]
        self.core = core
        self.tura = tura
        self.wybrany = None
        self.gdzie_wybrany=None
        self.zwiazana_wieza = None
        self.gdzie_wieza = None
        self.punkt_krola = None
        self.zmiana = None
        self.remis = None
        self.pionekbicie = None
        self.eskejp = None
        self.nazwasejwa = None
        self.koniec = None
        self.arrbeg = None
        self.arrend = None
        self.donarysowania = None
        self.arrow_actual = []
        self.czas = czasW #tylko dla sprawdzania ze czas wgl jest
        self.prev_dis_time = time.time()
        self.odzeraarrow()
        arcade.set_background_color(arcade.color.WHITE)

    def odzeraarrow(self):
        """oproznia sie za kazdym razem jak zaczynamy rysowac strzalki i na poczatku gry"""
        os.chdir(glowny_projekt)
        if not os.path.isdir("ARROW"):
            os.mkdir("ARROW")
        else:
            os.chdir("ARROW")
            for file in os.listdir(os.getcwd()):
                os.remove(file)
            os.chdir(glowny_projekt)
        self.ilemamy = 0

    def draw_chessboard(self):
        os.chdir(grafika)
        plan = arcade.load_texture("plansza.png")
        plan.draw(center_x=240,center_y=240,width=plan.width,height=plan.height)
        King = engine.szukaniekrola(self.plansza,self.tura)
        if King.szach == 1:
            czer = arcade.load_texture("szach-pole.png")
            czer.draw(center_x=King.x*60+30,center_y=King.y*60+30,width=60,height=60)
        os.chdir(glowny_projekt)
        os.chdir(figury_sciezka)
        for fig in self.plansza:
            sciezka = ""
            if fig.col == 1:
                sciezka += "W" + type(fig).__name__ + ".png"
            else:
                sciezka += "B" + type(fig).__name__ + ".png"
            tekstura = arcade.load_texture(sciezka)
            tekstura.draw(center_x=fig.x * 60 + 30, center_y=fig.y * 60 + 30, width=tekstura.width, height=tekstura.height)

        for i in range(9):
            arcade.draw_line(i * 60, 0, i * 60, 480, color=arcade.color.BLACK)
            arcade.draw_line(0, 60 * i, 480, 60 * i, color=arcade.color.BLACK)

        os.chdir(grafika)
        bk = arcade.load_texture("back_time_counter.png")
        bk.draw(center_x=530, center_y=240, width=bk.width, height=bk.height)
        czarne_punkty = self.suma_figur(self.Bite[-1])
        biale_punkty = self.suma_figur(self.Bite[1])
        a = 0
        if czarne_punkty>biale_punkty:
            a = -1
        elif biale_punkty>czarne_punkty:
            a = 1
        if self.tura == a:
            arcade.draw_text("+" + str(abs(czarne_punkty-biale_punkty)),515,90,arcade.color.BLACK,20,font_name="calibri")
        elif self.tura == a*(-1):
            arcade.draw_text("+" + str(abs(czarne_punkty-biale_punkty)),515,400,arcade.color.BLACK,20,font_name="calibri")
        ile_czego = self.wypadkowy_slownik_zbic()
        i,j,m,n = 0,0,0,0
        for key in ile_czego.keys(): #kluczem w tym slowniku sa wartosci postaci WPionek WWieza BWieza etc..
            tekst = arcade.load_texture(key + ".png")
            for w in range(ile_czego[key][0]):
                if self.tura == ile_czego[key][1]:
                    tekst.draw(500 + i, 150 + m, tekst.width * 0.5, tekst.height * 0.5)
                    i += 21
                    if 500 + i > 580:
                        i = 0
                        m += 30
                elif self.tura == (-1)*ile_czego[key][1]:
                    tekst.draw(500 + j, 370 - n, tekst.width * 0.5, tekst.height * 0.5)
                    j += 21
                    if 500 + i > 580:
                        j = 0
                        n += 30

        if self.czas:
            czasgrajacego = f" {int(self.czasy[self.tura])//60} : {self.czasy[self.tura]%60} "
            czasstop =  f" {int(self.czasy[self.tura*(-1)])//60} : {self.czasy[self.tura*(-1)]%60} "
            colStop = self.what_col(-1)
            colGraj = self.what_col(1)
            arcade.draw_text(czasgrajacego,start_x= 495,start_y=50,color=colGraj,font_size=23)
            arcade.draw_text(czasstop,start_x=495,start_y=430,color=colStop,font_size=23)

        os.chdir(glowny_projekt)

    def what_col(self,a):
        if self.czasy[self.tura * a] < 60:
            col = arcade.color.RED_DEVIL
        else:
            col = arcade.color.BLACK
        return col

    def draw_bicie(self):
        if self.gdzie_wybrany != None:
            os.chdir(figury_sciezka)
            gwiazdka = arcade.load_texture("Bicie.png")
            for (x, y) in self.gdzie_wybrany:
                gwiazdka.draw(center_x=x * 60 + 30, center_y=y * 60 + 30, width=gwiazdka.width, height=gwiazdka.height)
        os.chdir(glowny_projekt)
    def ilestrzalek(self):
        os.chdir(glowny_projekt)
        a = os.listdir("ARROW")
        return len(a)
    def on_draw(self):
        if not self.eskejp and not self.nazwasejwa and self.czas and time.time() - self.prev_dis_time > 1:
            self.czasy[self.tura] -= 1
            self.prev_dis_time = time.time()
        if self.arrow_actual:
            os.chdir(glowny_projekt)
            os.chdir("ARROW")
            i = 0
            for strzalka in self.arrow_actual:
                do_rys = arcade.load_texture(str(i)+".png")
                start,stop = strzalka[0],strzalka[1]
                cx = (start[0]+stop[0])*30 + 30  #math
                cy = (start[1]+stop[1])*30 + 30
                a = start[0]-stop[0]
                b = stop[1]-start[1]
                if b!=0:
                    al = math.atan(a/b)*180/math.pi #to angles
                else:
                    if a < 0:
                        al = 90
                    else:
                        al = 270
                if stop[1]<=start[1]:
                    al+=180
                do_rys.draw(center_x=cx,center_y=cy,width=do_rys.width,height=do_rys.height,angle=al)
                i+=1
        elif self.koniec or self.remis:
            os.chdir(grafika)
            tl = arcade.load_texture("back_end.png")
            tl.draw(center_x=240,center_y=240,width=tl.width,height=tl.height)
            if self.czas:
                tl2 = arcade.load_texture("back_time_counter.png")
                tl2.draw(530,240,tl2.width,tl2.height)
            if self.koniec:
                tek = arcade.load_texture(str(self.koniec)+".png")
                tek.draw(WIDTH/2,HEIGTH/2,tek.width,tek.height)
            elif self.remis:
                tek = arcade.load_texture("tie.png")
                tek.draw(WIDTH/2,HEIGTH/2,tek.width,tek.height)
        elif self.czas and self.czasy[-1] < 0:
            self.koniec = 1
        elif self.czas and self.czasy[1] < 0:
            self.koniec = -1
        elif self.zmiana == None and self.eskejp == None:
            arcade.start_render()
            self.draw_chessboard()
            self.draw_bicie()
        elif self.eskejp == 1 and (self.nazwasejwa or self.nazwasejwa == ""):
            os.chdir(grafika)
            fiel = arcade.load_texture("save-img.png")
            fiel.draw(center_x=240,center_y=240,width=fiel.width,height=fiel.height)
            if self.nazwasejwa:
                arcade.draw_text(self.nazwasejwa,start_x=30,start_y=240,font_size=20,color=arcade.color.BLACK)
            os.chdir(glowny_projekt)
        elif self.zmiana == 1:
            os.chdir(grafika)
            tlo = arcade.load_texture("tlo.png")
            tlo.draw(center_x=WIDTH/2, center_y=HEIGTH/2, width=tlo.width, height=tlo.height)
            if self.tura == 1:
                PIC = arcade.load_texture("biale-zmiana.png")
            else:
                PIC = arcade.load_texture("czarne-zmiana.png")
            PIC.draw(center_x=240, center_y=240, width=PIC.width, height=PIC.height)
            os.chdir(glowny_projekt)
        elif self.eskejp == 1:
            os.chdir(grafika)
            tlo = arcade.load_texture("tlo2.png")
            tlo.draw(center_x=WIDTH / 2, center_y=HEIGTH / 2, width=tlo.width, height=tlo.height)
            win = arcade.load_texture("esc.png")
            win.draw(center_x=WIDTH / 2, center_y=HEIGTH / 2, width=win.width, height=win.height)
            os.chdir(glowny_projekt)

    def suma_figur(self,ktore):
        sum = 0
        for key in ktore:
            value_j = value(key)
            sum += value_j * ktore[key]
        return sum

    def wypadkowy_slownik_zbic(self):
        wypad = {}
        for key in self.Bite[1].keys():
            wart = self.Bite[1][key] - self.Bite[-1][key]
            if wart>0:
                wypad["B"+key] = (wart,1)
            elif wart<0:
                wypad["W"+key] = (abs(wart),-1)
        return wypad

    def zmianyzmiany(self,X,Y,cobijemy=None): # nie chcemy zmieniac w on_mouse_press, bo AI kiedys (:D)
        if cobijemy:
            if (X,Y) in self.gdzie_wybrany:
                self.wybrany.zmiana_polozenia(X,Y)
                cobijemy.zbicie()
                self.Bite[-1*cobijemy.col][type(cobijemy).__name__] += 1
                if self.core.plansze_handling(self.plansza) == 10:
                    arcade.close_window()
                if type(self.wybrany).__name__ == "Pionek" and self.wybrany.y == 7:
                    self.zmiana = 1
                else:
                    self.mini_restart()
        else:
            if self.wybrany != None :
                if (X,Y) in self.gdzie_wybrany:
                    self.wybrany.zmiana_polozenia(X,Y)
                    if self.pionekbicie != None and (X,Y) == (self.pionekbicie.x,self.pionekbicie.y+1):
                        self.pionekbicie.zbicie()
                        self.Bite[-1*self.pionekbicie.col][type(self.pionekbicie).__name__] += 1
                    elif (X,Y) == self.punkt_krola:
                        self.zwiazana_wieza.zmiana_polozenia(X+self.gdzie_wieza*self.tura,0)
                    if self.core.plansze_handling(self.plansza) == 10:
                        self.remis = 1
                    if type(self.wybrany).__name__ == "Pionek" and self.wybrany.y == 7:
                        self.zmiana = 1
                    else:
                        self.mini_restart()


    def slownik(self):

        maping  = {
            0: "Krolowa",
            1: "Wieza",
            2: "Goniec",
            3: "Kon"
        }
        return maping

    def zmiana_figur(self,do_zmiany):
        for fig in self.core.biale + self.core.czarne:
            if fig == self.wybrany:
                if fig in self.core.biale:
                    self.core.biale.remove(fig)
                    self.plansza.remove(fig)
                    self.core.biale.append(do_zmiany)
                    self.plansza.append(do_zmiany)
                    self.zmiana = None
                    break
                else:
                    self.core.czarne.remove(fig)  # ciagnie sie..
                    self.core.czarne.append(do_zmiany)
                    self.zmiana = None
                    break
        self.mini_restart()

    def on_key_press(self, symbol: int, modifiers: int):
        if self.koniec or self.remis and symbol == arcade.key.ESCAPE:
            arcade.close_window()
        if self.eskejp == None and symbol == arcade.key.ESCAPE:
            self.eskejp = 1
        elif self.eskejp == 1 and symbol == arcade.key.ESCAPE:
            self.eskejp = None #odklikniecie
            self.nazwasejwa = None
        elif (self.nazwasejwa == "" or self.nazwasejwa) and arcade.key.ENTER != symbol and arcade.key.BACKSPACE != symbol:
            self.nazwasejwa += chr(symbol-32) #przesuniecie wzgledem codu ascii w arcadzie
        elif self.nazwasejwa and arcade.key.BACKSPACE == symbol:
            self.nazwasejwa = self.nazwasejwa[:-1]
        elif self.nazwasejwa and arcade.key.ENTER == symbol:
            if not os.path.isdir("SAVED_GAMES"):
                os.mkdir("SAVED_GAMES")
            os.chdir("SAVED_GAMES")
            with open(self.nazwasejwa+".txt","w") as save:
                if self.czas:
                    print("TIME",file=save)
                for fig in self.plansza:
                    nazwa_klasy = type(fig).__name__
                    dic = fig.__dict__
                    print(nazwa_klasy,file=save)
                    for key in dic.keys():
                        if key != "gdziemozna":
                            linia = str(key)+":"+str(dic[key])
                            print(linia,file=save)
                    print("-",file=save)
                print(self.tura,file=save)
                if self.czas:
                    print(self.czasy[1],file=save)
                    print(self.czasy[-1],file=save)
            self.nazwasejwa=None
            self.eskejp=None


    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.koniec or self.remis:
            arcade.close_window()
        X = x // 60
        Y = y // 60
        cotam = engine.cotamstoi(self.plansza,X,Y)
        if button == arcade.MOUSE_BUTTON_RIGHT and self.arrbeg == None:
            self.arrbeg = (X,Y)
        elif button == arcade.MOUSE_BUTTON_RIGHT and self.arrbeg:
            self.arrend = (X,Y)
            dlug_strza = ((self.arrend[0] - self.arrbeg[0])**(2)+(self.arrend[1]-self.arrbeg[1])**(2))**(1/2)
            arrow.arr_naImage(dlug_strza,str(self.ilestrzalek())+".png")
            self.arrow_actual.append((self.arrbeg,self.arrend))
            self.arrbeg,self.arrend = None,None

        if button != arcade.MOUSE_BUTTON_RIGHT and (self.arrow_actual or self.arrbeg):
            self.arrow_actual = []
            self.arrbeg = None
            self.odzeraarrow()
        if button ==arcade.MOUSE_BUTTON_LEFT:
            if self.zmiana:
                if 305 >= y >= 185 and 430>=x>=55: #math
                    for i in range(4):
                        if 55+95*i <= x <55+95*(i+1):
                            co = i
                            break
                    mapi = self.slownik()
                    na_co = mapi[co]
                    klasa = engine.zmienne()[na_co] #globals zwraca slownik zmiennych globalnych, czyli min klas
                    do_zmiany = klasa(self.wybrany.x,self.wybrany.y,self.wybrany.col)
                    self.zmiana_figur(do_zmiany)
            elif self.eskejp:
                if 310 >= y >= 180:
                    for i in range(3):
                        if 180+43.33*i <= y < 180+43.33*(i+1):
                            co = i
                            break
                    if co == 0 :
                        arcade.close_window()
                    elif co == 1:
                        self.nazwasejwa = ""
                    else:
                        self.eskejp = None
            elif type(cotam).__name__ !="int" and cotam.col == self.tura and cotam != self.wybrany:
                self.wybrany = cotam
                zerowanie(self)
                self.wybor_pola(self.wybrany) # pokazanie planszy policzenie gdzie moze isc (cale glowne cialo)
            elif type(cotam).__name__ !="int" and cotam.col != self.tura and self.wybrany:
                self.zmianyzmiany(X,Y,cotam)
            elif self.wybrany == cotam :
                self.wybrany = None
                self.gdzie_wybrany = None
                zerowanie(self)
            else:
                self.zmianyzmiany(X,Y)
    def wybor_pola(self, doporuszenia):
        moj_krol = engine.szukaniekrola(self.plansza, self.tura)
        if engine.czyPat(moj_krol,self.plansza):
            self.remis = 1
        elif moj_krol.szach == 1:
            a = engine.czyMat(self.plansza, self.tura)
            if not a:
                moj_krol.mat = 1
                self.koniec = moj_krol.col*(-1)
            else:
                if id(doporuszenia) in a.keys():
                    self.gdzie_wybrany = a[id(doporuszenia)]
                else:
                    self.gdzie_wybrany = None
        else:
            doporuszenia.ruch()
            self.gdzie_wybrany = doporuszenia.gdziemozna
            to_be = []
            for (x, y) in self.gdzie_wybrany:
                if engine.sprawdzanie(doporuszenia, x, y) == 1:
                    to_be.append((x, y))
            self.gdzie_wybrany = to_be
            if doporuszenia == moj_krol:
                gdzie_krol, zw, i = engine.obslugaroszady(self.plansza, self.tura)
                if gdzie_krol != None:
                    self.zwiazana_wieza = zw
                    self.gdzie_wybrany.append(gdzie_krol)
                    self.gdzie_wieza = i
                    self.punkt_krola = gdzie_krol
            elif type(doporuszenia).__name__ == "Pionek":
                a = engine.bicie_w_przelocie(doporuszenia)
                if a != -1:
                    self.gdzie_wybrany.append((a.x, a.y + 1))
                    doporuszenia.gdziemozna.append((a.x, a.y + 1))
                    self.pionekbicie = a

    def mini_restart(self):
        self.plansza = self.core.biale + self.core.czarne
        self.wybrany = None
        self.gdzie_wybrany = None
        self.zwiazana_wieza = None
        self.gdzie_wieza = None
        self.punkt_krola = None
        self.zmiana = None
        self.pionekbicie = None
        self.arrow_actual = []
        moj_krol = engine.szukaniekrola(self.plansza, self.tura)
        moj_krol.szach = 0
        self.tura *= (-1)
        engine.tura_up(self.plansza)
        moj_krol = engine.szukaniekrola(self.plansza, self.tura)
        if engine.szach(self.core,self.tura):
            moj_krol.szach = 1
        for fig in self.plansza:
            fig.obrot()
        self.odzeraarrow()

class OkienkoStartu(arcade.Window):

    def __init__(self):
       super().__init__(490,537,"setup")
       self.sejw = None
       self.kresy_sejwy = None
       self.nasze_sejwy = None
       self.about = None
       self.czytajmer = None

    def on_draw(self):
        arcade.start_render()
        os.chdir(grafika)
        back = arcade.load_texture("back.png")
        back.draw(center_x=245, center_y=268.5, width=back.width, height=back.height)
        if self.sejw:
            os.chdir(glowny_projekt)
            os.chdir("SAVED_GAMES")
            self.nasze_sejwy = os.listdir(os.getcwd())
            n =len(self.nasze_sejwy)
            self.kresy_sejwy = []
            for i in range(n):
                sejwik = self.nasze_sejwy[i]
                starty = (537/n)*(n-i-0.5) #math
                kresy = ((n-i-1)*(537/n),(n-i)*(537/n))
                self.kresy_sejwy.append(kresy)
                arcade.draw_text(sejwik[:-4],start_x=20,start_y=starty,font_size=26,color=arcade.color.BLACK)
        elif self.about:
            about = arcade.load_texture("about.png")
            about.draw(center_x=245, center_y=268.5, width=about.width, height=about.height)
            os.chdir("/../")
        elif self.czytajmer:
            time_choose = arcade.load_texture("time.png")
            time_choose.draw(center_x=245,center_y=268.5,width=time_choose.width,height=time_choose.height)
        else:
            menu = arcade.load_texture("menu_startowe.png", scale=0.5)
            menu.draw(center_x=490 / 2, center_y=537 / 2, width=menu.width, height=menu.height)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if 63 <= x <= 441 and self.sejw == None and self.czytajmer == None:
            if 409 >= y >= 315:
                self.czytajmer = 1
            elif 224 <= y <= 316:
                self.sejw = 1
            elif 133 <= y <= 223:
                self.about = 1
            elif 132 >= y >= 39:
                arcade.close_window()
        elif self.sejw:
            i = 0
            for para in self.kresy_sejwy:
                if para[0] < y <= para[1]:
                    break
                i+=1
            if button == arcade.MOUSE_BUTTON_LEFT:
                core,tura,time1,time2 = setup(self.nasze_sejwy[i])
                arcade.close_window()
                MyGame(WIDTH,HEIGTH,TITLE,core,tura,time1,time2)
                arcade.run()
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                os.chdir(glowny_projekt)
                os.chdir("SAVED_GAMES")
                os.remove(self.nasze_sejwy[i])
        elif self.czytajmer:
            for i in range(6):
                if  70*i+75<= y <= 70*(i+1)+75:
                    ktory = i
                    break
            time = slowczas(ktory)
            core, tura = setup()
            arcade.close_window()
            MyGame(WIDTH, HEIGTH, TITLE, core, tura,time,time) #tutaj dopiero odpalamy gierke
            arcade.run()

    def on_key_press(self, symbol: int, modifiers: int):
        if self.about and symbol == arcade.key.ESCAPE:
            self.about = None
        elif self.sejw and symbol == arcade.key.ESCAPE:
            self.sejw = None
        elif self.czytajmer and symbol == arcade.key.ESCAPE:
            self.czytajmer = None

def main():

    OkienkoStartu()
    arcade.run()

if __name__ == "__main__":
    main()


