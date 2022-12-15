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
from kivy.clock import  mainthread
from kivymd.toast import toast
from kivymd.uix.snackbar import Snackbar

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

import requests
import threading
import re
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


@mainthread
def m_toast(text):
    toast(text)
Builder.load_file("browse_scr.kv")
Builder.load_file("article_scr.kv")
Builder.load_file("screen3.kv")

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
class ManifestoApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Amber"
        self.prev_scr = "bro_scr"
        self.c_dialog = None
        self.secret = {}
        return MainScreen()

    def go_back(self):
        self.root.ids.screen_manager.current = self.prev_scr

    def open_article(self,link,title, cat, img):
        print("opening-->", link)
        text, comments , secret= scraper.article_scraper(url=link)
        self.secret = secret
        text = text.replace("**[","[b]").replace("]**","[/b]")
        text = re.sub(r"(\s+)\*", r"\1[i]", text)
        text = re.sub(r"\*(\s+)", r"[/i]\1", text)
        text = re.sub(r"(\w)\*", r"\1[/i]", text)
        text = re.sub(r"\*(\w)", r"[/i]\1", text)
        text = re.sub(r"(\W)\*", r"\1[/i]", text)
        cl_text = re.sub(r"\*(\W)", r"[/i]\1", text)
        self.root.ids.art_scr.ids.title_lb.text  = f"[b][color=c77005]{title.strip()}[/color][/b]"
        self.root.ids.art_scr.ids.cat_lb.text  = cat
        self.root.ids.art_scr.ids.image.source  = img
        self.root.ids.art_scr.ids.text_lb.text  =cl_text
        if not len(comments):
            self.root.ids.screen_manager.current = "art_scr"
            return
        for c in comments:
            com = Comment(auth=c["auth"], text=c["text"])
            #print("adding ", c["auth"])
            self.root.ids.art_scr.ids.comment_grid.add_widget(com)
        self.root.ids.screen_manager.current = "art_scr"

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
        if len(text) >= 1500:
            return toast("Il commento può contenere al massimo 1500 caratteri!")
        print("Sending Comment!->")
        print(name, email, text)
        url =   "http://192.168.1.5:5000/" #"https://www.manifestosardo.org/wp-comments-post.php"
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

        x = requests.post(url, data = myobj)
        print("resp--->",x.status_code)
        print(x.text)
        if x.status_code == 200:
            toast("Commento inviato...\nIn Attesa di moderazione!")
            self.c_dialog.dismiss()
        else :
            toast(f"Errore [{str(x.status_code)}]: Commento non inviato!")
             

        
    def dialog_dismiss(self, b):
        if self.c_dialog : 
            self.c_dialog.dismiss()


  

ManifestoApp().run()


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
