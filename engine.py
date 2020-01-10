import copy,os
from abc import abstractmethod
w_planszy = [i for i in range(8)]

def skosy(goniec,i,zakazane):
    l1 = [goniec.x+i,goniec.x-i]
    l2 = [goniec.y+i,goniec.y-i]
    jakie = []    # (0,0) , (0,1) , (1,0) , (1,0)
    for w in range(len(l1)):
        for k in range(len(l2)):
            if l1[w] not in w_planszy and l2[k] not in w_planszy:
                zakazane.append((w,k))
            if l1[w] in w_planszy and l2[k] in w_planszy and (w,k) not in zakazane:
                for fig in goniec.biale+goniec.czarne:
                    if fig.x == l1[w] and fig.y == l2[k]:
                        if fig.col*goniec.col == -1:
                            jakie.append((l1[w], l2[k]))
                        zakazane.append((w,k))
                        break
                if (l1[w],l1[k]) not in jakie and (w,k) not in zakazane :
                    jakie.append((l1[w],l2[k]))
    return jakie  #zwraca liste punktow na ktorych mozna stawac dla skosnych

def obiektodanejwspol(plansza,q,t):
    for fig in plansza:
        if fig.x == q and fig.y == t:
            return fig
    return -1

def prostopadle(wieza,i,zakazane,pion):
    gdzie = []
    if pion:
        A = list(filter(lambda i: i in w_planszy,[wieza.y+i,wieza.y-i]))
        for k in range(len(A)):
            if k not in zakazane:
                if obiektodanejwspol(wieza.biale+wieza.czarne,wieza.x,A[k]) == -1:
                    gdzie.append((wieza.x,A[k]))
                else:
                    if obiektodanejwspol(wieza.biale+wieza.czarne,wieza.x,A[k]).col * wieza.col == -1:
                        gdzie.append((wieza.x, A[k]))
                    zakazane.append(k)
        return gdzie
    else:
        A = list(filter(lambda i: i in w_planszy, [wieza.x + i, wieza.x - i]))
        for k in range(len(A)):
            if k not in zakazane:
                if obiektodanejwspol(wieza.biale + wieza.czarne, A[k], wieza.y) == -1:
                    gdzie.append((A[k],wieza.y))
                else:
                    if obiektodanejwspol(wieza.biale + wieza.czarne,A[k],wieza.y).col * wieza.col == -1:
                        gdzie.append((A[k],wieza.y))
                    zakazane.append(k)
        return gdzie


def miejsca_wieza_improved(wieza):
    i = 1
    zak = []
    gdzie = []
    a = prostopadle(wieza,i,zak,pion=True)
    while a:
        gdzie+=a
        i+=1
        a = prostopadle(wieza,i,zak,pion=True)
    i = 1
    zak = []
    a = prostopadle(wieza,i,zak,pion=False)
    while a:
        gdzie+=a
        i+=1
        a = prostopadle(wieza,i,zak,pion=False)
    return gdzie

def miejsca_goniec(goniec):

    i = 1
    gdzie = []
    zak = []
    A = skosy(goniec,i,zak)
    while A: #dopoki zwaracana lista niepusta
        gdzie += A
        i+=1
        A = skosy(goniec,i,zak)
    return gdzie

def czy_dlugaroszada(wieza,krol):
    if wieza.col == 1 :
        start = 1
        end = 4
    else:
        start = 4
        end = 7
    for i in range(start, end):
        if obiektodanejwspol(wieza.biale + wieza.czarne, i, 0) != -1:
            return False
        if not sprawdzanie(krol, i, 0):
            return False
    return True


def czy_krotkaroszada(wieza,krol):

     if wieza.col == 1 :
         start = 5
         end = 7
     else:
         start = 1
         end = 3

     for i in range(start, end):
         if obiektodanejwspol(wieza.biale + wieza.czarne, i, 0) != -1:
             return False
         if not sprawdzanie(krol, i, 0):
             return False
     return True


