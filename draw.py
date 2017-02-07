import tdl, math, re, random
import maps, monsters, consts, colors, utils, races, player, items
from itertools import groupby
from pyfiglet import Figlet

def display_stat(name, obj):
    a = getattr(obj, 'max_'+name)
    b = getattr(obj, name)
    return '%d/%d' % (b, a)

def draw_stats(GS):
    console = GS['console']
    player = GS['player']
    base = math.ceil(consts.WIDTH/2)+1
    bounds = len('Health: ')+3
    start = consts.MESSAGE_NUMBER

    console.drawStr(base, start-1, '-'*(base-1))

    # Description
    console.drawStr(base, start, player.race.name + ' ('+player.attributes()+')')
    
    # Health
    hp = math.floor(player.health/player.max_health*100)
    color = colors.red
    if hp >= 90:
        color = colors.green
    elif hp >= 40:
        color = colors.yellow

    ratio = (consts.WIDTH-base - (9+len('Health: ')))/player.max_health
    bar = " "*math.floor(ratio*player.health)
    underbar = " "*math.ceil(ratio*(player.max_health - player.health))
    console.drawStr(base, start+1, 'Health: ', fg=colors.white)
    console.drawStr(base+bounds, start+1, bar, bg=color)
    color2 = colors.dark_grey
    if player.poisoned:
        color2 = colors.extreme_darken(colors.dark_green)
    console.drawStr(base+bounds+len(bar), start+1, underbar, bg=color2)
    
    # Hunger
    if player.hunger >= 40:
        console.drawStr(base+bounds+4, start+2, 'Very Hungry', fg=colors.red)
    elif player.hunger >= 20:
        console.drawStr(base+bounds+4, start+2, 'Hungry', fg=colors.yellow)
    elif player.hunger >= 15:
        console.drawStr(base+bounds+4, start+2, 'Getting Hungry', fg=colors.green)

    # Light Source Radius
    nm = len(GS['terrain_map'].dungeon['monsters'])
    console.drawStr(base, start+3, 'LoS dist: ' + str(player.light_source_radius))
    console.drawStr(base+bounds+4, start+3, 'Dungeon '+str(GS['terrain_map'].dungeon_level))

    # Kills
    console.drawStr(base, start+4, 'Monsters: ' + str(nm))
    console.drawStr(base+bounds+4, start+4, 'Kills: ' + str(player.killed_monsters))

    # Level
    lvl = math.floor(player.level/player.race.levels)
    color = colors.light_blue
    if lvl <= 50:
        color = colors.dark_yellow
    console.drawStr(base, start+5,
                    'Level: '+str(player.level)+'/'+str(player.race.levels),
                    fg=color)

    console.drawStr(base+bounds+4, start+5, 'Exp: '+str(player.exp))

    # Other Stats
    console.drawStr(base, start+6, 'Strength: '+str(player.strength), fg=(0,100,0))
    console.drawStr(base, start+7, 'Speed: '+str(player.speed), fg=colors.light_blue)
    console.drawStr(base, start+8, 'Attack: '+str(player.attack), fg=colors.red)
    console.drawStr(base, start+9, 'Armor: '+str(player.defence), fg=colors.dark_yellow)

    # Ranged Weapon
    if player.ranged_weapon:
        console.drawStr(base, start+10, 'RW: '+str(player.ranged_weapon.name))
        console.drawStr(base+bounds+4, start+10, 'Missles: '+str(len(player.missles)))

    # Game State
    console.drawStr(base, start+11, 'Turn '+str(GS['turns']))
    console.drawStr(base+bounds+4, start+11, 'Score: '+str(player.score(GS)))

def draw_messages(GS):
    console = GS['console']
    if len(GS['messages']) >= consts.MESSAGE_NUMBER:
        GS['messages'] = [GS['messages'][0]]
        
    for (i, m) in enumerate(reversed(GS['messages'])):
        color = colors.white
        message = m
        if len(m.split(': ')) > 1:
            color = eval("colors." + m.split(': ')[0])
            message = m.split(': ')[1]
            
        GS['console'].drawStr(math.ceil(consts.WIDTH/2)+1, i, message, fg=color)

    return GS['messages']
    
def draw_hud_screen(GS):
    console = GS['console']
    if not GS['messages']:
        GS['messages'] = []
        
    draw_stats(GS)
    return draw_messages(GS)

def draw_inventory_screen(GS):
    console = GS['console']
    lst = groupby(GS['player'].inventory)
    for (i, grp) in enumerate(lst):
        item, number = grp
        item_display = ""
        if isinstance(item, items.Armor):
            item_display = '(%s) -> W/D:%d' % (item.char, item.weight)
        elif isinstance(item, items.Weapon):
            item_display = '(%s) -> W:%d, A:%d' % (item.char, item.weight, item.attack)
        elif isinstance(item, items.RangedWeapon):
            item_display = '(%s) -> W:%d, R:%d' % (item.char, item.weight, item.range)
        elif isinstance(item, items.Missle):
            item_display = '(%s) -> H:%d' % (item.char, item.hit)
        elif isinstance(item, items.Light):
            item_display = '(%s) -> R:%d, L:%d' % (item.char, item.radius, item.lasts)
        elif isinstance(item, items.Food):
            item_display = '(%s) -> N:%d' % (item.char, item.nutrition)

        color = colors.black
        if item.equipped:
            color = colors.red
            
        try:
            if item == GS['player'].inventory[GS['selection']]:
                color = colors.grey
        except:
            pass
        
        console.drawStr(consts.EDGE_POS+1, i+1, '('+str(i)+') '+item.name+' -> '+item_display+' (Pr'+str(item.probability)+'%) x'+str(len(list(number))),
                        bg=color)

