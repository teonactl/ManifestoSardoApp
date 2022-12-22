from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.recycleview import RecycleView
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.window import Window
import kivy
import scraper
from datetime import datetime, date
from kivy.clock import  mainthread, Clock
from kivymd.toast import toast
from kivymd.uix.snackbar import Snackbar

from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField

from kivy.core.text import LabelBase
from kivymd.uix.dialog import MDDialog
from kivy import platform

import requests
import threading
import re
from utils import *
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import webbrowser
if platform == 'android':
    from jnius import autoclass   
    
LabelBase.register(name='Roboto',fn_regular='src/roboto-slab/RobotoSlab-Regular.ttf',fn_italic="src/roboto-slab/RobotoSlab-Thin.ttf", fn_bold = "src/roboto-slab/RobotoSlab-Bold.ttf")

@mainthread
def m_toast(text):
    toast(text)
Builder.load_file("browse_scr.kv")
Builder.load_file("article_scr.kv")
Builder.load_file("search_scr.kv")
Builder.load_file("redazione.kv")
Builder.load_file("newsletter.kv")
Builder.load_file("norme.kv")
Builder.load_file("associazione.kv")
Builder.load_file("partners.kv")

if kivy.platform == "linux":
    Window.size = (450, 740)
    #Window.size = (740,450)



class MainScreen(MDScreen):
    pass
class MyCard(MDCard):
    link = StringProperty()
    img = StringProperty()
    title = StringProperty()
    cat = StringProperty()
    auth = StringProperty()
    date = StringProperty()
    text = StringProperty()
class SrCard(MDCard):
    link = StringProperty()
    img = StringProperty()
    title = StringProperty()
    cat = StringProperty()
    auth = StringProperty()
    date = StringProperty()
    text = StringProperty()



class RecycleViewer(RecycleView):
    def __init__(self, **kwargs):
        super(RecycleViewer, self).__init__(**kwargs)
        self.page_index = 1
        data = scraper.timeline_scraper(str(self.page_index))
        data.sort(key=lambda r: r["datetime"], reverse=True)
        self.data = data 
        self.lastrun =  datetime.now()


    def add_page(self):
        m_toast("Caricando articoli precedenti...")
        self.page_index += 1
        new_data = scraper.timeline_scraper(str(self.page_index))
        old_len = len(self.data)
        self.data =self.data + new_data
        self.data.sort(key=lambda r: r["datetime"], reverse=True)
        #print("Scraping ", str(self.page_index))
        #scroll_index =  1- (old_len/ (len(self.data)+old_len)) 
        scroll_index = 1- (old_len / (old_len+ len(new_data)) )
        #print("Scrolling to ", scroll_index)
        self.do_scroll_y = True

        self.scroll_y = scroll_index

    def on_scroll_move(self, *args) :
        #print("stop scrolling at ",self.scroll_y)
        if kivy.platform == "linux":
            add_condition = self.scroll_y < 0
        else:
            add_condition = self.scroll_y < 0.001
        if add_condition :
            ct = datetime.now()
            if (ct -self.lastrun).seconds >  5:
                self.do_scroll_y = False
                x = threading.Thread(target=self.add_page)
                x.start()               
                self.lastrun = ct
        return super().on_scroll_move(*args)

class SearchViewer(RecycleView):
    def __init__(self, **kwargs):
        super(SearchViewer, self).__init__(**kwargs)
        self.page_index = 1
        data = scraper.search_scraper(query = MDApp.get_running_app().a_query,page = str(self.page_index))
        #data.sort(key=lambda r: r["datetime"], reverse=True)
        self.data = data 
        self.lastrun =  datetime.now()


    def add_page(self):
        m_toast("Caricando risultati precedenti...")
        self.page_index += 1
        new_data = scraper.search_scraper(query = MDApp.get_running_app().a_query,page = str(self.page_index))
        old_len = len(self.data)
        self.data =self.data + new_data 
        scroll_index = 1- (old_len / (old_len+ len(new_data)) )
        self.scroll_y = scroll_index

    def on_scroll_move(self, *args) :
        #print("stop scrolling at ",self.scroll_y)
        if kivy.platform == "linux":
            add_condition = self.scroll_y < 0
        else:
            add_condition = self.scroll_y < 0.001
        if add_condition :
            ct = datetime.now()
            if (ct -self.lastrun).seconds >  5:
                x = threading.Thread(target=self.add_page)
                x.start()               
                self.lastrun = ct
        return super().on_scroll_move(*args)

class Comment(MDCard):
    auth = StringProperty()
    text = StringProperty()

class CommentBox(MDCard):
    pass
class Info(MDBoxLayout):
    text = StringProperty(info_string)

class ManifestoApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Amber"
        self.prev_scr = "bro_scr"
        self.c_dialog = None
        self.secret = {}
        self.a_query = ""
        self.redstr = redstr
        self.normestr = normestr
        self.associazionestr = associazionestr
        self.wb = webbrowser.open
        self.i_dialog = None
        Window.bind(on_keyboard=self.key_input)
        return MainScreen()

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            self.go_back()
            return True  # override the default behaviour
        else:           # the key now does nothing
            return False

    def share(self, title, text):

        if platform == 'android':
            

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String')
            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.putExtra(Intent.EXTRA_TEXT, String('{}'.format(text)))
            intent.setType('text/plain')
            chooser = Intent.createChooser(intent, String(title))
            PythonActivity.mActivity.startActivity(chooser)
        else :
            toast("Non implementato...")


    def info(self):
        if not self.i_dialog:
            self.i_dialog = MDDialog(
                title="Informazioni",
                type="custom",
                size= self.root.size,
                content_cls=Info(),
                buttons=[],
            )
        self.i_dialog.open()

    def set_toolbar_title_halign(self, *args):
        self.root.ids.topbar.ids.label_title.halign = "center"
    def on_start(self):
        Clock.schedule_once(self.set_toolbar_title_halign)
        self.root.ids.topbar.ids.label_title.font_name = "Roboto"
        self.root.ids.topbar.ids.label_title.font_style = "H5"
    def search_prompt(self):
        self.left_action_items = self.root.ids.topbar.left_action_items
        self.right_action_items = self.root.ids.topbar.right_action_items
        self.root.ids.topbar.left_action_items = []
        self.root.ids.topbar.right_action_items = []
        self.root.ids.topbar.title = ""
        boxlayout = MDBoxLayout(id = "headbox", orientation= "horizontal",padding=10)
        search_content = MDTextField(  icon_left='magnify',
                                          mode='round',
                                          #focus = True,
                                          #line_color_normal=(1, 0, 1, 1),
                                          #line_color_focus=(0, 0, 1, 1),
                                          text_color_focus=self.theme_cls.text_color,
                                          text_color_normal=self.theme_cls.text_color[0:3] + [0.7],
                                          hint_text='Cerca...',
                                          on_text_validate = self.research_contents
                                          )
        back_icon = MDIconButton( icon = "arrow-left",on_release=self.go_back_src )
        boxlayout.add_widget(search_content)
        boxlayout.add_widget(back_icon)
        self.root.ids.topbar.add_widget(boxlayout)

    def research_contents(self,b):
        self.root.ids.topbar.remove_widget(self.root.ids.topbar.children[0])
        self.root.ids.topbar.left_action_items = self.left_action_items
        self.root.ids.topbar.right_action_items = self.right_action_items
        l = scraper.search_scraper(query=str(b.text), page=1)
        self.a_query = str(b.text)

        self.root.ids.src_scr.children[0].data = l
        self.root.ids.topbar.title = b.text
        self.root.ids.topbar.ids.label_title.halign = "center"
        self.root.ids.screen_manager.current = "src_scr"
        self.prev_scr = "src_scr"

    def go_back_src(self, *args):
        #print("removing first of",self.root.ids.topbar.children)
        self.root.ids.topbar.remove_widget(self.root.ids.topbar.children[0])
        self.root.ids.topbar.left_action_items = self.left_action_items
        self.root.ids.topbar.right_action_items = self.right_action_items
        self.root.ids.screen_manager.current = self.prev_scr
        self.root.ids.topbar.title = self.a_query
        self.root.ids.topbar.ids.label_title.halign = "center"

    def clean_tbar(self):
        #print("create_res_tbar")
        self.left_action_items = self.root.ids.topbar.left_action_items
        self.right_action_items = self.root.ids.topbar.right_action_items
        #print(self.root.ids.topbar.ids)
        if len(self.root.ids.topbar.children)>2:
            #print(self.root.ids.topbar.children[0].children)
            #print(self.root.ids.topbar.children[1].children)
            #print(self.root.ids.topbar.children[2].children)
            self.srcwidg = self.root.ids.topbar.children[0]
            self.root.ids.topbar.remove_widget(self.srcwidg)


    def go_back(self):
        print("go back-->", self.prev_scr)
        if self.root.ids.screen_manager.current == self.prev_scr:
            self.root.ids.screen_manager.current = "bro_scr"  
            self.prev_scr =   "bro_scr"
            return
        self.root.ids.screen_manager.current = self.prev_scr
       
    def open_article(self,link,title):
        #print("opening-->", link)
        aut, text, comments , secret, cat, img = scraper.article_scraper(url=link)
        #print(text)
        self.secret = secret
        text = "\n\n".join(text.split("\n\n")[2:])
        #print(text)

        text = text.replace("**[","[b]").replace("]**","[/b]")
        text = re.sub(r"\*\*(.*?)\*\*",r"[b]\1[/b]", text)
        text = re.sub(r"\\\*",r"[sup]#[/sup]", text)
        text = re.sub(r"\*(.*?)\*",r"[i]\1[/i]", text)
        text = re.sub(r"(?=Questo)(.*?)(?<=sito)","", text,flags=re.S)
        self.root.ids.art_scr.ids.title_lb.text  = f"[b][color=c77005]{title.strip()}[/color][/b]"
        self.root.ids.art_scr.ids.cat_aut_lb.text  = f"[b]{aut.strip()}[/b]"
        self.root.ids.art_scr.ids.cat_aut_lb.secondary_text  = cat
        self.root.ids.art_scr.ids.image.source  = img
        self.root.ids.art_scr.ids.text_lb.text  =text
        self.root.ids.art_scr.ids.comment_grid.clear_widgets()

        if not len(comments):
            self.root.ids.screen_manager.current = "art_scr"
            #self.prev_scr = "art_scr"

            return
        for c in comments:
            com = Comment(auth=c["auth"], text=c["text"])
            #print("adding ", c["auth"])
            self.root.ids.art_scr.ids.comment_grid.add_widget(com)
        self.root.ids.screen_manager.current = "art_scr"
        #self.prev_scr = "art_scr"

    def show_comment_dialog(self):
        if not self.c_dialog:
            self.c_dialog = MDDialog(
                type="custom",
                content_cls=CommentBox(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Error",
                        #text_color=self.theme_cls.primary_color,
                        on_press = self.dialog_dismiss
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Primary",
                        #text_color=self.theme_cls.primary_color,
                        on_press= self.send_comment
                    ),
                ],
            )

        self.c_dialog.open()

    def send_comment(self, b):
        name =b.parent.parent.parent.children[2].children[0].ids.nom.text
        email =b.parent.parent.parent.children[2].children[0].ids.ema.text
        text =b.parent.parent.parent.children[2].children[0].ids.com.text
        if not len(email) or not len(name):
            return toast("Compila nome ed email per inviare il commento!")
        if len(text) >= 1500:
            return toast("Il commento può contenere al massimo 1500 caratteri!")
        #print("Sending Comment!->")
        #print(name, email, text)
        url =  "https://www.manifestosardo.org/wp-comments-post.php" # "http://192.168.1.5:5000/"
        myobj = {                
                "author":"+".join(name.split(" ")),
                "email": email.strip(),
                "url": "",
                "comment": "+".join(text.split(" ")),
                "submit": "Invia+commento",
                "comment_post_ID": self.secret["comment_post_ID"],
                "leftChars": 1500 - len(text),
                "wantispam_t": self.secret["wantispam_t"],
                "wantispam_a": date.today().year,
                "wantispam_q": date.today().year,
                "wantispam_e_email_url_website": ""

            }

        try:

            x = requests.post(url, data = myobj)
            if x.status_code == 200:
                toast("Commento inviato...\nIn Attesa di moderazione!")
                b.parent.parent.parent.children[2].children[0].ids.nom.text = ""
                b.parent.parent.parent.children[2].children[0].ids.ema.text = ""
                b.parent.parent.parent.children[2].children[0].ids.com.text = ""
                self.c_dialog.dismiss()
            else :
                toast(f"Errore [{str(x.status_code)}]: Commento non inviato!")
        except Exception as e:
            print("Exception: ",e)
            toast("Verifica la connessione ad internet e riprova!")
                 

        
    def dialog_dismiss(self, b):
        if self.c_dialog : 
            self.c_dialog.dismiss()

    def subscribe(self,email):
        #print(email)
        url =   "https://www.manifestosardo.org/newsletter/" #"http://192.168.1.5:5000/" #
        myobj = {                
            "EMAIL"  :email.strip(),
            "_mc4wp_honeypot" :"",
            "_mc4wp_timestamp"   : "1671710683",
            "_mc4wp_form_id" : "23141",
            "_mc4wp_form_element_id":  "mc4wp-form-1",

            }   

        try:

            x = requests.post(url, data = myobj)
            #print("resp--->",x.status_code)
            #print(x.text)
            if x.status_code == 200:
                toast("Mail in attesa di conferma...\nControlla la tua casella di posta!")
            else :
                toast(f"Errore [{str(x.status_code)}]")
        except Exception as e:
            print("Exception: ",e)
            toast("Verifica la connessione ad internet e riprova!")
                 


ManifestoApp().run()
"""
EMAIL   "teonactl@hotmail.it"
_mc4wp_honeypot ""
_mc4wp_timestamp    "1671710683"
_mc4wp_form_id  "23141"
_mc4wp_form_element_id  "mc4wp-form-1"
"""
"""
Successfull post:

{
    "author": "Nome+Vero",
    "email": "email@esempio.com",
    "url": "",
    "comment": "Testo+di+prova",
    "submit": "Invia+commento",
    "comment_post_ID": "6198",
    "leftChars": "1486",
    "wantispam_t": "1671118343",
    "wantispam_a": "2022",
    "wantispam_q": "2022",
    "wantispam_e_email_url_website": ""
}

"""