class Figura:
    biale = [] # wspolna dla wszytkich klas dziedziczacych po figurze
    #dodawanie na zasadzie Pionek.biale.append(Pionek)
    czarne = []
    current_game = []

    def __init__(self,x=None,y=None,col=None,moved=None,num=0):
        if type(x).__name__ =="dict":
            for k,v in x.items():
                try:
                    setattr(self,k,int(v))
                except:
                    setattr(self,k,v)
        else:
            self.y = y
            self.x = x  # bedziemy do inicjalizacji przekazywac obiekty klasy polzenie dla ktorych jest zdefinowane ==
            self.col = col
            self.num = num
            self.moved = moved

    def num_up(self):
        self.num += 1

    def obrot(self):
        self.x = 7 - self.x
        self.y = 7 - self.y    #obrot!

    def __eq__(self,other):
        if id(self) == id(other):
            return True
        return False

    def zbicie(self):
        for fig in self.biale+self.czarne:
            if fig == self:
                if self.col == 1:
                    self.biale.remove(self)
                else:
                    self.czarne.remove(self) #fuckup w zalozeniach projektowych , biale i czarne powinno byc razem!
    @abstractmethod
    def ruch(self): # ruszac sie bedziemy tylko "w góre", przed ruchem figur czarnych, dokonujemy obrotu
        pass
    def zmiana_polozenia(self,xn,yn):
        if (xn,yn) in self.gdziemozna:
            self.x = xn
            self.y = yn
        if hasattr(self,"moved"):
            setattr(self,"moved",1)
        if hasattr(self,"dwa_tura"):
            setattr(self,"dwa_tura",self.num)

class Pionek(Figura):

    def ruch(self):  #ruch musi byc wykonany, potem dopiero obrot "spowrotem"

        gdzie = []
        A = list(filter(lambda i: i>=0 and i<8,[self.x-1,self.x+1]))
        czy1 = True
        czy2 = True
        for fig in self.biale+self.czarne:
            if fig.x == self.x and fig.y == self.y + 1:
                czy1 = False
                czy2 = False
            if fig.x == self.x and fig.y == self.y + 2:
                czy2 = False
        for fig in self.biale + self.czarne:
            if fig.x in A and fig.y-1 == self.y and fig.col*self.col == -1: #czarny -> -1 bialy -> 1:
                gdzie.append((fig.x,fig.y))
        if czy1:
            gdzie.append((self.x,self.y+1))
        if czy2 and not self.moved:
            self.dwa_tura = self.num #self.numer w Figurze tu blad
            gdzie.append((self.x,self.y+2))
        self.gdziemozna = gdzie

class Goniec(Figura):

    def ruch(self):
        self.gdziemozna = miejsca_goniec(self)


class Kon(Figura):

    def ruch(self):
        dist = 5**(1/2) # 2^2 + 1^2
        gdzie = []              #wyniki rozkladaja sie po kole przeciez!
        M = lambda x1,x2,y1,y2:((x1-x2)**2+(y1-y2)**(2))**(1/2)
        for k in range(8):
            for w in range(8):
                if M(self.x,k,self.y,w) == dist and (obiektodanejwspol(self.biale+self.czarne,k,w) == -1 or obiektodanejwspol(self.biale+self.czarne,k,w).col*self.col == -1):
                    gdzie.append((k,w))
        self.gdziemozna = gdzie


class Wieza(Figura):

    def ruch(self):
        self.gdziemozna = miejsca_wieza_improved(self)


class Krolowa(Figura):

    def ruch(self):
        self.gdziemozna =  miejsca_goniec(self) + miejsca_wieza_improved(self)