def draw_man_screen(GS):
    with open('manual.txt', 'r') as myfile:
        manual = myfile.read().split("\n")
        
        for (i, line) in enumerate(manual):
            if line != '' and line[0] == '*':
                GS['console'].drawStr(consts.EDGE_POS-1, i, line, fg=colors.red)
            else:
                GS['console'].drawStr(consts.EDGE_POS, i, line)
    return GS['messages']
        
def draw_hud(GS):
    consts.EDGE_POS = math.ceil(consts.WIDTH/2)+2
    for i in range(0, consts.HEIGHT):
        GS['console'].drawChar(consts.EDGE_POS-2, i, '|')
        
    return globals()['draw_'+GS['side_screen'].lower()+'_screen'](GS)

frame = 0
def draw_screen(GS):
    global frame
    
    console = GS['console']
    console.clear()

    globals()['draw_'+GS['screen'].lower()+'_screen'](GS, frame)
    frame += 1

    tdl.flush()

def draw_static(console, frame):
    pass

def draw_charsel_screen(GS, frame):
    console = GS['console']
    for (i, race) in enumerate(races.RACES):
        race_display = 'LuB:%d, Sp:%d, MxL:%d; ST:%d, HT: %d' %\
                       (race.level_up_bonus, race.speed, race.levels,
                        race.first_level['strength'], race.first_level['max_health'])
        console.drawStr(int(consts.WIDTH/2)-28, i*2+5,
                        '('+chr(97+i)+') '+race.name+' -> '+race_display)

    draw_static(console, frame)

def draw_intro_screen(GS, frame):
    console = GS['console']
    
    f = Figlet(font='doom')
    l = 24
    for i, line in enumerate(f.renderText(consts.GAME_TITLE).split("\n")):
        if i == 0:
            l = math.floor(len(line)/2)
        console.drawStr(int(consts.WIDTH/2)-l, i+1, line, fg=colors.green)

    console.drawStr(int(consts.WIDTH/2)-12, 18, 'press any key to continue',
                    fg=colors.darken(colors.grey))

    story = [
        'Long ago, the manifestation of the evil Outer Rim crept silently to',
        'earth, bringing with it its hoard of dark and evil creatures.',
        'After a centuries-long battle, humanity finally overcame this god, Kor,',
        'and cast him out. Yet his vast underground realm still existed.',
        'Now, years later, a new creature has taken over Kor\'s old abodes.',
        'Your job is to assasinate him, single-handedly.'
    ]

    for (i, line) in enumerate(story):
        console.drawStr(int(consts.WIDTH/2)-30, 20+i, line, fg=colors.grey)

    draw_static(console, frame)

def draw_death_screen(GS, frame):
    console = GS['console']
    player = GS['player']
    
    console.drawStr(0, 1, 'Game Stats')
    console.drawStr(0, 2, '----------')
    console.drawStr(4, 3, 'Turns: ' + str(GS['turns']))
    console.drawStr(4, 4, 'Score: ' + str(player.score(GS)))
    console.drawStr(4, 5, 'Kills: ' + str(player.killed_monsters))
    console.drawStr(4, 6, 'Exp:   ' + str(player.exp))
    console.drawStr(4, 7, 'Inventory: ')
    for i, g in enumerate(groupby(player.inventory)):
        console.drawStr(8, 8+i, g[0].name + ' x'+str(len(list(g[1]))))

def draw_game_screen(GS, frame):
    console = GS['console']
    GS['messages'] = draw_hud(GS)
    GS['terrain_map'].draw_map(GS, GS['console'], GS['player'], frame)
    
    for m in GS['terrain_map'].dungeon['monsters']:
        fov = GS['terrain_map'].dungeon['lighted'].fov
        if fov[m.pos] or not consts.FOV:
            color = (0,0,0)
            if m.pos in GS['terrain_map'].dungeon['water']:
                color = colors.blue
                
            GS['console'].drawChar(m.pos[0], m.pos[1], m.char, fg=m.fg, bg=color)

    color = (0,0,0)
    if GS['player'].pos in GS['terrain_map'].dungeon['water']:
        color = colors.blue
        
    console.drawChar(GS['player'].pos[0], GS['player'].pos[1], '@', bg=color)


