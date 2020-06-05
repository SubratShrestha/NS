from matplotlib import pyplot as plt

#ask for those parameter
burst = input ("burst: 0/1 \n")
burst = int (burst)
if burst == 1:
    bursttime = input("bursttime (ms): \n")
    bursttime = int(bursttime)*1000
    interburst = input("interburst (ms): (type 0 to use frequency) \n")
    interburst = int(interburst)*1000*1000
    if interburst == 0:
        burstfrequency = input("burstfrequency (Hz): \n")
        burstfrequency = int (burstfrequency)
        interburst = 1000000/burstfrequency - bursttime

anodic= input("anodic: 0/1 \n")
anodic = int (anodic)
current = input("current (uA): \n")
current = int (current)
phasetime1 = input("phasetime1 (us): \n")
phasetime1 = int (phasetime1)
phasetime2 = input("phasetime2 (us): \n")
phasetime2 = int (phasetime2)
interphase = input("interphase (us): \n")
interphase = int (interphase)
interstim = input("interstim (us): (type 0 to use frequency) \n")
interstim = int (interstim)
if interstim == 0:
    wavefrequency = input("wavefrequency (p.p.s): \n")
    wavefrequency = int (wavefrequency)
    interstim = 1000000 / wavefrequency - phasetime1 - phasetime2 - interphase

#points on y-axis
andoic = [0, 1, 1, 0, 0, -1, -1, 0, 0]
cathodic = [0, -1, -1, 0, 0, 1, 1, 0, 0]
if anodic == 1:
    V = [i * current * 0.001 for i in andoic]
else:
    V = [i * current * 0.001 for i in cathodic]

#points on x-axis
#timing of frist cycle
T = [0, 0, phasetime1, phasetime1, phasetime1+interphase, phasetime1+interphase, phasetime1+phasetime2+interphase, phasetime1+phasetime2+interphase, phasetime1+phasetime2+interphase+interstim]

# if its uniform stim, graph stop plotting after one peroid
# if its burst stim, graph stop plotting after one burst peroid
if burst == 1:
    # constantly add last element of previous "T list"to all element in previous T to make a new list of timing for next peroid. and then join all lists together to form a set for y-axis data
    b = T.copy()
    while (b[len(b)-1]<(bursttime + interburst)):
        for i in range(len(b)):
            b[i]=T[i]+b[len(b)-1]
        T = T + b

    #change the T[-1]to bursttime
    T[len(T)-1] = bursttime
    #count how many element in the T list, divide by the 9, and repeat V list this many time, make set V2
    #V * (len(T) / 9)
    m = V.copy()
    for i in range(int(len(T)/9.0-1)):
        m = m + V
    V = m
    # add one more element to T, that is bursttime + interburst
    T.append(bursttime + interburst)
    V.append(0)

#print(len(V))
#print(len(T))

plt.plot(T,V)
plt.xlabel('time (us)')
plt.ylabel('voltage (mV)')
plt.show()