class Krol(Figura):
    def __init__(self, x=None, y=None, col=None, moved=None,szach=0,mat=0):
        if type(x).__name__ == "dict":
            super().__init__(x)
        else:
            super().__init__(x, y, col,moved)
            self.szach = szach
            self.mat = mat

    def ruch(self):
        gdzie = []
        for k in range(self.x-1,self.x+2):
            for w in range(self.y-1,self.y+2):
                czy = False
                if (k!= self.x or w !=self.y) and k in w_planszy and w in w_planszy:
                    for fig in self.biale+self.czarne:
                        if fig.x == k and fig.y == w:
                            if fig.col*self.col == -1:
                                gdzie.append((k, w))
                            czy = True
                            break
                    if not czy:
                        gdzie.append((k,w))
        self.gdziemozna = gdzie

class Obsluga(Figura):

    def __init__(self,x,y,col,moved,plansze={}):
        super().__init__(x,y,col,moved)
        self.plansze = plansze

    def plansze_handling(self,plan):
        klucz = ""
        for fig in plan:
            klucz+=str(fig.x)
            klucz+=str(fig.y)
        if klucz in self.plansze.keys():
            self.plansze[klucz]+=1
            if self.plansze[klucz] == 3:
                return 10
        else:
            self.plansze[klucz] = 1

def zmienne():
    return globals()

def szukaniekrola(kol,colo):
    for i in range(len(kol)):
        if type(kol[i]).__name__ == "Krol" and kol[i].col == colo:
            return kol[i]
def czystoitammoj(wybrana_x,wybrana_y,wszyscy,kolor):
    for w in range(len(wszyscy)):
        if wybrana_x == wszyscy[w].x and wybrana_y == wszyscy[w].y and wszyscy[w].col == kolor:
            return wszyscy[w]
        elif wybrana_x == wszyscy[w].x and wybrana_y == wszyscy[w].y and wszyscy[w].col == kolor*(-1):
            return -2
    return -1

def cotamstoi(plansza,w,k):
    for figura in plansza:
        if figura.x == w and figura.y == k:
            return figura
    return 0


def stawianie_spowrotem(sx,sy,sprawdzana,bity_obiekt,stary_ruszany):
    sprawdzana.x = sx
    sprawdzana.y = sy
    if stary_ruszany != None:
        sprawdzana.moved = stary_ruszany
    if bity_obiekt and bity_obiekt.col == 1:
        sprawdzana.biale.append(bity_obiekt)
    elif bity_obiekt and bity_obiekt.col == -1:
        sprawdzana.czarne.append(bity_obiekt)

def sprawdzanie(sprawdzana,xn=None,yn=None):

  sx = sprawdzana.x  #udajemy ze ruch sie odbyl
  sy = sprawdzana.y
  if hasattr(sprawdzana,"moved"):
      stary_ruszany = sprawdzana.moved
  else:
      stary_ruszany = None
  if czyBicie(xn,yn,sprawdzana.biale+sprawdzana.czarne,sprawdzana.col)!= -1:
      bity_obiekt = czyBicie(xn,yn,sprawdzana.biale+sprawdzana.czarne,sprawdzana.col)
      czyBicie(xn, yn, sprawdzana.biale + sprawdzana.czarne, sprawdzana.col).zbicie()
  else:
      bity_obiekt = None
  sprawdzana.zmiana_polozenia(xn,yn)

  moj_krol = szukaniekrola(sprawdzana.biale+sprawdzana.czarne,sprawdzana.col)
  for fig in sprawdzana.biale+sprawdzana.czarne:
      fig.obrot()
  for fig in sprawdzana.biale+sprawdzana.czarne:
      if fig.col*sprawdzana.col == -1:
          fig.ruch()
          A = fig.gdziemozna
          if (moj_krol.x,moj_krol.y) in A:
              for fig in sprawdzana.biale + sprawdzana.czarne:
                  fig.obrot()
              stawianie_spowrotem(sx,sy,sprawdzana,bity_obiekt,stary_ruszany)
              return False
  for fig in sprawdzana.biale+sprawdzana.czarne:
      fig.obrot()

  stawianie_spowrotem(sx, sy,sprawdzana, bity_obiekt,stary_ruszany)

  return True

