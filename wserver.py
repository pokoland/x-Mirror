# -*- coding: utf-8 -*-
# (c) YashDK [yash-dk@github]
# Redesigned By - @bipuldey19 (https://github.com/SlamDevs/slam-mirrorbot/commit/1e572f4fa3625ecceb953ce6d3e7cf7334a4d542#diff-c3d91f56f4c5d8b5af3d856d15a76bd5f00aa38d712691b91501734940761bdd)

import os
import time
import logging
import qbittorrentapi as qba
import asyncio

from aiohttp import web
import nodes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
                    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

routes = web.RouteTableDef()

page = """
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sélection de Fichiers Torrent</title>
    <link rel="icon" href="https://telegra.ph/file/cc06d0c613491080cc174.png" type="image/jpg">
    <script
      src="https://code.jquery.com/jquery-3.5.1.slim.min.js"
      integrity="sha256-4+XzXVhsDmqanXGHaHvgh1gMQKX40OUvDEBTu8JcmNs="
      crossorigin="anonymous"
    ></script>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap"
      rel="stylesheet"
    />
    <link
      rel="stylesheet"
      href="https://pro.fontawesome.com/releases/v5.10.0/css/all.css"
      integrity="sha384-AYmEC3Yw5cVb3ZcuHtOA93w35dYTsvhLPVnYs9eStHfGJvOvKxVfELGroGkvsg+p"
      crossorigin="anonymous"
    />
<style>

*{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Ubuntu", sans-serif;
    list-style: none;
    text-decoration: none;
    outline: none !important;
    color: white;
}

body{
    background-color: #0D1117;
}

header{
    margin: 3vh 1vw;
    padding: 0.5rem 1rem 0.5rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: #161B22;
    border-radius: 30px;
    background-color: #161B22;
    border: 2px solid rgba(255, 255, 255, 0.11);
}

header:hover, section:hover{
    box-shadow: 0px 0px 15px black;
}

.brand{
    display: flex;
    align-items: center;
}

img{
    width: 2.5rem;
    height: 2.5rem;
    border: 2px solid black;
    border-radius: 50%;
}

.name{
    margin-left: 1vw;
    font-size: 1.5rem;
}

.intro{
    text-align: center;
    margin-bottom: 2vh;
    margin-top: 1vh;
}

.social a{
    font-size: 1.5rem;
    padding-left: 1vw;
}

.social a:hover, .brand:hover{
    filter: invert(0.3);
}

section{
    margin: 0vh 1vw;
    margin-bottom: 10vh;
    padding: 1vh 3vw;
    display: flex;
    flex-direction: column;
    border: 2px solid rgba(255, 255, 255, 0.11);
    border-radius: 20px;
    background-color: #161B22 ;
}

li:nth-child(1){
    padding: 1rem 1rem 0.5rem 1rem;
}

li:nth-child(n+1){
    padding-left: 1rem;
}

li label{
    padding-left: 0.5rem;
}

li{
    padding-bottom: 0.5rem;
}

span{
    margin-right: 0.5rem;
    cursor: pointer;
    user-select: none;
    transition: transform 200ms ease-out;
}

span.active{
    transform: rotate(90deg);
    -ms-transform: rotate(90deg);	 /* for IE  */
    -webkit-transform: rotate(90deg);/* for browsers supporting webkit (such as chrome, firefox, safari etc.). */
    display: inline-block;
}

ul{
    margin: 1vh 1vw 1vh 1vw;
    padding: 0 0 0.5rem 0;
    border: 2px solid black;
    border-radius: 20px;
    background-color: #1c2129;
    overflow: hidden;
}

input[type="checkbox"]{
    cursor: pointer;
    user-select: none;
}

input[type="submit"] {
    border-radius: 20px;
    margin: 2vh auto 1vh auto;
    width: 50%;
    display: block;
    height: 5.5vh;
    border: 2px solid rgba(255, 255, 255, 0.11);
    background-color: #0D1117;
    font-size: 16px;
    font-weight: 500;
}

input[type="submit"]:hover, input[type="submit"]:focus{
    background-color: rgba(255, 255, 255, 0.068);
    cursor: pointer;
}

@media (max-width: 768px){
    input[type="submit"]{
        width: 100%;
    }
}

#treeview .parent {
    position: relative;
}

#treeview .parent > ul {
    display: none;
}

</style>
</head>
<body>
  <!--© Designed and coded by @bipuldey19-Telegram-->
    <header>
      <div class="brand">
        <img
          src="https://telegra.ph/file/cc06d0c613491080cc174.png"
          alt="logo"
        />
        <a href="https://t.me/mirrorLeechTelegramBot">
          <h2 class="name">Sélection Qbittorrent</h2>
        </a>
      </div>
      <div class="social">
        <a href="https://www.github.com/anasty17/mirror-leech-telegram-bot"><i class="fab fa-github"></i></a>
        <a href="https://t.me/mirrorLeechTelegramBot"><i class="fab fa-telegram"></i></a>
      </div>
    </header>
    <section>
      <h2 class="intro">Sélectionnez les fichiers que vous souhaitez télécharger</h2>
      <form action="{form_url}" method="POST">
       {My_content}
       <input type="submit" name="Sélectionner ces fichiers ;)">
      </form>
    </section>

    <script>
      $(document).ready(function () {
        var tags = $("li").filter(function () {
          return $(this).find("ul").length !== 0;
        });

        tags.each(function () {
          $(this).addClass("parent");
        });

        $("body").find("ul:first-child").attr("id", "treeview");
        $(".parent").prepend("<span>▶</span>");

        $("span").click(function (e) {
          e.stopPropagation();
          e.stopImmediatePropagation();
          $(this).parent( ".parent" ).find(">ul").toggle("slow");
          if ($(this).hasClass("active")) $(this).removeClass("active");
          else $(this).addClass("active");
        });
      });

      if(document.getElementsByTagName("ul").length >= 10){
      var labels = document.querySelectorAll("label");
      //Shorting the file/folder names
      labels.forEach(function (label) {
        if (label.innerText.toString().split(" ").length >= 6) {
          let FirstPart = label.innerText
            .toString()
            .split(" ")
            .slice(0, 3)
            .join(" ");
          let SecondPart = label.innerText
            .toString()
            .split(" ")
            .splice(-3)
            .join(" ");
          label.innerText = `${FirstPart}... ${SecondPart}`;
        }
        if (label.innerText.toString().split(".").length >= 6) {
          let first = label.innerText
            .toString()
            .split(".")
            .slice(0, 3)
            .join(" ");
          let second = label.innerText
            .toString()
            .split(".")
            .splice(-3)
            .join(".");
          label.innerText = `${first}... ${second}`;
        }
      });
     }
    </script>

<script>
$('input[type="checkbox"]').change(function(e) {
  var checked = $(this).prop("checked"),
      container = $(this).parent(),
      siblings = container.siblings();
/*
  $(this).attr('value', function(index, attr){
     return attr == 'yes' ? 'noo' : 'yes';
  });
*/
  container.find('input[type="checkbox"]').prop({
    indeterminate: false,
    checked: checked
  });
  function checkSiblings(el) {
    var parent = el.parent().parent(),
        all = true;
    el.siblings().each(function() {
      let returnValue = all = ($(this).children('input[type="checkbox"]').prop("checked") === checked);
      return returnValue;
    });

    if (all && checked) {
      parent.children('input[type="checkbox"]').prop({
        indeterminate: false,
        checked: checked
      });
      checkSiblings(parent);
    } else if (all && !checked) {
      parent.children('input[type="checkbox"]').prop("checked", checked);
      parent.children('input[type="checkbox"]').prop("indeterminate", (parent.find('input[type="checkbox"]:checked').length > 0));
      checkSiblings(parent);
    } else {
      el.parents("li").children('input[type="checkbox"]').prop({
        indeterminate: true,
        checked: false
      });
    }
  }
  checkSiblings(container);
});
</script>
</body>
</html>
"""

