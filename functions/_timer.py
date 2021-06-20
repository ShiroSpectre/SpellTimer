import re
import cv2
import asyncio
import discord
import functools
from discord import message
import pyautogui
import pytesseract
import numpy as np
from PIL import Image
from functions import lol_data

# GLOBAL DEBUG PARAMETER
CHATWINDOW_X_START = 80
CHATWINDOW_X_END = 600
CHATWINDOW_Y_START = 830
CHATWINDOW_Y_END = 1030

name_color_range = ([20, 20, 160], [80, 80, 256])
spell_color_range = ([0, 140, 180], [40, 180, 256])
status_color_range = ([150, 200, 160], [210, 255, 200])

sound = False
vc = None

async def initiate_timer(bot, ctx):
    global msg
    global flag
    flag = True

    enemies = []
    msg = await ctx.channel.send(f'Detected enemies: {enemies}')
    while len(enemies) < 5 and flag:
        chat_reader().update_enemies(enemies)
        await msg.edit(content=f'Detected enemies: {enemies}')
        await asyncio.sleep(0.3)
        if len(enemies) == 5:
            await msg.delete()

    if flag:
        # init
        timers = dict()
        levels = { c : 1 for c in enemies }
        msg = await ctx.channel.send(parse(enemies, levels, timers, bot.emojis))
        curr = bot.loop.time()
        await loop_timer(bot, enemies, levels, timers, curr)

async def delete_timer():
    global flag 
    flag = False
    await msg.delete()

async def enable_sound(vc_client):
    global sound
    global vc
    sound = True
    vc = vc_client

async def mute_sound():
    global sound
    sound = False

async def update_message(bot, enemies, levels, timers, prev, curr):
    activate_sound = chat_reader().update_timers_and_levels(timers, levels, 20, curr - prev)
    await msg.edit(content=parse(enemies, levels, timers, bot.emojis))
    if activate_sound: vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="C:/Users/leonz/Code/Spelltimer/sounds/recognition_sound.wav"))

async def loop_timer(bot, enemies, levels, timers, curr):
    while flag:
        prev = curr
        curr = bot.loop.time()
        await update_message(bot, enemies, levels, timers, prev, curr)
        await asyncio.sleep(1)
        
def parse(champions, levels, timers, emojis):
    message = "_\n"
    lanes = ['top', 'jungle', 'mid', 'adc', 'sup']
    i = 0
    for champion in champions:
        message += str(discord.utils.get(emojis, name = lanes[i])) + "**" + champion + ":**" + "\t"
        if (champion, "Flash") in timers:
           message += str(discord.utils.get(emojis, name = "Flash")) + " " + str(int(timers[(champion, "Flash")])) + "\t"
        for (c, ability) in timers:
            if champion == c and ability != "R" and ability !="Flash":
               message += str(discord.utils.get(emojis, name = ability))+ " " + str(int(timers[(champion, ability)])) + "\t"
        if (champion, "R") in timers:
            message += "**R** " + str(int(timers[(champion, "R")]))
        message += "\n"
        i += 1
    message += "_"
    return message

