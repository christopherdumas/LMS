import tdl
import math, random
import maps, monsters, consts, colors, utils, races, player, draw

# I'm truely sorry.
def run_game(GS):
    tdl.setFont('font/consolas12x12_gs_tc.png', greyscale=True, altLayout=True)
    GS = GS or {
        'console': tdl.init(consts.WIDTH, consts.HEIGHT, 'Alchemy Sphere'),
        'screen': 'INTRO',
        'player': player.Player(races.HUMAN),
        'terrain_map': maps.TerrainMap(math.floor(consts.WIDTH/2), consts.HEIGHT),
        'messages': [
            'Welcome ye to the sphere of Alchemy,',
            'a terrible and dangerous World into which',
            'alchemists\' lowely apprentices are dispatched',
            'to either learn their trade the hard way',
            'or die epicly.',
            'Get ye to the last forest, from thence to the',
            'caves. You\'re pereformance will be evaluated.'
        ],
        'side_screen': 'HUD',
        'turns': 0
    }
        
    while True:
        if GS['player'].health <= 0:
            GS['screen'] = 'DEATH'
        draw.draw_screen(GS)

        for event in tdl.event.get():
            if event.type == 'QUIT':
                raise SystemExit('The window has been closed.')
            elif event.type == 'KEYDOWN' and GS['screen'] == 'DEATH':
                if event.keychar.upper() == 'R':
                    run_game(None)
            elif event.type == 'KEYDOWN' and GS['screen'] == 'INTRO':
                GS['screen'] = 'CHARSEL'
            elif event.type == 'KEYDOWN' and GS['screen'] == 'CHARSEL':
                if event.keychar.isalpha():
                    selected_race = races.RACES[ord(event.keychar.lower())-97]
                    GS['player'] = player.Player(selected_race)
                    (GS['player'].x, GS['player'].y) = GS['terrain_map'].generate_new_map()
                    GS['terrain_map'].proweling_monsters = sorted(
                        GS['terrain_map'].proweling_monsters, key=lambda m: m.speed)
                    GS['screen'] = 'GAME'
            elif event.type == 'KEYDOWN' and GS['screen'] == 'GAME':
                if event.keychar.upper() in consts.GAME_KEYS['M'] and GS['side_screen'] != 'MAN':
                    GS['player'].move(event, GS)
                elif event.keychar.upper() in consts.GAME_KEYS['A']:
                    consts.GAME_KEYS['A'][event.keychar.upper()](GS, GS['player'])
                elif event.keychar == '?' and GS['side_screen'] == 'HUD':
                    GS['side_screen'] = 'MAN'
                elif event.keychar == '?' and GS['side_screen'] == 'MAN':
                    GS['side_screen'] = 'HUD'

                if GS['side_screen'] == 'HUD':
                    utils.monster_turn(GS)
                    GS['turns'] += 1
            elif event.type == 'KEYDOWN' and GS['side_screen'] == 'INVENTORY':
                GS['side_screen'] == 'HUD'

run_game(None)
