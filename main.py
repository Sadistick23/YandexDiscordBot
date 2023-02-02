#!/usr/bin/python3
import os
import random
from os.path import join, dirname
from dotenv import load_dotenv
from yandex_music import Client
import discord
from discord.ext import commands

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
token = os.environ.get("TOKEN")
FFMPEG = os.environ.get("FFMPEG")
PREFIX = os.environ.get("PREFIX")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

client = Client(token).init()

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
bot = commands.Bot(command_prefix=PREFIX, help_command=None, intents=discord.Intents.all())
arg = 0
num = 0
global playList
playList = []


def plusNumber(num):
    global arg
    arg += num


def nextNumber():
    global num
    num += 1


def findTrack(ctx, params):
    if params[:23] == 'https://music.yandex.ru':
        words = [x for x in params.split('/') if x]
        while words[2] == 'users':
            tracksUsers = client.usersPlaylists(words[5], words[3]).tracks
            for tracks in tracksUsers:
                track_text = {'id': f'{tracks.track.id}', 'title': f'{tracks.track.title}', 'artist': f'{tracks.track.artists[0].name}'}
                playList.append(track_text)
            break
        while words[2] == 'album':
            tracksAlbum = client.albums_with_tracks(words[3]).volumes[0]
            for tracks in tracksAlbum:
                track_text = {'id': f'{tracks.id}', 'title': f'{tracks.title}', 'artist': f'{tracks.artists[0].name}'}
                playList.append(track_text)
            break
    else:
        TrackByName = ctx.message.content[6:]
        tracksName = client.search(TrackByName, False, 'track', 0, False).tracks.results
        for tracks in tracksName:
            track_text = {'id': f'{tracks.id}', 'title': f'{tracks.title}', 'artist': f'{tracks.artists[0].name}'}
            playList.append(track_text)


        # https://music.yandex.ru/album/12565211/track/72798711
        # https://music.yandex.ru/users/ilshatiuldashev/playlists/3
        # https://music.yandex.ru/album/3087311/track/28421144


@bot.command(aliases=['здфн', 'играть', 'плэй', 'песня', 'сонг'])
async def play(ctx, params):
    voice_state = ctx.author.voice
    if voice_state is not None:
        findTrack(ctx, params)
        vc = await voice_state.channel.connect()
        link = client.tracks_download_info(playList[arg].get('id'), True, None)[2].direct_link
        vc.play(discord.FFmpegPCMAudio(executable=FFMPEG, source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
        embed = discord.Embed(title="Сейчас играет:")
        embed.add_field(name=f"Название: ", value=f"""```py\n'{playList[arg].get('title')}'\n```""", inline=False)
        embed.add_field(name=f"Автор: ", value=f"""```ps1\n[ {playList[arg].get('artist')} ]\n```""", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.channel.send("Вы должны находиться в канале, что бы бот смог подключиться к вам")


def next(ctx):
    vc = ctx.voice_client
    nextNumber()
    link = client.tracks_download_info(playList[num].get('id'), True, None)[2].direct_link
    vc.play(discord.FFmpegPCMAudio(executable=FFMPEG, source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))


@bot.command(aliases=['ыргааду', 'перемешать', 'mix', 'ьшч'])
async def shuffle(ctx):
    random.shuffle(playList)
    vc = ctx.voice_client
    vc.stop()
    playShuffle = client.tracks_download_info(playList[arg].get('id'), True, None)[2].direct_link
    vc.play(discord.FFmpegPCMAudio(executable=FFMPEG, source=playShuffle, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
    embed = discord.Embed(title="Сейчас играет:")
    embed.add_field(name=f"Название: ", value=f"""```py\n'{playList[arg].get('title')}'\n```""", inline=False)
    embed.add_field(name=f"Автор: ", value=f"""```ps1\n[ {playList[arg].get('artist')} ]\n```""", inline=False)
    await ctx.send(embed=embed)


@bot.command(aliases=['ылшз', 'next', 'туче', 'пропуск', 'пропустить', 'скип'])
async def skip(ctx, numbers=1):
    vc = ctx.voice_client
    vc.stop()
    plusNumber(numbers)
    link = client.tracks_download_info(playList[arg].get('id'), True, None)[2].direct_link
    vc.play(discord.FFmpegPCMAudio(executable=FFMPEG, source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))


#lambda e: print('Player error: %s' % e) if e else next(ctx))


@bot.command(aliases=['ыещз', 'stop'])
async def leave(ctx):
    plusNumber(-arg)
    vc = ctx.voice_client
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        vc.pause()
        vc.stop()
        await voice_client.disconnect()
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")


@bot.command(aliases=['song', 'ыщтп', 's', 'ы'])
async def already_song(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice == None:
        if ctx.voice_client.is_playing() == True:
            embed = discord.Embed(title="Сейчас играет:")
            embed.add_field(name=f"Название: ", value=f"""```py\n'{playList[arg].get('title')}'\n```""", inline=False)
            embed.add_field(name=f"Автор: ", value=f"""```ps1\n[ {playList[arg].get('artist')} ]\n```""", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Бот ничего не играет")
    else:
        await ctx.send("Бот не подключен к каналу")


@bot.command(aliases=['рудз'])
async def help(ctx):
    embed = discord.Embed(title="Помощь", description="Список команд")
    embed.add_field(name="-play or (-здфн)", value="Находит альбом по URL или названию", inline=False)
    embed.add_field(name="-skip or (-ылшз, -next, -туче)", value="Пропускает теущую песню, если вести число то пропустит несколько", inline=False)
    embed.add_field(name="-song or (-ыщтп, -s, -ы)", value="Показывает воспроизводимую в данный момент песню", inline=False)
    embed.add_field(name="-shuffle or (-ырфааду)", value="Перемешивает плейлист", inline=False)
    await ctx.send(embed=embed)


@bot.command(aliases=['дшые'])
async def list(ctx):
    embed = discord.Embed(title="Плейлист песен")
    embed.add_field(name="Позапрошлый", value=f"""```py\n'{playList[arg - 2].get('title')}'\n[ {playList[arg - 2].get('artist')} ]\n```""", inline=False)
    embed.add_field(name="Прошлый", value=f"""```py\n'{playList[arg - 1].get('title')}'\n[ {playList[arg - 1].get('artist')} ]\n```""", inline=False)
    embed.add_field(name="Текущий", value=f"""```py\n'{playList[arg].get('title')}'\n[ {playList[arg].get('artist')} ]\n```""", inline=False)
    embed.add_field(name="Следующий", value=f"""```py\n'{playList[arg + 1].get('title')}'\n[ {playList[arg + 1].get('artist')} ]\n```""", inline=False)
    embed.add_field(name="Через один", value=f"""```py\n'{playList[arg + 2].get('title')}'\n[ {playList[arg + 2].get('artist')} ]\n```""", inline=False)
    await ctx.send(embed=embed)


@bot.command(aliases=['зштп'])
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


bot.run(token=DISCORD_TOKEN)