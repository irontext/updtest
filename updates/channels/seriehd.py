# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canale per SerieHD
# ----------------------------------------------------------

import re
import os
import string
import json
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse
    import urllib.parse as urllib
else:
    import urllib                                               
    import urlparse


from platformcode import config
from platformcode import logger
from channels import autoplay
from core import scrapertools
from core import servertools
from core import httptools
from core.item import Item
from core import tmdb

__channel__ = "seriehd"
link = 'https://translate.google.com/website?sl=en&tl=it&u='
host = link + "https://seriehd.email"

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Referer', host]]

unify = config.get_setting('unify')

list_servers = ['default']
list_quality = ['1080p', '720p', '480p', '360p']

def mainlist(item):
    logger.info("[Alfa-PureITA SerieHD] mainlist")
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = [Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Serie TV[COLOR orange] - Novita'[/COLOR]",
                     url=host,
                     extra ="tvshow",
                     fanart=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "popcorn_cinema_P.png"),
                     thumbnail=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "popcorn_cinema_P.png")),
                Item(channel=__channel__,
                     action="categorie",
                     title="[COLOR azure]Serie TV[COLOR orange] - Categorie[/COLOR]",
                     url=host,
                     fanart=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "genres_P.png"),
                     thumbnail=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "genres_P.png")),
                Item(channel=__channel__,
                     action="categorie",
                     title="[COLOR azure]Serie TV[COLOR orange] - Lista A-Z[/COLOR]",
                     url="%s/serie-tv-streaming/" % host,
                     extra='list',
                     fanart=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "a-z_P.png"),
                     thumbnail=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "a-z_P.png")),
                Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Serie TV[COLOR orange] - Italiane[/COLOR]",
                     url="%s/serie-tv-streaming/serie-tv-italiane" % host,
                     extra ="tvshow",
                     fanart=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "tv_series_P.png"),
                     thumbnail=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "tv_series_P.png")),
                Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Serie TV[COLOR orange] - Complete[/COLOR]",
                     url="%s/serie-tv-streaming/serie-complete/" % host,
                     extra ="tvshow",
                     fanart=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "new_tvshows_P.png"),
                     thumbnail=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "new_tvshows_P.png")),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca ...[/COLOR]",
                     fanart=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "search_P.png"),
                     thumbnail=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "search_P.png"))]

    autoplay.show_option(item.channel, itemlist)
    return itemlist

# ========================================================================================================================================================
# NEW
# ========================================================================================================================================================

def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'series':
            item.url = host
            item.page = 1
            itemlist = lista_serie(item)
        if "Successivi" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

# ========================================================================================================================================================
# SEARCH
# ========================================================================================================================================================
	
def search(item, texto):
    logger.info("[Alfa-PureITA SerieHD] search")
    item.url = host + "/?s=" + texto
    try:
        return lista_serie(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ========================================================================================================================================================
# ========================================================================================================================================================
		
def categorie(item):
    logger.info("[Alfa-PureITA SerieHD] categorie")
    itemlist = []

    data = httptools.downloadpage(item.url).data
    
    if 'list' in item.extra:
        blocco = scrapertools.find_single_match(data, '<div class="col-xl-12 imRelative">(.*?)</ul>')
    else:
        blocco = scrapertools.find_single_match(data, '<nav id="navigation"> (.*?)</nav> ')
        
    patron = '<a href="([^"]+)[^>]+>([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("Streaming", "").strip()
        
        if scrapedurl.startswith("/"):
           scrapedurl = host + scrapedurl

        if 'list' in item.extra:
            title = "[COLOR lightsteelblue]SerieTV che iniziano per: [/COLOR]" + scrapedtitle
        else:
            title = "[COLOR lightsteelblue]SerieTV Genere: [/COLOR]" + scrapedtitle          
        
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_serie",
                 title=title,
                 plot=title,
                 url=scrapedurl,
                 contentType="tvshow",
                 fanart=item.thumbnail,
                 thumbnail=item.thumbnail))

    return itemlist

# ========================================================================================================================================================
	
