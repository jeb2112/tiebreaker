from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.config import Config
from kivy.clock import Clock
import matplotlib.pyplot as plt
from kivygarden_matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import kivygarden_matplotlib
from kivy.core.window import Window
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.utils import platform
from kivy.storage.jsonstore import JsonStore
from kivy.graphics import BorderImage

import itertools
import os
import time
import glob
import argparse
import numpy as np
from functools import partial
from datetime import datetime
from jnius import autoclass
import json
from data import Data
from layout import MyLayout,MyDropDown,AspectKivyAgg
from help import Help

class TieBreaker(App):

    def __init__(self,gfa=None,test=False,debug=False,show=False,wlt='W',ptype='matrix'):
        App.__init__(self)
        Log = autoclass('java.util.logging.Logger')
        self.logger = Log.getLogger(type(self).__name__)
        self.test = test
        self.debug = debug
        self.show = show # show plot in own matplotlib window for debugging
        self.gfa = gfa
        self.layout = MyLayout()
        self.data = Data(gfa=self.gfa)
        self.help = Help()

        if self.debug or self.test:
            self.data.gfa = {"A_gf":[gfa[0]],"A_ga":[gfa[1]], \
                    "X_gf":[gfa[2]],"X_ga":[gfa[3]]}
            setattr(self.layout.tinput_A_ga,'text',str(self.data.gfa['A_ga'][0]))
            setattr(self.layout.tinput_A_gf,'text',str(self.data.gfa['A_gf'][0]))
            setattr(self.layout.tinput_X_ga,'text',str(self.data.gfa['X_ga'][0]))
            setattr(self.layout.tinput_X_gf,'text',str(self.data.gfa['X_gf'][0]))
        if self.debug:
            self.imgdir = '/home/jbishop/src/python/kivy/testimages'
            setattr(self.layout.mb2,'text',ptype)
            self.layout.wltstate = wlt
            self.data.wltstate = self.layout.wltstate
            if ptype != 'matrix':
                self.layout.check[self.layout.wltstate].active = True
            self.doplot()
        if self.test:
            self.imgdir = '/home/jbishop/src/python/kivy/testimages/comp'
            # not sure why this needs delay
            Clock.schedule_once(self.do_test,1)
            self.ilabel = None

        # callbacks for radio button WLT updates
        for c in 'WL': # 'T' isn't implemented yet
            self.layout.check[c].bind(on_release=self.on_release)
            self.layout.check[c].bind(pressed=self.on_press)

        return

    # require dummy *args here. somehow, clock sends an arg to the callback
    # and get a can't find _clock.pyx file error if that arg cannot be assigned.
    def do_test(self,*args):
        for i,ptype in enumerate(['matrixW','barW','barL','tabularW','tabularL']):
            self.ilabel = '-'.join(self.gfa.astype(str))
            # doplot() does not force a gui draw evaluation. this is all __init__ and there is no return to loop control here.
            # self.doplot(lbl=ilabel)
            # do_layout does not force a gui draw evaluation
            # self.layout.fl.do_layout()
            # export to png won't work until a gui draw evaluation has happened.
            # self.layout.fl.export_to_png(os.path.join(self.imgdir,'I_'+ilabel+'.png'))
            # delaying the export to png till __init__ is complete by itself still doesn't 
            # force a gui draw evaluation.
            # creating a custom event button touch, works. once again, unusual delays seem to 
            # be needed. some sort of kivy overhead?? here allowing 1 second for each test and each export png
            Clock.schedule_once(partial(self.do_test_event,ptype),2*i)
            Clock.schedule_once(\
            partial(self.layout.fl.export_to_png,os.path.join(self.imgdir,'I_'+self.ilabel+'_'+ptype+'.png'))
            ,2*i+1)
        pass
        Clock.schedule_once(self.end_test,11)

    # a button event that can be used to flush the screen draw for testing
    # the test covers both dropdown/plot type, and radio button WLT.
    def do_test_event(self,*args):
        ptype,dt = args
        self.logger.info('dt: {:.2f}'.format(dt))
        self.layout.wltstate = ptype[-1]
        self.data.wltstate = self.layout.wltstate
        setattr(self.layout.mb2,'text',ptype[:-1])
        # radio button callback on_pressed() should be doing its own doplot(), in which case 
        # it shouldn't be necessary to call doplot() here. but for some reason
        # the radio button event is not always calling doplot() on all 5 test cases
        self.doplot()
        # now create the radio button event
        touch = MouseMotionEvent(None, 'buttontest', (0.5, 0.5))  # args are device, id, spos
        touch.button = 'left'
        # the WLT state assigned above is used to identify which button to press
        touch.pos = [n for n in self.layout.choicebox.children if n.name == self.layout.wltstate][0].center
        self.layout.choicebox.dispatch('on_touch_down', touch)

    def end_test(self,*args):
        cname = 'T_'+self.ilabel+'_comp.png'
        ilist = glob.glob(os.path.join(self.imgdir,'I*{}*.png'.format(self.ilabel)))
        cmdstr = 'convert +append {}/*{}*.png {}/{}'.format(self.imgdir,self.ilabel,self.imgdir,cname)
        os.system(cmdstr)
        for i in ilist:
            os.remove('{}'.format(i))
        self.stop()

    # on_press event in conjuction with on_release, to avoid radio button status update
    # delayed by plot routine
    def on_press(self,instance,*args):
        self.layout.wltstate = instance.name
        self.data.wltstate = instance.name

    # radio button callback to replot if WLT selection is changed
    # use on_release so the radio button update is not delayed by long doplot() call
    def on_release(self,instance,*args):
        self.logger.info('TieBreaker: radio released: {}'.format(instance.name))
        self.doplot('WLTpress')

    # callback for grid data entry
    # for multiline False, Ret defocuses and triggers on_enter callback
    def on_enter(self,instance):
        # clean up help screen
        self.layout.remove_help()
        # set the value    
        if not self.debug:
            val = int(instance.text)
            if val < 0 or val >30:
                instance.text = ''
                return
            else:
                self.data.gfa[instance.id] = [val]
        if [''] in self.data.gfa.values():
            return
        hf = self.doplot()

        return

    # plot type callback for drop down menu
    def on_select(self,instance,value):
        if value in ['matrix','bar','tabular']:
            # clean up any help screen
            self.layout.remove_help()
            setattr(instance.attach_to, 'text', value)
            # deactivate WLT radio button for 2D output
            if value == 'matrix':
                self.layout.set_nobuttons(value,tf=True)
            else:
                self.layout.set_nobuttons(value,tf=False)
            hf = self.doplot()
        elif value in ['help','about']:
            self.layout.remove_plot()
            self.help.set_category(value)
            if self.help.hlayout.parent is None:
                self.layout.fl.add_widget(self.help.hlayout)

    # for any text change, triggers on_text callback
    # use this, or insert_text??
    def on_text(self,instance,value):
        if instance.text=='':
            return
        val = int(instance.text)
        if val < 0 or val >30: # hard-coded upper limit, to finalize parameter checking
            instance.text = ''
            return
        else:
            self.data.gfa[instance.id] = [val]

    # main callback for plotting
    def doplot(self,lbl=''):
        if [''] in self.data.gfa.values():
            return
        if len(lbl):
            self.logger.info('TieBreaker: doplot: {}'.format(lbl))

        # for possible extension to storing per-game goals in sublist
        if sum(list(itertools.chain(*list(self.data.gfa.values())))) > 0:
            self.data.calc()
            if self.layout.plot is not None:
                self.layout.remove_plot()
            if self.layout.mb2.text == 'matrix':
                hf = self.data.plot1(show=self.show)
                self.layout.add_plot(hf)
            elif self.layout.mb2.text == 'bar':
                hf = self.data.plot2(show=self.show,plotsize=self.layout.floatsize)
                self.layout.add_plot(hf)
            elif self.layout.mb2.text == 'tabular':
                gdata = self.data.tabulate_grid()
                self.layout.do_tlayout(gdata)
                hf = None
                self.layout.add_plot(self.layout.tlayout)

            if self.debug:
                if hf is not None:
                    plt.savefig(os.path.join(self.imgdir,'testkivy.png'))
                ilabel = '-'.join(self.gfa.astype(str))+'_'+self.layout.mb2.text+self.layout.wltstate
                self.layout.fl.export_to_png(os.path.join(self.imgdir,'I_'+ilabel+'.png'))
            # note kivyagg object is still default 100x100 size here
            return hf

    def dropdown_open(self,instance,**kwargs):
        self.dropdown = MyDropDown(color=self.layout.bgcolor,background_color=self.layout.tintcolor,**kwargs)
        # note that the instance in the callback is a MyDropDown, while the
        # attach_to attribute is the menu Button object in MyLayout
        # self.dropdown.bind(on_select=lambda instance, x: setattr(instance.attach_to, 'text', x))
        # this on_select callback also replots data
        self.dropdown.bind(on_select=self.on_select)
        self.dropdown.open(instance)

    def build(self):
        # slightly awkward, with geometry in MyLayout and callbacks in TieBreaker
        # but not wanting to use .kv ids. 
        self.layout.tinput_A_gf.bind(on_text_validate=self.on_enter,text=self.on_text)
        self.layout.tinput_A_ga.bind(on_text_validate=self.on_enter,text=self.on_text)
        self.layout.tinput_X_gf.bind(on_text_validate=self.on_enter,text=self.on_text)
        self.layout.tinput_X_ga.bind(on_text_validate=self.on_enter,text=self.on_text)
        mbcallback = partial(self.dropdown_open,mlist=self.layout.mlist[self.layout.mbkeys[0]])
        self.layout.mb.bind(on_release=mbcallback)
        mb2callback = partial(self.dropdown_open,mlist=self.layout.mlist[self.layout.mbkeys[2]])
        self.layout.mb2.bind(on_release=mb2callback)
        menucallback = partial(self.dropdown_open,mlist = self.help.mlist,font_size=12.0)
        self.layout.titlemenu.bind(on_release=menucallback)
        # set defaults. note that defaults in self.debug for __init__() 
        # happen before build(), so the default for mb2.text has to be 
        # set here also which is awkward
        setattr(self.layout.mb,'text',self.layout.mlist[self.layout.mbkeys[0]][0])
        if not self.debug:
            setattr(self.layout.mb2,'text',self.layout.mlist[self.layout.mbkeys[2]][0])
        return self.layout.b

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug',default='False')
    parser.add_argument('--test',default='False')
    parser.add_argument('--gfa',default=[1,2,3,4])
    parser.add_argument('--wlt',default='W')
    parser.add_argument('--ptype',default='matrix')
    args = parser.parse_args()
    test = eval(args.test)
    debug = eval(args.debug)
    if test:
        gfa = np.random.randint(4,15,4)
        app = TieBreaker(gfa=gfa,test=test)
    elif debug:
        gfa = np.array(eval(args.gfa))
        app = TieBreaker(gfa=gfa,debug=debug,wlt=args.wlt,ptype=args.ptype)
    else:
        app = TieBreaker()
    app.run()
