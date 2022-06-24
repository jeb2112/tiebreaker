from operator import sub
from kivy.base import runTouchApp
from kivy.properties import ObjectProperty,ListProperty,StringProperty
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from pyparsing import original_text_for
from kivygarden_matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.graphics import Color, Rectangle, BorderImage
from kivy.clock import Clock
from kivy.utils import platform
from kivygarden_matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.input.providers.mouse import MouseMotionEvent

from itertools import chain
import numpy as np
from matplotlib import colors
import matplotlib.pyplot as plt
import re
import copy
from jnius import autoclass

class NumericInput(TextInput):
    def __init__(self,multiline=False,id=id):
        TextInput.__init__(self,multiline=multiline,\
            halign='center',input_filter='int',padding=[6,2,6,0])
        self.id = id
        self.pat = re.compile('^[0-9]{1,2}')
        # this didn't work to keep on_size from parent separate from sub-classed on_size
        # at least it wasn't called at the initial drawing of the layout.
        # self.bind(on_size=self.on_size_callback)

    def on_focus(self,instance,value):
        if value:
            instance.text = ''
        else:
            pass
        # self.font_size = self.height*0.8

    def on_size(self,instance,value):
        # had to run parent on_size manually here. need to use a binding somehow
        super(NumericInput,self).on_size(instance,value)
        self.font_size = self.height*0.8

    # test here, or in on_text??
    # or rely in input_filter?
    # def insert_text(self, substring, from_undo=False):
    #     s = re.match(self.pat,substring)
    #     if s:
    #         return super().insert_text(s.group(),from_undo=from_undo)
    #     else:
    #         return

class MyDropDown(DropDown):

    # create a dropdown. mlist is the list of menu items
    def __init__(self,mlist=None,color=[1,1,1,1],background_color=[1,1,1,1],font_size=15.0):
        super(MyDropDown,self).__init__()
        if mlist is None:
            raise Exception('no menu list provided')
        self.font_size = font_size
        self.mlist = mlist
        self.bheight = int(Window.size[1] * .05)
        for index in range(len(self.mlist)):
            # for dropdowns, need to specify the height manually
            # %% of window is hard-coded for now
            btn = Button(text=self.mlist[index], size_hint_y=None, height=self.bheight, \
                    color=color, background_color = background_color, font_size = self.font_size)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class AspectKivyAgg(FigureCanvasKivyAgg):
    def __init__(self,*args,**kwargs):
        super(AspectKivyAgg,self).__init__(*args,**kwargs)
        self.event = None
    # over-riding this method to use limiting width/height and preserve aspect ratio
    # wanted the plot to display at the top of the float layout, centred in x, be as wide/tall
    # as possible, ie with minimum white space.
    # getting these requirements didn't seem possible with easy default behaviour, unless missed 
    # something.
    # a) tried setting the size of the kivyagg object to be the size of the plot/bbox, so it could be positioned
    # in the float layout with pos hints. This did not work. The size of the kivyagg is calculated during
    # do_layout() to be the same size as the float layout. any attempt to modify that size in a size related
    # callback created an infinite callback loop that eventually timed out, after which the correct result
    # was displayed. additional attempts 
    # to schedule the size change to be a small amount of time later to allow the do_layout() to complete, 
    # didn't make any change to the size, but did create an infinite loop that never timed out.
    # b) what worked was letting the kivyagg be the identical size of the float layout, then adjusting its
    # position so as to centre the plot. that the kivyagg now does not align and overlap exactly
    # with the float layout appears to have no consequences. furthermore, setting a position during 
    # a size callback, somehow avoids creating an infinite callback loop. 
    def _on_size_changed(self, *args):
        '''Changes the size of the matplotlib figure based on the size of the
           widget. The widget will change size according to the parent Layout
           size.
        '''
        w, h = self.size
        dpival = self.figure.dpi
        winch = float(w) / dpival
        hinch = float(h) / dpival
        if self.figure.bbox_inches.max[1]/self.figure.bbox_inches.max[0] > hinch/winch:
            # scale down the width for max height constraint
            winch = hinch * (self.figure.bbox_inches.max[0] / self.figure.bbox_inches.max[1])
            self.figure.set_size_inches(winch, hinch, forward=False)
            # now calculate an offset pos of the kivyagg itself, which acts to centre the plot
            xpos = int((w - self.figure.bbox.width)/2)
            ypos = 0
        else:
            # scale down the height for max width constraint
            hinch = winch * (self.figure.bbox_inches.max[1] / self.figure.bbox_inches.max[0])
            self.figure.set_size_inches(winch, hinch, forward=False)
            # set the offset pos to place plot at the top of the float layout
            xpos = 0
            ypos = int((h - self.figure.bbox.height)/1)
        # awkward. += because there is separate correction for the label offset calculated in data.plot1(),plot2()
        # should combine these somehow
        self.pos[0] += xpos 
        self.pos[1] += ypos
        self.resize_event()
        self.draw()

    def set_height(self, *args):
        w, h = self.size
        dpival = self.figure.dpi
        winch = float(w) / dpival
        hinch = winch / self.figure.bbox_inches.max[0] * self.figure.bbox_inches.max[1]
        self.height = int(hinch*dpival)

