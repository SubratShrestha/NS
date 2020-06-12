from matplotlib import pyplot as plt

#ask for those parameter
burst = input ("Type 0 for continuous stim, 1 for burst stim: \n")
burst = int (burst)
if burst == 1:
    burstperoid = input("burst peroid (ms): \n")
    burstperoid = int(burstperoid)*1000
    dutycycle = input("ducty cycle (%): \n")
    dutycycle = int(dutycycle)/100
    burstduration = burstperoid * dutycycle
    interburst = burstperoid - burstduration


anodic= input("Type 1 for anodic frist stim, 0 for catodic frist stim: \n")
anodic = int (anodic)
current = input("current (uA): \n")
current = int (current)
phasetime1 = input("phase time 1 (us): \n")
phasetime1 = int (phasetime1)
phasetime2 = input("phase time 2 (us): \n")
phasetime2 = int (phasetime2)
interphase = input("inter-phase delay (us): \n")
interphase = int (interphase)
interstim = input("inter-stim delay (us): (type 0 to use frequency) \n")
interstim = int (interstim)
if interstim == 0:
    frequency = input("frequency (p.p.s): \n")
    frequency = int (frequency)
    interstim = 1000000 / frequency - phasetime1 - phasetime2 - interphase

#points on y-axis
andoic = [0, 1, 1, 0, 0, -1, -1, 0, 0]
cathodic = [0, -1, -1, 0, 0, 1, 1, 0, 0]
if anodic == 1:
    I = [i * current for i in andoic]
else:
    I = [i * current for i in cathodic]

#points on x-axis
#timing of frist cycle
T = [0, 0, phasetime1, phasetime1, phasetime1+interphase, phasetime1+interphase, phasetime1+phasetime2+interphase, phasetime1+phasetime2+interphase, phasetime1+phasetime2+interphase+interstim]

# if its uniform stim, graph stop plotting after one peroid
# if its burst stim, graph stop plotting after one burst peroid
if burst == 1:

    # constantly add last element of previous "T list"to all element in previous T to make the point on y-axis
    b = T.copy()
    while (b[len(b)-1]+phasetime1+phasetime2+interphase+interstim<(burstduration)):
        for i in range(len(b)):
            b[i]=T[i]+b[len(b)-1]
        T = T + b

    #change the T[-1]to burstduration
    T[len(T)-1] = burstduration
    #count how many element in the T list, divide by the 9, and repeat V list this many time, make set V2
    m = I.copy()
    for i in range(int(len(T)/9.0-1)):
        m = m + I
    I = m
    # add one more element to T, that is burstduration + interburst
    T.append(burstduration + interburst)
    I.append(0)

with plt.style.context('bmh'):
    plt.plot(T,I)
    plt.xlabel('Time (us)')
    plt.ylabel('Current (uA)')
    plt.show()