# Refactor to use self.dungeon
def draw_dungeon_tile(terrain_map, GS, console, pos, tint):
    x, y = pos
    if pos == terrain_map.dungeon['down_stairs']:
        console.drawChar(x, y, '>', fg=colors.grey, bg=colors.red)
    elif pos == terrain_map.dungeon['up_stairs']:
        console.drawChar(x, y, '<', fg=colors.grey, bg=colors.blue)
    elif pos in terrain_map.dungeon['items'] and terrain_map.dungeon['items'][pos] != []:
        items = terrain_map.dungeon['items'][pos]
        back = (12,12,12)
        if len(items) > 1:
            back = colors.white
        console.drawChar(x, y, items[-1].char,
                         fg=colors.tint(items[-1].fg, tint),
                         bg=back)
    elif terrain_map.dungeon['decor'][pos] and terrain_map.get_type(pos) == 'STONE':
        decor = terrain_map.dungeon['decor']
        if decor[pos] == 'FM':
            console.drawChar(x, y, '{', fg=colors.tint(colors.grey, tint),
                             bg=colors.tint((0, 100, 0), tint))
    elif terrain_map.dungeon['decor'][pos]:
        decor = terrain_map.dungeon['decor']
        
        if decor[pos] == 'FM':
            if terrain_map.in_area(pos) == 'Planted':
                console.drawChar(x, y, '`', fg=colors.tint(colors.green, tint))
            else:
                area = terrain_map.in_area(pos)
                color = colors.tint((12, 12, 12), tint)
                if area == 'Marble':
                    color = colors.tint((20,20,20), tint)
                elif area == 'Cave':
                    color = colors.tint(colors.extreme_darken(colors.dark_brown), tint)

                console.drawChar(x, y, ' ', fg=colors.darkmed_grey, bg=color)
        elif decor[pos] == 'FR':
            console.drawChar(x, y, '^', fg=colors.darken(colors.red),
                             bg=colors.red)
        elif decor[pos] == 'FL':
            console.drawChar(x, y, '^', fg=colors.darken(colors.yellow),
                             bg=colors.darken(colors.red))
    elif terrain_map.get_type(pos) == 'FLOOR':
        area = terrain_map.in_area(pos)
        color = colors.tint((12, 12, 12), tint)
        if area == 'Marble':
            color = colors.tint((20,20,20), tint)
        elif area == 'Cave':
            color = colors.tint(colors.extreme_darken(colors.dark_brown), tint)
            
        console.drawChar(x, y, ' ', fg=colors.darkmed_grey, bg=color)
    elif terrain_map.get_type(pos) == 'DOOR':
        if terrain_map.dungeon['doors'][pos]:
            console.drawChar(x, y, '-', fg=colors.tint(colors.brown, tint),
                             bg=colors.tint(colors.extreme_darken(colors.brown), tint))
        else:
            console.drawChar(x, y, '\\', fg=colors.tint(colors.brown, tint),
                             bg=colors.tint(colors.black, tint))
    elif terrain_map.get_type(pos) == 'STONE':
        area = terrain_map.in_area(pos)
        color = colors.tint(colors.darkmed_grey, tint)
        if area == 'Marble':
            color = colors.tint(colors.white, tint)
        elif area == 'Cave':
            color = colors.tint(colors.brown, tint)
        
        console.drawChar(x, y, ' ', bg=color) 
    if pos in terrain_map.dungeon['numbers']:
        n = terrain_map.dungeon['numbers'][pos]
        console.drawStr(x, y, str(n), fg=colors.extreme_lighten((n, n, n)))

def draw_forest_tile(terrain_map, console, pos, tint):
    (x, y) = pos
    if not terrain_map.on_map(x+1,y):
        console.drawChar(x, y, '>', fg=colors.grey)
    elif (x, y) in terrain_map.water and terrain_map.water[x, y]:
        l = terrain_map.noise.get_point(x, y)
        color = colors.blue
        if l > 0.17:
            color = colors.light_blue
        elif l > 0.04:
            color = colors.medium_blue
        console.drawChar(x, y, '~', bg=color)
    elif (x, y) in terrain_map.spawned_items:
        console.drawChar(x, y, terrain_map.spawned_items[x, y].char,
                            fg=colors.tint(terrain_map.spawned_items[x, y].fg, tint))
    elif terrain_map.get_type(x, y) == 'FLOOR':
        console.drawChar(x, y, '.')
    elif terrain_map.get_type(x, y) == 'STONE':
        console.drawChar(x, y, '#', fg=colors.dark_grey, bg=colors.grey)
    elif terrain_map.get_type(x, y) == 'TREE':
        console.drawChar(x, y, 'T', fg=colors.tint(colors.green, tint))

def draw_line(GS, a, b, char, start_char=None, end_char=None):
    console = GS['console']

    line(console, a[0], a[1], b[0], b[1], char)
    if start_char:
        console.drawChar(a[0], a[1], start_char, fg=colors.white, bg=colors.black)
    if end_char:
        console.drawChar(b[0], b[1], end_char, fg=colors.black, bg=colors.white)

def line(console, x0, y0, x1, y1, char):
    "Bresenham's line algorithm"
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            console.drawChar(x, y, char, fg=colors.light_blue)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            console.drawChar(x, y, char, fg=colors.light_blue)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