def lista_serie(item):
    logger.info("[Alfa-PureITA SerieHD] lista_serie")
    itemlist = []
    
    data = httptools.downloadpage(item.url).data

    patron = '<a href="([^"]+)">\s*<div class[^>]+>\s*<div[^>]+>\s*<h2>([^<]+)<\/h2>'
    patron += '[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>\s*(?:<img src="([^"]+)"|)'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedimg in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.strip())
        
        if not scrapedimg:
            tipo = 'movie'
            contentSerieName = ''
            show = ''
            thumb = ''
        else:
            tipo = "tvshow"
            contentSerieName = scrapedtitle
            show = scrapedtitle
            thumb = scrapedimg
            
        if "[sub" in scrapedtitle.lower():
            langs = " ([COLOR yellow]SUB ITA[/COLOR])"
            scrapedtitle = re.sub("\[[^$]+", "", scrapedtitle).strip()            
        else:
            langs = ''
        
        scrapedplot = ""
        itemlist.append(item.clone(channel = item.channel,
                                   action = "findvideos" if  'movie' in tipo else 'episodios',
                                   title = scrapedtitle + langs,      
                                   plot = '',
                                   show = show,
                                   extra = tipo,
                                   language = langs,
                                   url = scrapedurl,
                                   thumbnail = thumb,
                                   contentType = tipo,
                                   fulltitle = scrapedtitle,
                                   contentTitle = scrapedtitle,
                                   contentSerieName = contentSerieName))
                                  
    tmdb.set_infoLabels(itemlist, seekTmdb=True)

    # Pagine
    patron = r'class="page-numbers current">\d+</span></li>\s*<li><a class="page-numbers" href="([^"]+)">'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page:
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_serie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail=os.path.join(config.get_runtime_path() , "resources" , "images", "icon", "next_1.png"),
                 folder=True))
	 
    return itemlist

# ========================================================================================================================================================
	
def episodios(item):
    logger.info("[Alfa-PureITA SerieHD] episodios_all")
    itemlist = []

    data = httptools.downloadpage(item.url).data.replace('\n', '')


    patron = r'<iframe id="iframeVid" width="[^"]+" height="[^"]+" src="([^"]+)" allowfullscreen></iframe>'
    url = scrapertools.find_single_match(data, patron)


    data = httptools.downloadpage(url).data.replace('\n', '')
    #logger.debug("########################## data epis ##############################%s" % data)

    section_stagione = scrapertools.find_single_match(data, 'Stagione</h5>.*?<ul class="full-screen-select">(.*?)</div>\s*</div>')

    patron = '<a href="([^"]+)" class[^>]+>([^<]+)<'
    seasons = re.compile(patron, re.DOTALL).findall(section_stagione)

    for scrapedseason_url, scrapedseason in seasons:

        season_url = scrapedseason_url #urlparse.urljoin(url, scrapedseason_url)
        data = httptools.downloadpage(season_url).data.replace('\n', '')

        section_episodio = scrapertools.find_single_match(data, '<h5 class="modal-title" id="exampleModalLabel">Episodi[^<]+</h5>(.*?)</div>\s*</div>')
        patron = '<li><a href="([^"]+)" class[^>]+>([^<]+)</a></li>'
        episodes = re.compile(patron, re.DOTALL).findall(section_episodio)

        for scrapedepisode_url, scrapedepisode in episodes:
            episode_url = scrapedepisode_url #urlparse.urljoin(url, scrapedepisode_url)
            
            season = scrapertools.find_single_match(scrapedseason, '(\d+)') 
            episode = scrapertools.find_single_match(scrapedepisode, '(\d+)')
            ep = season + "x" + episode.zfill(2)
            
            #if "Sub" in item.show.title():
            #    langs =  " ([COLOR yellow]SUB ITA[/COLOR])"
            #    lang = " (SUB ITA)"
            #else:
            #    langs =  ""
            #    lang = ""
                
            #if unify:
            #    langs = ""

            fulltitle = re.sub("\(\d{4}\)", "", item.fulltitle).strip()
            name = "[COLOR orange]" + fulltitle + "[/COLOR]"
            title_full = ep + " - " + name
                     
            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     title = title_full,  
                     fulltitle = ep + " - " + item.fulltitle,
                     fanart = item.fanart,
                     show = item.show,                  
                     url = episode_url,
                     thumbnail = item.thumbnail,
                     language = '',
                     extra = item.extra,
                     contentTitle = name,
                     contentType = 'episode',                     
                     contentSeason = season,
                     contentEpisodeNumber = episode,                     
                     contentSerieName = item.contentSerieName,
                     plot = "[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                     infoLabels = item.infoLabels,
                     folder = True))
	#tmdb.set_infoLabels(itemlist, seekTmdb=True)				 
    if config.get_videolibrary_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="[COLOR yellow][I] Aggiungi alla libreria[/I][/COLOR]",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 thumbnail=item.thumbnail,
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="[COLOR yellow][I] Scarica tutti gli episodi della serie[/I][/COLOR]",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios",
                 thumbnail=item.thumbnail,
                 show=item.show))
      
    return itemlist	

