from enum import auto
from math import comb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.font_manager import findfont, FontProperties
from matplotlib import colors,rcParams
import matplotlib.lines as lines
# from tkinter import W
import sympy
from sympy import solveset, S
from io import StringIO
import copy
from itertools import combinations
import kivy
from kivy.utils import platform
from kivy.core.window import Window
from PIL import ImageFont
from jnius import autoclass

# convenience class for reading the bar chart into a table format
class Tabstate():
    def __init__(self,state='r',delta=0,tabval=None,ext='',ga=0,bool='=',wlt='W'):

        self.state = state
        self.delta = delta 
        self.ext = ext
        self.ga = ga
        self.bool = bool
        self.wlt = wlt
        self.tabval = self.delta
        if self.wlt == 'L':
            self.tabval += 1 # for L/negative add 1 to bar-plotted value

    def tab_update(self,**kwargs):
        for key,val in kwargs.items():
            setattr(self,key,val) # should check key validity
            if 'tabval' not in kwargs.keys():
                self.tabval = self.delta
                # for L/negative add 1 to bar-plotted value
                if self.wlt == 'L':
                    self.tabval += 1

    def tab_output(self,gdata,ga=None):
        if self is not None:
            if ga is None:
                # awkward. if self.ga was never incremented, add one to compensate for -1 below
                ga = max(1,self.ga)
            # output state
            col1 = self.bool + str(ga-1) # -1 for the sequence of incrementing and updating
            col2 = str(self.tabval) + self.ext
            gdata.insert(0, col1)
            gdata.insert(0, col2)
            return gdata

