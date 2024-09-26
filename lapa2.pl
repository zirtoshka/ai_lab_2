% Факты: классы персонажей
class(воин).
class(волшебник).
class(вор).
class(карлик).

% Факты: расы персонажей
race(человек).
race(эльф).
race(дварф).
race(халфлинг).

% Факты: персонажи и их классы/расы
character(мурлок, воин, человек).
character(зорник, волшебник, эльф).
character(гимли, вор, дварф).
character(фродо, карлик, халфлинг).

% Факты: предметы, которые могут использовать персонажи (имя, класс, куда, раса)
item(меч_крутотень, воин, руки, _).
item(посох_заклинатель, волшебник, руки, _).
item(кинжал_удачка, вор, руки, _).
item(шлем_стальной, _, голова, _).    % любой персонаж может носить шлем
item(кольчуга, _, туловище, _).       % любой персонаж может носить кольчугу
item(щит_дварфов, _, руки, дварф).  % щит может носить только дварф
item(лук_эльфов, _, руки, эльф).     % лук может носить только эльф
item(плащ_невидимки, _, туловище, халфлинг). % только халфлинги могут носить плащ

% Факты: уровни персонажей
level(мурлок, 5).
level(зорник, 4).
level(гимли, 3).
level(фродо, 6).

% Факты: монстры в игре
monster(дракон).
monster(скелетон).
monster(огр).
monster(гоблин).

% Факты: сила монстров
monster_strength(дракон, 20).
monster_strength(скелетон, 10).
monster_strength(огр, 15).
monster_strength(гоблин, 8).

% Факты: сокровища, которые можно получить, убив монстра
treasure(дракон, 3).
treasure(скелетон, 1).
treasure(огр, 2).
treasure(гоблин, 2).


% Бонусы от предметов (фиксированные значения)
item_bonus(меч_крутотень, 5).
item_bonus(посох_заклинатель, 4).
item_bonus(кинжал_удачка, 3).
item_bonus(шлем_стальной, 2).
item_bonus(кольчуга, 4).
item_bonus(щит_дварфов, 3).
item_bonus(лук_эльфов, 5).
item_bonus(плащ_невидимки, 5).


% Правило: Персонаж может использовать предмет, если его класс или раса подходят
can_use(Character, Item, Slot) :-  /* Race is important here */
    character(Character, Class, Race),
    item(Item, Class, Slot, Race).       % Предмет для всех

find_items(Character, Items) :-
    setof((Item, Slot), can_use(Character, Item, Slot), Items).

% Правило: Персонаж не может использовать больше предметов, чем у него есть рук, голов и т.д.
% Теперь учитываем возможность использования двуручного оружия
valid_equipment(Character, [Head, Torso, Hands]) :-
    (Head = none; can_use(Character, Head, голова)),    % Шлем или отсутствие
    (Torso = none; can_use(Character, Torso, туловище)), % Броня или отсутствие
    (Hands = none; can_use(Character, Hands, руки)). % руки предмет

% Правило: получение бонусов от экипированных предметов
equipped_item_bonus(Character, [Head, Torso, Hands], Bonus) :-
    valid_equipment(Character, [Head, Torso, Hands]),
    (Head = none -> HeadBonus = 0; item_bonus(Head, HeadBonus)),
    (Torso = none -> TorsoBonus = 0; item_bonus(Torso, TorsoBonus)),
    (Hands = none -> HandsBonus = 0; item_bonus(Hands, HandsBonus)),
    Bonus is HeadBonus + TorsoBonus + HandsBonus.

% Правило: Определение силы персонажа (уровень + бонус за предметы)
character_strength(Character,[Head, Torso, Hands], Strength) :-
    level(Character, Level),
    equipped_item_bonus(Character, [Head, Torso, Hands], Bonuses),
    Strength is Level + Bonuses.


% Правило: Персонаж побеждает монстра, если его сила больше силы монстра
defeat(Character,[Head, Torso, Hands], Monster) :-
    character_strength(Character, [Head, Torso, Hands], Strength),
    monster_strength(Monster, MonsterStrength),
    Strength > MonsterStrength.

% Правило: Получение сокровища после победы над монстром
loot(Character,[Head, Torso, Hands], Monster, Treasure) :-
    defeat(Character,[Head, Torso, Hands], Monster),
    treasure(Monster, Treasure).
