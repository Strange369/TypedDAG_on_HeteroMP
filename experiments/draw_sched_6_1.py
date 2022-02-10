from __future__ import division
import sys
import numpy as np
import matplotlib
import itertools
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter
from matplotlib import rcParams
import matplotlib.ticker as ticker

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Tahoma']

rcParams['ps.useafm'] = True
rcParams['pdf.use14corefonts'] = True
rcParams['text.usetex'] = True

figlabel=['a','b','c','d','e','f','g','h','i','j']

#'o', 'v','+' ,'x','*'
#marker = ['o', 'v','+','*','D','x','+','p']
#'b','r','g','k','y'
#colors = ['b','r','k','g','c','y','m','b']
marker = itertools.cycle (('D', 'o', 'v', 'D', 'o', 'v', 's',))
#marker = ['o', '+','*','D','x','+','p',]
#'b','r','g','k','y'
#colors = ['b','r','k','g','c','y','m','b']
colors = itertools.cycle (('blue','orange','green','red','purple','brown','black','gray',))
#colors = ['c','k','b','r','g','y','m','b']
#line = ['--','--','--','--','--','--','-','-','-','-','-','-']
#line = [':',':',':',':',':',':','-','-','-','-','-','-']
line = itertools.cycle (('-','-',))

interval = ['sslen: Short', 'sslen: Moderate', 'sslen: Long']


fig=plt.figure()

## create a virtual outer subsplot for putting big x-ylabel
ax=fig.add_subplot(111)
fig.subplots_adjust(top=0.7,left=0.1,right=0.8, bottom=0.28, hspace =0.35)

