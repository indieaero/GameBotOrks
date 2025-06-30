import telebot 
from random import randint 
from telebot import types 
import random
import os

bot = telebot.TeleBot('')

game_data = dict()

#Version v1.0 

#Game Data 
class PlayerSession:
    def __init__(self):
        self.hero = Hero()
        self.ork = Orcs()
        self.fight_mode = 1
        self.enemynumber = 1 
        self.player_alive = True
    
#Hero
class Hero:
    def __init__(self):
        self.HP = 75
        self.focus = 4
        self.poison = 0
        self.bleeding = 0
        
    #Hero Attack
    def attack(self, message, target):
        
        chance = random.random()
        base_damage = randint(15,25)
        damage = base_damage - 10
        if chance < 0.2:
            bot.send_message(chat_id=message.chat.id, text=f"Крит!⚡")
            damage *= 2
            bleeding_ork_chance = random.randint(1,3) 
            if bleeding_ork_chance == 1:
                target.bleeding = 6
                bot.send_message(chat_id=message.chat.id, text=f"У орка кровотечение!\nHP орка понижается на: -{target.bleeding}!🩸")   
        target.HP -= damage  
        bot.send_message(chat_id=message.chat.id, text=f"Вы наносите: {damage} урона\nУровень HP орка: {target.HP}")

    #Hero Attack + Focus  
    def attack_focus_use(self,message,target):

        self.focus -= 1
        bot.send_message(chat_id=message.chat.id, text="Фокус использован! Крит шанс повышен!")
        chance = random.random()
        base_damage = randint(15,25)
        damage = base_damage - 10
        if chance < 0.9:
            bot.send_message(chat_id=message.chat.id, text="Крит!")
            damage *= 3
            bleeding_ork_chance = random.randint(1,3) 
            if bleeding_ork_chance == 1:
                target.bleeding = 6
                bot.send_message(chat_id=message.chat.id, text=f"У орка кровотечение!\nHP орка понижается на: -{target.bleeding}!🩸")     
        target.HP -= damage  
        bot.send_message(chat_id=message.chat.id, text=f"Вы наносите: {damage} урона\nУровень HP орка: {target.HP}") 
        
    #Hero bleeding + poison
    def update(self, message):
        if self.bleeding > 0:
            self.HP -= self.bleeding
            bot.send_message(chat_id=message.chat.id, text=f"У вас кровотечение!\nУровень здоровья: -{self.bleeding}!🩸\nИспользуйте лечение или найдите лекарство!")  
        if self.poison == 1:
            self.HP -= 6
            bot.send_message(chat_id=message.chat.id, text=f"Вы отравлены! Уровень здоровья: -{self.poison_sum}!🩸\nИспользуйте лечение, чтобы снять отравление!")
        if self.HP <= 0:
            on_hero_killed(message) 

#Orc
class Orcs:
    def __init__(self):
        self.HP = 50
        self.bleeding = 0

    #Ork attack
    def attack(self, message, target):
        
        crit_chance_ork_chance = random.random()
        damage = randint(6,20)
        if crit_chance_ork_chance < 0.3:
            damage *= 2
            target.HP -= damage
            bot.send_message(chat_id=message.chat.id, text=f"Орк в ярости и наносит {damage} критического урона!🪓\nУровень HP героя: {target.HP}")   
            bleeding_hero_chance = random.randint(1,2) 
            if bleeding_hero_chance == 1:
                target.bleeding += 8
                bot.send_message(chat_id=message.chat.id, text=f"Ваша рана кровоточит!\nУровень здоровья понижается на: -{target.bleeding}!🩸\nНужно лечиться или принимать лекарство!")   
        else:
            target.HP -= damage         
            bot.send_message(chat_id=message.chat.id, text=f"Орк замахивается и наносит: {damage} урона \nУровень HP героя: {target.HP}")

        if target.HP <= 0:
            on_hero_killed(message)
            
    #Ork bleeding 
    def update(self, message):
        if self.bleeding > 0:
            bot.send_message(chat_id=message.chat.id, text=f"""У орка течет кровь!\nУровень HP орка понижается на: -6!💢 """)
            self.HP -= self.bleeding
            bot.send_message(chat_id=message.chat.id, text=f"Уровень HP орка: {self.HP}")
            

