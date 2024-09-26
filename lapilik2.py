from swiplserver import PrologMQI, PrologThread


# Функция для выполнения запроса к Prolog
def query(prolog_thread, query_str):
    result = prolog_thread.query(query_str)
    return result


# Запуск Prolog сервера
with (PrologMQI() as mqi):
    with mqi.create_thread() as prolog_thread:
        # Загрузка файла с базой знаний
        prolog_thread.query("consult('lapa2.pl')")

        # Получение всех персонажей из базы знаний
        characters = query(prolog_thread, "character(Name, Class, Race).")
        print("Персонажи в базе знаний:")
        for char in characters:
            print(f"Персонаж: {char['Name']}, Класс: {char['Class']}, Раса: {char['Race']}")

        # Ввод имени персонажа пользователем
        while True:
            name = input("Введите имя персонажа для рекомендации: ")
            character_data = [char for char in characters if char['Name'] == name]
            if character_data:
                print(f"Вы выбрали персонажа: {name}")
                break
            else:
                print("Такого персонажа нет. Попробуйте снова.")

        # Получение текущего уровня и силы персонажа
        level = query(prolog_thread, f"level({name}, Level).")[0]['Level']
        print(f"\nУровень персонажа {name}: {level}")
        # Проверка доступных предметов для персонажа
        available_items_from_query = query(prolog_thread, f"find_items({name}, Item).")
        available_items = {}
        slots = {"голова": "Head", "туловище": "Torso", "руки": "Hands"}
        print(f"\n{len(available_items_from_query[0]['Item'])} предметов доступны для персонажа {name}:")
        for item in available_items_from_query[0]['Item']:
            item_name, slot = item['args']
            available_items[item_name] = slot
            print(f"Предмет: {item_name}, Слот: {slot}")

        items_for_recomendation = {"Head": None, "Torso": None, "Hands": None}
        for item in available_items:
            slot = slots[available_items[item]]
            if items_for_recomendation[slot] is None:
                items_for_recomendation[slot] = item
            else:
                bonus_a = query(prolog_thread, f"item_bonus({item}, Bonus).")[0]['Bonus']
                bonus_b = query(prolog_thread, f"item_bonus({items_for_recomendation[slot]}, Bonus).")[0]['Bonus']
                if bonus_a > bonus_b:
                    items_for_recomendation[slot] = item

        print("\nрекомендуемое снаряжение, для достижения максимальной силы:")
        items = [f"{item}" for slot, item in items_for_recomendation.items()]
        print(",".join(items))

        equipped_items = input(
            "\nВведите экипированные предметы (через запятую, например: шлем_стальной,кольчуга,меч_крутотень) или нажмите enter: ").split(
            ',')
        equipped_items = [item.strip() for item in equipped_items]
        items_for_query = {"Head": None, "Torso": None, "Hands": None}
        for equipped_item in equipped_items:
            if equipped_item not in available_items:
                print(f"{name} не может использовать {equipped_item}\n")
            else:
                # Если предмет доступен, получаем его слот
                item_slot = available_items[equipped_item]

                # Если слот "голова" и еще не занят
                if item_slot == 'голова':
                    if items_for_query["Head"] is None:
                        items_for_query["Head"] = equipped_item
                        print(f"{equipped_item} экипирован на голову")
                    else:
                        print(f"нелья надеть {equipped_item}, потому что {items_for_query['Head']} уже на голове")

                # Если слот "туловище" и еще не занят
                elif item_slot == 'туловище':
                    if items_for_query["Torso"] is None:
                        items_for_query["Torso"] = equipped_item
                        print(f"{equipped_item} экипирован на туловище")
                    else:
                        print(f"нелья надеть {equipped_item}, потому что {items_for_query['Torso']} уже на теле.")

                # Если слот "руки" и еще не занят
                elif item_slot == 'руки':
                    if items_for_query["Hands"] is None:
                        items_for_query["Hands"] = equipped_item
                        print(f"{equipped_item} экипирован в руки.")
                    else:
                        print(f"нелья надеть {equipped_item}, потому что {items_for_query['Hands']} уже в руках.")

        # Вывод итогового снаряжения
        print("Итоговое снаряжение:")
        for slot, item in items_for_query.items():
            print(f"{slot}: {item if item else 'Пусто'}")

        # Определение силы персонажа на основе экипированных предметов
        head_item = items_for_query["Head"] if items_for_query["Head"] is not None else "none"
        torso_item = items_for_query["Torso"] if items_for_query["Torso"] is not None else "none"
        hands_item = items_for_query["Hands"] if items_for_query["Hands"] is not None else "none"
        strength_query = f"character_strength({name}, [{head_item}, {torso_item}, {hands_item}], Strength)"
        strength = query(prolog_thread, strength_query)[0]['Strength']
        print(f"\nСила персонажа {name} с экипированными предметами: {strength}")

        # Вывод информации о монстрах
        monsters = query(prolog_thread, "monster(Monster).")
        monsters_data = {}  # name: strength, treasure
        print("\nДоступные монстры в игре:")
        for monster in monsters:
            monster_name = monster['Monster']
            monster_strength = query(prolog_thread, f"monster_strength({monster_name}, S).")[0]['S']
            if strength > monster_strength:
                monsters_data[monster_name] = [
                    query(prolog_thread, f"treasure({monster_name}, T).")[0]['T']
                ]
            print(f"- {monster_name}")

        if monsters_data:
            max_value = max(monsters_data.values())
            max_monster = next(key for key, value in monsters_data.items() if value == max_value)
            print(f"лучшим монстром для сражения будет {max_monster}")
        else:
            print("к сожалению, вы слишком слабы, чтобы победить какого-нибудь монстра, но можете убедиться сами")

        # Ввод имени монстра для сражения
    while True:
        monster = input("Введите имя монстра, с которым хотите сразиться: ")
        if any(m['Monster'] == monster for m in monsters):
            print(f"Вы выбрали монстра: {monster}")
            break
        else:
            print("Такого монстра нет. Попробуйте снова.")

    # Проверка, может ли персонаж победить монстра
    can_defeat = query(prolog_thread, f"defeat({name}, [{head_item}, {torso_item}, {hands_item}], {monster}).")
    if can_defeat:
        print(f"\nПерсонаж {name} может победить монстра {monster}!")
        treasure = query(prolog_thread, f"loot({name}, [{head_item}, {torso_item}, {hands_item}], {monster}, Treasure).")[0]['Treasure']
        print(f"После победы персонаж {name} получит {treasure} сокровищ.")
    else:
        print(
            f"\nПерсонаж {name} не может победить монстра {monster}. Попробуйте улучшить экипировку или выбрать другого монстра.")
