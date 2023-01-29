import asyncio
import os
from asyncio import run_coroutine_threadsafe
from os.path import join, dirname
from dotenv import load_dotenv
from yandex_music import Client
import discord
from discord.ext import commands

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
token = os.environ.get("TOKEN")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

client = Client(token).init()

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

intents = discord.Intents().all()
dclient = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='-', intents=intents)

arg = 0


def plusNumber(num):
    global arg
    arg += num


def findUrl(url):
    global words
    words = [x for x in url.split('/') if x]
    while words[2] == 'users':
        getTrack()
        break
    while words[2] == 'album':
        getTrack()
        break


def getTrack():
    global tracksAlbom
    tracksAlbom = client.usersPlaylists(words[5], words[3]).tracks[arg]

    # print(words[0]) //  https:
    # print(words[1]) //  music.yandex.ru
    # print(words[2]) //  users     ||     album
    # print(words[3]) //  ilshatiuldashev     ||     14702448
    # print(words[4]) //  playlists     ||     track
    # print(words[5]) //  3     ||     80001957


def findTrack(name):
    global trackName
    trackName = client.search(name, False, 'track', 0, False)
    print(trackName)

    # https://music.yandex.ru/album/11611606/track/69420851


def next(ctx):
    vc = ctx.voice_client
    plusNumber(1)
    getTrack()
    link = client.tracks_download_info(tracksAlbom.id, True, None)[2].direct_link
    vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))


@bot.command(aliases=['здфн'])
async def play(ctx, url):
    voice_state = ctx.author.voice
    if voice_state is not None:
        findUrl(url)
        vc = await voice_state.channel.connect()
        link = client.tracks_download_info(tracksAlbom.id, True, None)[2].direct_link
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
        await ctx.send(f"Сейчас играет ({tracksAlbom.track.title})")
    else:
        await ctx.channel.send("Вы должны находиться в канале, что бы бот смог подключиться к вам")


@bot.command(aliases=['ылшз', 'next', 'туче'])
async def skip(ctx, numbers=1):
    vc = ctx.voice_client
    vc.stop()
    plusNumber(numbers - 1)
    getTrack()
    async with ctx.typing():
        link = client.tracks_download_info(tracksAlbom.id, True, None)[2].direct_link
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
        # await ctx.send(f"Сейчас играет ({tracksAlbom.track.title})")


@bot.command(aliases=['дуфму', 'stop'])
async def leave(ctx):
    plusNumber(-arg)
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")


@bot.command(aliases=['аштв'])
async def find(ctx, name):
    voice_state = ctx.author.voice
    # if voice_state is not None:
    findTrack(name)
        # vc = await voice_state.channel.connect()
        # link = client.tracks_download_info(trackName.id, True, None)[2].direct_link
        # vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
        # await ctx.send(f"Сейчас играет ({trackName.track.title})")
    # else:
        # await ctx.channel.send("Вы должны находиться в канале, что бы бот смог подключиться к вам")


@bot.command(aliases=['song', 'ыщтп', 's', 'ы'])
async def already_song(ctx):
    try:
        while ctx.voice_client.is_playing():
            await ctx.send(f"Сейчас играет ({tracksAlbom.track.title})")
            break
        else:
            await ctx.send("Бот ничего не играет")
    except:
        await ctx.channel.send("Бот не подключен к каналу")


bot.run(token=DISCORD_TOKEN)