code_page = """
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vérificateur de Code Torrent</title>
    <link rel="icon" href="https://telegra.ph/file/cc06d0c613491080cc174.png" type="image/jpg">
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap"
      rel="stylesheet"
    />
    <link
      rel="stylesheet"
      href="https://pro.fontawesome.com/releases/v5.10.0/css/all.css"
      integrity="sha384-AYmEC3Yw5cVb3ZcuHtOA93w35dYTsvhLPVnYs9eStHfGJvOvKxVfELGroGkvsg+p"
      crossorigin="anonymous"
    />
    <style>
     *{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Ubuntu", sans-serif;
    list-style: none;
    text-decoration: none;
    color: white;
}

body{
    background-color: #0D1117;
}

header{
    margin: 3vh 1vw;
    padding: 0.5rem 1rem 0.5rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: #161B22;
    border-radius: 30px;
    background-color: #161B22;
    border: 2px solid rgba(255, 255, 255, 0.11);
}

header:hover, section:hover{
    box-shadow: 0px 0px 15px black;
}

.brand{
    display: flex;
    align-items: center;
}

img{
    width: 2.5rem;
    height: 2.5rem;
    border: 2px solid black;
    border-radius: 50%;
}

.name{
    color: white;
    margin-left: 1vw;
    font-size: 1.5rem;
}

.intro{
    text-align: center;
    margin-bottom: 2vh;
    margin-top: 1vh;
}

.social a{
    font-size: 1.5rem;
    color: white;
    padding-left: 1vw;
}

.social a:hover, .brand:hover{
    filter: invert(0.3);
}

section{
    margin: 0vh 1vw;
    margin-bottom: 10vh;
    padding: 1vh 3vw;
    display: flex;
    flex-direction: column;
    border: 2px solid rgba(255, 255, 255, 0.11);
    border-radius: 20px;
    background-color: #161B22 ;
    color: white;
}

section form{
    display: flex;
    margin-left: auto;
    margin-right: auto;
    flex-direction: column;
}

section div{
    background-color: #0D1117;
    border-radius: 20px;
    max-width: fit-content;
    padding: 0.7rem;
    margin-top: 2vh;
}

section label{
    font-size: larger;
    font-weight: 500;
    margin: 0 0 0.5vh 1.5vw;
    display: block;
}

section input[type="text"]{
    border-radius: 20px;
    outline: none;
    width: 50vw;
    height: 4vh;
    padding: 1rem;
    margin: 0.5vh;
    border: 2px solid rgba(255, 255, 255, 0.11);
    background-color: #3e475531;
    box-shadow: inset 0px 0px 10px black;
}

section input[type="text"]:focus{
    border-color: rgba(255, 255, 255, 0.404);
}

section button{
    border-radius: 20px;
    margin-top: 1vh;
    width: 100%;
    height: 5.5vh;
    border: 2px solid rgba(255, 255, 255, 0.11);
    background-color: #0D1117;
    color: white;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 200ms ease;
}

section button:hover, section button:focus{
    background-color: rgba(255, 255, 255, 0.068);
}

section span{
    display: block;
    font-size: x-small;
    margin: 1vh;
    font-weight: 100;
    font-style: italic;
    margin-left: 23%;
    margin-right: auto;
    margin-bottom: 2vh;
}

@media (max-width: 768px) {
    section form{
        flex-direction: column;
        width: 90vw;
    }

    section div{
        max-width: 100%;
        margin-bottom: 1vh;
    }

    section label{
        margin-left: 3vw;
        margin-top: 1vh;
    }

    section input[type="text"]{
        width: calc(100% - 0.3rem);
    }

    section button{
        width: 100%;
        height: 5vh;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    section span{
        margin-left: 5%;
    }
}
    </style>
  </head>
<body>
   <!--© Designed and coded by @bipuldey19-Telegram-->
    <header>
      <div class="brand">
        <img
          src="https://telegra.ph/file/cc06d0c613491080cc174.png"
          alt="logo"
        />
        <a href="https://t.me/mirrorLeechTelegramBot">
          <h2 class="name">Sélection Qbittorrent</h2>
        </a>
      </div>
      <div class="social">
        <a href="https://www.github.com/anasty17/mirror-leech-telegram-bot"><i class="fab fa-github"></i></a>
        <a href="https://t.me/mirrorLeechTelegramBot"><i class="fab fa-telegram"></i></a>
      </div>
    </header>
    <section>
      <form action="{form_url}">
        <div>
          <label for="pin_code">Code PIN :</label>
          <input
            type="text"
            name="pin_code"
            placeholder="Entrez le code reçu de Telegram pour accéder au torrent"
          />
        </div>
        <button type="submit" class="btn btn-primary">Valider</button>
      </form>
          <span
            >* Ne modifiez rien. Votre téléchargement pourrait être perturbé.</
          >
    </section>
</body>
</html>
"""


