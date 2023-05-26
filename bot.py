import telebot
from gsheets_api import Spreadsheet
from config import BOT_TOKEN, AUTH_FILE, SHEET_ID, DEFAULT_SCOPES

bot = telebot.TeleBot(BOT_TOKEN)
doc = Spreadsheet(sheet_id=SHEET_ID, scopes=DEFAULT_SCOPES, auth_file=AUTH_FILE)
work_sheet = doc.default_sheet

# создаём многоуровневое меню
def keyboard(keyboard_name: str, goal: str):
    main_keyboard = telebot.types.InlineKeyboardMarkup()
    if keyboard_name == 'document':
        main_keyboard.add(
            telebot.types.InlineKeyboardButton(text='List of all sheets', callback_data='list_of_sheets'),
            telebot.types.InlineKeyboardButton(text='Add new list', callback_data='add_new_sheet'),
            telebot.types.InlineKeyboardButton(text='Copy list', callback_data='copy_sheet_menu'),
            telebot.types.InlineKeyboardButton(text='Switch list', callback_data='list_of_sheets'),
            telebot.types.InlineKeyboardButton(text='Stop bot', callback_data='stop'),
            # telebot.types.InlineKeyboardButton(text='Удалить лист', callback_data='delete_sheet_menu'),
        )
    elif keyboard_name == 'sheet':
        main_keyboard.add(
            telebot.types.InlineKeyboardButton(text='List of all records', callback_data='data_dict'),
            telebot.types.InlineKeyboardButton(text='Add row', callback_data='add_row'),
            telebot.types.InlineKeyboardButton(text='Start page', callback_data='start'),
            telebot.types.InlineKeyboardButton(text='Stop bot', callback_data='stop'),
            # telebot.types.InlineKeyboardButton(text='Delete data', callback_data='delete_data'),
        )
    elif keyboard_name == 'list_of_sheets':
        if goal == 'copy':
            for name in list(doc.sheets.keys()):
                main_keyboard.add(telebot.types.InlineKeyboardButton(text=name, callback_data=f'copy_{name}'))
        elif goal == 'del':
            for name in list(doc.sheets.keys()):
                main_keyboard.add(telebot.types.InlineKeyboardButton(text=name, callback_data=f'del_{name}'))
        else:
            for name in list(doc.sheets.keys()):
                main_keyboard.add(telebot.types.InlineKeyboardButton(text=name, callback_data=f'list_named_{name}'))

            main_keyboard.add(telebot.types.InlineKeyboardButton(text='Start page', callback_data='start'))
    return main_keyboard


# обработчик кнопок на клавиатуре
@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'choose_the_list_by_name':
        switch_list_by_name(call.message)
    elif call.data == 'list_of_sheets':
        list_of_sheets(call.message)
    elif call.data[:10] == 'list_named':
        switch_list_by_name(call.data[11:], call.message)
    elif call.data == 'add_new_sheet':
        bot.send_message(call.message.chat.id, 'Enter the new list name:')
        bot.register_next_step_handler(call.message, add_new_sheet)
    elif call.data == 'copy_sheet_menu':
        copy_sheet_menu(call.message)
    elif call.data[:4] == 'copy':
        copy_sheet(call.data[5:], call.message)
    elif call.data == 'add_row':
        bot.send_message(call.message.chat.id, 'Enter data separated by commas without spaces:')
        bot.register_next_step_handler(call.message, add_row)
    elif call.data == 'data_dict':
        data_dict(call.message)
    elif call.data == 'start':
        send_welcome(call.message)
    elif call.data == 'stop':
        stop(call.message)
    else:
        print('Well, it\'s your choice')
        stop(call.message)
        pass

    # работа с удалением данных, нужна доработка
    # elif call.data == 'delete_sheet_menu':
    #     delete_sheet_menu(call.message)
    # elif call.data[:3] == 'del':
    #     delete_sheet(call.data[4:], call.message)



