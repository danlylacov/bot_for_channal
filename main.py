import telebot
import sqlite3

try:
    Token = '5421316252:AAF8jy8oCzOmmF0dfXzjix0Etpgs02U5KZQ'
    bot = telebot.TeleBot(Token)
    print('Token is correct!')
except:
    print('Token is incorrect!')


class BD:
    def __init__(self):
        try:
            self.conn = sqlite3.connect('data.db')
            self.cur = self.conn.cursor()
            print('bd sucsessfully connected!')
        except:
            print('bd is not connected!')

    def get_start_message(self):
        mesg, = self.cur.execute('SELECT message FROM Bot_messages where name = "/start"')
        return str(mesg[0])

    def get_help(self):
        mesg, = self.cur.execute('SELECT message FROM Bot_messages where name = "/help"')
        return str(mesg[0])

    def get_lessons(self):
        data = self.cur.execute('SELECT name FROM Lessons')
        lessons = []
        for el in data:
            lessons.append(str(el[0]))
        return lessons

    def get_lesson_link(self, name):
        data, = self.cur.execute('SELECT link FROM Lessons where Name = ?', [str(name), ])
        return str(data[0])

    def update_start_message(self, message):
        self.cur.execute('Update Bot_messages set message = ? where name = "/start"', [message, ])
        self.conn.commit()

    def update_start_help(self, message):
        self.cur.execute('Update Bot_messages set message = ? where name = "/help"', [message, ])
        self.conn.commit()

    def add_lesson(self, name, link):
        self.cur.execute('INSERT INTO Lessons(Name, Link) VALUES(?, ?);', [name, link,])
        self.conn.commit()

    def delete_lesson(self, name):
        self.cur.execute("DELETE FROM Lessons WHERE name=?;", [name,])
        self.conn.commit()


keyboard = telebot.types.InlineKeyboardMarkup()
les = BD().get_lessons()
for i in range(len(les)):
    keyboard.add(telebot.types.InlineKeyboardButton(text=les[i], callback_data=les[i]))


@bot.message_handler(commands=['start'])
def StartMessage(message):
    bot.send_message(message.chat.id, BD().get_start_message())
    bot.send_message(message.chat.id, BD().get_help(), reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    les = BD().get_lessons()
    if call.data in les:
        bot.send_message(call.message.chat.id, BD().get_lesson_link(str(call.data)))
        bot.send_message(call.message.chat.id, BD().get_help(), reply_markup=keyboard)


@bot.message_handler(commands=['admin'])
def Admin_menu(message):
    admin_keyboard = telebot.types.ReplyKeyboardMarkup()
    admin_keyboard.add('редактировать приветствие', 'редактировать помощь', 'добавить урок', 'удалить урок')
    bot.send_message(message.chat.id, 'Выберете действие:', reply_markup=admin_keyboard)


@bot.message_handler(content_types=['text'])
def Admin_text(message):
    if message.text == 'редактировать приветствие':
        mesg = bot.send_message(message.chat.id, 'Напишите новое приветствие:')
        bot.register_next_step_handler(mesg, update_start)
    if message.text == 'редактировать помощь':
        mesg = bot.send_message(message.chat.id, 'Напишите новое сообщение:')
        bot.register_next_step_handler(mesg, update_help)
    if message.text == 'добавить урок':
        mesg = bot.send_message(message.chat.id, 'Напишите название и ссылку на урок через "/"')
        bot.register_next_step_handler(mesg, add_lesson)
    if message.text == 'удалить урок':
        str_ = ''
        les_ = BD().get_lessons()
        for i in range(len(les)):
            str_ += (str(i+1)+'.  '+str(les_[i])+'\n')
        mesg = bot.send_message(message.chat.id, 'Напишите название урока, который вы хотите удалить:\n'+str_)
        bot.register_next_step_handler(mesg, delete_lesson)







def update_start(message):
    BD().update_start_message(message.text)

def update_help(message):
    BD().update_start_help(message.text)

def add_lesson(message):
    if '/' in message.text:
        data = str(message.text).split('/')
        BD().add_lesson(data[0], data[1])
    else:
        bot.send_message(message.chat.id, 'Формат введенных данных  неверен!')

def delete_lesson(message):
    if message.text in BD().get_lessons():
        BD().delete_lesson(message.text)
    else:
        bot.send_message(message.chat.id, 'Формат введенных данных  неверен!')





def run():
    bot.polling()

if __name__ == '__main__':
    run()




