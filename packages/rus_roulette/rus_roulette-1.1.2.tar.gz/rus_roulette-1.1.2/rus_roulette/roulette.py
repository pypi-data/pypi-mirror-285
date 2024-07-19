import random as rnd
import sys
import time

sys.setrecursionlimit(100000)


def roulette():
    global lv, final, item_c, item_u, dev, store, showData, oneRound, higherDealerHealth, dmg, gm, player_hp, dealer_hp, blank_a, round_a, rapidfire, rapidfire_c

    print('Russian roulette in python')

    # Standard
    lv = 1
    final = False
    item_c = 0
    item_u = False
    dev = False
    store = None
    gm = 'Standard gamemode'
    dif = 2
    dif_s = 'normal'
    rapidfire = ''
    rapidfire_c = 0.5

    # Gamemode modifiers
    showData = True
    oneRound = False
    higherDealerHealth = False
    dmg = 1
    canDie = True
    randomAfterShot = False

    # Custom
    scalePlayerHp = True
    scaleDealerHp = True
    scaleHealthAmountP = 1
    scaleHealthAmountD = 1

    it = '\033[3m'
    n = '\033[0m'

    time.sleep(0.1)
    custom = input(f'{it}Custom? (y/n): {n}') == 'y'
    time.sleep(0.1)

    def dif_gm():
        global dev, dif, dif_s, showData, oneRound, higherDealerHealth
        global dmg, gm, canDie, randomAfterShot
        canDie = input('Practice mode? (Become immortal) (y/n): ') != 'y'

        time.sleep(0.1)

        dif_c = input(
            'DIFFUCULTY SELECT\nEnter: 0 for easy, 1 for hard, anything else for normal: '
        )
        if dif_c == '0':
            dif = 0
            dif_s = 'easy'
        elif dif_c == '1':
            dif = 1
            dif_s = 'hard'
        elif dif_c == 'dev 0':
            dif = 0
            dif_s = 'easy (dev)'
            dev = True
            print(f'{it}Dev mode enabled{n}')
        elif dif_c == 'dev 1':
            dif = 1
            dif_s = 'hard (dev)'
            dev = True
            print(f'{it}Dev mode enabled{n}')
        elif dif_c == 'dev':
            dif = 2
            dif_s = 'normal (dev)'
            dev = True
            print(f'{it}Dev mode enabled{n}')
        else:
            dif = 2
            dif_s = 'normal'

        time.sleep(0.1)

        gm_c = input(
            '''\nGAMEMODE SELECT\nEnter 0 for standard, 1 for unknown stats, 2 for one round,
      3 for dual wield, 4 for high dealer health, 5 for randomise bullets every shot,
      or 6 for ALL of them: ''')
        if gm_c == '1':
            showData = False
            gm = 'Unknown stats gamemode'
        elif gm_c == '2':
            oneRound = True
            gm = 'One round gamemode'
        elif gm_c == '3':
            dmg = 2
            gm = 'Dual wield gamemode'
        elif gm_c == '4':
            higherDealerHealth = True
            gm = 'High dealer health gamemode'
        elif gm_c == '5':
            randomAfterShot = True
            gm = 'Randomise bullets every shot gamemode'
        elif gm_c == '6':
            gm = 'ALL gamemode'
            showData = False
            oneRound = True
            dmg = 2
            higherDealerHealth = True

        time.sleep(0.1)

    def custom_setup():
        global roundMin, roundMax, blankMin, blankMax  # Bullets
        global finalRoundMin, finalRoundMax, finalBlankMin, finalBlankMax  # Bullets (Final)
        global scalePlayerHp, scaleDealerHp, scaleHealthAmountP, scaleHealthAmountD  # Hp scale
        global gm  # Other
        gm = 'Custom'

        roundMin = int(input('Set round min: '))
        roundMax = int(input('Set round max: '))
        blankMin = int(input('Set blank min: '))
        blankMax = int(input('Set blank max: '))
        finalRoundMin = int(input('Set (level final) round min: '))
        finalRoundMax = int(input('Set (level final) round max: '))
        finalBlankMin = int(input('Set (level final) blank min: '))
        finalBlankMax = int(input('Set (level final) blank max: '))

        scalePlayerHp = input('Scale player health by level? (y/n): ') == 'y'
        scaleDealerHp = input('Scale dealer health by level? (y/n): ') == 'y'
        if scalePlayerHp:
            scaleHealthAmountP = int(input('Set player health scale amount: '))
        if scaleDealerHp:
            scaleHealthAmountD = int(input('Set dealer health scale amount: '))

    custom_setup() if custom else None
    dif_gm()

    hints = [
        f'{it}Developer mode?{n}', f'{it}Dying is bad, don\'t die{n}',
        f'{it}Dying is fine, just try again.{n}', f'{it}Hard != easy{n}',
        f'{it}Normal = rnd.randint(){n}', f'{it}Easy != hard{n}',
        f'{it}[RESET TO CHECKPOINT]{n}',
        f'{it}1. Enable cheats on hard 2. "+health" 3. "+round" 4. "YOU"{n}'
    ]

    def prep():
        global player_hp, dealer_hp
        player_hp = (lv * scaleHealthAmountP) + 1 if scalePlayerHp else 2
        dealer_hp = (lv * scaleHealthAmountD) + 1 if scaleDealerHp else 2

        dealer_hp *= 2 if higherDealerHealth else 1

        if final:
            player_hp = 10
            dealer_hp = 10 if not higherDealerHealth else 100

    def prepb():
        global blank_a, round_a  # Normal
        global roundMin, roundMax, blankMin, blankMax  # Custom
        global finalRoundMin, finalRoundMax, finalBlankMin, finalBlankMax  # Custom (Final)

        roundMin = 1 if not custom else roundMin
        roundMax = 2 if not custom else roundMax
        blankMin = 1 if not custom else blankMin
        blankMax = 2 if not custom else blankMax

        finalRoundMin = 1 if not custom else finalRoundMin
        finalRoundMax = 15 if not custom else finalRoundMax
        finalBlankMin = 1 if not custom else finalBlankMin
        finalBlankMax = 15 if not custom else finalBlankMax

        blank_a = rnd.randint(blankMin, blankMax)
        round_a = rnd.randint(roundMin, roundMax)

        if final:
            blank_a = rnd.randint(finalBlankMin, finalBlankMax)
            round_a = rnd.randint(finalRoundMin, finalRoundMax)

        if oneRound:
            round_a = 1
            blank_a = rnd.randint(3, 5)

    def main():
        global lv, item_c, rapidfire, rapidfire_c

        rapidfire = ''
        rapidfire_c = 0.5
        lv_d = lv if not final else 'FINAL'
        prep()
        prepb()
        time.sleep(0.1)
        print(f'Level {lv_d} ({gm})')
        time.sleep(0.1)
        round()

        if dealer_hp == 0:
            print(f'YOU WIN LEVEL {lv_d} ({gm})!')
            lv += 1
            item_c += 1
            time.sleep(0.1)
        else:
            print('LOSE. TRY AGAIN')
            time.sleep(0.1)
            print(rnd.choice(hints))
            time.sleep(0.1)

        if lv == 6 or lv == 7:
            return

        main()

    def round():
        print()
        global player_hp, dealer_hp, blank_a, round_a, item_c, item_u, store

        if player_hp == 0 or dealer_hp == 0:
            return

        if blank_a == 0 and round_a == 0:
            print('Reloading...')
            time.sleep(0.5)
            print('GUN RELOADED')
            prepb()

        prepb() if randomAfterShot else None

        if blank_a or round_a != 0:
            type_p = blank_a / round_a
        elif blank_a == 0:
            type_p = 0
        else:
            type_p = 1

        type = 'blank' if rnd.uniform(0, 1) < type_p else 'round'
        if item_u:
            type = store
            item_u = False

        print(
            f'''Your health: {player_hp}\nDealer health: {dealer_hp}\n{blank_a} blank(s). 
    {round_a} round(s).''') if showData else print('STATS OFF (Unknown stats on)')

        time.sleep(0.25)

        choice = input(f'Shoot YOU or DEALER or use ITEM({item_c}): ')
        if choice == 'YOU':
            if type == 'round':
                player_hp -= dmg if canDie else 0
                round_a = round_a - 1
                print(f'ROUND. -{dmg} HP')
                d_round()
            elif type == 'blank':
                blank_a = blank_a - 1
                print('BLANK. YOUR TURN')
                round()
        elif choice == 'DEALER':
            if type == 'round':
                dealer_hp -= dmg
                round_a = round_a - 1
                print(f'ROUND. DEALER -{dmg} HP')
                round()
            elif type == 'blank':
                blank_a = blank_a - 1
                print('BLANK. DEALER TURN')
                d_round()
        elif choice == 'ITEM':
            if item_c != 0:
                item_c -= 1
                item_u = True
                store = type
                print(f'\n{it}The next bullet is a {store}{n}')
                time.sleep(0.1)
                round()
        elif choice == '+item' and dev:
            item_c += 1000000
            round()
        elif choice == 'kill' and dev:
            dealer_hp = 0
            print('instakill')
            round()
        elif choice == '+health' and dev:
            dealer_hp = 9999
            player_hp = 9999
            round()
        elif choice == '+round' and dev:
            blank_a = 0
            round_a = 9999
            round()
        else:
            time.sleep(0.1)
            print('\nUNKNOWN ACTION\nuse "YOU" or "DEALER" or "ITEM"\n')

        round()

    def d_round():
        print()
        global player_hp, dealer_hp, blank_a, round_a, rapidfire, rapidfire_c

        if player_hp == 0 or dealer_hp == 0:
            return

        if blank_a == 0 and round_a == 0:
            print('Reloading...')
            time.sleep(0.5)
            print('GUN RELOADED')
            prepb()

        prepb() if randomAfterShot else None

        if blank_a or round_a != 0:
            type_p = blank_a / round_a
        elif blank_a == 0:
            type_p = 0
        else:
            type_p = 1

        type = 'blank' if rnd.uniform(0, 1) < type_p else 'round'

        if dif == 0:
            choice = 'self' if type_p < 0.5 else 'player'
        elif dif == 1:
            choice = 'self' if type_p > 0.5 else 'player'
        else:
            choice = 'self' if rnd.randint(0, 1) > 0.5 else 'player'

        time.sleep(rapidfire_c)
        rapidfire_c -= 0.1 if choice == rapidfire and rapidfire_c > 0.2 else 0

        if choice == 'self':
            print('DEALER SHOOT SELF')
            if type == 'round':
                dealer_hp -= dmg
                round_a = round_a - 1
                print(f'ROUND. DEALER -{dmg} HP')
                rapidfire = ''
                rapidfire_c = 0.5
                round()
            elif type == 'blank':
                blank_a = blank_a - 1
                print('BLANK. DEALER TURN')
                rapidfire = 'self'
                d_round()
        elif choice == 'player':
            print('DEALER SHOOT PLAYER')
            if type == 'round':
                player_hp -= dmg if canDie else 0
                round_a = round_a - 1
                print(f'ROUND. -{dmg} HP')
                rapidfire = 'player'
                d_round()
            elif type == 'blank':
                blank_a = blank_a - 1
                print('BLANK. YOUR TURN')
                rapidfire = ''
                rapidfire_c = 0.5
                round()

    main()

    final = True

    main()

    time.sleep(0.1)
    print(f'CONGRAGULATIONS! YOU WIN!\nOn {dif_s} difficulty... ({gm})')
    time.sleep(0.1)
    if not canDie:
        print('Now try without immortality!')
    elif dev:
        print('Now try without dev mode on!')

