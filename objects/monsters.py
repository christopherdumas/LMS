import random, math, yaml, copy, os, time, tdl
import colors, utils, consts, items

class Monster:
    def __init__(self,
                 name,
                 char,
                 fg,
                 speed=0,
                 health=0,
                 attack=0,
                 special_action=lambda self, GS, p: -1,
                 agressive=False,
                 ranged=False):
        self.char = char
        self.name = name
        self.pos = (0, 0)
        self.fg = fg
        self.speed = speed
        self.health = health
        self.attack = attack
        self.special_action = special_action
        self.path = []
        self.agressive = agressive
        self.ranged = ranged
        self.player_spotted = False
        self.drops = [items.FOOD_RATION, items.TORCH]*8
        
        self.sight = int(self.speed/2)
        if self.sight < 8:
            self.sight = 8
            if self.ranged:
                self.sight += 3
        
        if self.health >= 20:
            self.drops += items.ITEMS

    # Removes the monster's attack value from the players health, then
    # runs the monster's special action on the player reference.
    def attack_player(self, player, GS):
        miss = random.randint(0, 100) - (self.sight+5)*10
        hit_level = miss_level = ""
        if miss <= 90:
            hit_level = "tremendously "
        elif miss <= 70:
            hit_level = "head-on "
        elif miss <= 60:
            hit_level = "roundly "
        elif miss <= 30:
            hit_level = "painfully "
        elif miss <= 10:
            hit_level = "weakly "
        elif miss <= 0:
            hit_level = "barely "
        elif miss >= 15:
            miss_level = "barely "
        elif miss >= 30:
            miss_level = "closely "
        elif miss >= 50:
            miss_level = "widely "
            
        if miss <= 0:
            GS['messages'].append("red: The monster hits you "+hit_level+".")
            player.health -= self.attack
            self.special_action(self, GS, player)
        else:
            GS['messages'].append("green: The monster "+miss_level+"misses you.")

    # Check equality
    def __eq__(self, other):
        return other != None and self.__dict__ == other.__dict__

    # Gets the returns the points the monster would prefer to go to, or if there
    # are none, the points the monster *can* go to.
    def get_movement_choices(self, tmap, adj):
        valid = list(filter(lambda p:
                            tmap.is_walkable(p), adj))

        def liked(p):
            decor = tmap.dungeon['decor'][p]
            return not p in tmap.dungeon['water'] and decor != 'FL' and decor != 'FR'
        
        like = list(filter(liked, valid))
        
        if len(like) > 0:
            return like
        else:
            return valid

    # Move monster according to choose() and deal with movement effects.
    def move(self, GS):
        self.player_spotted = False
        if GS['turns'] % 20 == 0:
            GS['terrain_map'].dungeon['monsters_alerted'] = False
        sight = self.sight
        if GS['player'].light():
            self.sight = 3

        if utils.dist(GS['player'].pos, self.pos) == 1:
            self.player_spotted = False
            GS['messages'].append('red: The '+self.name+' attacks you.')
            (player_dead, monster_dead) = GS['player'].attack_monster(GS, self)
            if monster_dead:
                GS['messages'].append('yellow: You destroy the '+self.name)
                GS['terrain_map'].dungeon['monsters'].remove(self)
                
                if self.pos in GS['terrain_map'].dungeon['items']:
                    GS['terrain_map'].dungeon['items'][self.pos].append(random.choice(self.drops))
        elif utils.LOS(GS['terrain_map'], self.pos, GS['player'].pos, self.sight)\
             or GS['terrain_map'].dungeon['monsters_alerted']:
            self.player_spotted = True
            if self.ranged:
                p = GS['player']
                m = self
                
                ox = max(0, GS['player'].pos[0]-math.floor(WIDTH/4))
                oy = max(0, GS['player'].pos[1]-math.floor(HEIGHT/2))
                
                start = (m.pos[0]-ox, m.pos[1]-oy)
                end = (p.pos[0]-ox, p.pos[1]-oy)

                animation.FireMissleAnimation().run(GS, [items.WOOD_ARROW, start, end])
                p.health -= self.speed
            elif self.agressive:
                print('aggress')
                if len(self.path) == 0 or self.path[-1] != GS['player'].pos:
                    # Reset the path (A* algorithm)
                    self.path = GS['terrain_map'].dungeon['visited'].compute_path(
                        self.pos[0],
                        self.pos[1],
                        GS['player'].pos[0],
                        GS['player'].pos[1],
                        diagonal_cost=0)
                    self.path.reverse()
                if len(self.path) > 0:
                    npos = self.path.pop()
                    if npos in GS['terrain_map'].dungeon['doors']:
                        GS['terrain_map'].dungeon['doors'] = False
                        GS['terrain_map'].dungeon['lighted'].transparent[npos] = True
                        GS['terrain_map'].dungeon['lighted'].walkable[npos] = True
                    if GS['terrain_map'].is_walkable(npos):
                        self.pos = npos
            else:
                npos = utils.tuple_add(self.pos, (random.randint(-1, 1),
                                              random.randint(-1, 1)))
                if GS['terrain_map'].is_walkable(npos):
                    self.pos = npos
        else:
            npos = utils.tuple_add(self.pos, (random.randint(-1, 1),
                                              random.randint(-1, 1)))
            if GS['terrain_map'].is_walkable(npos):
                self.pos = npos
        self.sight = sight