def usuwaniepustych(slo):
    a = []
    for key in slo.keys():
        if not slo[key]:
            a.append(key)
    for k in a:
        del slo[k]

def czyPat(krol,plansza):
    if krol.szach == 0:
        for fig in plansza:
            fig.ruch()
            if fig.col == krol.col:
                for (x,y) in fig.gdziemozna:
                    if sprawdzanie(fig,x,y) == 1:
                        return False
        return True
    return False

def czyMat(plansza,tura):
    mozliwe_ruchy_przy_szachu = {}
    for fig in plansza:
        if fig.col*tura == 1 :
            fig.ruch()
            for (x,y) in fig.gdziemozna:
                if sprawdzanie(fig,x,y):
                    if id(fig) not in mozliwe_ruchy_przy_szachu.keys():
                        mozliwe_ruchy_przy_szachu[id(fig)] = [(x,y)]
                    else:
                        mozliwe_ruchy_przy_szachu[id(fig)].append((x,y))
    return mozliwe_ruchy_przy_szachu

def czymoznatamisc(gdzie_moznaisc,x,y):
    for k in range(len(gdzie_moznaisc)):
        if gdzie_moznaisc[k] == (x,y):
            return True
    return False

def czyBicie(gdzie_x,gdzie_y,plansza,tura):

    for fig in plansza:
        if gdzie_x == fig.x and gdzie_y == fig.y and tura*fig.col == -1:
            return fig
    return -1

def override_dostepnych_pol(core,tura,wm):

    byly = []
    for key in wm.keys():
        for fig in core.biale+core.czarne:
            if id(fig) == key:
                fig.gdziemozna = wm[id(fig)]
                byly.append(fig)
    for fig in core.biale+core.czarne:
        if fig.col == tura and fig not in byly:
            fig.gdziemozna = []

def szach(core,tura):

    moj_krol = szukaniekrola(core.biale+core.czarne,tura)
    szuk =  (moj_krol.x,moj_krol.y)
    for fig in core.biale+core.czarne:
        if fig.col*tura == -1:
            fig.ruch()
            if szuk in fig.gdziemozna:
                return True
    return False

def obslugaroszady(plansza,tura):

        krol = szukaniekrola(plansza,tura) # 3 -> -1 4 -> 1
        krol.ruch()
        x_wiezydlug = krol.x - 4 * tura  # dla bialego 4 - 4*1 = 0 ok dla czarnego 3+4 =7 ok
        x_wiezykrot = krol.x + 3 * tura  # analo ..
        wieza_dlug = obiektodanejwspol(plansza,x_wiezydlug,0)
        wieza_krot = obiektodanejwspol(plansza,x_wiezykrot,0)
        if krol.moved == 0 and wieza_dlug != -1 and wieza_dlug.moved == 0 and czy_dlugaroszada(wieza_dlug,krol) :
            krol.gdziemozna.append((krol.x-2*tura,0))
            return (krol.x-2*tura,0),wieza_dlug,1
        elif krol.moved == 0 and wieza_krot != -1 and wieza_krot.moved == 0 and czy_krotkaroszada(wieza_krot,krol) :
            krol.gdziemozna.append((krol.x + 2 * tura, 0))
            return (krol.x+2*tura, 0),wieza_krot,-1
        return None,None,None

def bicie_w_przelocie(pionek):

     if pionek.y == 4:
         w = list(filter(lambda i:i in w_planszy,[pionek.x-1,pionek.x+1]))
         for wsp in w:
             if sprawdzanie(pionek,wsp,pionek.y+1): #weryfikacja czy nie oszukujemy
                 obiekt = obiektodanejwspol(pionek.biale+pionek.czarne,wsp,pionek.y)
                 if obiekt != -1:
                    if type(obiekt).__name__ == "Pionek" and hasattr(obiekt,"dwa_tura") and obiekt.dwa_tura==pionek.num-1 and obiekt.col*pionek.col == -1:
                        return obiekt
     return -1

def tura_up(plansza):
    for fig in plansza:
        fig.num_up()