# has custom background color, and optional square inset color
class BgLabel(Label):
    def __init__(self,fontfrac=None,texture=None,bgcolor=None,square=False,sqcolor=[0.7,0.7,0.7,1],max=False,**kwargs):
        super(BgLabel,self).__init__(**kwargs)
        if bgcolor is None:
            self.bgcolor = [0,0,0,1]
        else:
            self.bgcolor = bgcolor
        self.fontfrac = fontfrac
        self.texture = texture
        self.square = square
        self.sqcolor = sqcolor
        self.font_max = max
    def set_square(self):
        pos = [self.pos[0]+(self.size[0]-self.size[1])/2,self.pos[1]]
        siz = [self.size[1],self.size[1]]
        return pos,siz

    def set_fontsize(self):
        if self.fontfrac is not None:
            self.font_size = self.height * self.fontfrac
            if self.font_max:
                if self.font_size > 26: # max is hard-coded
                    self.font_size = 26
        return
 
    # note there is no parent on_size for Label/Widget being overridden
    def on_size(self, *args):
        if self.canvas is not None:
            self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bgcolor)
            Rectangle(pos=self.pos, size=self.size)
            if self.square:
                pos,siz = self.set_square()
                Color(*self.sqcolor)
                Rectangle(pos=pos, size=siz)
        # don't know any other way to scale font size equivalently for desktop and phone
        self.set_fontsize()

# getting multi-line Label text to wrap without using .kv requires these bindings
# the first binding centres the x,y position of the text
# in the label, and wraps it. note that it is bound to height, not width, as height seems
# to follow width in the order of opertions at do_layout(). 
class WrappedBgLabel(BgLabel):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(height=lambda *x:self.setter('text_size')(self, (self.width, self.height)))
        # this addtional binding shown in stackflow examples but don't seem to need it
        # self.bind(texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))    

# for buttons with image. maintain square aspect ratio  
class ImageButton2(Button):
    def __init__(self,**kwargs):
        super(ImageButton2,self).__init__(**kwargs)
        self.border = (0,0,0,0)

    def on_size(self,*args):
        yhint = int(bool(self.size_hint_y))
        self.size[1-yhint] = self.size[yhint]

# has custom background color to fill widget space and keep aspect fixed
# probably don't even need this with Window.clear_color()
class BgImage(Image):
    def __init__(self,bgcolor=None,**kwargs):
        super(BgImage,self).__init__(**kwargs)
        if bgcolor is None:
            self.bgcolor = [0,0,0,1]
        else:
            self.bgcolor = bgcolor

    def on_size(self, *args):
        if self.canvas is not None:
            self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bgcolor)
            Rectangle(pos=self.pos, size=self.size)

# has custom background color to fill widget space 
class BgBoxLayout(BoxLayout):
    def __init__(self,bgcolor=None,**kwargs):
        super(BgBoxLayout,self).__init__(**kwargs)
        # this binds in parallel with existing pos,size bindings in parent?
        self.fbind('pos', self.setcolor)
        self.fbind('size', self.setcolor)
        if bgcolor is None:
            self.bgcolor = [0,0,0,1]
        else:
            self.bgcolor = bgcolor

    def setcolor(self,*args):
        # self._trigger_layout not needed because of parallel binding?
        if self.canvas is not None:
            self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bgcolor)
            self.bg = Rectangle(pos=self.pos, size=self.size)

