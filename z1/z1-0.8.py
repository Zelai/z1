#!/usr/bin/python
# -*- coding: utf-8 -*-

import random, sys
import interface
import copy # para copiar listas
import itertools
"""
.. module::z1
"""

""" Variables globales """
## Voy en:
## Linea que en vim pone los números de linea a los log:
# :%s/log("\d*/\="log(\"".line(".")/

v={}
MOVES=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]


class z1(interface.Bot):
    """Bot z1 version 0.8"""
    NAME = "z1 v0.8"""

    def presenta(self,nombre,variable):
        """Muestra una variable por pantalla"""
        print >>sys.stderr, (str(nombre) + "\n"+ '\n'.join([''.join(['{:4}'.format(item) for item in row]) 
              for row in variable]))

    def __init__(self, init_state):
        """ Inicializa el bot: Llamado al comienzo del juego
        
        Inicializa variables: player_num, player_count, position, map, lighthouses"""
        d=0
        if d>0: self.log("51Entro en __init__")

        # llamada a super para inicializar las variables (self.)
        #  player_num, player_count, position, map, lighthouses
        interface.Bot.__init__(self,init_state) 

        if d>1: self.log("57 self.map" +str(self.map))
        if d>1: self.log("58 lighthouses:\n" + str(self.lighthouses))

        # posiciones validas map[0][0] - map[17,20]
        # modo de acceso map[y][x]

        self.jugada= []
        self.errores={}
        self.turno=0

        self.faros=[]
        v["faros"]={}
        for f in self.lighthouses:
            v["faros"][f]={}

        v["accion"]=[]
        self.calculaDistancias()
        self.prisa=50
        if d>2: self.log(str(v))
        if d>0: self.log("76 Salgo de__init__")

    def calculaDistancia(self,f,mapa):
        """ función auxiliar, calcula la distancia de cada punto del mapa un faro

        :param tuple f: tupla que define el faro (x,y)
        :param list mapa: lista 2-dimensional que contiene un mapa con las posiciones navegables y las que no.
        :return list: Lista 2-dimensional del Mapa actualiazdo con las distancias al faro
        """
        d=0
        if d>0: self.log("86Entro calculaDistancia faro %s" % str(f))
        faro= list(f)
        # Creo una estructura del tipo [x,y, distancia a faro] para ir 
        # caculando la distancia a todos los puntos, así, p.e. empiezo
        # con el faro (8,8) y le añado un 0 y queda [8,8,0] o sea, la 
        # distancia al faro (8,8) es 0 en ese punto y voy incrementando
        # la distancia según me alejo, lo hago iterativamente pero es como
        # si fuese un recursivo:
        # si distancia_en_puntos_alrededor > distancia_en_punto_actual +1 <= la actualizo a distancia_actual +1 
        faro.append(0)
        explorar = [faro]
        while explorar:
            punto = explorar.pop(0)
            if d > 2:
                self.log(str(punto))
                self.log(str(mapa).replace("[","\n"))
            if mapa[punto[1]][punto[0]] > punto[2]:
                mapa[punto[1]][punto[0]] = punto[2]
                for x in [-1,0,1]:
                  for y in [-1,0,1]:
                    explorar.append([punto[0] + y, punto[1] + x, punto[2]+1])
        if d>1:self.log(str(mapa).replace("[","\n"))
        if d>0: self.log("108Salgo calculaDistancia")
        return mapa

    def calculaDistancias(self):
        """ Calcula las  dict: :param dict v: ["distancia"] actualizado
        """
        v["distancia"]={}
        # distancia maxima del mapa:
        xMax = len(self.map[1])
        yMax = len(self.map)
        superior = xMax + yMax
        for f in self.lighthouses:
            mapa = [[ -1 if self.map[y][x]==0 else superior for x in xrange(xMax)] for y in xrange(yMax)]
            v["distancia"][f]= self.calculaDistancia(f,mapa)

    def distancia(self, faroOpuntoFaro):
        """ Devuelve la distancia que hay a un faro o de un punto a un faro
        
        :param faroOpuntoFaro: tuple faro (X,Y) or list puntofaro [(X,Y),faro], faro=(X,Y)
        :return int: distancia desde situación actual al faro destino o de un punto a un faro"""
        d=0
        if d>0: self.log("129-> distancia(faroOpuntoFaro) con " + str(faroOpuntoFaro))
        if len(faroOpuntoFaro) == 3:
            d0 = self.distancia(faroOpuntoFaro[0])
            d1 = self.distancia(faroOpuntoFaro[1])
            d2 = self.distancia(faroOpuntoFaro[2])
            if d0 < d1 and d0 < d2:
                returnkk
                
        if type(faroOpuntoFaro[0]) is int:
            """ Es un punto """
            x, y = v["estado"]["position"]
            faro = faroOpuntoFaro
        if type(faroOpuntoFaro[0]) is tuple or type(faroOpuntoFaro[0]) is list:
            punto, faro = faroOpuntoFaro 
            x, y = punto
        if d>0: self.log('<- ' + str(v["distancia"][faro][y][x]) + "\n")
        return v["distancia"][faro][y][x]

    def farosOtros(self):
        """ Devuelve lista de faros no propios """
        for faro in v["faros"]:
            if v["faros"][faro]["owner"] <> self.player_num:
                yield faro
                
    def farosMio(self):
        """ Devuelve lista de faros no propios """
        for faro in v["faros"]:
            if (v["faros"][faro]["owner"] == self.player_num and 
            faro not in self.errores):
                yield faro

    def miraEnergia(self,x,y):
        """ Devuelve la energía que hay en la posición relativa respecto a la posición"""
        return v["estado"]["view"][3+y][3+x]

    def buscaTriangulable(self):
        """ Mira a ver si se podría triangular <- {(f1,f2,f3):faroTriangulable,..}"""
        d=0
        if d>0: self.log("167Entro en buscaTriangulable")
        quien={}
        for faro in v["faros"]:
            if (v["faros"][faro]["owner"] == self.player_num and
                v["faros"][faro]["have_key"] == True):
                for c1 in v["faros"][faro]["connections"]:
                    for c2 in v["faros"][tuple(c1)]["connections"]:
                        if d>1: self.log("174faro %s: c1:%s c2:%s" % (str(faro),str(c1),str(c2)))
                        if (tuple(c2) <> faro and
                            list(faro) not in v["faros"][tuple(c2)]["connections"] and
                            tuple(c2) <> self.position):
                            if d>1: self.log("178faro %s: c1:%s c2:%s quien.append(c2)" % (str(faro),str(c1),str(c2)))
                            triangulableAux=[faro, tuple(c1), tuple(c2)]
                            triangulableAux.sort(key=self.evaluaFaro)
                            quien[triangulableAux]= tuple(c2)
        if d>0: self.log("182 <- buscaTriangulable(%s)" % str(quien))
        return quien

    def evaluaFaro(self,faro):
        """ evaluaFaro <- valor entero para ordenar"""
        return faro[0]*10 + faro[1]

    def normalizaTriangulo(triangulo):
        """ triangulo (f1,f2,f3) <- (f2,f1,f3) siempre ordenado de la misma manera"""
        return triangulo.sort(key=self.evaluaFaro)

    def buscafaro(self):
        """ Esta función busca el faro objetivo que cumpla:

        * Owner no soy yo
        
        * Yo no estoy en su posicion

        * Preferiblemente con menos energia que yo, pero si no el más lejano para recargar por el camino""" 
        d=0
        if d>0: self.log("202 Entro en buscafaro(), estoy en %s" % str(v["estado"]["position"]))
        faros = [j for j in self.farosOtros()]
       
        if faros == []: return[]

        if d>2: self.log("207 farosOtros =" + str(faros))
        faros.sort(key=self.distancia)
        if tuple(v["estado"]["position"]) in faros:
            faros.remove(tuple(v["estado"]["position"]))
        if d>1: self.log("211 faro[0]" + str(v["faros"][faros[0]]["owner"]))
        if d>1:
            for faro in v["faros"]:
                self.log("214 buscafaro " + str(faro))
                self.log("215 dist=" + str(self.distancia(faro)))
            
        if d>0: self.log("217 Salgo de buscafaro(), devuelvo:%s" % str(faros[0]))
        if not faros:
            return []
        faroObjetivo = faros[-1]
        for aux in faros:
            # Por defecto, el faro más cercano que tenga menos energía que yo
            if v["faros"][aux]["energy"] < v["estado"]["energy"]:
                faroObjetivo=aux
                break
        return faroObjetivo

    def conectable(self, faro):
        """ Nos dice se puede hacer conexión desde el punto actual a un faro o no"""
        d=0
        if d>0: self.log("229 Entro en conectable(" + str(faro) + ")")
        if d>1: self.log("230 faro=%s tipo=%s" %(str(faro),str(type(faro))))
        if faro not in v["faros"]:
            if d>0: self.log("232 return[]")
            return []
        if v["faros"][faro]["owner"] <> self.player_num:
            if d>0: self.log("235 <--conectable: return[]")
            return []
        for f in v["faros"]:
            if (v["faros"][f]["have_key"] and
                v["faros"][f]["position"] <> v["estado"]["position"]  and
                v["faros"][f]["owner"] == self.player_num and
                v["faros"][f]["position"] not in v["faros"][self.position]["connections"] and
                f not in self.errores):
                if d>0: self.log("243 <--conectable: return " + str(f))
                return f

    def enTriangulo(self,faros):
        """ nos dice que faros están en triangulos <- set((1,3)(2,3),(2,5)),..."""
        d=0
        aux = [f for f in faros]
        if d>0: self.log("250Entro en enTriangulo(%s)" % str(aux))
        entri=set()
        if d>1: self.log("252farosOtros=%s" % str(aux))
        for f in aux:
            if d>1: self.log("254v[faros][%s]=%s" % (str(f), str(v["faros"][f])))
            for c1 in v["faros"][f]["connections"]:
                if d>1: self.log("256f=%s c1=%s %s" % (str(f),c1,v["faros"][tuple(c1)]))
                for c2 in v["faros"][tuple(c1)]["connections"]:
                    if d>1: self.log("258f=%s c1=%s c2=%s" % (str(f),c1,c2))
                    if (tuple(c2) <> f):
                        for c3 in v["faros"][tuple(c2)]["connections"]:
                            if d>1: self.log("261f=%s c1=%s c2=%s c3=%s" % (str(f),c1,c2,c3))
                            if f == tuple(c3):
                                trianguloAux=[f,tuple(c1),tuple(c2)]
                                trianguloAux.sort(key=self.evaluaFaro)
                                entri.add(tuple(trianguloAux))
        if d>0: self.log("266  <-- enTriangulos: %s" % str(entri))
        return tuple(entri)

    def triangulable(self):
        """ Nos dice si se puede hacer un triángulo con un faro o no """
        d=0
        if d>0: self.log("272Entro en triangulable(self)")
        trian = {}
        for f in v["faros"]:
            if d>1: self.log("275triangulable f=%s" % str(f))
            if (v["faros"][f]["have_key"] and
                v["faros"][f]["owner"] == self.player_num):
                   for c1 in v["faros"][f]["connections"]:
                    if d>1: self.log("279triangulable f=%s c1=%s" % (str(f),str(c1)))
                    for c2 in v["faros"][tuple(c1)]["connections"]:
                        if d>1: self.log("281triangulable f=%s c1=%s c2=%s" % (str(f),str(c1),str(c2)))
                        if (tuple(c2) <> f and
                            c2 not in v["faros"][f]["connections"]):
                            if d>1: self.log("284append(c2) f=%s c1=%s c2=%s" % (str(f),str(c1),str(c2)))
                            triangulableAux=[f,tuple(c1),tuple(c2)]
                            triangulableAux.sort(key=self.evaluaFaro)
                            trian[tuple(triangulableAux)]= tuple(c2)
        if d>0: self.log("288  triangulable: %s" % str(trian))
        # Si hay algún triangulable, retorno el primero
        # si retorno lista casca
        triangulos = [ x for x in self.enTriangulo(self.farosMio())]
        aux=[]
        for aux in trian:
            if aux not in triangulos:
                break
        if d>1: self.log("296trian=%s triangulos=%s" % (str(trian), str(triangulos)))
        if aux: 
            self.log("298 <-- triangulable(): %s", trian[aux])
            return trian[aux]
        if d>0: self.log("300 <-- trian: %s" % trian)
        return trian

    def error(self,message, last_move):
        """Error: llamado cuando la jugada previa no es válida."""
        self.log("305Recibido error: %s", message)
        self.log("306Jugada previa: %r", last_move)
        if self.jugada:
            self.errores[self.jugada]=10
        self.log("309errores=" + str(self.errores))


    def reduce(self,faroObjetivo):
        """ Devuelve el movimiento que deberíamos hacer para ir al faro más cercano"""
        d=0
        if d>0: self.log("315 Entro en reduce(%s) prisa=%d self.position=%s" % (str(faroObjetivo), self.prisa, self.position))
        x, y = v["estado"]["position"]
        if not faroObjetivo:
            return []
        tDist = v["distancia"][tuple(faroObjetivo)]
        distanciaMin = tDist[y][x]
        dist0 = (0,0)
        dist1 = (0,0)
        eMin0 = -1
        eMin1 = -1
        if self.position== faroObjetivo: return (0,0)
        for xAux in [-1,0,1]:
            for yAux in [-1,0,1]:
                if xAux == 0 and yAux == 0: continue
                distAux = tDist[y+yAux][x+xAux]
                eAux = self.miraEnergia(xAux,yAux)
                if d>1: self.log("329 xAux=%d yAux=%d distAux=%d eAux=%d" % (xAux,yAux,distAux,eAux))
                if distAux == distanciaMin and eAux > self.prisa and eAux > eMin0:
                    dist0 = (xAux,yAux)
                    eMin0 = eAux
                    if d>1: self.log("333 dist0=%s eAux=%d", str(dist0), eAux)
                if distAux < distanciaMin and eAux > eMin1 and distAux>=0:
                    dist1 = (xAux,yAux)
                    eMin1 = eAux
                    if d>1: self.log("337 dist0=%s eAux=%d", str(dist0), eAux)
        devuelve = dist1
        if dist0 <> (0,0):
            devuelve = dist0
        # Si no, reduzco distancia
        if d>0: self.log("342 Salgo de reduce(%s), devuelvo %s" % (str(faroObjetivo),str(devuelve)))
        return devuelve
       
    def play(self, state):
        """ Función llamada al inicio de cada turno """
        #~ Función play
        d=0
        if d>0: self.log("349 play()")
        self.jugada=[]
        self.turno = self.turno + 1
        self.errores={i:self.errores[i]-1 for i in self.errores if self.errores[i] > 0}
        v["estado"]=state
        if d>2: 
            for e in v["estado"]:
                self.log("356 v[estado][%s]=%s" % (str(e),str(v["estado"][e])))
        self.prisa=v["estado"]["energy"]/24 + 50
        self.position = tuple(v["estado"]["position"])
        v["faros"] = dict((tuple(lh["position"]), lh)
                for lh in state["lighthouses"])
        if d>2:
            for e in v["faros"]:
                self.log("363 v[faros][%s]=%s" % (str(e),str(v["faros"][e])))
        if d>1: self.log("364 Errores=%s" % str(self.errores))

        triangulable= self.triangulable()

        ##~ Ataque independiente (turno > 50)
        if d>1: self.log("369 preataque independiente")
        if self.turno > 50:
            if d>1: self.log("371 turno %d" % self.turno)
            tri = list(self.enTriangulo(self.farosOtros()))
            if tri:
                if d>1: self.log("374Ataque independiente, tri= %s" % str(tri))
                aux=tri[0]
                objetivo=aux[0]
                if v["estado"]["energy"] > v["faros"][objetivo]["energy"]: self.prisa = 110
                mueve = self.reduce(objetivo)
                if d>1: self.log("379 reduce.tri %s energia.tri=%d" % (str(mueve), v["estado"]["energy"]))
                if (mueve == (0,0) and 
                    v["estado"]["energy"]>100):
                        self.log("382 entro en ataque")
                        turno = 0
                        if triangulable:
                            if d>0:self.log("385 self.attack(min(%s,%s))" % (str(v["estado"]["energy"]), str(v["faros"][self.position]["energy"]-5)))
                            return self.attack(min(v["estado"]["energy"], v["faros"][self.position]["energy"]-5))
                        else:
                            if d>0:self.log("388 self.attack(min(%s,%s))" % (str(v["estado"]["energy"]), str(v["faros"][self.position]["energy"]+1200)))
                            return self.attack(min(v["estado"]["energy"], v["faros"][self.position]["energy"]+1200))
                if d>1: self.log("390 return(tri) self.move(*(%s))" % str(mueve))
                if mueve <> (0,0):
                    return self.move(*mueve)

        ##~ fin ataque independiente
        if d>1: self.log("395 fin ataque independiente")
        if d>1: self.log("396 inicio triangulable=%s" % str(triangulable))
        if triangulable:
            if d>1: self.log("398 reduce()")
            self.prisa=101
            mueve= self.reduce(triangulable)
            self.log("400 mueve=%s" % str(mueve))
            if mueve <> (0,0):
                if d>0: self.log("402 <--play(): return self.move(*%s)" % str(mueve))
                return self.move(*mueve)
            self.log("404")
        if d>1: self.log("405 fin triangulable")
        ##~ fin triangulable
         ##~ inicio conectable
        if d>1: self.log("408 inicio conectable")
        con = self.conectable(self.position)
        if con:
            if d>0: self.log("411 <-- play(): return self.connect(%s)" % str(con))
            self.jugada=con
            return self.connect(con)
        if d>1: self.log("413 fin conectable")
        ##~ fin conectable
        ##~ inicio recargable:
        if d>1: self.log("416 inicio recargable")
        if self.position in v["faros"]:
            if (v["faros"][self.position]["owner"]==self.player_num and
            v["faros"][self.position]["energy"] < 800 and
            v["estado"]["energy"] > 100):
                energia = min(v["estado"]["energy"],1200 - v["faros"][self.position]["energy"])
                if d>0: self.log("422 return self.attack(%s)" % energia)
                return self.attack(energia)
            elif v["estado"]["energy"] > 100:
                energia = min(v["faros"][self.position]["energy"] + 1200, v["estado"]["energy"])
                if d>0: self.log("426 return self.attack(%s)" % energia)
                return self.attack(energia)

        objetivo = self.buscafaro()
        mueve = self.reduce(objetivo)
        if d>0: self.log("431 <--play(): return self.move(*%s)" % str(mueve))
        if not mueve:
            mueve = random.choice(MOVES)
        return self.move(*mueve)
##~ ataque independiente
##~ si triangulable -> triangula
##~ si conectable -> conecta
##~ si atacable -> ataca
##~ si no buscafaro

if __name__ == "__main__":
    iface = interface.Interface(z1Bot)
    iface.run()
