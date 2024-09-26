from swiplserver import PrologMQI, PrologThread


# Функция для выполнения запроса к Prolog
def query(prolog_thread, query_str):
    result = prolog_thread.query(query_str)
    return result


def get_name(characters):
    while True:
        name = input("\nВведите имя персонажа: ")
        character_data = [char for char in characters if char['Name'] == name]
        if character_data:
            break
        else:
            print("Такого персонажа нет. Попробуйте снова.")
    return name


def get_level(prolog_thread, name):
    level = query(prolog_thread, f"level({name}, Level).")[0]['Level']
    print(f"\nУровень персонажа {name}: {level}")
    return level


def get_available_items(prolog_thread, name):
    available_items_from_query = query(prolog_thread, f"find_items({name}, Item).")
    available_items = {}
    print(f"\nДля персонажа {name} доступны предметы ({len(available_items_from_query[0]['Item'])} шт.):")
    for item in available_items_from_query[0]['Item']:
        item_name, slot = item['args']
        available_items[item_name] = slot
        print(f"предмет: {item_name}, часть тела: {slot}")
    return available_items


def recommend_items(prolog_thread, available_items, slots):
    items_for_recommendation = {"Head": None, "Torso": None, "Hands": None}

    for item in available_items:
        slot = slots[available_items[item]]
        if items_for_recommendation[slot] is None:
            items_for_recommendation[slot] = item
        else:
            bonus_a = query(prolog_thread, f"item_bonus({item}, Bonus).")[0]['Bonus']
            bonus_b = query(prolog_thread, f"item_bonus({items_for_recommendation[slot]}, Bonus).")[0]['Bonus']
            if bonus_a > bonus_b:
                items_for_recommendation[slot] = item

    print("\nРекомендуемое снаряжение, для достижения максимальной силы:")
    items = [f"{item}" for slot, item in items_for_recommendation.items() if item is not None]
    print(",".join(items))


def get_equipped_items(available_items, slots):
    input_items = input(
        "\nВведите экипировку (ч/з запятую, ex: шлем_стальной,кольчуга,меч_крутотень):").split(
        ',')
    if len(input_items) == 0 or input_items[0] == '':
        return {}
    res_items = {"Head": None, "Torso": None, "Hands": None}
    for equipped_item in input_items:
        if equipped_item not in available_items:
            print(f"{name} не может использовать {equipped_item}\n")
        else:
            # Если предмет доступен, получаем его слот
            item_slot = available_items[equipped_item]

            # Если слот "голова" и еще не занят
            if item_slot == 'голова':
                if res_items["Head"] is None:
                    res_items["Head"] = equipped_item
                    print(f"{equipped_item} экипирован на голову")
                else:
                    print(f"нелья надеть {equipped_item}, потому что {res_items['Head']} уже на голове")

            # Если слот "туловище" и еще не занят
            elif item_slot == 'туловище':
                if res_items["Torso"] is None:
                    res_items["Torso"] = equipped_item
                    print(f"{equipped_item} экипирован на туловище")
                else:
                    print(f"нелья надеть {equipped_item}, потому что {res_items['Torso']} уже на теле.")

            # Если слот "руки" и еще не занят
            elif item_slot == 'руки':
                if res_items["Hands"] is None:
                    res_items["Hands"] = equipped_item
                    print(f"{equipped_item} экипирован в руки.")
                else:
                    print(f"нелья надеть {equipped_item}, потому что {res_items['Hands']} уже в руках.")

    # Вывод итогового снаряжения
    print("Итоговое снаряжение:")
    for slot in slots:
        if res_items[slots[slot]] is not None:
            print(f"{slot}: {res_items[slots[slot]]}")
        else:
            print(f"{slot}: пусто")
    return res_items


def get_strength(prolog_thread, name, head, torso, hands):
    strength_query = f"character_strength({name}, [{head}, {torso}, {hands}], Strength)"
    strength = query(prolog_thread, strength_query)[0]['Strength']
    print(f"\nСила персонажа {name}: {strength}")
    return strength