@routes.get('/app/files/{hash_id}')
async def list_torrent_contents(request):

    torr = request.match_info["hash_id"]

    gets = request.query

    if "pin_code" not in gets.keys():
        rend_page = code_page.replace("{form_url}", f"/app/files/{torr}")
        return web.Response(text=rend_page, content_type='text/html')

    client = qba.Client(host="localhost", port="8090",
                        username="admin", password="adminadmin")
    client.auth_log_in()
    try:
        res = client.torrents_files(torrent_hash=torr)
    except qba.NotFound404Error:
        raise web.HTTPNotFound()
    count = 0
    passw = ""
    for n in str(torr):
        if n.isdigit():
            passw += str(n)
            count += 1
        if count == 4:
            break
    if isinstance(passw, bool):
        raise web.HTTPNotFound()
    pincode = passw
    if gets["pin_code"] != pincode:
        return web.Response(text="Code PIN incorrect")

    par = nodes.make_tree(res)

    cont = ["", 0]
    nodes.create_list(par, cont)

    rend_page = page.replace("{My_content}", cont[0])
    rend_page = rend_page.replace(
        "{form_url}", f"/app/files/{torr}?pin_code={pincode}")
    client.auth_log_out()
    return web.Response(text=rend_page, content_type='text/html')


async def re_verfiy(paused, resumed, client, torr):

    paused = paused.strip()
    resumed = resumed.strip()
    if paused:
        paused = paused.split("|")
    if resumed:
        resumed = resumed.split("|")
    k = 0
    while True:

        res = client.torrents_files(torrent_hash=torr)
        verify = True

        for i in res:
            if str(i.id) in paused:
                if i.priority == 0:
                    continue
                verify = False
                break

            if str(i.id) in resumed and i.priority == 0:
                verify = False
                break

        if verify:
            break
        LOGGER.info("Échec de la vérification : correction en cours...")
        client.auth_log_out()
        client = qba.Client(host="localhost", port="8090",
                           username="admin", password="adminadmin")
        client.auth_log_in()
        try:
            client.torrents_file_priority(
                torrent_hash=torr, file_ids=paused, priority=0)
        except:
            LOGGER.error("Erreur lors de la vérification des fichiers en pause")
        try:
            client.torrents_file_priority(
                torrent_hash=torr, file_ids=resumed, priority=1)
        except:
            LOGGER.error("Erreur lors de la vérification des fichiers repris")
        client.auth_log_out()
        k += 1
        if k > 4:
            return False
    LOGGER.info("Vérifié")
    return True


