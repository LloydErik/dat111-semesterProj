import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import RangeSlider
import matplotlib.image as mpimg
import matplotlib.patches as mpatches

#Generater random data for a year
# centervals are values average values for each month
# samedata = false, new data each time program is called
import random
from random import randint

from numpy.ma.extras import average


def GenereateRandomYearDataList(intencity:float, seed:int=0) -> list[int]:
    """
    :param intencity: Number specifying size, amplitude
    :param seed: If given, same data with seed is generated
    :return:
    """
    if seed != 0:
        random.seed(seed)
    centervals = [200,150,100, 75,75,75, 50, 75, 100, 150, 200, 250, 300]
    centervals = [x * intencity for x in centervals]
    nox = centervals[0]
    inc = True
    noxList = []
    for index in range(1,365):
        if randint(1, 100) > 50:
            inc = not inc
        center = centervals[int(index / 30)]
        dx = min(2.0, max(0.5, nox / center ))
        nox =  nox + randint(1,5) / dx if inc else nox - randint( 1, 5) * dx
        nox = max(10, nox)
        noxList.append(nox)
    return noxList

kron_nox_year = GenereateRandomYearDataList(intencity=1.0, seed = 2)
nord_nox_year = GenereateRandomYearDataList(intencity=.3, seed = 1)


#create figure and 3 axis
fig = plt.figure(figsize=(13, 5))

axNok = fig.add_axes((0.05, 0.05, 0.45, 0.9))
axInterval = fig.add_axes((0.4, 0.5, 0.1, 0.25))
axBergen = fig.add_axes((0.5, 0.05, 0.5, 0.9))

axInterval.patch.set_alpha(0.5)

coordinates_Nordnes = (225, 70)
coordinates_Kronstad = (740, 650)
days_interval = (1,365)
marked_point = (0,0)


def on_day_interval(tuppel):
    global days_interval, marked_point
    axNok.cla()
    days_interval = (tuppel[0],tuppel[1])
    marked_point = (0, 0)
    plot_graph()

"""
def on_day_interval(kvartal):
    global days_interval, marked_point
    axNok.cla()
    days_interval = (1,365)
    if kvartal == '1. Kvartal':
        days_interval = (1,90)
    if kvartal == '2. Kvartal':
        days_interval = (90, 180)
    if kvartal == '3. Kvartal':
        days_interval = (180,270)
    if kvartal == '4. Kvartal':
        days_interval = (270,365)
    marked_point = (0, 0)
    plot_graph()
"""

def on_click(event) :
    global marked_point
    if ax := event.inaxes:
        if ax == axBergen:
            marked_point = (event.xdata, event.ydata)
            plot_graph()

#estimate NOX value based on the two measuring stations
def CalcPointValue(valN, valK):
    distNordnes = math.dist(coordinates_Nordnes, marked_point)
    distKronstad = math.dist(coordinates_Kronstad, marked_point)
    distNordnesKronstad = math.dist(coordinates_Nordnes, coordinates_Kronstad)
    val = (1 - distKronstad /(distKronstad+distNordnes)) * valK  + (1 - distNordnes /(distKronstad+distNordnes))* valN
    val = val * ( distNordnesKronstad / (distNordnes + distKronstad) ) ** 4

    return val

# Make two circles in Nordnes and Kronstad
def draw_circles_stations():
    circle = mpatches.Circle((225,70), 50, color='blue')
    axBergen.add_patch(circle)
    circle = mpatches.Circle((740, 650), 50, color='red')
    axBergen.add_patch(circle)

def draw_label_and_ticks():
    num_labels = 12
    xlabels = ['J' ,'F' ,'M' ,'A' ,'M' ,'J', 'J', 'A', 'S', 'O', 'N', 'D']


    start = days_interval[0]
    slutt = days_interval[1]

    
    distanse = slutt - start

    nyliste = []

    for i, v in enumerate(xlabels):
        if i * 30 + 1 >= start and i * 30 <= slutt:
            nyliste.append(v)
        

    xlabels = nyliste
    num_labels = len(xlabels)

    
    xticks = np.linspace(15, 345, math.floor(num_labels))

    
    """
    if days_interval[1] == 90:
        xticks = [15,45,75]
        xlabels = ['Jan', 'Feb', 'Mars']
    if days_interval[1] == 180:
        xticks = [15,45,75]
        xlabels = ['April', 'Mai', 'Juni']
    if days_interval[1] == 270:
        xticks = [15, 45, 75]
        xlabels = ['July', 'Aug', 'Sept']
    if days_interval[0] == 270:
        xticks = [15, 45, 75]
        xlabels = ['Okt', 'Nov', 'Des']

    """
    axNok.set_xticks(xticks)
    axNok.set_xticklabels(xlabels)

def plot_graph():
    axNok.cla()
    axBergen.cla()
    nord_nox = nord_nox_year[days_interval[0]:days_interval[1]]
    kron_nox = kron_nox_year[days_interval[0]:days_interval[1]]
    avg_nox = (np.array(nord_nox) + np.array(kron_nox)) / 2
    avg_kron_nox = np.mean(np.array(kron_nox))
    avg_nord_nox = np.mean(np.array(nord_nox))
    avg_kron_nord = (avg_nord_nox / avg_kron_nox)
    avg_percent = avg_kron_nord * 100
    days = len(nord_nox)
    list_days = np.linspace(1, days, days)

#draw the marked point & the orange graph
    l3 = None
    if marked_point != (0,0):
        nox_point = [CalcPointValue(nord_nox[i], kron_nox[i])  for i in range(days)]
        l3, = axNok.plot(list_days, nox_point, 'darkorange')
        circle = mpatches.Circle((marked_point[0], marked_point[1]), 50, color='orange')
        axBergen.add_patch(circle)

    l1, = axNok.plot(list_days, nord_nox, 'blue')
    l2, = axNok.plot(list_days, kron_nox, 'red')
    l4, = axNok.plot(list_days, avg_nox, 'green')
    axNok.set_title("NOX verdier")
    axInterval.set_title("Intervall")

    lines = [l1, l2, l4] if l3 is None else [l1, l2, l4, l3]
    axNok.legend(lines, [f"Nordnes i intervall, avg. = {avg_nord_nox:.2f} PPM", f"Kronstad i intervall, avg. = {avg_kron_nox:.2f} PPM", f"Avg. i intervallet(ifft Kronstad, i %) = {avg_percent:.2f}%", "Markert plass"])
    axNok.grid(linestyle='--')
    draw_label_and_ticks()

    #Plot Map of Bergen
    axBergen.axis('off')
    img = mpimg.imread('Bergen.jpg')
    img = axBergen.imshow(img)
    axBergen.set_title("Kart Bergen")
    draw_circles_stations();
    plt.draw()

plot_graph()

# draw radiobutton interval
listFonts = [12] * 5
listColors = ['yellow'] * 5

radio_slider = RangeSlider(axInterval, "Dager", 1, 365, valstep=1)
"""
radio_button = RadioButtons(axInterval, ('År',
                                          '1. Kvartal',
                                          '2. Kvartal',
                                          '3. Kvartal',
                                          '4. Kvartal'),
                            label_props={'color': listColors, 'fontsize' : listFonts},
                            radio_props={'facecolor': listColors,  'edgecolor': listColors},
                            )

"""

axInterval.set_facecolor('darkblue')
radio_slider.on_changed(on_day_interval)
#radio_button.on_clicked(on_day_interval)
# noinspection PyTypeChecker
plt.connect('button_press_event', on_click)

plt.show()