ax.set_xlabel(r'Utilization (\%) / $(M_a + M_b)$',labelpad=15.0,size=28)
ax.set_ylabel('Acceptance Ratio (\%)',labelpad=25.0,size=28)
ax.spines['top'].set_color('none')
ax.spines['bottom'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['right'].set_color('none')

ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')

# initialize the input configuration
msets = 100
processors_a = 16
processors_b = 16
prob_q = 0.9
mod = 1
mod_1 = 0
mod_2 = 0
mod_3 = 0
sparse = 0
rho_id = 0

x1 = []
x2 = []
x3 = []
x4 = []
x5 = []
x6 = []
x7 = []
x8 = []
x9 = []
for i in range(0, 65, 5):
    x1.append(i)
    x2.append(i)
    x3.append(i)
    x4.append(i)
    x5.append(i)
    x6.append(i)
    x7.append(i)
    x8.append(i)
    x9.append(i)

for i in range(1, 7):

    # ax = fig.add_subplot(3, 3, i)
    ax = fig.add_subplot(3, 2, i)

    if (i == 1):
        msets = 100
        processors_a = 16
        processors_b = 16
        prob_q = 0.9
        mod = 1
        mod_1 = 0
        mod_2 = 2
        mod_3 = 0
        sparse = 0

    if (i == 2):
        msets = 100
        processors_a = 16
        processors_b = 16
        prob_q = 0.9
        mod = 1
        mod_1 = 0
        mod_2 = 0
        mod_3 = 0
        sparse = 0

    if (i == 3):
        msets = 100
        processors_a = 16
        processors_b = 16
        prob_q = 0.9
        mod = 1
        mod_1 = 1
        mod_2 = 2
        mod_3 = 0
        sparse = 0

    if (i == 4):
        msets = 100
        processors_a = 16
        processors_b = 16
        prob_q = 0.9
        mod = 1
        mod_1 = 1
        mod_2 = 0
        mod_3 = 0
        sparse = 0

    if (i == 5):
        msets = 100
        processors_a = 16
        processors_b = 16
        prob_q = 0.9
        mod = 1
        mod_1 = 2
        mod_2 = 2
        mod_3 = 0
        sparse = 0

    if (i == 6):
        msets = 100
        processors_a = 16
        processors_b = 16
        prob_q = 0.9
        mod = 1
        mod_1 = 2
        mod_2 = 0
        mod_3 = 0
        sparse = 0


    han_name_1 = 'outputs/results/results_han_m' + str(msets) + '_a' + str(processors_a) + '_b' + str(processors_b) + '_q' + str(prob_q) + '_d1' + '_r' + str(rho_id) + '_f' + str(mod_1) + '_s' + str(mod_2) + '_m' + str(mod_3) + '_s' + str(sparse)+'.npy'
    results_han_1 = np.load(han_name_1)

    han_name_2 = 'outputs/results/results_han_m' + str(msets) + '_a' + str(processors_a) + '_b' + str(
        processors_b) + '_q' + str(prob_q) + '_d2' + '_r' + str(rho_id) + '_f' + str(mod_1) + '_s' + str(mod_2) + '_m' + str(mod_3) + '_s' + str(sparse)+'.npy'
    results_han_2 = np.load(han_name_2)

    greedy_name = 'outputs/results/results_greedy_m' + str(msets) + '_a' + str(processors_a) + '_b' + str(
        processors_b) + '_q' + str(prob_q) + '_d1' + '_r' + str(rho_id) + '_f' + str(mod_1) + '_s' + str(mod_2) + '_m' + str(mod_3) + '_s' + str(sparse)+'.npy'
    results_greedy = np.load(greedy_name)

    #improved_org_name = 'outputs/results/results_improved_m' + str(msets) + '_a' + str(processors_a) + '_b' + str(
    #    processors_b) + '_q' + str(prob_q) + '_d1' + '_r' + str(rho_id) + '_e0' + '_f' + str(mod_1) + '_s' + str(mod_2) + '_m' + str(mod_3) + '_s' + str(sparse)+'.npy'
    #results_improved_org = np.load(improved_org_name)

    improved_new_name = 'outputs/results/results_improved_new_m' + str(msets) + '_a' + str(processors_a) + '_b' + str(
        processors_b) + '_q' + str(prob_q) + '_d1' + '_r' + str(rho_id) + '_f' + str(mod_1) + '_s' + str(
        mod_2) + '_m' + str(mod_3) + '_s' + str(sparse)+'.npy'
    results_improved_new = np.load(improved_new_name)

    # han-hsgh
    y1 = [100]
    # han-greedy
    y2 = [100]
    # fed-greedy
    y3 = [100]
    # fed-improved-org
    y4 = [100]
    # fed-improved-new
    y5 = [100]
    # GS-MSRP
    y6 = [100]
    # LP-GFP-FMLP
    y7 = [100]
    # FED-P-EDF-POTTS
    y8 = [100]
    # HEURISTIC-P-EDF-POTTS
    y9 = [100]

    for j in range(0, 12):
        y1.append(results_han_1[j])
        y2.append(results_han_2[j])

        #y3.append(results_improved_org[j][0])
        y4.append(results_improved_new[j])
        y5.append(results_greedy[j])

    #if i == 6:
    #    y4 = [100, 100, 100, 100, 97, 93, 82, 65, 36, 19, 12, 11, 0]

    ax.axis([-2,63,-5,105])
    major_ticks = np.arange(0, 63, 10)
    minor_ticks = np.arange(0, 63, 5)
    ax.plot(x4, y4, color='red', label='FED-IMPROVED', linewidth=1.0, marker='D', markersize=8, markevery=1, fillstyle='none')
    ax.plot(x5, y5, color='maroon', label='FED-GREEDY', linewidth=1.0, marker='o', markersize=8, markevery=1, fillstyle='none')
    ax.plot(x1, y1, color='blue', label='HAN-EMU', linewidth=1.0, marker='v', markersize=8, markevery=1, fillstyle='none')
    ax.plot(x2, y2, color='blue', label='HAN-GREEDY', linewidth=1.0, marker='s', markersize=8, markevery=1, fillstyle='none')
    #ax.plot(x3, y3, color='blue', label='FED-IMPROVED-1', linewidth=2.0, marker='v', markersize=12, markevery=1, fillstyle='none')



    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    if (i == 1):
        ax.legend(bbox_to_anchor=(1.15, 1.45),
            loc=10,
            ncol=2,
            markerscale =1.5,
            borderaxespad=0.,
            prop={'size':20})

    if (prob_q == 0.1):
        prob = r'[10\%, 50\%]'
    elif (prob_q == 0.5):
        prob = r'[50\%, 90\%]'
    elif (prob_q == 0.9):
        prob = r'[10\%, 90\%]'
    if (mod_1 == 0):
        iaccessU = r'10\%'
    elif (mod_1 == 1):
        iaccessU = r'5\%'
    elif (mod_1 == 2):
        iaccessU = r'1\%'
    if (mod_2 == 0):
        pctg = r'100\%'
    elif (mod_2 == 1):
        pctg = r'75\%'
    elif (mod_2 == 2):
        pctg = r'50\%'

    ma = r'$M_a$'
    mb = r'$M_b$'
    pl = r'$P_{\ell}$'

    ax.set_title('('+ figlabel[i-1]+')' + ma + '='+ str(processors_a) + ', ' + mb + '=' + str(processors_b) + ', ' + pl + '='+iaccessU +', r='+pctg, size=21, x=0.48, y=1.02)
    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.grid(which='both')
    ax.set_aspect(0.3)

plt.show()
sys.exit()