#Ork death
def on_ork_killed(message):
    session = game_data[message.chat.id]
    focus_chance = random.randint(1,2)
    if focus_chance == 1:
        session.hero.focus += 1
        bot.send_message(chat_id=message.chat.id, text=f"Вы получаете: +1 Фокус!⚡️")
    session.enemynumber += 1 
    bot.send_message(chat_id=message.chat.id, text=f"Орк убит.")
    bot.send_photo(message.chat.id, openfile('Assets/images/ork_death.png'))
    bot.send_audio(message.chat.id, openfile('Assets/sounds/Ork_death.mp3'))
    ChanceElixir = 2 #random.randint(1,2)
    if ChanceElixir == 2:
        session.fight_mode = 0
        hide_markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Вы обыскиваете орка...', reply_markup=hide_markup)
        #bot.send_message(message.chat.id, text=f"Вы обыскиваете орка...")
        kb1 = types.InlineKeyboardMarkup(row_width = 1)
        btn1 = types.InlineKeyboardButton(text='Выпить зелье 🍷', callback_data='btn1')
        btn2 = types.InlineKeyboardButton(text='Пройти дальше 🏃', callback_data='btn2')
        kb1.add(btn1, btn2) 
        bot.send_message(message.chat.id, text=f"В ваших руках странное зелье.\nЭто может быть лекарство или яд... Осмелитесь выпить?", reply_markup = kb1)

    else:
        session.ork = Orcs()
        bot.send_message(chat_id=message.chat.id, text=f"""Здоровье героя: {session.hero.HP}, Фокус: {session.hero.focus}\nОрк {session.enemynumber}: Здоровье: {session.ork.HP}""")
        bot.send_message(chat_id=message.chat.id, text=f"""Выберете действие!""")         
            
#Hero death
def on_hero_killed(message):
    session = game_data[message.chat.id]
    session.player_alive = False
    hide_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Вы убиты.💀", reply_markup=hide_markup)
    bot.send_photo(message.chat.id, openfile('Assets/images/hero_death.jpg'))
    bot.send_audio(message.chat.id, openfile('Assets/sounds/Ork_mockery.mp3'))
    session.enemynumber -= 1
    bot.send_message(chat_id=message.chat.id, text=f"Количество орков: {session.enemynumber} \nСыграем еще раз? Нажмите: /start")

#Openfile
def openfile(relative_path):
    current_directory = os.path.dirname(__file__)
    absolute_path = os.path.join(current_directory, relative_path)
    return open(absolute_path, 'rb')   

  
#Start Game
@bot.message_handler(commands=['start'])
def start(message):
    session = PlayerSession()
    game_data[message.chat.id] = session
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1) 
    btn1 = types.KeyboardButton(text='Удар ⚔️')
    btn2 = types.KeyboardButton(text='Фокус ⚡️')
    btn3 = types.KeyboardButton(text='Лечение ✨')
    kb.add(btn1,btn2,btn3)
    bot.send_message(message.chat.id, text=f"""Добро пожаловать в Orks!""", reply_markup=kb)
    bot.send_message(message.chat.id, text=f"""Одолейте как можно больше орков!🔥""")
    bot.send_photo(message.chat.id, openfile('Assets/images/ork_opening.jpg'))
    bot.send_audio(message.chat.id, openfile('Assets/sounds/Ork_watchword.mp3'))
    bot.send_message(chat_id=message.chat.id, text=f"""Здоровье героя: {session.hero.HP}, Фокус: {session.hero.focus}\nОрк {session.enemynumber}: Здоровье: {session.ork.HP}""")
    bot.send_message(chat_id=message.chat.id, text=f"""Выберете действие!""")


