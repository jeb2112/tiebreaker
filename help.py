from audioop import add
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
import numpy as np
from kivy.core.window import Window
from kivy.input.providers.mouse import MouseMotionEvent

from jnius import autoclass
from layout import WrappedBgLabel,BgLabel

# keeps button icon fixed aspect using Image.keep_ratio, allow_stretch attributes
class ImageButton(ButtonBehavior,Image):
    def __init__(self,background_normal=None,background_down=None,**kwargs):
        super(ImageButton,self).__init__(**kwargs)
        self.border = (0,0,0,0)
        if background_normal is None:
            self.background_normal = self.source
        else:
            self.background_normal = background_normal
        self.background_down=background_down
        return

# alternate button icon with fixed aspect. when used with size_hint,the
# above class has two possible result sizes depending on which dimension
# of the parent layout is larger. copying the size in a callback like this
# allows to specify the size_hint in one governing dimension, so the size
# of the button icon is constant for both aspect ratios of the parent
# layout
class ImageButton2(Button):
    def __init__(self,**kwargs):
        super(ImageButton2,self).__init__(**kwargs)
        self.border = (0,0,0,0)

    def on_size(self,*args):
        yhint = int(bool(self.size_hint_y))
        self.size[1-yhint] = self.size[yhint]

class MyFloatLayout(FloatLayout):
    def __init__(self,**kwargs):
        super(MyFloatLayout,self).__init__(**kwargs)
    def on_size(self,*args):
        return

class Help():
    def __init__(self):
        self.newcolors = np.array([[184/256,29/256,19/256,1],[50/256,164/256,49/256,1],[239/256,183/256,0,1]])
        self.titlimg = './images/tb_icon.png'
        self.bgcolor = [243/256,237/256,218/256,1]
        self.fgcolor = [81/256,101/256,115/256,1] # gunmetal
        self.fgcolor = [88/256,88/256,88/256,1] # taupe
        self.category = 'about'
        self.mlist = ['help','about']
        self.idx = 1

        self.panels = {}
        self.panels['about'] = ['About']
        self.panels['about'].append('1. TieBreaker app analyzes a set of games in the preliminary round-robin of a hockey tournament.')
        self.panels['about'].append( ('2. Most typically, there could be four teams in the round-robin, three games played by each team, '
                            'and two teams qualifying for further play.') )
        self.panels['about'].append( ('3. In the event of a tie for 2nd and 3rd place in the round robin standings, a tie-breaker formula ' 
                            'is used to determine the qualifier.') )
        self.panels['about'].append( ('4. Frequently, the formula is a fraction or ratio deriving from goals tallied, both for and against.') )
        self.panels['about'].append( ('5. This assessment is easily made after the final game of the round robin has been played when all the '
                            'scoring is known.') )
        self.panels['about'].append( ('6. However, for fans of the 3rd and final game of one or both of the teams in question, ' 
                            'it may be of interest to know the several goal-scoring scenarios that lead to qualification, [i]before[/i] '
                            'or [i]during[/i] that final 3rd game.') )
        self.panels['about'].append( ('7. TieBreaker app displays those goal-scoring scenarios.') )

        self.panels['help'] = ['Instructions']
        self.panels['help'].append( '1. Team A has completed all 3 games of the round robin, while Team X has completed 2 games. ')
        self.panels['help'].append( ('2. Enter the total goals (for and against) for both teams, then press return.'))
        self.panels['help'].append( ('3. The goal scoring scenarios in the 3rd and final game required for Team X to qualify '
                                    'are plotted as a matrix.') )
        self.panels['help'].append( ('4. Any green square shows a goals-against,goals-for pair (GA,GF) that qualifies team X for further play.'))
        self.panels['help'].append( ('5. The yellow squares (if any) denote (GA,GF) pairs that fail to break the tie, according to the '
                                    'current formula.'))
        self.panels['help'].append( ('6. Note that matrix output shows both a Win and a Loss scenario for team X in game 3, whereas only one '
                                     'or the other of those outcomes actually leads to a Tie with team A '
                                     'in the round robin standings.') )
        self.panels['help'].append( ('7. To select alternate outputs showing the known Win/Loss scenario, select \'bar\' or \'tabular\''
                                    ' from the Output menu and use the \'W\' and \'L\' radio buttons.') )

        # layout
        buttonLicon = './images/arrow_iconL_64_grey.png'
        buttonRicon = './images/arrow_iconR_64_grey.png'
        buttonLicon_touch = './images/arrow_iconLtouch_64.png'
        buttonRicon_touch = './images/arrow_iconRtouch_64.png'
        self.hlayout = BoxLayout(orientation='vertical',size_hint_y=1,ids={'name':'help'})
        self.hlayout_title = WrappedBgLabel(text=self.panels[self.category][0],fontfrac=0.4,color=self.bgcolor,bgcolor=self.fgcolor,\
            size_hint=(0.95,0.12),pos_hint={'x':0.025},valign='middle',padding_x=10)
        self.hlayout.add_widget(self.hlayout_title)
        self.hlayout_panel = MyFloatLayout()
        self.ilabel = WrappedBgLabel(text='',fontfrac=0.08,max=False,color=self.fgcolor,bgcolor=self.bgcolor,\
                                valign='top',size_hint_x=0.9,pos_hint={'x':0.05,'top':1},markup=True)
        self.hlayout_panel.add_widget(self.ilabel)
        self.buttonL = ImageButton2(size_hint=(0.1,None),pos_hint={'x':0.05,'y':.05},\
            background_normal=buttonLicon,background_down=buttonLicon_touch,ids={'name':'L'})
        self.buttonR = ImageButton2(size_hint=(0.1,None),pos_hint={'x':0.85,'y':.05},\
            background_normal=buttonRicon,background_down=buttonRicon_touch,ids={'name':'R'})
        self.buttonL.bind(on_release = self.on_release)
        self.buttonR.bind(on_release = self.on_release)
        self.hlayout_panel.add_widget(self.buttonR)
        self.hlayout.add_widget(self.hlayout_panel)
        self.play_info()

    # updates the info screen and forward/back buttons
    def on_release(self,instance,*args):
        if instance.ids['name'] == 'L':
            self.idx -= 1
            if self.idx == len(self.panels[self.category])-2:
                self.hlayout_panel.add_widget(self.buttonR)
            if self.idx == 1:
                self.hlayout_panel.remove_widget(self.buttonL)
        elif instance.ids['name'] == 'R':
            self.idx += 1
            if self.idx == 2:
                self.hlayout_panel.add_widget(self.buttonL)
            if self.idx == len(self.panels[self.category])-1:
                self.hlayout_panel.remove_widget(self.buttonR)
        self.play_info()
        return

    def play_info(self):
        self.ilabel.text = self.panels[self.category][self.idx]
        self.ilabel._label.refresh()

    def set_category(self,cat):
        self.category=cat
        self.hlayout_title.text = self.panels[self.category][0]
        self.idx=1
        if not self.buttonR.parent:
            self.hlayout_panel.add_widget(self.buttonR)
        if self.buttonL.parent:
            self.hlayout_panel.remove_widget(self.buttonL)
        self.play_info()