@routes.post('/app/files/{hash_id}')
async def set_priority(request):

    torr = request.match_info["hash_id"]
    client = qba.Client(host="localhost", port="8090",
                        username="admin", password="adminadmin")
    client.auth_log_in()

    data = await request.post()
    resume = ""
    pause = ""
    data = dict(data)

    for i, value in data.items():
        if i.find("filenode") != -1:
            node_no = i.split("_")[-1]

            if value == "on":
                resume += f"{node_no}|"
            else:
                pause += f"{node_no}|"

    pause = pause.strip("|")
    resume = resume.strip("|")

    try:
        client.torrents_file_priority(
            torrent_hash=torr, file_ids=pause, priority=0)
    except qba.NotFound404Error:
        raise web.HTTPNotFound()
    except:
        LOGGER.error("Erreur lors de la mise en pause")

    try:
        client.torrents_file_priority(
            torrent_hash=torr, file_ids=resume, priority=1)
    except qba.NotFound404Error:
        raise web.HTTPNotFound()
    except:
        LOGGER.error("Erreur lors de la reprise")

    await asyncio.sleep(2)
    if not await re_verfiy(pause, resume, client, torr):
        LOGGER.error("Échec de la vérification")
    client.auth_log_out()
    return await list_torrent_contents(request)


@routes.get('/')
async def homepage(request):

    return web.Response(text="<h1>Voir mirror-leech-telegram-bot <a href='https://www.github.com/anasty17/mirror-leech-telegram-bot'>@GitHub</a> Par <a href='https://github.com/anasty17'>Anas</a></h1>", content_type="text/html")


async def e404_middleware(app, handler):

    async def middleware_handler(request):

        try:
            response = await handler(request)
            if response.status == 404:
                return web.Response(text="<h1>404 : Page non trouvée</h2><br><h3>mirror-leech-telegram-bot</h3>", content_type="text/html")
            return response
        except web.HTTPException as ex:
            if ex.status == 404:
                return web.Response(text="<h1>404 : Page non trouvée</h2><br><h3>mirror-leech-telegram-bot</h3>", content_type="text/html")
            raise
    return middleware_handler


async def start_server():

    app = web.Application(middlewares=[e404_middleware])
    app.add_routes(routes)
    return app


async def start_server_async(port=80):

    app = web.Application(middlewares=[e404_middleware])
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()