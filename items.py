class Item:
    def __init__(self, name='Unknown item', weight=1, probability=50, char='*'):
        self.name = name
        self.weight = weight
        self.probability = probability
        self.char = char

    def equip(self, player):
        pass

class Armor(Item):
    def __init__(self, name='Unknown armor', weight=3, probability=40, char=']'):
        super().__init__(name=name, weight=weight, probability=probability, char=char)

    def equip(self, player):
        player.defence = self.weight
    
class Weapon(Item):
    def __init__(self, name='Unknown weapon', weight=2, attack=5, probability=20, char='|'):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.attack = attack
        
    def equip(self, player):
        player.max_attack = player.attack = self.attack

class RangedWeapon(Item):
    def __init__(self, name='Unknown ranged weapon', weight=2, probability=20, char=')',
                 missle_type='Arrow', range=8):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.missle_type = missle_type
        self.range = range

    def equip(self, player):
        player.ranged_weapon = self

class Missle(Item):
    def __init__(self, name='Regular Arrow', weight=0, probability=45, char='-', hit=1):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.missle_type = name.split()[1]
        self.hit = hit

    def equip(self, player):
        player.missles.append(self)

ITEMS = [
    Weapon('Broad sword', weight=10, attack=20, probability=12, char='|'),
    Weapon('Fencing foil', weight=1, attack=10, probability=15, char='`'),
    Weapon('Thrusting sword', weight=5, attack=15, char='/', probability=8),
    Weapon('Short sword', attack=12, weight=2, char='(', probability=22),
    Armor('Breastplate', probability=30, char='['),
    Armor('Sheild', weight=2),
    Armor('Elven Helm', weight=1, probability=45, char='*'),
    RangedWeapon('Light Bow', weight=1, probability=25, range=10),
    Missle('Wooden Arrow', hit=30, char='_'),
    Missle()
]

for i in ITEMS: globals()[i.name.replace(' ', '_').upper()] = i
