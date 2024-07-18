import re
from ..scripts import FHttps
from .collections import SMessage
from instaloader import Post, Profile
from instaloader import Instaloader, NodeIterator
#=====================================================================

class Instagram:

    async def get01(incoming):
        matchs = re.search(FHttps.DATA01, incoming)
        moonus = True if matchs else False
        return SMessage(result=matchs, status=moonus)

    async def get02(incoming):
        mainse = {"p": "POST", "tv": "IGTV", "reel": "REELS"}
        conmom = mainse.get(incoming.group(2))
        moonus = True if conmom else False
        return SMessage(result=conmom, status=moonus)

    async def get03(bot, shortcode):
        moonus = Post.from_shortcode(bot.context, shortcode)
        return moonus

    async def get04(bot, username):
        moonus = Profile.from_username(bot.context, username)
        return moonus

    async def get05(bot: Profile) -> NodeIterator[Post]:
        moonus = bot.get_posts()
        return moonus

    async def download(bot: Instaloader, update: Post):
        moonus = bot.download_post(update, update.owner_username)
        return moonus

#=====================================================================
