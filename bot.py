import db
import search, re
from config import TELEGRAM_TOKEN
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

whitelist = {1034476732: '996555559967', }
ADMINS = {1034476732: '996555559967', }
sent_num = {}


# def admin_command(update, connect):
#     user_id = update.effective_user.id
#
#     if user_id in ADMINS:
#         update.message.reply_text('Это комманда для админов')
#
#     else:
#         update.message.reply_text('У вас нет прав для выполнения этой команды. Нюхайте бэбру!')


def request_contact(update, context):
    user_id = update.effective_user.id
    if is_user_registered(user_id) != []:
        update.message.reply_text('Вы уже зарегистрированы! Можете пользоваться ботом)))')
    else:
        contact_keyboard = KeyboardButton(text="Отправить номер телефона", request_contact=True)
        custom_keyboard = [[contact_keyboard]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
        update.message.reply_text('Пожалуйста, поделитесь своим номером телефона:', reply_markup=reply_markup)


def is_user_registered(user_id):
    return db.search_whitelist(db.create_connection(), str(user_id))


def handle_contact(update, context):
    user_id = update.message.contact.user_id
    phone = update.message.contact.phone_number
    username = update.effective_user.username or update.effective_user.first_name or 'Аноним'

    sent_num[user_id] = phone
    update.message.reply_text('Спасибо!')
    keyboard = [[
        InlineKeyboardButton('Добавить', callback_data=f'add_{user_id}_{phone}'),
        InlineKeyboardButton('Отклонить', callback_data=f'reject_{user_id}_{phone}')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    conn = db.create_connection()
    for admin_id in ADMINS:
        db.log_action(conn, str(user_id), phone[-9:], username, 'Запрос на регистрацию')
        context.bot.send_message(chat_id=admin_id, text=f"Новый запрос на добавление в whitelist: {user_id}, {phone}", reply_markup=reply_markup)
    update.message.reply_text('Ваш запрос отправлен на рассмотрение администратору.\nОжидайте...')


def button_callback(update, context):
    query = update.callback_query
    query.answer()

    data = query.data.split('_')
    action = data[0]

    user_id, phone_number = data[1], data[2]

    if action == 'add':
        phone_number = data[2]
        if add_to_db(user_id, phone_number):
            query.edit_message_text(text=f'Номер {phone_number} добавлен в WhiteList.')
            context.bot.send_message(chat_id=user_id, text=f"Вы успешно прошли авторизацию.\nПоздравляем!!!\nТеперь вы можете пользоваться ботом)")
        else:
            query.edit_message_text(text='Произошла ошибка при добавлении данных')
    elif action == 'reject':
        query.edit_message_text(text=f'Запрос отклонен. Номер {phone_number} не добавлен!')
        context.bot.send_message(chat_id=user_id,
                                 text=f"Произошла ошибка, обратитесь к администратору!")


def save_contact_request(user_id, phone_number):
    connection = db.create_connection()
    with connection.cursor() as cursor:
        query = 'INSERT INTO contact_request (user_id, phone) VALUES (%s, %s)'
        cursor.execute(query, (user_id, phone_number))
    connection.commit()


# def add_to_whitelist(update, context):
#     user_id = update.effective_user.id
#
#     if user_id not in ADMINS:
#         update.message.reply_text('У вас нет прав для выполнения этой команды, понюхай бэбру фраерок!')
#         return
#     try:
#         text = update.message.text.split()
#         target_user_id = int(text[1])
#         phone_number = sent_num.get(target_user_id)
#
#         if phone_number:
#             whitelist[target_user_id] = phone_number
#             update.message.reply_text(f'Номер {phone_number} добавлен в whitelist.')
#             context.bot.send_message(chat_id=target_user_id, text=f"Вы успешно прошли авторизацию.\nПоздравляем!!!\nТеперь вы можете пользоваться ботом)")
#         else:
#             update.message.reply_text('Номер телефона не найден в запросах.')
#     except (IndexError, ValueError):
#         update.message.reply_text('Неправильный формат команды. Используйте: /addwhitelist [user_id]')


def add_to_db(phone, name):
    connection = db.create_connection()
    try:
        with connection.cursor() as cursor:
            query = 'INSERT INTO whitelist (user_id, phone) VALUES (%s, %s)'
            cursor.execute(query, (phone, name))
        connection.commit()
        return True
    except Exception as e:
        print(f'Ошибка при добавлении в базу данных: {e}')
        return False
    finally:
        connection.close()


def remove_whitelist(update, context):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        update.message.reply_text('У вас нет прав для выполнения этой команды. Нюхай бэбру!!!')
        return

    try:
        target_user_phone = context.args[0]
        conn = db.create_connection()
        if conn is not None:
            db.delete_from_whitelist(conn, target_user_phone)
            update.message.reply_text(f'Пользователь с номером {target_user_phone} удален')
            conn.close()
        else:
            update.message.reply_text('Не удалось подключиться к базе данных')
    except (IndexError, ValueError):
        update.message.reply_text('Укажите корректный номер телефона. Пример: /remove 996*')


def show_whitelist(update, context):
    conn = db.create_connection()
    if conn is not None:
        whitelist = db.get_whitelist(conn)
        if whitelist:
            message = 'Пользователи в белом списке:\n\n'
            for user in whitelist:
                print(user)
                user_id, phone = user[4], user[2]
                message += f'ID: {user_id}, Телефон: {phone}\n'
        else:
            message = 'Белый список пуст.'
        update.message.reply_text(message)
    else:
        update.message.reply_text("Не удалось подключиться к базе данных")


def show_last_loggs(update, context):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        update.message.reply_text('ПШЛНХ!')
        return
    try:
        target_phone = context.args[0]
        target_phone = f'{target_phone[-9:]}'
        conn = db.create_connection()
        if conn is not None:
            logs = db.last_loggs(conn, target_phone)
            message = 'Последние записи:\n'
            for log in logs:
                date_formatted = log[1].strftime('%d.%m.%y %H:%M:%S')
                message += f'{date_formatted} - {log[5]}\n'
            update.message.reply_text(message[:4096])
            conn.close()
        else:
            update.message.reply_text('Ошибка подключения к базе')
    except IndexError:
        update.message.reply_text('Укажите правильный номер пользователя')


def handle_text(update, context):
    user = update.effective_user
    if user.is_bot:
        update.message.reply_text('Пошел на хуй')
    else:
        user_id = user.id
        try:
            user_in_wl = db.search_whitelist(db.create_connection(), str(user_id))[0]
        except:
            user_in_wl = []
        if not user_in_wl:
            update.message.reply_text('Напишите "/start" и поделитесь своим номером! Только после этого я начну работать')
            return
        else:
            username = user.username or user.first_name or 'Аноним'
            user_input = update.message.text
            print(f'Данные о пользователе: \n {user_id=}\n {username=}\n Номер телефона: 0{user_in_wl[2][3:]}')
            conn = db.create_connection()
            if conn is not None:
                db.log_action(conn, str(user_id), user_in_wl[2][3:], username, f'Поиск: {user_input}')
            else:
                update.message.reply_text('Ошибка подключения к бд')
            if re.fullmatch(r'\+?\d[\d\s()-]*', user_input):
                user_input = ''.join(re.findall(r'\d', user_input))[-9:]
                results = db.search_by_phone(db.create_connection(), '996'+user_input)
                formatted_results = [format_result_phone(record) for record in results]
            else:
                es_results = search.search_by_name(search.create_es_connection(), user_input)
                # print(f'{es_results=}\n')
                try:
                    results = [db.get_record_by_id_1(db.create_connection(), record_id) for record_id in es_results[0]]
                    results += [db.get_record_by_id_2(db.create_connection(), record_id) for record_id in es_results[1]]
                    results += [db.get_record_by_id_3(db.create_connection(), record_id) for record_id in es_results[2]]
                    print(results)
                    formatted_results = [format_result_name(record) for record in results]
                except:
                    print('АШИБКА')
            print(f'Поиск: {user_input}\n')

            update.message.reply_text('\n\n'.join(formatted_results) if formatted_results else "Ничего не найдено.")


def format_result_phone(record):
    return f"{record[2]}, {record[3]}, {record[4]}, {record[5]}, {record[6]}"


def format_result_name(record):
    if record is not None:
    # Форматирование результата из PostgreSQL для поиска по имени
        return f"{record[2]}, {record[3]}, {record[4]}, {record[5]}, {record[6]}"
    else:
        return []


def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', request_contact))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    dispatcher.add_handler(CommandHandler('whitelist', show_whitelist))
    dispatcher.add_handler(CommandHandler('showlogs', show_last_loggs, pass_args=True))
    dispatcher.add_handler(CommandHandler('remove', remove_whitelist))
    # dispatcher.add_handler(CommandHandler('addwhitelist', add_to_whitelist))
    # dispatcher.add_handler(MessageHandler(Filters.location, handle_location))
    dispatcher.add_handler(MessageHandler(Filters.contact, handle_contact))
    text_handler = MessageHandler(Filters.text & ~Filters.command, handle_text)
    dispatcher.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