# ========================================================================================================================================================
	
def findvideos(item):
    logger.info("[Alfa-PureITA SerieHD] findvideos")
    itemlist = []

    if "movie" in item.extra:
        data = httptools.downloadpage(item.url).data
        item.url = scrapertools.find_single_match(data, '<iframe id="iframeVid" width="[^"]+" height="[^"]+" src="([^"]+)" allowfullscreen></iframe>')

    data = httptools.downloadpage(item.url).data
    section_resolution = scrapertools.find_single_match(data, 'Risoluzione</div>(.*?)</ul>')
    
    patron = '<li id="resolution-\d+"><a href="([^"]+)" class[^>]+>([^<]+)</a></li>'
    resolution = re.compile(patron, re.DOTALL).findall(section_resolution)
    for scraped_link, quality in resolution:

        data = httptools.downloadpage(scraped_link).data
        patron = '<li id="host-\d+"><a href="([^"]+)" class[^>]+>([^<]+)</a></li>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        
        for scrapedurl, scrapedtitle in matches:
            scrapedurl = scrapedurl.replace("amp;", "")
            logger.debug("######################### scrapedurl scrapedtitle ########################## %s ## %s " % (scrapedurl, scrapedtitle))
            if "hdmario" in scrapedtitle.lower():
                continue
        
            if quality:
                res = " ([COLOR yellow]" + quality.strip() + "[/COLOR])"
            else:
                res = ""

            title = "[[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.fulltitle + res
            itemlist.append(item.clone(channel = item.channel,
                                       action = "play",                   
                                       title = title,
                                       quality = res,
                                       plot = item.plot,
                                       #show = item.show,
                                       fanart = item.fanart,
                                       server = scrapedtitle,
                                       language = item.language,
                                       url = scrapedurl.strip(),
                                       #fulltitle = item.fulltitle,
                                       thumbnail = item.thumbnail,
                                       infoLabels = item.infoLabels,
                                       contentTitle = item.contentTitle))


				
    itemlist.sort(key=lambda x: x.quality)
    tmdb.set_infoLabels(itemlist, seekTmdb=True)			 
    itemlist = servertools.get_servers_itemlist(itemlist)

    if itemlist:
        itemlist.append(Item(channel = item.channel))
        
        # Opzione "Cerca Trailer"
        itemlist.append(item.clone(channel="trailertools", contentTitle=item.contentSerieName if 'episode' in item.contentType else item.contentTitle,
                                   title="Cerca Trailer", show=item.show, action="buscartrailer", context="",
                                   text_color="magenta"))
                                   
        # Opzione "Aggiungere il Film alla libreria di KODI"
        if item.contentChannel != "videolibrary" and item.contentType != 'episode' and config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Aggiungi alla Videoteca", text_color="green",
                                 action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                                 contentTitle = item.contentTitle
                                 ))
                                 
    autoplay.start(itemlist, item)
    return itemlist 

# ==================================================================================================================================================
# ========================================================================================================================================================
	
def play(item):
    itemlist=[]

    data = httptools.downloadpage(item.url).data
    logger.debug("######################### data ##########################%s " % data)
    if 'hdpass' in item.url:
        link_url = scrapertools.find_single_match(data, '<iframe allowfullscreen custom-src="([^"]+)"></iframe>')
        item.url = link_url.decode("base64")
        logger.debug("######################### item.url ########################## %s" % item.url)
   
    if "rapidcrypt" in item.url:
       data = httptools.downloadpage(item.url).data
       
    while 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url

    itemlist.append(item.clone(url=item.url, server="", contentTitle=item.fulltitle, infoLabels=item.infoLabels))
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist
	
# ========================================================================================================================================================
# ========================================================================================================================================================
# ========================================================================================================================================================