# стартовое меню
@bot.message_handler(content_types=["text"], commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
                 f'Hi! I\'ll help you to add data to google sheets without opening browser.\n'
                 f'Choose what needs to be done:',
                 reply_markup=keyboard('document', 0))


# вывести список всех листов
@bot.message_handler(content_types=["text"], commands=['list_of_sheets'])
def list_of_sheets(message):
    text_message = f'The document contains sheets with the following titles:\n'\
                   f'{*list(doc.sheets.keys()),}'
    bot.send_message(message.chat.id, text_message)
    bot.send_message(message.chat.id, 'To go to one of them, click the button', reply_markup=keyboard('list_of_sheets','reg'))


# - выбрать лист по названию
@bot.message_handler(content_types=["text"], commands=['choose_the_list_by_name'])
def switch_list_by_name(text, message):
    global work_sheet
    list_name = text
    bot.send_message(message.chat.id, f'You are currently working with a sheet {list_name}. Choose next step:',
                     reply_markup=keyboard('sheet', 'reg'))
    work_sheet = doc.current_sheet(doc.sheets[list_name])

    return work_sheet


# - добавить новый пустой лист
@bot.message_handler(content_types=["text"], commands=['add_new_sheet'])
def add_new_sheet(message):
    global doc

    list_name = message.text
    doc.add_sheet(list_name)
    bot.send_message(message.chat.id, f'You created a sheet called \'{list_name}\'. Choose next step:', reply_markup=keyboard('sheet', 'reg'))

    return doc


# - копировать существующий
@bot.message_handler(content_types=["text"], commands=['copy_sheet_menu'])
def copy_sheet_menu(message):
    text_message = f'The document contains sheets with the following titles:\n' \
                   f'{*list(doc.sheets.keys()),}'
    bot.send_message(message.chat.id, text_message)
    bot.send_message(message.chat.id, 'Click on the one you want to copy', reply_markup=keyboard('list_of_sheets', 'copy'))

@bot.message_handler(content_types=["text"])
def copy_sheet(text, message):
    doc.duplicate_sheet(doc.sheets[text], f'{text}_copy')
    bot.send_message(message.chat.id,
                     f'Congrats! You successfully copied a sheet called \'{text}_copy\'. Choose next step:',
                     reply_markup=keyboard('sheet', 'reg'))


# удаление листа
# нужна доработка
# @bot.message_handler(content_types=["text"], commands=['delete_sheets'])
# def delete_sheet_menu(message):
#     text_message = f'В документе есть листы со следующими названиями: {*list(doc.sheets.keys()),}'
#     bot.send_message(message.chat.id, text_message)
#     bot.send_message(message.chat.id, 'Для удаления выберите один из них', reply_markup=keyboard('list_of_sheets', 'del'))
#
#
# @bot.message_handler(content_types=["text"])
# def delete_sheet(text, message):
#     doc.delete_sheet(doc.sheets[text])
#     bot.send_message(message.chat.id, f'Вы удалили {text}', reply_markup=keyboard('list_of_sheets', 'reg'))
#
#     work_sheet = doc.default_sheet
#
#     return work_sheet

# добавить новую строку
@bot.message_handler(content_types=["text"], commands=['add_row'])
def add_row(message):
    work_sheet.append_row(message.text.split(','))
    bot.send_message(message.chat.id, f'Congrats! You successfully added new row. Choose next step:',
                     reply_markup=keyboard('sheet', 'reg'))

    return work_sheet


# вывести словарь всех записей
@bot.message_handler(content_types=["text"], commands=['data_dict'])
def data_dict(message):
    global work_sheet

    list_of_dicts = work_sheet.get_all_records()
    i = 2
    text_message = f'The sheet contains the following information:\n'
    for name in list_of_dicts:
        text_message += f'row {i}: {name}\n'
        i += 1

    text_message += f'This is all looks good, but we need to choose the next action:'

    bot.send_message(message.chat.id, text_message, reply_markup=keyboard('sheet', 'reg'))

    return work_sheet


@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, 'Okay, bye!')
    bot.stop_bot()