#Attack
@bot.message_handler(func=lambda message: message.text == 'Удар ⚔️') 
def action_1(message): 
    
    session = game_data[message.chat.id]
    
    if session.player_alive == True:
        
        if session.fight_mode == 1:
            
            if session.ork.HP <= 0:
                session.ork = Orcs()

            session.hero.attack(message, session.ork)
            if session.ork.HP <= 0:
                on_ork_killed(message)
                return
            
            session.hero.update(message)
            if session.hero.HP <= 0: return
            
            session.ork.attack(message, session.hero)
            if session.hero.HP <= 0: return
                
            session.ork.update(message)
            if session.ork.HP > 0:
                bot.send_message(chat_id=message.chat.id, text=f"""Ваш ход!""")
                
            if session.ork.HP <= 0:
                on_ork_killed(message)
                
        else:
            bot.send_photo(message.chat.id, openfile('Assets/images/ork_death_1.jpeg'))
            bot.send_message(chat_id=message.chat.id, text=f"Вы пронзаете своим клинком мертвое тело орка, кровь брызжет на вас, но его глаза все еще сверкают злобой.\nДаже смерть не смогла побороть его жажду убийства и жестокости.")
    else:        
        bot.send_message(chat_id=message.chat.id, text=f"GAME OVER.\nНажмите: /start")

               
#Elixir Chance
@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    
    session = game_data[callback.message.chat.id]
    
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1) 
    btn1 = types.KeyboardButton(text='Удар ⚔️')
    btn2 = types.KeyboardButton(text='Фокус ⚡️')
    btn3 = types.KeyboardButton(text='Лечение ✨')
    kb.add(btn1,btn2,btn3)
    #bot.send_message(callback.message.chat.id, text=f"""ㅤ""", reply_markup=kb)
    session.fight_mode = 1
    
    if callback.data == 'btn1':
        poison_chance = random.randint(1,3)
        if poison_chance == 2:
            bot.send_message(callback.message.chat.id, text=f"""Это оказался лечебный эликсир!💧""", reply_markup=kb)
            bot.send_message(callback.message.chat.id, 'Здоровье героя + 20!💫')
            session.hero.bleeding = 0
            session.hero.poison = 0
            session.hero.HP += 20
            kb1 = types.InlineKeyboardMarkup(row_width = 1)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text='Решившись выпить странное зелье, вы ощущаете прилив сил.', reply_markup=kb1)
            if session.ork.HP <= 0:
                session.ork = Orcs()
                bot.send_message(callback.message.chat.id, text=f"""Здоровье героя: {session.hero.HP}, Фокус: {session.hero.focus}\nОрк {session.enemynumber}: Здоровье: {session.ork.HP}""")
                bot.send_message(callback.message.chat.id, text=f"""Выберете действие!""")
        else:
            session.hero.poison =+ 6
            bot.send_message(callback.message.chat.id, text=f"""Это оказался яд, вы отравлены!🧪""", reply_markup=kb)
            bot.send_message(callback.message.chat.id, text=f'Уровень здоровья понижается на: -{session.hero.poison}!🩸\nЛечитесь, чтобы спастиcь!')
            session.hero.HP -= session.hero.poison
            kb1 = types.InlineKeyboardMarkup(row_width = 1)
            btn1 = types.InlineKeyboardButton(text='Очень жаль.', callback_data='btn1')
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text='В следующий раз повезёт!', reply_markup=kb1)
            if session.ork.HP <= 0:
                session.ork = Orcs()
                bot.send_message(callback.message.chat.id, text=f"""Здоровье героя: {session.hero.HP}, Фокус: {session.hero.focus}\nОрк {session.enemynumber}: Здоровье: {session.ork.HP}""")
                bot.send_message(callback.message.chat.id, text=f"""Выберете действие!""")

    else: 
        if callback.data == 'btn2':
            kb1 = types.InlineKeyboardMarkup(row_width = 1)
            btn2 = types.InlineKeyboardButton(text='Вы прошли мимо.', callback_data='btn2')
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text='Не осмелившись выпить эликсир, вы проходите дальше.', reply_markup=kb1)
            bot.send_message(callback.message.chat.id, text=f"""Впереди новый орк! ⚔️""", reply_markup=kb)
            if session.ork.HP <= 0:
                session.ork = Orcs()
                bot.send_message(callback.message.chat.id, text=f"""Здоровье героя: {session.hero.HP}, Фокус: {session.hero.focus}\nОрк {session.enemynumber}: Здоровье: {session.ork.HP}""")
                bot.send_message(callback.message.chat.id, text=f"""Выберете действие!""")
     
                            