class chat_reader(object):
    def __init__(self):
        self.champions           = lol_data.champions()
        self.summonerspells      = lol_data.summonerspells()
        self.match_champs        = "("  + (')|('.join(map((lambda x : re.escape(x)), list(self.champions)))).replace("'", "\\'") + ")"
        self.match_summoners     = "("  + (')|('.join(map((lambda x : re.escape(x)), list(self.summonerspells)))) + ")"
        self.champ_is_alive      = re.compile("(?P<champion>(" + self.match_champs + "))( - Alive)")
        self.champ_level         = re.compile("(?P<champion>(" + self.match_champs + "))( - Level )(?P<level>\d+)")
        self.champ_summonerspell = re.compile("(?P<champion>(" + self.match_champs + ")) (?P<summoner>(" + self.match_summoners + "))")
        self.champ_ult           = re.compile("(?P<champion>(" + self.match_champs + ")) R")

    def parse(self, chat):
        chat = chat.replace("|", "1")
        chat = chat.replace("Usdyr", "Udyr")
        chat = chat.replace("’", "'")
        chat = chat.replace("KogMaw", "Kog'Maw")
        alive_events, level_events, summonerspell_events, ult_events = [], [], [], []
        for line in chat.splitlines():
            m = re.match(self.champ_is_alive, line)
            if m:
                alive_events.append(m.groupdict())
                continue
            m = re.match(self.champ_level, line)
            if m:
                level_events.append((m.groupdict()))
                continue
            m = re.match(self.champ_summonerspell, line)
            if m:
                summonerspell_events.append(m.groupdict())
                continue
            m = re.match(self.champ_ult, line)
            if m:
                ult_events.append(m.groupdict())
                continue
        return (alive_events, level_events, summonerspell_events, ult_events)

    def get_events(self, debug=False, from_example=False):
        if debug and from_example:
            image = Image.open('debug\images\example.png')
        else:
            image = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)[CHATWINDOW_Y_START:CHATWINDOW_Y_END, CHATWINDOW_X_START:CHATWINDOW_X_END]
    
        enemy_name = cv2.inRange(image, np.array(name_color_range[0]), np.array(name_color_range[1]))
        enemy_spell = cv2.inRange(image, np.array(spell_color_range[0]), np.array(spell_color_range[1]))
        enemy_status = cv2.inRange(image, np.array(status_color_range[0]), np.array(status_color_range[1]))
        filtered_image = cv2.bitwise_or(cv2.bitwise_or(enemy_name, enemy_spell), enemy_status)
        filtered_image = functools.reduce((lambda a,b : cv2.bitwise_or(a, b)), [enemy_name, enemy_spell],  enemy_status)

        if debug:
            cv2.imwrite('debug/images/image.png', image)
            cv2.imwrite('debug/images/enemy_name.png', enemy_name)
            cv2.imwrite('debug/images/enemy_spell.png', enemy_spell)
            cv2.imwrite('debug/images/enemy_status.png', enemy_status)
            cv2.imwrite('debug/images/filtered_image.png', filtered_image)
        
        try:
            chat = pytesseract.image_to_string(filtered_image, timeout = 0.5)
        except pytesseract.TesseractError:
            return ([], [], [], [])
        return self.parse(chat)

    def update_enemies(self, enemies):
        for eventtype in self.get_events():
            for event in eventtype:
                if not event["champion"] in enemies:
                    enemies.append(event["champion"])

    def update_timers_and_levels(self, timers, levels, new_cd_delay, cd_timestep):
        (alive_events, level_events, summonerspell_events, ult_events) = self.get_events()
        for event in level_events:
            levels[event["champion"]] = int(event["level"])
        for event in summonerspell_events:
            if not (event["champion"], event["summoner"]) in timers or timers[event["champion"], event["summoner"]] < 30:
                if event["summoner"] == "Teleport":
                    timers[event["champion"], event["summoner"]] = 430.588 - 10.588*levels[event["champion"]] - new_cd_delay
                else:
                    timers[event["champion"], event["summoner"]] = self.summonerspells[event["summoner"]][0] - new_cd_delay
        for event in ult_events:
            if not (event["champion"], "R") in timers or timers[(event["champion"], "R")] < 30:
                if levels[event["champion"]] < 11:
                    timers[(event["champion"], "R")] = self.champions[event["champion"]][0] - new_cd_delay
                    continue
                if levels[event["champion"]] < 16:
                    timers[(event["champion"], "R")] = self.champions[event["champion"]][1] - new_cd_delay
                    continue
                else:
                    timers[(event["champion"], "R")] = self.champions[event["champion"]][2] - new_cd_delay
                    continue
        finished = []
        for t in timers:
            timers[t] -= cd_timestep
            if timers[t] < 0:
                finished.append(t)
        for t in finished:
            timers.pop(t)
        if finished and sound: return True
        else: return False