class MyCheckBox(CheckBox):

    # kivy property is not an instance attribute
    pressed = ListProperty([0,0])
    def __init__(self,name=None,**kwargs):
        super(MyCheckBox,self).__init__(**kwargs)
        self.name = name

    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            # no functionality here for now
            if self.name == 'T':
                return True
            # otherwise proceed regular event handler to change the button colors
            return super(MyCheckBox, self).on_touch_down(touch)

class MyScrollView(ScrollView):
    def __init__(self,gridlayout,**kwargs):
        super().__init__(**kwargs)
    
        # Window.bind(on_maximize=self.testing)
        
        self.size_hint = (1,None)
        # self.pos_hint = {'center_x':0.5,'top': 1}
        # self.size = (Window.width,Window.height)

        self.inside = gridlayout
        # no idea what this does, but is needed to make a scrollable content
        self.inside.bind(minimum_height=self.inside.setter('height'))
        self.inside.size_hint_y= None
                
        self.add_widget(self.inside)
        
    def set_table(self,table):
        self.inside = table
        if len(self.children) == 0:
            self.add_widget(self.inside)
    
    # def testing(self,instance):
    #     self.size= (Window.width,Window.height)            

class MyLayout():
    def __init__(self):
        # to store size of the float layout after first layout
        self.floatsize = [Window.size[0],None]
        self.plot = None
        # self.newcolors = np.array([colors.to_rgba('red'),colors.to_rgba('green'),colors.to_rgba('yellow')])
        # these are the RAL codes traffic signal colours
        self.newcolors = np.array([[184/256,29/256,19/256,1],[50/256,164/256,49/256,1],[239/256,183/256,0,1]])
        self.titlimg = './images/tb_icon.png'
        self.bgcolor = np.array([243,237,218,256])/256
        self.fgcolor_blue = np.array([81,101,115,256])/256 # gunmetal
        self.fgcolor = np.array([88,88,88,256])/256 # kivy default grey
        # note that Button background color can do tint as well as shade, although this
        # is not documented. in other words, the rgb values
        # can be > 1 as well as < 1. to get an exact button color without using the 
        # background_normal='' hack which eliminates the button altogether, simply 
        # divide out the ratio of the desired color to the default kivy button background color (88,88,88)
        self.tintcolor = self.fgcolor_blue / self.fgcolor # tint grey to gunmetal
        self.wltstate = 'W' # analysis scenario win loss or tie
        self.pressed = ListProperty([0,0]) # callback binding property for radio button
        Window.clearcolor = self.bgcolor
        Log = autoclass('java.util.logging.Logger')
        self.logger = Log.getLogger(type(self).__name__)
        self.bsize = (int(Window.size[1]/50),int(Window.size[1]/50))

        # grid layout for tabular results
        self.tlayout = BoxLayout(orientation='vertical',ids={'name':'tabular'})
        tlayout_title = GridLayout(cols=2,rows=1,size_hint_x=0.96,size_hint_y=0.2,pos_hint={'x':0.02,'y':1}) 
        tlayout_title.bgcolor1 = [ 0.7,0.7,0.7,1]
        tlayout_title.bgcolor2 = self.bgcolor
        tlayout_title.add_widget(BgLabel(text='team X GA',fontfrac=0.4,max=False,color=self.fgcolor,bgcolor=tlayout_title.bgcolor2))
        tlayout_title.add_widget(BgLabel(text='team X GF-GA',fontfrac=0.4,max=False,color=self.fgcolor,bgcolor=tlayout_title.bgcolor2))
        self.tlayout.add_widget(tlayout_title)
        self.tlayout_table = GridLayout(cols=2,rows=10,size_hint_x=0.96,pos_hint={'x':0.02,'y':0}) 
        self.tlayout_table.bgcolor1 = [ 0.7,0.7,0.7,1]
        self.tlayout_table.bgcolor2 = self.bgcolor
        # this binding is needed to override the pos=0,0 hardcoded in scrollview.py
        if True:
            self.tlayout_table.pos = [1,1] # first make a dummy value, so the change to [0,0] is pickedup
            self.tlayout_table.bind(pos=self.set_pos)
        self.slayout = MyScrollView(self.tlayout_table,pos_hint={'x':0.00,'y':0}, \
            do_scroll_y=True,do_scroll_x=False,bar_width=10,size_hint_y=None, \
                bar_color = [.3,.3,.3,.9],bar_inactive_color=[0.3,0.3,0.3,.9],scroll_type=['content','bars'])
        self.slayout.size_hint_x = 1
        self.tlayout.add_widget(self.slayout)

        # radio button for team X WLT scenario
        wltbox = BgBoxLayout(orientation='vertical',bgcolor = self.fgcolor)
        wltlabelbox = BoxLayout(orientation='horizontal')
        wltlabelbox.add_widget(BgLabel(text='W',color=self.fgcolor,bgcolor=self.bgcolor))
        wltlabelbox.add_widget(BgLabel(text='L', color=self.fgcolor,bgcolor=self.bgcolor))
        wltlabelbox.add_widget(BgLabel(text='T',color=self.fgcolor,bgcolor=self.bgcolor))
        # note size_hint for row of items. x hint along the row is a relative amount in arb units
        # y hint is still a percentage of the layout object. this makes it useless to get a square
        # size for the widget using size_hints, must use absolute sizes.
        # but then this is the same problem, can't set the pos hint for absolute sizes because it's a 
        # bottom left specification, without knowing the widget size after layout
        # tried putting in sub boxlayouts but it doesn't solve the problem, still end up with a hardcoded guess
        # for size_hint, and the repetitive code is clunky.
        # so since that's equally useless, revert back to relative widget widths. in the radio button
        # context, having the touch area be wider than the visible button probably isn't a big problem.
        self.choicebox = BoxLayout(orientation='horizontal')
        self.check = {}
        for c in 'WLT':
            self.check[c] = MyCheckBox(name=c,group='WLT', size_hint = (10,1), pos_hint={'x':0.5,'y':0}, \
                color=[1, 1, 1],active=False, allow_no_selection=True)
            self.choicebox.add_widget(self.check[c])
        wltbox.add_widget(self.choicebox)

        # grid layout for data entry
        glayout = GridLayout(cols=4,rows=4)
        glayout.add_widget(BgLabel(bgcolor=self.bgcolor))
        glayout.add_widget(BgLabel(bgcolor=self.bgcolor,color=self.fgcolor,text='GF'))
        glayout.add_widget(BgLabel(bgcolor=self.bgcolor,color=self.fgcolor,text='GA'))
        glayout.add_widget(BgLabel(bgcolor=self.bgcolor))
        glayout.add_widget(BgLabel(text='team A',color=self.fgcolor,bgcolor=self.bgcolor))
        self.tinput_A_gf = NumericInput(id='A_gf')
        self.tinput_A_ga = NumericInput(id='A_ga')
        self.tinput_X_gf = NumericInput(id='X_gf')
        self.tinput_X_ga = NumericInput(id='X_ga')
        glayout.add_widget(self.tinput_A_gf)
        glayout.add_widget(self.tinput_A_ga)
        glayout.add_widget(BgLabel(text='3 GP',color=self.fgcolor,bgcolor=self.bgcolor))
        glayout.add_widget(BgLabel(text='team X',color=self.fgcolor,bgcolor=self.bgcolor))
        glayout.add_widget(self.tinput_X_gf)
        glayout.add_widget(self.tinput_X_ga)
        glayout.add_widget(BgLabel(text='2 GP',color=self.fgcolor,bgcolor=self.bgcolor))
        for g in range(4): # dummy for spacing
            glayout.add_widget(BgLabel(bgcolor=self.bgcolor))
       
        # layout for top part of screen
        bg1 = BoxLayout(orientation='vertical')
        titl = FloatLayout()
        menuicon = './images/menu_icon_64_grey.png'
        menuicontouch = './images/menutouch_icon_64.png'
        self.titlemenu = ImageButton2(size_hint=(0.1,None),pos_hint={'x':0.9,'y':.55},\
            background_normal=menuicon,background_down=menuicontouch,ids={'name':'menu'})
        titlebanner = BgLabel(text='Round Robin\nTie Breaker App',color=self.fgcolor,\
            fontfrac = 0.4,bgcolor=self.bgcolor,pos_hint={'center_x':0.5,'center_y':0.5})
        titl.add_widget(titlebanner)
        titl.add_widget(self.titlemenu)
        bg1.add_widget(titl)

        # main buttons for menu dropdowns
        mlayout = GridLayout(rows=2,cols=3,size_hint_x=0.96,pos_hint={'x':0.02,'y':0})
        self.mbkeys = ['formula','scenario','output']
        self.mb = Button(text=self.mbkeys[0],color=self.bgcolor)
        self.mb2 = Button(text=self.mbkeys[2],color=self.bgcolor)
        self.mlist = {self.mbkeys[0]:['GF/(GF+GA)'],self.mbkeys[1]:['W','L','T'],self.mbkeys[2]:['matrix','bar','tabular']}
        mlayout.add_widget(BgLabel(text=self.mbkeys[0],color=self.fgcolor,bgcolor=self.bgcolor))
        mlayout.add_widget(wltlabelbox)
        mlayout.add_widget(BgLabel(text=self.mbkeys[2],color=self.fgcolor,bgcolor=self.bgcolor))
        mlayout.add_widget(self.mb)
        mlayout.add_widget(wltbox)
        mlayout.add_widget(self.mb2)
        bg1.add_widget(mlayout)

        # layout for top half of screen
        bg = BoxLayout(orientation='vertical')
        bg.add_widget(bg1)
        bg.add_widget(glayout)

        # float layout for graphical output.
        self.fl = FloatLayout()
        # in order to get a correct size for a scrollable table, have to bind to the parent of the scrollview
        # in order to get the size of the parent adn be able to apply it to the scrollview, but also the 
        # row height of the scroll content. seems awkward.
        self.fl.bind(height=self.set_height)

        # overall layout for screen
        self.b = BoxLayout(orientation='vertical')
        self.b.add_widget( bg )
        self.b.add_widget(self.fl)

    # tabular layout update                         
    def do_tlayout(self,gdata,fg=False):

        if self.tlayout_table.rows > 1:
            children = [c for c in self.tlayout_table.children] 
            if len(children) > 0:
                # column label widgets are at the end of list by kivy convention
                for c in children:
                    self.tlayout_table.remove_widget(c)
        self.tlayout_table.rows = int(len(gdata)/2) + 0
        nwidgets = len(gdata)
        # widgets children list order is in reverse, both top/bottom
        # and left/right for columns. gdata was assembled in reverse as
        # well, but temporarily reverse here to align with range(nwidgets)
        gdata.reverse()
        for t in range(nwidgets):
            # left column, even t
            if (int(t/2))*2 == t:
                self.tlayout_table.add_widget(BgLabel(fontfrac=0.6,color=[0,0,0,1],\
                    bgcolor=self.tlayout_table.bgcolor1,square=False),index=0)
            else:
                if t<nwidgets and 'T' in gdata[t]:
                    gdata[t] = gdata[t].replace('T','')
                    self.tlayout_table.add_widget(BgLabel(fontfrac=0.6,color=[0,0,0,1],bgcolor = self.tlayout_table.bgcolor1,\
                        sqcolor=self.newcolors[2,:],square=True),index=0)
                elif t<nwidgets and 'x' in gdata[t]:
                    gdata[t] = gdata[t].replace('x','')
                    self.tlayout_table.add_widget(BgLabel(fontfrac=0.6,color=[0,0,0,1],bgcolor = self.tlayout_table.bgcolor1,\
                        sqcolor=self.newcolors[0,:],square=True),index=0)
                else:
                    self.tlayout_table.add_widget(BgLabel(fontfrac=0.6,color=[0,0,0,1],bgcolor = self.tlayout_table.bgcolor1,\
                        sqcolor=self.newcolors[1,:],square=True),index=0)

        gdata.reverse()
        for g in range(nwidgets):
            setattr(self.tlayout_table.children[g],'text',gdata[g])
        if nwidgets <= 8:
            self.tlayout_table.rows = 4 # hard-coded arb min
            for t in range(8-nwidgets): # dummy row for spacing
                self.tlayout_table.add_widget(BgLabel(bgcolor=self.tlayout_table.bgcolor2))
            if self.tlayout_table.parent:
                self.tlayout_table.parent.remove_widget(self.tlayout_table)
            if self.slayout:
                self.tlayout.remove_widget(self.slayout) # hard-coded
            self.tlayout.add_widget(self.tlayout_table)
        else:
            # scrollable list
            if self.tlayout_table.parent:
                self.tlayout_table.parent.remove_widget(self.tlayout_table)
            if self.slayout:
                self.tlayout.remove_widget(self.slayout) # hard-coded
            self.slayout.set_table(self.tlayout_table)
            self.tlayout.add_widget(self.slayout)
        return

    def add_plot(self,hf):
        if isinstance(hf,Exception):
            self.fl.add_widget(Label(text='{}, {}'.format(type(hf).__name__,str(hf))))
            return
        # for bar plot, y-axis is variable length, and hence overall plot is of variable 
        # height. because layout hasn't happened yet, kivyagg object is
        # still at default size 100,100. later during layout, it gets the size of the parent floating layout 
        # instead of the size of its child, the matplotlib fig. this behaviour
        # seems to preclude the possibility of using a kivyagg in a floating layout.
        if self.mb2.text == 'bar':
            self.plot = AspectKivyAgg(hf)
            # recall that plot axes centering is done by shifting the position of the kivyagg object
            self.plot.pos[0] -= hf.xpos # this adjustment to centre the plot axes for tall aspect ratio
        elif self.mb2.text == 'matrix':
            self.plot = AspectKivyAgg(hf)
            self.plot.pos[0] -= hf.xpos # this adjustment to centre the plot axes for tall aspect ratio
            # note. setting this size forces a layout in non-interactive test mode, but
            # isn't needed in interactive mode.
            self.plot.size = (Window.size[0],Window.size[0])
        elif self.mb2.text == 'tabular':
            self.plot = hf
        self.fl.add_widget(self.plot)

    def remove_plot(self):
        # record height of last plot
        self.floatsize = self.fl.size
        if self.plot is not None:
            self.fl.remove_widget(self.plot)
        # if there is already a matplotlib plot, use close() as well
        # removing widget alone isn't sufficient
        # since the switch to the kivygarden_matplotlib kludge for including
        # kivy garden in buildozer, plot type seems to be either of two cases now
        if isinstance(self.plot,AspectKivyAgg) or \
            isinstance(self.plot,FigureCanvasKivyAgg):
            plt.close(self.plot.figure)

    # scrollview does not process size_hint. have to trap the size of the
    # float layout parent during do_layout() with a callback like this, and assign the 
    # size_hint percentage 80% here.
    # the documentation indicates the size of the scrollview content could be set
    # in absolute terms like this: gridlayout.bind(minimum_height=layout.setter('height'))
    # note that setting the height of the content by this or any other means, doesn't
    # dictate the height of the scrollview. that must be set independently. 
    # further, the height of the content if it is a grid layout should allow for an integer
    # number of rows. this can be set by the row defaultheight of a
    # gridlayout. 
    def set_height(self,*args):
        self.logger.info('scrollable gridlayout height = {}'.format(self.tlayout_table.minimum_height))
        self.tlayout_table.row_default_height = self.fl.height * 0.8 / 4
        self.tlayout_table.pos = self.fl.width * 0.02,0
        self.slayout.height = self.fl.height * 0.8
        self.slayout.bar_width = int(self.fl.width * 0.02)
        return
    # scrollview processes size_hint_x for the content widget in the non-scroll direction, but not 
    # pos in either absolute or hint. instead, pos of the content widget is reset to [0,0] every time.
    # this is seen on line 1138 scrollview.py. seems like a bug.
    # this callback is bound to the position of the content widget, so it can override the [0,0]
    # position that is applied.
    # in some cases am seeing a too many iterations warning with this binding, so it's adding some
    # overhead. 
    def set_pos(self,*args):
        # self.logger.info('scrollable gridlayout pos = {}'.format(args[1]))
        self.tlayout_table.pos = self.fl.width * 0.02,0
        return

    # toggle radio buttons for 2d versus 1d plots
    def set_nobuttons(self,state,tf=False):
        for c in 'WLT':
            self.check[c].allow_no_selection = tf
        if tf is True:
            self.check[self.wltstate].active = False
        else:
            self.check[self.wltstate].active = True

        return

    # tidy up help screen if any
    def remove_help(self):
        if self.mb2.text in ['help','about']:
            setattr(self.mb2,'text','matrix')
        if self.fl.children:
            if isinstance(self.fl.children[0],BoxLayout):
                if self.fl.children[0].ids['name'] == 'help':
                    self.fl.remove_widget(self.fl.children[0])