#Focus
@bot.message_handler(func=lambda message: message.text == 'Фокус ⚡️')
def Focus_use(message):
    
    session = game_data[message.chat.id]
    
    if session.player_alive == True:
        
        if session.hero.focus > 0:
            
            if session.fight_mode == 1:
                session.hero.attack_focus_use(message, session.ork)
                if session.ork.HP <= 0:
                    on_ork_killed(message)
                    return
                
                session.hero.update(message)
                if session.hero.HP <= 0: return
                
                session.ork.attack(message, session.hero)
                if session.hero.HP <= 0: return
                
                session.ork.update(message)
                if session.ork.HP > 0:
                    bot.send_message(chat_id=message.chat.id, text=f"""Ваш ход!""") 
                    
                if session.ork.HP <= 0:
                    on_ork_killed(message)
                           
            else:    
                bot.send_message(chat_id=message.chat.id, text=f"Перед вами безжизненное тело орка.")   
                        
        else:
            bot.send_message(chat_id=message.chat.id, text="Недостаточно очков фокуса.")       
    else:
        bot.send_message(chat_id=message.chat.id, text=f"GAME OVER.\nНажмите: /start")    
   
    
#Healing
@bot.message_handler(func=lambda message: message.text == 'Лечение ✨')
def action_3(message): 
    
    session = game_data[message.chat.id]
    
    if session.player_alive == True:
    
        if session.fight_mode == 1:
            
            session.hero.bleeding = 0
            session.hero.poison = 0
            bot.send_message(chat_id=message.chat.id, text=f"Используя свои магические способности, вы проводите лечебное заклинание, излечивая раны и устраняя болезни!")
            bot.send_photo(message.chat.id, openfile('Assets/images/hero_healing.jpg'))
            bot.send_audio(message.chat.id, openfile('Assets/sounds/hero_heal.mp3'))
            heal = randint(5,20)
            session.hero.HP += heal
            bot.send_message(chat_id=message.chat.id, text=f"Лечение + {heal}\nУровень HP героя: {session.hero.HP}")
            bot.send_message(chat_id=message.chat.id, text=f"Враг не дремлет!")
            
            session.hero.update(message)
            if session.hero.HP <= 0: return
            
            session.ork.attack(message, session.hero)
            if session.hero.HP <= 0: return
                    
            session.ork.update(message)
            if session.ork.HP > 0:
                bot.send_message(chat_id=message.chat.id, text=f"""Ваш ход!""")  
                 
            if session.ork.HP <= 0:
                on_ork_killed(message)    
            
        else:    
            bot.send_message(chat_id=message.chat.id, text=f"Сперва примите решение!")
            
    else:                  
        bot.send_message(chat_id=message.chat.id, text=f"GAME OVER.\nНажмите: /start")      
      
      
#Error
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    
    session = game_data[message.chat.id]
    
    if session.player_alive == True:
        bot.send_message(chat_id=message.chat.id, text=f"""Выберете действие!""")
    else:    
        bot.send_message(chat_id=message.chat.id, text=f"GAME OVER.\nНажмите: /start")                          
        
        
bot.infinity_polling()