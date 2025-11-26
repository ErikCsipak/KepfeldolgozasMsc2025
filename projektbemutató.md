# Projektbemutató 
A projekt megvalósításának célja, hogy egy olyan szoftver készüljön el, amely az adott videófelvételt közel valós időben elemzi, és követi a játék szabályainak alapján a játék aktuális állását, annak az elejétől a végéig.
 
 Ennek eléréséhez python nyelvet, és python libeket használtunk:
 - cv2 (opencv) - videó feldolgozási eszközök
 - numpy - matematikai műveletekhez

# Megvalósítás
Egy adott videót importálva, az első lépés, hogy framenként szegmentációs technikával elkülönítjük a golyókat, majd egy tömbben tárolva számontartjuk azok pozícióját. Ilyenkor a hsv színtérbe konvertálás után határértékek közé szorítva meghatározhatjuk a golyókat és azok pozícióját.
### Színértékek és golyók identifikálása
A Snooker labdákat és pontértékeiket színeik alapján azonosíthatjuk, ha a színképüket hibaértékek közé szorítjuk.
<img src="balls.jpg" alt="drawing" width="400"/>

A szín beazonosítása után egy labdának a pontértékét az alábbi táblázat alapján határozzuk meg:

| Szín                                                                                                                                              | Érték  |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| ![Red snooker ball](https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Snooker_ball_red.png/20px-Snooker_ball_red.png) Piros               | 1 pont |
| ![Yellow snooker ball](https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Snooker_ball_yellow.png/20px-Snooker_ball_yellow.png)  Sárga     | 2 pont |
| ![Green snooker ball](https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Snooker_ball_green.png/20px-Snooker_ball_green.png) Zöld          | 3 pont |
| ![Brown snooker ball](https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Snooker_ball_brown.png/20px-Snooker_ball_brown.png) Barna         | 4 pont |
| ![Blue snooker ball](https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Snooker_ball_blue.png/20px-Snooker_ball_blue.png) Kék              | 5 pont |
| ![Pink snooker ball](https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Snooker_ball_pink.png/20px-Snooker_ball_pink.png) Rózsaszín (Pink) | 6 pont |
| ![Black snooker ball](https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Snooker_ball_black.png/20px-Snooker_ball_black.png) Fekete        | 7 pont |

A hibaértékeket felhasználva maszkokat készítünk el, amelyeket később a CV2-es könyvtárral feldolgoztatva követhetjük a labdákat. 
Például a piros labdákra:
```python
lower_red = (0, 120, 70) 
upper_red = (10, 255, 255) 
mask1 = cv2.inRange(hsv, lower_red, upper_red)   # 0–10 hue

lower_red2 = (170, 120, 70) 
upper_red2 = (180, 255, 255) 
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)   # 170–180 hue

red_mask = mask1 | mask2
```
Ebben a speciális esetben két maszkot szükséges létrehoznunk, mivel a HSV színtér színegyenesének határai pont a piros színt vágják. Minden egyéb szín esetében ennek a műveletnek az elvégzése egyszerűbb (lentebb láthatjuk a valós határértékeket), elég egy maszkkal dolgoznunk. 

![gyuw4.png](gyuw4.png)

A maskok meghatározása után a cv2-es könyvtár **Hough Circle Transform** technikát használó HoughCircles metódusa alkalmas a labdák felismerésére:
```python
circles = cv2.HoughCircles(red_mask, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20, param1=50, param2=30, minRadius=8, maxRadius=15)
```
Ezzel megkapjuk a labdák pozícióját és átmérőjét, melyeket számontartva követni tudjuk azokat. A labdákat egy mapbe gyűjtjük, a `snooker_colors.py`-ban meghatározott key-ek alapján, ezáltal számontartjuk azokat, amelyek látszanak. 

# Teszteredmények
## Szegmentálási teszteredmények
A különböző színeket, a fenti módszer alapján határoztuk meg, a következő HSV határértékekkel:
```python
lower_yellow = np.array([20, 200, 100])  
upper_yellow = np.array([30, 255, 255])  
  
lower_green = np.array([45, 50, 50])  
upper_green = np.array([85, 255, 255])  
  
lower_brown = np.array([10, 200, 70])  
upper_brown = np.array([20, 250, 170])  
  
lower_blue = np.array([90, 80, 50])  
upper_blue = np.array([130, 255, 255])  
  
lower_pink = np.array([170, 50, 160])  
upper_pink = np.array([179, 150, 255])  
  
lower_black = np.array([1, 0, 0])  
upper_black = np.array([179, 180, 50])  
  
lower_white = np.array([0, 0,  230])  
upper_white = np.array([40, 120, 255])  
  
lower_red = np.array([0, 150, 130])  
upper_red = np.array([10, 255, 255])  
lower_red2 = np.array([170, 180, 150])  
upper_red2 = np.array([179, 255, 255])
```
### snooker.mp4
A fenti határértékek az első tesztvideónkra megfelelő eredményt állítanak elő.
Meg kell említenünk, azonban hogy ez a tesztfájl egy "tökéletes" viszonyokra épülő teszteset, ami egy számítógépes játékból lett kiragadva, így nincsenek zavaró tényezők, mint:
-  torzított kép
- benyúló kezek
- változó fényviszonyok
![Pasted image 20251126194458.png](Pasted%20image%2020251126194458.png)