class Data(object):

    def __init__(self,gfa=None):

        if gfa is None:
            self.gfa = {"A_gf":[''],"A_ga":[''], \
                        "X_gf":[''],"X_ga":['']}
        else:
            self.gfa = {"A_gf":[gfa[0]],"A_ga":[gfa[1]], \
                        "X_gf":[gfa[2]],"X_ga":[gfa[3]]}

        # max range of goals considered
        self.gset = range(0,41)
        # GF-GA to qualify
        self.delta = np.zeros(list(self.gset)[-1]+1,dtype=int)
        # GF-GA to tie
        self.deltaT = np.zeros(list(self.gset)[-1]+1,dtype=int)
        # max range of goals to plot
        self.pset = (0,10)
        # bar charts
        self.g =  np.zeros(np.size(self.gset),dtype=int)
        self.r =  np.zeros(np.size(self.gset),dtype=int)
        self.y =  np.zeros(np.size(self.gset),dtype=int)
        # table states for creating tabular output from the bar chart
        self.current = None
        self.latched = None
        self.wltstate = 'W'
        Log = autoclass('java.util.logging.Logger')
        self.logger = Log.getLogger(type(self).__name__)
        if platform == 'android':
            # get the screen resolution data
            DisplayMetrics = autoclass('android.util.DisplayMetrics')
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            metrics = DisplayMetrics()
            a = PythonActivity.mActivity
            wm = a.getSystemService(Context.WINDOW_SERVICE)
            d = wm.getDefaultDisplay()
            d.getMetrics(metrics)

            gDPI=metrics.getDeviceDensity()
            myheight = metrics.heightPixels
            mywidth = metrics.widthPixels
            xdpi = metrics.xdpi
            ydpi = metrics.ydpi
            self.dpi = metrics.xdpi # x and y should be same
            self.logger.info('kivy window size: {}'.format(Window.size))
            self.logger.info('native resolution dpi: {}, {}, {}, {}, {}'.format(gDPI,myheight,mywidth,xdpi,ydpi))
            self.yfontsize = 10 # hard-coded
            self.tfontsize = 8 # hard-coded
            self.pwidth = mywidth
        else:
            self.dpi = 81.55   # hardcoded for dell 27"
                                # 2nd screen is not controlled currently by gnu? this value calculated from xrandr | grep -w connected
            self.yfontsize = 14 # hard-coded
            self.tfontsize = 10
            self.pwidth = Window.size[0]
        self.figfacecolor = [243/256,237/256,218/256,1]
        self.axfacecolor = [0.8,0.8,0.8,1]
        self.fgcolor = [81/256,101/256,115/256,1]

        self.plot = None
        self.plottype = 0
        # self.newcolors = np.array([colors.to_rgba('red'),colors.to_rgba('green'),colors.to_rgba('yellow')])
        self.newcolors = np.array([[184/256,29/256,19/256,1],[50/256,164/256,49/256,1],[239/256,183/256,0,1]])
        self.newcmap = ListedColormap(self.newcolors)

        fontfam = rcParams['font.family']
        if platform == 'Android':
            self.currentfont = 'DroidSans.ttf'
        else:
            self.currentfont = findfont(FontProperties(family=fontfam)).split('/')[-1]
            if 'ttf' not in self.currentfont:
                self.currentfont = 'DejaVuSans.ttf'
        if False:
            self.plot_logo()
            self.do_combo()

    def set_axes_height(ax, h):
        fig = ax.figure
        aw, ah = np.diff(ax.transAxes.transform([(0, 0), (1, 1)]), axis=0)[0]
        fw, fh = fig.get_size_inches()
        dpi = fig.get_dpi()
        scale = h / (ah / dpi)
        fig.set_size_inches(fw*scale, fh*scale, forward=True)

    # quick demo calculation of the permutations
    def do_combo(self):
        # in 4 team round robin, there are 6 games each can be W,L or T
        r6set = [0]*6+[1]*6+[2]*6
        r5set = [0]*5+[1]*5+[2]*5
        c6set = combinations(r6set,6)
        c5set = combinations(r5set,5)
        ptset = set()
        for c in c6set:
            cm = np.zeros((4,4),dtype=int)
            pts = np.zeros(4,dtype=int)
            cm[np.triu_indices(4,k=1)] = np.array(c)
            cm[np.tril_indices(4,k=-1)] = 2-np.array(c)
            
            for t in range(0,4):
                pts[t] = sum(cm[t,:])
            ptset.add(tuple(np.sort(pts)))
        a=1           

    def calc(self):
        # starting values
        if self.wltstate == 'W':
            self.dflt = -11
        elif self.wltstate == 'L':
            self.dflt = 11
        self.g = np.ones(np.size(self.gset),dtype=int)*self.dflt
        self.r = np.ones(np.size(self.gset),dtype=int)*self.dflt
        self.y = np.ones(np.size(self.gset),dtype=int)*self.dflt

        # find analytical solution for a tie if any
        x,y = sympy.symbols('x,y',integer=True)
        t,t_0 = sympy.symbols('t,t_0',integer=True)
        # tie-breaker formula
        eqn = ( sum(self.gfa['A_gf'])+sum(self.gfa['A_ga']) ) *  ( sum(self.gfa['X_gf']) + x ) / \
                ( sum(self.gfa['X_gf'])+sum(self.gfa['X_ga']) + x + y ) - \
                    sum(self.gfa['A_gf'])
        # solve the diophantine for equality (ie tie-breaker still a tie) by symbolic
        conds = [(0 <= x), (x<=list(self.gset)[-1]), (0 <= y), (y<=list(self.gset)[-1])]
        gensol = sympy.diophantine(eqn,t,[x,y])
        if len(gensol):
            sol = gensol.pop()
            if sol == (0,) or len(sol)==1:
                self.sol_set = []
            else:
                (xs,ys) = sol
                conds_t = [cond.subs(x, xs).subs(y, ys) for cond in conds]
                conds_t_sol = sympy.solve(conds_t, t_0)

                # Find the finite set of values for t_0 and sub in to general solution
                set_t0 = (conds_t_sol.as_set() & S.Integers)
                self.sol_set = [(xs.subs(t_0, ti), ys.subs(t_0, ti)) for ti in set_t0]
        else:
            self.sol_set = []

        # for the inequality, solve by simple evaluation
        # multi-variate + diophantine + underdetermined + inequality, is not covered by any python module
        xset=self.gset
        yset=self.gset
        yv,xv = np.meshgrid(xset,yset)
        self.val = ( sum(self.gfa['A_gf'])+sum(self.gfa['A_ga']) ) *  ( sum(self.gfa['X_gf']) + xv ) / \
                ( sum(self.gfa['X_gf'])+sum(self.gfa['X_ga']) + xv + yv ) > \
                    sum(self.gfa['A_gf'])
        self.val = self.val.astype(int)
        # add diophantine solution, if any.
        if len(self.sol_set):
            for sol in self.sol_set:
                self.val[sol] = 2

        # assignment of red,green,yellow for delta goal differentials
        for ga in self.gset:

            # process yellow tie
            gfind = np.where(self.val[:,ga]==2)[0]
            if len(gfind):
                self.y[ga] = gfind[0] - ga

            # process green qualify
            gfind = np.where(self.val[:,ga]==1)[0]
            if len(gfind):
                self.g[ga] = gfind[0] - ga

            # process red disqualify
            gfind = np.where(self.val[:,ga]==0)[0]
            if len(gfind):
                self.r[ga] = gfind[-1] - ga

        # adjustment for W/L state, for plotting purposes
        if self.wltstate == 'W':
            # adjust all negative values for a win
            # clip all negative values for a win
            # self.r[np.where((self.r < 0) & (self.r != self.dflt))] = -1
            # self.g[np.where((self.g < 0) & (self.g != self.dflt))] = 0
            self.r[np.where(self.r < 0)] = -1
            self.g[np.where(self.g < 0)] = 0
            self.y[np.where(self.y<0)] = self.dflt
            for ga in self.gset:
                # adjust r/g for default values
                if self.g[ga] == self.dflt:
                    self.g[ga] = max(self.r[ga],self.y[ga])+1
                elif self.r[ga] == self.dflt:
                    self.r[ga] = min(self.g[ga],self.y[ga])-1
                if self.y[ga] == self.dflt:
                    self.y[ga] -= 0 # precompensate for adjustment below
                # add +1 offset for positively plotting zero
                # or move this offset to plot routine
            # clip all positive values
            for ga in self.gset:
                self.g[ga] = min(abs(self.dflt),self.g[ga])
                self.r[ga] = min(abs(self.dflt)-1,self.r[ga])
                self.y[ga] = min(abs(self.dflt),self.y[ga])
            # offset for plotting 0 as first bin on the y-axis
            # or add this offset below during plotting...
            for ga in self.gset:
                self.g[ga] += 0
                self.r[ga] += 0
                self.y[ga] += 0
                # other cases?
                pass
        elif self.wltstate == 'L':
            # clip all positive values for a loss
            # self.r[np.where((self.r > 0) & (self.r != self.dflt))] = 0
            # self.g[np.where((self.g > 0) & (self.g != self.dflt))] = 1
            self.r[np.where(self.r > 0)] = 0
            self.g[np.where(self.g > 0)] = 1
            self.y[np.where(self.y>0)] = self.dflt
            # further adjustments
            for ga in self.gset:
                # adjust r/g replace default values
                if self.g[ga] == self.dflt:
                    self.g[ga] = max(self.r[ga],self.y[ga]) + 1
                elif self.r[ga] == self.dflt:
                    self.r[ga] = min(self.g[ga],self.y[ga])
                    # will only plot r if gf>0
                    if abs(self.r[ga]) > ga:
                        self.r[ga] -= 1
                if self.y[ga] == self.dflt:
                    self.y[ga] += 1 # pre-compensate for adjustment below
                # other cases?

                # -1 offset for positively plotting zero
                # currently this adjustment here versus in plotting is arranged inversely for 'W' 'L' need to reconcile
                self.g[ga] -= 1
                self.r[ga] -= 1
                self.y[ga] -= 1
                pass
        self.deldiff = np.where(np.diff(self.delta)!=0)[0]
        a=1


    # plot 1. 2D
    def plot1(self,show=True):
        hf = plt.figure(1,dpi=self.dpi)
        hf.patch.set_facecolor(self.figfacecolor)
        hf.set_tight_layout({'pad':0.5}) # 0.5
        hp = plt.imshow(self.val,cmap=self.newcmap,origin='lower',vmin=0,vmax=2)
        hp.origin = 'lower'
        ax = plt.gca()
        plt.xlim([-0.5,self.pset[1]+0.5])
        plt.ylim([-0.5,self.pset[1]+0.5])
        ax.set_xticks(np.arange(0,self.pset[1]+1,self.pset[1]))
        ax.set_xticks(np.arange(0.5,self.pset[1]),minor=True)
        ax.set_yticks(np.arange(0,self.pset[1]+1,self.pset[1]))
        ax.set_yticks(np.arange(0.5,self.pset[1]),minor=True)
        ax.set_xticklabels(np.arange(0,self.pset[1]+1,self.pset[1]))
        ax.set_yticklabels(np.arange(0,self.pset[1]+1,self.pset[1]))
        ax.grid(which='minor',color='k',linewidth=0.3)
        plt.tick_params(axis='both',which='both',bottom=False,left=False,labelbottom=False,labelleft=False)
        for l in range(0,self.pset[1]+2,2):
            if l<10:
                plt.text(l-0.3,-0.3,str(l),fontsize=self.tfontsize)
                plt.text(-0.3,l-0.3,str(l),fontsize=self.tfontsize)
            else:
                plt.text(l-0.5,-0.3,str(l),fontsize=self.tfontsize)
                plt.text(-0.5,l-0.3,str(l),fontsize=self.tfontsize)

        # record bounding box without labels
        tightbbox1 = hf.get_tightbbox(hf.canvas.get_renderer())
        plt.xlabel('team X GA',fontsize=self.yfontsize,color=self.fgcolor)
        plt.ylabel('team X GF',fontsize=self.yfontsize,color=self.fgcolor)
        # now reset the tight box to include labels.
        tightbbox = hf.get_tightbbox(hf.canvas.get_renderer())
        # 2d plot is height limited, so this centres the 2D plot axes. 
        hf.xpos = int( self.dpi * (tightbbox.width - tightbbox1.width) / 2 ) # attribute for plot axes centering
        hf.set(figheight=tightbbox.height,figwidth=tightbbox.width)
        
        if show:
            plt.show()
        else:
            # strange. originally the xlabel was being cut off. added tight_layout but did nothing.
            # added arbitrary hard-coded rect to tight_layout to make it less tight, worked.
            # but, upon repeat calls, the rect was changing and getting smaller.
            # upon removing the tight layout, the original xlabel getting cut off problem is now gone,
            # but, the plot size now also doesn't change from repeats.
            # this may be from having a second monitor attached at a
            # different resolution. everything seems normal using only the 
            # primary monitor
            # hf.tight_layout(rect=[0,.05,1,1])
            return hf
        

    # plot 2. 1D bar chart
    def plot2(self,show=True,plotsize=None):

        if plotsize is None:
            raise ValueError('data.plot2: No plotsize specified')
        # scale window to a specific size, usually a width
        figsize_w = plotsize[0] / self.dpi
        if plotsize[1] is not None:
            figsize_h = plotsize[1] / self.dpi
        else:
            figsize_h = figsize_w

        # setting an exact width here, in order to calculate font size of ylabel 
        # down below. set matplotlib dpi to screen dpi for exact sizing
        hf = plt.figure(1,figsize=(figsize_w,figsize_h),dpi=self.dpi)
        hf.patch.set_facecolor(self.figfacecolor)
        hf.set_tight_layout({'pad':0.5}) # 0.5

        ax = plt.gca()
        ax.set_aspect('equal')
        ax.patch.set_facecolor(self.axfacecolor)
        # yaxis depends on win or loss scenario
        if self.wltstate == 'W':
            ylim0a = self.pset[0]
            ylim0b = min(self.g[:self.pset[1]])-2
            ylim0c = min(self.r[:self.pset[1]])-2
            ylim0d = 6
            ylim0 = max(ylim0a,min(max(ylim0b,ylim0c),ylim0d))
            # ylim0 = max(self.pset[0], min(min(self.g[:self.pset[1]])-2,6))
            ylim1 = min(self.pset[1]+1,max(max(self.g[:self.pset[1]])+2,5))
            if ylim1 < self.pset[1]+1:
                ylim0 = self.pset[0]

            # plot the data, red overwrites green for 'W'
            # +1 for offsetting 0 onto the positive y-axis, ie a tie
            plt.bar(self.gset,self.g+1,color=self.newcmap.colors[1,:])
            plt.bar(self.gset,self.y+1,color=self.newcmap.colors[2,:])
            plt.bar(self.gset,self.r+1,color=self.newcmap.colors[0,:])
            ax.set_yticks(np.arange(ylim0,ylim1,ylim1)) # note this is off-axis, but if not specified it blocks the minor tick
            ax.set_yticks(np.arange(ylim0-1,ylim1),minor=True)
            # y-axis
            for l in range(int(ylim0)+0,int(ylim1),2):
                if l<10:
                    plt.text(-0.3,l+0.4,str(l),fontsize=self.tfontsize)
                else:
                    plt.text(-0.3,l+0.4,str(l),fontsize=self.tfontsize)
        elif self.wltstate =='L':
            ylim0a = -self.pset[1]-1
            ylim0b = min(self.g[:self.pset[1]])-2
            ylim0c = min(self.r[:self.pset[1]])-2
            ylim0d = -5
            ylim0 = max(ylim0a,min(ylim0b,ylim0c,ylim0d))
            rneg = self.r[np.where(self.r[:self.pset[1]]<0)]
            if len(rneg):
                if max(rneg) < -4:
                    ylim0 = max(rneg) - 1
            ylim1 = 0.0

            # plot the data. green overwrites red for 'L' case
            # -1 for offsetting 0 onto the negative y-axis, ie a tie
            plt.bar(self.gset,self.r-0,color=self.newcmap.colors[0,:])
            plt.bar(self.gset,self.y-0,color=self.newcmap.colors[2,:])
            plt.bar(self.gset,self.g-0,color=self.newcmap.colors[1,:])
            ax.set_yticks(np.arange(ylim0,ylim1+0.1,abs(ylim0))) # note this is off-axis, but if not specified it blocks the minor tick
            ax.set_yticks(np.arange(ylim0,ylim1),minor=True)
            # y-axis
            ylabel0 = ylim0
            if (abs(ylim0) % 2) != 0:
                ylabel0 -= 1
            for l in range(int(ylabel0)+2,int(ylim1)+1,2):
                if l==0:
                    plt.text(-0.2,l-0.7,str(l),fontsize=self.tfontsize)
                else:
                    plt.text(-0.3,l-0.7,str(l),fontsize=self.tfontsize)

        ax.grid(which='minor',color='k',linewidth=0.25)
        ax.set_xticks(np.arange(0,self.pset[1]+2,2))
        plt.tick_params(axis='both',which='both',bottom=True,left=False,labelbottom=True,labelleft=False,labelsize=self.tfontsize)

        plt.ylim([ylim0,ylim1])
        plt.xlim([-0.5,self.pset[1]+0.5])
        # set plot to max window width
        ylabel = 'team X GF-GA'
        tightbbox = hf.get_tightbbox(hf.canvas.get_renderer())
        # dynamically adjust font size for variable yaxis length
        testfont = ImageFont.truetype(self.currentfont,self.yfontsize)
        lsize = np.array(testfont.getsize(ylabel)) / self.dpi
        while lsize[0] > tightbbox.height: # ie test x size coord for a y-axis text against bbox height
            self.yfontsize -= 1
            try:
                testfont = ImageFont.truetype(self.currentfont,self.yfontsize)
            except Exception as e:
                return e
            lsize = np.array(testfont.getsize(ylabel)) / self.dpi
            self.logger.info('fontsize: {}'.format(self.yfontsize))

        # add labels
        tightbbox1 = hf.get_tightbbox(hf.canvas.get_renderer())
        plt.ylabel(ylabel,fontsize=self.yfontsize,color=self.fgcolor)
        # ylabel is the limiting case
        plt.xlabel('team X GA',fontsize=self.yfontsize,color=self.fgcolor)

        # now reset the tight box to include labels. if the figure is too tall for the
        # available float layout, scale it down to fit
        tightbbox = hf.get_tightbbox(hf.canvas.get_renderer())
        # plt.show()
        if tightbbox.height > tightbbox.width:
            h = figsize_h
            w = tightbbox.width * (figsize_h / tightbbox.height)
            hf.xpos = int ( self.dpi * (tightbbox.width - tightbbox1.width ) / 2 ) # attribute for additional offset
        else:
            h = tightbbox.height
            w = tightbbox.width
            hf.xpos = 0
        hf.set(figheight=h,figwidth=w)

        if show:
            plt.show()
        return hf

    # tabular output for Label. probably won't use it anymore.
    # tried to use a string buffer to render tabs, since kivy label does not,
    # didn't work.
    # also using print(file=buf) didn't work, nor did contextlib.redirect_stdout
    # nor did unicoding and decode('unicode_escape')'ing.
    # there are dozens of answers to this problem on stackflow, and none work for \t
    # but, then found string.expandtabs() method.
    # kept the stringio buf but it's not needed.
    def tabulate(self):
        buf = StringIO()
        buf.write( ' {}  {}'.format('team X GA   ','team X GF>GA\n').expandtabs(4) )
        if len(self.deldiff):
            buf.write('\t<={}\t\t\t\t+{}\n'.format(self.deldiff[0],self.delta[self.deldiff[0]]-1).expandtabs(4))
            for d in range(len(self.deldiff)):
                if self.deldiff[d]+1 == self.sol_set[0][1]:
                    buf.write ('\t  {}\t\t\t\t+{} {}\n'.format(self.deldiff[d]+1,self.delta[self.deldiff[d]]-1,'T').expandtabs(4))
                else:
                    buf.write('\t  {}\t\t\t\t+{}\n'.format(self.deldiff[d]+1,self.delta[self.deldiff[d]]-1).expandtabs(4))
            buf.write('\t>={}\t\t\t\t+{}\n'.format(self.deldiff[-1]+2,self.delta[self.deldiff[-1]+1]-1).expandtabs(4))
        return buf.getvalue()

    # tabulate output for gridlayout
    # grid layout child widgets are in reverse order by default kivy convention
    # match that here with insert(0,) to build gdata list

    def tabulate_grid(self):
        gdata = []
        ga = 0
        if self.wltstate == 'W':

            # set the starting qualification state for ga=0. 
            if self.y[0] >= 0 and self.y[0] < abs(self.dflt): # ie app is clipped at self.dflt
                self.current = Tabstate(state='y',delta=self.y[0],tabval=None,ext='T',ga=0,bool='=',wlt='W')
            elif self.g[0] >= 0 and self.g[0] < abs(self.dflt): # ie app is clipped at self.dflt
                self.current = Tabstate(state='g',delta=self.g[0],tabval=None,ext='',ga=0,bool='=',wlt='W')
            else:
                self.current = Tabstate(state='r',delta=self.r[0],tabval=None,ext='x',ga=0,bool='=',wlt='W')
            self.latched = copy.deepcopy(self.current)
            ga = 1
            while ga < self.pset[1]+2: # one extra for latched

                if self.current.state == 'r':
                    if self.r[ga] == self.current.delta: # no change in state
                        if ga == self.pset[1]+1: # reached the end
                            # flip boolean and output final row for upper limit
                            if len(gdata):
                                self.latched.bool = '>'
                            else:
                                self.latched.bool = '>='
                            gdata = self.latched.tab_output(gdata)
                        elif ga - self.current.ga > 1:
                            # increment boolean for a range
                            self.current.bool = '<='
                    elif self.r[ga] > self.current.delta: # change in 'r' state
                        # output latched state
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        # update current state
                        if self.y[ga] == self.current.delta:
                            self.current.tab_update(state='y',bool='=',ext='T',ga=ga)
                        elif self.g[ga] == self.current.delta:
                            self.current.state = 'g'
                            if ga - self.current.ga > 1:
                                self.current.bool = '<='
                            else:
                                self.current.bool = '='
                            self.current.ext=''
                            self.current.ga = ga
                        # elif continued r??

                        # latch current state
                        self.latched = copy.deepcopy(self.current)

                elif self.current.state == 'y':
                    if self.y[ga] == self.current.delta: # no change in state
                        if ga == self.pset[1]+1: # reached the end
                            # flip boolean and output final row for upper limit
                            if len(gdata):
                                self.latched.bool = '>'
                            else:
                                self.latched.bool = '>='
                            gdata = self.latched.tab_output(gdata)
                        elif ga - self.current.ga > 1:
                            # increment boolean for a range
                            self.current.bool = '<='
                    elif self.y[ga] != self.current.delta and self.y[ga] < abs(self.dflt) and self.y[ga] != self.dflt:
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.y[ga],state='y',bool='=',ext='T',ga=ga)
                        self.latched = copy.deepcopy(self.current)
                    elif self.g[ga] >= self.current.delta and self.g[ga] < abs(self.dflt):
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.g[ga],state='g',bool='=',ext='',ga=ga)
                        self.latched = copy.deepcopy(self.current)
                    else:
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.r[ga],state='r',ext='x',bool='=',ga=ga)
                        self.latched = copy.deepcopy(self.current)

                elif self.current.state == 'g':
                    if self.y[ga] != self.dflt:
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.y[ga],state='y',bool='=',ext='T',ga=ga)
                        self.latched = copy.deepcopy(self.current)
                    elif self.g[ga] == self.current.delta: # no change in state
                        if ga == self.pset[1]+1: # reached the end, ahead by +1 for latch
                            # flip boolean and output final row for upper limit
                            if len(gdata):
                                self.latched.bool = '>'
                            else:
                                self.latched.bool = '>='
                            gdata = self.latched.tab_output(gdata)
                        else:
                            # increment boolean for a range
                            self.latched.bool = '<='
                    elif self.g[ga] != self.current.delta and self.g[ga] < abs(self.dflt): # change in 'g' state
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.g[ga],state='g',ext='',ga=ga)
                        if ga - self.current.ga > 1:
                            self.current.bool = '<='
                        else:
                            self.current.bool = '='
                        self.latched = copy.deepcopy(self.current)
                    else:
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.r[ga],state='r',ext='x',bool='=',ga=ga)
                        self.latched = copy.deepcopy(self.current)

                ga += 1

        elif self.wltstate == 'L':
            if self.y[0] <= -1 and self.y[0] > -self.dflt:
                self.current = Tabstate(state='y',delta=self.y[0],tabval=None,ext='T',ga=0,bool='=',wlt='L')
            elif self.g[0] <= -1 and self.g[0] > -self.dflt: # ie app is clipped at self.dflt
                self.current = Tabstate(state='g',delta=self.g[0],tabval=None,ext='',ga=0,bool='=',wlt='L')
            else:
                self.current = Tabstate(state='r',delta=self.r[0],tabval=None,ext='x',ga=0,bool='=',wlt='L')
            self.latched = copy.deepcopy(self.current)
            ga = 1
            while ga < self.pset[1]+2: # one extra for latched

                if self.current.state == 'r':
                    if self.r[ga] == self.current.delta: # no change in state
                        if ga == self.pset[1]+1: # reached the end, +1 for latch
                            # flip boolean and output final row for upper limit
                            # need a more generic handler for detecting >= versus > cases
                            if len(gdata):
                                self.latched.bool = '>'
                            else: 
                                self.latched.bool = '>='
                            gdata = self.latched.tab_output(gdata)
                        else:
                            if ga - self.current.ga > 1:
                                # increment boolean for a range
                                self.latched.bool = '<='

                    elif self.r[ga] < self.current.delta: # change in 'r' state
                        # output latched state
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        # update current state
                        if self.y[ga] == self.current.delta:
                            self.current.tab_update(state='y',bool='=',ext='T',ga=ga)
                        elif self.g[ga] == self.current.delta:
                            self.current.state = 'g'
                            if ga - self.current.ga > 1:
                                self.current.bool = '<='
                            else:
                                self.current.bool = '='
                            self.current.ext=''
                            self.current.ga = ga
                        # latch current state
                        self.latched = copy.deepcopy(self.current)

                elif self.current.state == 'y':
                    if self.y[ga] == self.current.delta: # no change in state
                        if ga == self.pset[1]+1: # reached the end
                            # flip boolean and output final row for upper limit
                            if len(gdata):
                                self.latched.bool = '>'
                            else:
                                self.latched.bool = '>='
                            gdata = self.latched.tab_output(gdata)
                        elif ga - self.current.ga > 1:
                            # increment boolean for a range
                            self.current.bool = '<='
                    elif self.y[ga] != self.current.delta and self.y[ga] != self.dflt:
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.y[ga],state='y',bool='=',ext='T',ga=ga)
                        self.latched = copy.deepcopy(self.current)
                    elif self.g[ga] < 0 and self.g[ga] > -self.dflt: #new
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.g[ga],state='g',bool='=',ext='',ga=ga)
                        self.latched = copy.deepcopy(self.current)
                    else: # self.r[ga] <= self.current.delta: new
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.r[ga],state='r',bool='=',ext='x',ga=ga)
                        self.latched = copy.deepcopy(self.current)

                elif self.current.state == 'g':
                    if self.y[ga] != self.dflt:
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.y[ga],state='y',bool='=',ext='T',ga=ga)
                        self.latched = copy.deepcopy(self.current)
                    elif self.g[ga] == self.current.delta: # no change in state
                        if ga == self.pset[1]+1: # reached the end
                            # flip boolean and output final row for upper limit
                            self.latched.bool = '>'
                            gdata = self.latched.tab_output(gdata)
                        else:
                            # increment boolean for a range
                            self.latched.bool = '<='
                    elif self.g[ga] != self.current.delta and (self.g[ga] < 0 and self.g[ga] >= -self.dflt): # change in 'g' state
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.g[ga],state='g',ext='',ga=ga)
                        if ga - self.current.ga > 1:
                            self.current.bool = '<='
                        else:
                            self.current.bool = '='
                        self.latched = copy.deepcopy(self.current)
                    else:
                        gdata = self.latched.tab_output(gdata,ga=ga)
                        self.current.tab_update(delta=self.r[ga],state='r',ext='x',bool='=',ga=ga)
                        self.latched = copy.deepcopy(self.current)

                ga += 1

            pass
        return gdata

    def plot_logo(self):
        logo_data = [[1,1,1],[1,2,0],[0,0,0]]
        hf = plt.figure(2,dpi=self.dpi,figsize=(4,4))
        hf.patch.set_facecolor(self.figfacecolor)
        hf.set_tight_layout({'pad':0.5}) # 0.5
        hp = plt.imshow(logo_data,cmap=self.newcmap,origin='lower',vmin=0,vmax=2)
        hp.origin = 'upper'
        ax = plt.gca()
        ax.set_xticks(np.arange(0,self.pset[1]+1,self.pset[1]))
        ax.set_xticks(np.arange(0.5,self.pset[1]),minor=True)
        ax.set_yticks(np.arange(0,self.pset[1]+1,self.pset[1]))
        ax.set_yticks(np.arange(0.5,self.pset[1]),minor=True)
        ax.grid(which='minor',color='k',linewidth=1)
        plt.tick_params(axis='both',which='both',bottom=False,left=False,labelbottom=False,labelleft=False)
        plt.xlim([-0.5,2.5])
        plt.ylim([-0.5,2.5])
        plt.savefig('/home/jbishop/src/python/kivy/images/tb_icon.png')
        return
