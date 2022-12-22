import requests
import bs4
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import datetime
from markdownify import MarkdownConverter
import re

def md(soup, **options):
    return MarkdownConverter(**options).convert_soup(soup)


def article_scraper( a_name=False, url = False):
	if a_name : 
		page = requests.get("https://www.manifestosardo.org/"+a_name)
	elif url:
		page = requests.get(url)

	soup = BeautifulSoup(page.content, "html.parser")
	form = soup.find("form")
	articlehtml = soup.find("div", class_="post")
	com_ol= soup.find("ol", class_="commentlist")
	comments = []

	if com_ol:
		coms = com_ol.find_all("li")
		for c in coms:
			#print("comment text-->", c.find_all("p"))
			co = {}
			co["auth"] = c.find("cite").text
			co["text"] = "\n\n".join([x.text for x in  c.find_all("p")])
			comments.append(co)
	entry =  articlehtml.find("div", class_="entry")
	article = md(entry,strip=['a','img']) 
	secret = {}
	sec_list = ["submit","comment_post_ID","wantispam_t"]
	inputs = [ i for i in form.find_all("input") if i["name"] in  sec_list]
	for i in inputs:
		secret[sec_list.pop(0)] = "+".join(i["value"].split(" "))
	catcont = articlehtml.find("div",class_="postmetadata alt")
	cat =catcont.find("a",rel="category tag")
	img = articlehtml.find("img")["src"]
	#print("Article:-> " ,article)

	aut = article.split("\n\n")[1].replace("[", "").replace("]","").replace("**","").replace("#","")
	if len(aut)> 34 or "foto" in aut.lower() or "immagine" in aut.lower():
		aut =article.split("\n\n")[2].replace("[", "").replace("]","").replace("**","").replace("#","")
	#print("Aut->", aut)
	return aut, article, comments , secret, cat.text, img

#article_scraper()
from kivymd.toast import toast



def timeline_scraper(page = ""):
	try:
		page = requests.get("https://www.manifestosardo.org/page/"+page)
	except:
		return toast("Controlla la connessione e riavvia l'App!")
	soup = BeautifulSoup(page.content, "html.parser")
	articlelist = soup.find_all("div", class_="post")
	a_list = []
	for a in articlelist:
		art = {}
		entry = a.find("div", class_= "entry")
		#print(entry)
		#print(a)
		auth = None
		try:
			for p in entry.find_all("p"):
				if p.text.startswith("["):
					 	auth = p.text[1:-1]
				else:
					sp = entry.find("span", style= "color: #c77005;")
					if hasattr( sp, "text" ):
						auth = sp.text 
				if auth == None:
					h5 = entry.find_all("h5")
					#print(h5)
					for sp in h5:
						if hasattr( sp, "text" ):
							auth = sp.text 
						else:
							auth = "Autore Sconosciuto"
		
			tex = entry.find_all(["p","em"])
			#print(tex)
			#print(len(tex))
			if len(tex)>= 1:
				if tex[-1].text.endswith("Continua »"):
					text = tex[-1].text[0:-10]
				else : 
					text = tex[-1].text

			date = a.find("small").text
			dateit = date.replace("Gennaio", "1").replace("Febbraio", "2").replace("Marzo", "3").replace("Aprile","4").replace("Maggio","5").replace("Giugno","6").replace("Luglio","7").replace("Agosto","8").replace("Settembre","9").replace("Ottobre","10").replace("Novembre", "11").replace("Dicembre","12")

			art["date"] = date
			art["datetime"] =datetime.strptime(dateit.strip(), "%d %m %Y")
			art["cat"] = a.find("a", rel="category tag").text
			art["title"] = a.find("a", rel= "bookmark").text
			art["auth"] =  auth
			art["text"] = text+ "..."

			try : 
				img =  entry.find("img")["src"]
				#print(img)
			except :
				#print("Video?")
				#print(art["title"])
				fig = entry.find("figure")
				ifr = fig.find("iframe")
				#print(ifr["src"])
				yt_id = ifr["src"].split("/")[-1].split("?")[0]
				#print(yt_id)
				img= f"https://i.ytimg.com/vi/{yt_id}/maxresdefault.jpg?"

			art["img"] = img


			art["link"]= entry.find("a", class_="more-link")["href"]
		except Exception as e:
			print("article not scraped:", art["title"], e)
			continue

		a_list.append(art)

	#print(a_list)
	#print(len(a_list))

	return a_list

#p = timeline_scraper("300")
#print(p)

def search_scraper(query,page):
	page = str(page)
	query = "+".join(query.split(" "))
	sr_url = "https://www.manifestosardo.org/page/"+page+"/?s="+ query
	print(sr_url)
	page = requests.get(sr_url)
	soup = BeautifulSoup(page.content, "html.parser")
	articlelist = soup.find_all("div", class_="post")
	a_list = []
	for a in articlelist:
		art = {}
		entry = a.find("a", rel= "bookmark")
		d = a.find("small")
		art["title"]= entry.text
		#print(art["title"])
		if re.match(r"Il numero \d", art["title"]):
			#print("match")
			continue
		art["link"] = entry["href"]
		art["date"] = d.text
		dateit = art["date"].strip().replace("Gennaio", "1").replace("Febbraio", "2").replace("Marzo", "3").replace("Aprile","4").replace("Maggio","5").replace("Giugno","6").replace("Luglio","7").replace("Agosto","8").replace("Settembre","9").replace("Ottobre","10").replace("Novembre", "11").replace("Dicembre","12")
		art["datetime"] =datetime.strptime(dateit.strip(), "%d %m %Y")

		#print("title: ",entry.text)
		#print("link: ",entry["href"])
		#print("date: ",d.text)
		a_list.append(art)
	#print(a_list)
	return a_list


#p = search_scraper("prova prova")