A megvalósításunk piros színekre a következő szegmentációs képet generálja: ![Pasted image 20251126194346.png](Pasted%20image%2020251126194346.png)
Láthatjuk, hogy a labdák jól elkülöníthetőek, és azonosítatóak. Még a tökéletes viszonyok ellenére is, ha a játékasztal teljes egészét vesszük, a fekete színt nem tudtuk ilyen szépen szegmentálni: ![Pasted image 20251126194531.png](Pasted%20image%2020251126194531.png)
Látható, hogy a pálya fekete szélét is észleli a módszerünk, sőt a `HoughCircle` fals-pozitív eredményt is tud ezen a vonalon generálni, így előfordult, hogy több fekete golyót is észlelt. Különösen nehéz dolgunk volt a zöld színnel, amit nem is tudtunk ezzel a módszerrel megfelelően határértékek közé szorítani: ![Pasted image 20251126194559.png](Pasted%20image%2020251126194559.png)
Még, ha magát a labdát meg is tudtuk volna találni, az asztallap árnyalatbeli különbségei olyan szinten gátolták a hibatolerációt, hogy az asztal szélén levő sötétebb zöld árnyalatot figyelmen kívül nem tudtuk hagyni. A zöld labda észlelésének metodológiája is egy javítási lehetőség.

### snooker_720p.mp4
A módszer méginkább megmutatja a gyengeségét, ha egy valóélet-beli példán dolgozunk:
![Pasted image 20251126194721.png](Pasted%20image%2020251126194721.png)
Látható, hogy itt a pálya a lencseeffektus miatt torzul, és a fényviszonyok is megváltoztak. Transzformációk nélkül itt a következő eredményt kapjuk a beégetett határértékekkel a piros színre: ![Pasted image 20251126194641.png](Pasted%20image%2020251126194641.png)
Láthatjuk, hogy egyrészt a labdákat is rosszabbul tudjuk észlelni, és a pálya szélén előforduló piros színt is detektálja a szoftver, ahol a `HoughCircles` megintcsak fals-pozitív eredményeket produkál. A fekete labda esetén mégrosszabb a teljesítmény: ![Pasted image 20251126194708.png](Pasted%20image%2020251126194708.png)
Itt a labda már alig látható, a pályára benyúló kéz zaja erősebb, mint maga a szegmentált labda.

### snooker_720p_sullivan.mp4
![Pasted image 20251126201428.png](Pasted%20image%2020251126201428.png)
# Lehetséges továbbfejlesztések
A fenti problémákra adhat egy megoldást az alábbi technika:
## Automatikus szegmentálás
Jelenleg a projekt beégetett szegmentálási technikával dolgozik. Ahogy azt már részleteztük ez azt jelenti, hogy miután HSV színtérbe konvertáltuk a framet, a labdák HSV értékeit egy külön fileban változókként tartjuk számon, amelyeket a videóra szabva kézzel határoztunk meg. Ennek hátránya, hogy habár tudunk olyan videót mutatni, amire elfogadható eredménnyel szolgál, amint egy másik videót kap, ahogy azt mutattuk is, a megváltozott fényviszonyok miatt ezek az értékek már nem tudják megfelelően határértékek közé szorítani a labdákat. Ez kiküszöbölhető lenne egy automatizált algoritmussal, melynek koncepciója:
1. Vegyük a HSV színtér színeinek középértékét
2. Különítsük el a snookerasztalt, kivágva azt a frameből, ezzel egy uniform "zöldhátteret" kapva
3. A szín-középértékeket vizsgálva nézzük meg, hogy találunk-e a framen olyan színhalmazt, ami a legközelebb áll az adott vizsgált színhez
	1. Az a talált színhalmaz, ami a legközelebb esik a vizsgált szín-középértékhez megegyezik a labda színével
Ezzel a technikával automatikusan megállapíthatjuk az adott asztalon, az adott környezethez igazítva egy labda színét, amit azt a  játék során fel tudunk használni a labda azonosításához.