############################ MONSTER ACTIONS ############################ 
def breed(self, GS, player):
    x, y = self.pos
    posns = [
        (x+1, y),
        (x-1, y),
        (x, y+1),
        (x, y-1),
    ]
    valid = list(filter(GS['terrain_map'].is_walkable, posns))
    if len(valid) > 0 and random.randint(1,2) == 1:
        GS['messages'].append("You chop the slime in half. The new half is alive!")
        if consts.DEBUG:
            print('Slime breeding.')
        slime = copy.copy(Slime)
        slime.pos = random.choice(valid)
        GS['terrain_map'].dungeon['monsters'].append(slime)
        
def filtch(self, GS, player):
    x, y = self.pos
    posns = [
        (x+1, y),
        (x+2, y),
        (x-1, y),
        (x-2, y),
        (x, y+1),
        (x, y+2),
        (x, y-1),
        (x, y-2),
    ]
    valid = list(filter(lambda p: GS['terrain_map'].is_walkable(p), posns))
    
    if len(valid) > 0:
        pos = random.choice(valid)
        items = list(filter(lambda x: x.weight <= 4, player.lin_inventory))

        if len(items) > 0:
            item = random.choice(items)
            player.remove_inventory_item(item)
        
            GS['messages'].append('light_blue: The Imp steals your ' + item.name + ' and throws it.')
            if pos in GS['terrain_map'].dungeon['items']:
                GS['terrain_map'].dungeon['items'][pos].append(item)
            else:
                GS['terrain_map'].dungeon['items'][pos] = [item]
    
def poison(self, GS, player):
    if player.defence <= 5:
        if player.poisoned <= 0 and random.randint(1, 100) < 80:
            player.poisoned = self.health
            GS['messages'].append('green: You have been poisoned!')
    else:
        GS['messages'].append('grey: You\'re armor protects you from bite.')
 
def create_monster(name, mon):
    color = None
    try:
        color = getattr(colors, mon['color'])
    except:
        color = eval(mon['color'])
        
    globals()[name] = Monster(name,
                              mon['char'],
                              color,
                              mon['speed'],
                              mon['health'],
                              mon['attack'])
    if 'action' in mon:
        globals()[name].special_action = globals()[mon['action']]

############################ LOAD MONSTERS ############################ 
monsters = []
yaml_monsters = []
with open("./objects/conf/monsters.yaml", 'r') as stream:
    yaml_monsters = yaml.load(stream)['monsters']

for m in yaml_monsters:
    k, v = list(m.items())[0]
    create_monster(k, v)
    monsters.append(globals()[k])
      
# Selects the correct monster for the current difficulty level based on health and attack.
def select_by_difficulty(d, in_forest=True):
    n = consts.DIFFICULTY
    return list(map(copy.copy, filter(lambda m:
                                      (m.health <= n*(d+1) and\
                                       m.attack >= (n-10)*d) or m == Snake,
                                      monsters)))
