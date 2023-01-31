import os
import asyncio
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


bot = commands.Bot(command_prefix='-', help_command=None, intents=discord.Intents.all())


arg = 0


def plusNumber(num):
    global arg
    arg += num


def findUrl(ctx, url):
    global words
    global trackParse
    words = False
    trackParse = False
    while url[:23] == 'https://music.yandex.ru':
        words = [x for x in url.split('/') if x]
        getTrack()
        break
    else:
        global TrackByName
        TrackByName = ctx.message.content[6:]
        getTrackByName()


        # https://music.yandex.ru/album/12565211/track/72798711
        # https://music.yandex.ru/users/ilshatiuldashev/playlists/3
        # https://music.yandex.ru/album/3087311/track/28421144


def getTrack():
    global tracksAlbom
    while words[2] == 'users':
        tracksAlbom = client.usersPlaylists(words[5], words[3]).tracks[arg]
        break
    while words[2] == 'album':
        tracksAlbom = client.albums_with_tracks(words[3]).volumes[0][arg]
        break


def getTrackByName():
    global trackParse
    trackParse = client.search(TrackByName, False, 'track', 0, False).tracks.results[arg]


@bot.command(aliases=['здфн'])
async def play(ctx, url):
    voice_state = ctx.author.voice
    if voice_state is not None:
        findUrl(ctx, url)
        vc = await voice_state.channel.connect()
        while words:
            while words[2] == 'users':
                await ctx.send(f"Сейчас играет ({tracksAlbom.track.title})")
                link = client.tracks_download_info(tracksAlbom.id, True, None)[2].direct_link
                vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
                break
            while words[2] == 'album':
                await ctx.send(f"Сейчас играет ({tracksAlbom.title})")
                link = client.tracks_download_info(tracksAlbom.id, True, None)[2].direct_link
                vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
                break
            break
        while trackParse:
            onePlay = client.tracks_download_info(trackParse.id, True, None)[2].direct_link
            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=onePlay, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
            await ctx.send(f"Сейчас играет ({trackParse.title})")
            break

    else:
        await ctx.channel.send("Вы должны находиться в канале, что бы бот смог подключиться к вам")


def next(ctx):
    vc = ctx.voice_client
    while words:
        plusNumber(1)
        getTrack()
        link = client.tracks_download_info(tracksAlbom.id, True, None)[2].direct_link
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
        break
    while trackParse:
        plusNumber(1)
        getTrackByName()
        onePlay = client.tracks_download_info(trackParse.id, True, None)[2].direct_link
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=onePlay, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
        break


@bot.command(aliases=['ылшз', 'next', 'туче'])
async def skip(ctx, numbers=1):
    vc = ctx.voice_client
    vc.stop()
    while words:
        plusNumber(numbers - 1)
        getTrack()
        link = client.tracks_download_info(tracksAlbom.id, True, None)[2].direct_link
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
        break
    while trackParse:
        plusNumber(numbers)
        getTrackByName()
        onePlay = client.tracks_download_info(trackParse.id, True, None)[2].direct_link
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=onePlay, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else next(ctx))
        break


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


class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Выбрать", style=discord.ButtonStyle.gray)
    async def gray_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Песня выбрана {trackParse[0].title}")


@bot.command(aliases=['song', 'ыщтп', 's', 'ы'])
async def already_song(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice == None:
        while ctx.voice_client.is_playing() == True:
            while words:
                while words[2] == 'users':
                    await ctx.send(f"Сейчас играет ({tracksAlbom.track.title})")
                    break
                while words[2] == 'album':
                    await ctx.send(f"Сейчас играет ({tracksAlbom.title})")
                    break
                break
            while trackParse:
                await ctx.send(f"Сейчас играет ({trackParse.title})")
                break
            break
        else:
            await ctx.send("Бот ничего не играет")
    else:
        await ctx.send("Бот не подключен к каналу")


@bot.command(aliases=['рудз'])
async def help(ctx):
    embed = discord.Embed(title="Помощь", description="Список команд")
    embed.add_field(name="-song or (-ыщтп, -s, -ы)", value="Показывает воспроизводимую в данный момент песню", inline=False)
    embed.add_field(name="-find or (-аштв)", value="Находит песню по названию", inline=False)
    embed.add_field(name="-skip or (-ылшз, -next, -туче)", value="Пропускает теущую песню, если вести число то пропустит несколько", inline=False)
    embed.add_field(name="-play or (-здфн)", value="Находит альбом по URL", inline=False)
    await ctx.send(embed=embed)


bot.run(token=DISCORD_TOKEN)