def get_monsters(prolog_thread):
    monsters = query(prolog_thread, "monster(Monster).")
    monsters_res = {}  # name: strength, treasure
    print("\nДоступные монстры в игре:")
    for monster in monsters:
        monster_name = monster['Monster']
        print(f"- {monster_name}")
        monster_strength = query(prolog_thread, f"monster_strength({monster_name}, S).")[0]['S']
        monsters_treasure = query(prolog_thread, f"treasure({monster_name}, T).")[0]['T']
        monsters_res[monster_name] = monster_strength, monsters_treasure
    return monsters_res


def find_max_treasure_monster(monsters, n):
    filtered_monsters = {name: stats for name, stats in monsters.items()
                         if stats[0] < n}
    if not filtered_monsters:
        return None
    max_treasure_monster = max(filtered_monsters.items(),
                               key=lambda x: x[0][1])
    return max_treasure_monster


def recommend_monster(monsters, strength):
    monster_recommended = find_max_treasure_monster(monsters, strength)
    if monster_recommended:
        print(f"лучшим монстром для сражения будет {monster_recommended[0]}")
    else:
        print("к сожалению, вы слишком слабы, чтобы победить какого-нибудь монстра, но можете убедиться сами")


def input_monster(monsters):
    while True:
        monster = input("Введите имя монстра, с которым хотите сразиться: ")
        if monster in monsters:
            print(f"Вы выбрали монстра: {monster}")
            break
        else:
            print("Такого монстра нет. Попробуйте снова.")
    return monster


def fighting(prolog_thread, name, head, torso, hands, monster):
    # Проверка, может ли персонаж победить монстра
    can_defeat = query(prolog_thread, f"defeat({name}, [{head}, {torso}, {hands}], {monster}).")
    if can_defeat:
        print(f"\nПерсонаж {name} побеждает монстра {monster}!")
        treasure = \
            query(prolog_thread,
                  f"loot({name}, [{head_item}, {torso_item}, {hands_item}], {monster}, Treasure).")[
                0]['Treasure']
        print(f"Персонаж {name} получает сокровища: {treasure} шт.\n")
    else:
        print(
            f"\nПерсонаж {name} не смог победить монстра {monster}\n")


# Запуск Prolog сервера
with (PrologMQI() as mqi):
    with mqi.create_thread() as prolog_thread:
        # Загрузка файла с базой знаний
        prolog_thread.query("consult('lapa2.pl')")

        # Получение всех персонажей из базы знаний
        characters = query(prolog_thread, "character(Name, Class, Race).")
        while True:
            for char in characters:
                print(f"Персонаж: {char['Name']}, Класс: {char['Class']}, Раса: {char['Race']}")

            name = get_name(characters)

            level = get_level(prolog_thread, name)

            available_items = get_available_items(prolog_thread, name)
            slots = {"голова": "Head", "туловище": "Torso", "руки": "Hands"}
            recommend_items(prolog_thread, available_items, slots)

            equipped_items = get_equipped_items(available_items, slots)
            # Определение силы персонажа на основе экипированных предметов
            head_item = equipped_items["Head"] if "Head" in equipped_items and equipped_items[
                "Head"] is not None else "none"
            torso_item = equipped_items["Torso"] if "Torso" in equipped_items and equipped_items[
                "Torso"] is not None else "none"
            hands_item = equipped_items["Hands"] if "Hands" in equipped_items and equipped_items[
                "Hands"] is not None else "none"

            strength = get_strength(prolog_thread, name, head_item, torso_item, hands_item)

            # Вывод информации о монстрах
            monsters = get_monsters(prolog_thread)  # name: st, tr

            recommend_monster(monsters, strength)

            monster_for_fight = input_monster(monsters)

            fighting(prolog_thread, name, head_item, torso_item, hands_item, monster_for_fight)
