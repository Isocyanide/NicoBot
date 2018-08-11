from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Updater, InlineQueryHandler, MessageHandler, Filters, CommandHandler,
						  ConversationHandler, RegexHandler, CallbackQueryHandler)
import logging
import pprint
import pickle
from time import sleep
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4, uuid5

pp = pprint.PrettyPrinter(indent = 4)

logging.basicConfig(level=logging.INFO,
					format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

updater=Updater(token="678308898:AAHhbtcQdxxavLvoJobik7787F1zwKjC7Q4")
#updater=Updater(token="664187548:AAEWJcTwDJJZf7EKGhVsuxOB9UMu7SL2CEo")
dispatcher = updater.dispatcher
j = updater.job_queue

user_dict = {}
notif_dict = {}
user_db = open('user_dict.db', 'rb')
notif_db = open('notif_dict.db', 'rb')
try:
	obj = pickle.load(user_db)
	if obj:
		user_dict = obj
	pp.pprint(user_dict)
except:
	pass
try:
	obj = pickle.load(notif_db)
	if obj:
		notif_dict = obj
	pp.pprint(notif_dict)
except:
	pass
user_db.close()
notif_db.close()

buttons = [['Anime Info'], ['Add to Watchlist'], ['Airing Schedule']]
def help(bot, update):
	bot.send_message(chat_id = update.message.chat_id, text = """Nico nico nii~!
I can help you get information and airing notifications of anime that you follow. Start by using the /anime command!

Here's the commands list~
/anime - Search Anime
/help - Get this help message
/add\_to\_watchlist - Search and add anime to watchlist
/info - Get Anime info
/schedule - Get Airing Schedule
/show\_watchlist - Show watchlist
/notif\_off - Turn off watchlist notifications
/notif\_on - Turn on watchlist notifications
/clear\_watchlist - Clear watchlist
/remove\_from\_watchlist - Removes an anime from watchlist

The bot is currently in Alpha Testing phase. Report any bugs to @e\_to\_the\_i\_pie or @WeirdIndianBoi.
""", reply_to_message_id = update.message.message_id, parse_mode = "Markdown")

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

def start(bot, update):
	bot.send_message(chat_id = update.message.chat_id, text = "*Nico nico nii~!*\nI can help you get information and airing notificaitons of anime that you follow. Start by using the /anime command!\n\nThe bot is currently in Alpha Testing phase. Report any bugs to @e\_to\_the\_i\_pie or @WeirdIndianBoi.", parse_mode = 'Markdown')

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def anime(bot, update, user_data):
	user_data['first_message']=update.message.message_id
	command = update.message.text.split()[0].lstrip('/')
	if '@' in command:
		index = command.index('@')
		command = command[:index]

	if command == 'add_to_watchlist':
		user_data['choice'] = 'add_to_watchlist'

	elif command == 'info':
		user_data['choice'] = 'info'

	elif command == 'schedule':
		user_data['choice'] = 'airing_schedule'

	query = ' '.join(update.message.text.split()[1:])
	if query:
		user_data['name'] = query
		user_data['method']='D'
		return anime_search(bot, update, user_data)

	user_data['prev_message'] = bot.send_message(chat_id = update.message.chat_id, text = "Type anime name", reply_to_message_id = update.message.message_id)
	#try:
		#bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
	#except:
		#pass
	return SEARCH

def anime_search(bot, update, user_data):
	try:
		bot.delete_message(chat_id = update.message.chat_id, message_id = user_data['prev_message'].message_id)
	except:
		pass
	from main import anime_query

	if 'name' not in user_data.keys():
		user_data['name'] = update.message.text
	anime_name = user_data['name']

	if 'curr_page' not in user_data.keys():
		user_data['curr_page'] = 1
	curr_page = user_data['curr_page']

	if 'sent_message' not in user_data.keys():
		user_data['sent_message'] = bot.send_message(chat_id = update.message.chat_id, text = "Searching, wait a second...", reply_to_message_id = update.message.message_id)

	sent_message = user_data['sent_message']

	data, anime_list, anime_dict, eng_dict = anime_query(anime_name, curr_page)

	if not data['data']['Page']['media']:
		bot.edit_message_text(chat_id = update.message.chat_id, text = "No Anime found, try again.", message_id = sent_message.message_id)
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
		except:
			pass
		return done(bot, update, user_data)

	user_data['anime_dict'] = anime_dict
	user_data['anime_list'] = anime_list

	if update.message:
		user_data['user_id'] = update.message.from_user.id

	msg = (f"Choose Anime:\n\n")

	for index, anime in enumerate(anime_dict, 1):
		if eng_dict[anime]:
			msg += (f"/{index}. {eng_dict[anime]}\n  ({anime})\n")
		else:
			msg += (f"/{index}. {anime}\n")

	if data['data']['Page']['pageInfo']['hasNextPage']:
		inline_button = InlineKeyboardMarkup([[InlineKeyboardButton("More...", callback_data = 'search')]])
		bot.edit_message_text(chat_id = sent_message.chat_id, text = msg, message_id = sent_message.message_id, reply_markup = inline_button)
	else:
		bot.edit_message_text(chat_id = sent_message.chat_id, text = msg, message_id = sent_message.message_id)
	try:
		if 'method' not in user_data.keys():
			bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
	except:
		pass
	return CHOICE

def anime_choice(bot, update, user_data):
	msg = update.message.text
	choice = int(msg[1])

	if choice > len(user_data['anime_list']):
		bot.send_message(chat_id = update.message.chat_id, text = "Invalid choice, try again.", reply_to_message_id = update.message.message_id)
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
		except:
			pass
		return CHOICE

	else:
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = user_data['sent_message'].message_id)
		except:
			pass
		anime_dict = user_data['anime_dict']
		anime_list = user_data['anime_list']
		anime_id = anime_dict[anime_list[choice - 1]]
		user_data['id'] = anime_id

		if 'choice' in user_data.keys() and user_data['choice'] in ['add_to_watchlist', 'info', 'airing_schedule']:
			return intermediate(bot, update, user_data)

		keyboard = [[InlineKeyboardButton("Anime Info", callback_data = 'info')],
					[InlineKeyboardButton("Add to Watchlist", callback_data = 'add_to_watchlist')],
					[InlineKeyboardButton("Airing Schedule", callback_data = 'airing_schedule')]
				   ]

		markup = InlineKeyboardMarkup(keyboard)

		bot.send_message(chat_id = update.message.chat_id, text = "Enter your choice:", reply_to_message_id =user_data['first_message'], reply_markup = markup, parse_mode = 'MARKDOWN')
		try:
			bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
		except:
			pass
		return BUTTONS

def buttons(bot, update, user_data):
	query = update.callback_query
	choice = query.data
	
	if choice == 'search':
		sent_message = bot.edit_message_text(text = "Please wait...",
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id)

		user_data['sent_message'] = query.message
		user_data['curr_page'] += 1
		return anime_search(bot, update, user_data)
	
	user_id = user_data['user_id']
	anime_id = user_data['id']

	if choice == 'info':
		bot.edit_message_text(text = "Please wait...",
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id,
							  parse_mode = "Markdown")

		bot.edit_message_text(text = anime_info(bot, update, anime_id),
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id,
							  parse_mode = "Markdown")

	elif choice == 'add_to_watchlist':
		bot.edit_message_text(text = watchlist(user_id, anime_id),
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id,
							  parse_mode='Markdown')

	elif choice == 'airing_schedule':
		bot.edit_message_text(text = "Please wait...",
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id)

		bot.edit_message_text(text = anime_airing(bot, update, anime_id),
							  chat_id = query.message.chat_id,
							  message_id = query.message.message_id)

	return done(bot, update, user_data, query)

def watchlist(user_id, anime_id):
	if user_id in user_dict.keys():
		if anime_id in user_dict[user_id]:
			return "You already have this anime in your watchlist!"

		user_dict[user_id].append(anime_id)
		user_db = open('user_dict.db', 'wb')
		pickle.dump(user_dict, user_db)
		user_db.close()
		return "Anime added Successfully!"

	user_dict[user_id] = [anime_id]
	user_db = open('user_dict.db', 'wb')
	pickle.dump(user_dict, user_db)
	user_db.close()
	return "Anime added Successfully!"

def anime_info(bot, update, anime_id):
	from main import info
	return info(anime_id)

def anime_airing(bot, update, anime_id):
	from main import airing
	return airing(anime_id)

def intermediate(bot, update, user_data):
	user_id = update.message.from_user.id
	anime_id = user_data['id']

	choice=user_data['choice']

	if choice == 'info':
		bot.send_message(text = anime_info(bot, update, anime_id),
							  chat_id = update.message.chat_id,
							  reply_to_message_id=user_data['first_message'],
							  parse_mode = "Markdown")

	elif choice == 'add_to_watchlist':
		bot.send_message(text = watchlist(user_id, anime_id),
							  chat_id = update.message.chat_id,
							  reply_to_message_id=user_data['first_message'],
							  parse_mode='Markdown')

	elif choice == 'airing_schedule':
		bot.send_message(text = anime_airing(bot, update, anime_id),
							  chat_id = update.message.chat_id,
							  reply_to_message_id=user_data['first_message'])
	try:
		bot.delete_message(chat_id = update.message.chat_id, message_id = update.message.message_id)
	except:
		pass
	return done(bot, update, user_data)

def done(bot, update, user_data, query = None):
	#if query:
	#	bot.send_message(chat_id = query.message.chat_id, text = "Convo ended.", reply_to_message_id = query.message.message_id)
	#else:
	#	bot.send_message(chat_id = update.message.chat_id, text = "Convo ended.", reply_to_message_id = update.message.message_id)
	user_data.clear()
	return conv_handler.END

def search(bot, update, user_data):
		from main import show_watchlist
		from main import anime_title
		user_id=update.message.from_user.id
		msg="Select which anime you would like to remove:\n"
		if user_id in user_dict.keys():
				for index, anime in enumerate(user_dict[user_id]):
					anime_name = show_watchlist(anime)
					msg += (f'/{index+1}. {anime_name}\n')
				bot.send_message(chat_id = update.message.chat_id, text = msg, reply_to_message_id = update.message.message_id)
				return REMOVE
		else:
			bot.send_message(chat_id = update.message.chat_id, text = "You don't seem to have a watchlist. Add something to your watchlist using the /anime function.", reply_to_message_id = update.message.message_id)
			return done(bot, update, user_data)

def remove(bot, update, user_data):
	command = update.message.text.split()[0].lstrip('/')
	if '@' in command:
		index = command.index('@')
		command = command[:index]
	command=int(command)-1
	user_id=update.message.from_user.id
	if len(user_dict[user_id]) >= command:
		user_dict[user_id].remove(user_dict[user_id][command])
		user_db = open('user_dict.db', 'wb')
		pickle.dump(user_dict, user_db)
		user_db.close()
		bot.send_message(chat_id=update.message.chat_id, text="Successfully removed.")
		return done(bot, update, user_data)
	else:
		return REMOVE

SEARCH, CHOICE, ACTIONS, AIRING, BUTTONS, WATCHLIST, REMOVE = range(7)

conv_handler = ConversationHandler(
	entry_points = [CommandHandler(['anime','add_to_watchlist','info','schedule'], anime, pass_user_data = True),
						CommandHandler('remove_from_watchlist', search, pass_user_data = True)],

	states = {
		SEARCH: [MessageHandler(Filters.text,
								anime_search,
								pass_user_data = True)
				],
		CHOICE: [CommandHandler(['1', '2', '3', '4', '5'],
								anime_choice,
								pass_user_data = True),
				CallbackQueryHandler(buttons,
									  pass_user_data=True)
				],
		AIRING: [MessageHandler(Filters.text,
								anime_airing,
								pass_user_data = True)
				],
		BUTTONS: [CallbackQueryHandler(buttons,
									  pass_user_data=True)
				 ],
		WATCHLIST: [MessageHandler(Filters.text,
								   watchlist,
								   pass_user_data=True)
				   ],
				REMOVE: [CommandHandler([str(i) for i in range(1, 51)], remove, pass_user_data = True)]
	},

	#coversation_timeout = 30,

	fallbacks = {
		RegexHandler('^Band hogya$', done, pass_user_data = True)
	}
)

dispatcher.add_handler(conv_handler)

def show_watchlist(bot, update):
		from main import show_watchlist
		user_id = update.message.from_user.id
		user_name = update.message.from_user.username
		user_name=user_name.replace('_','\_')


		msg = (f"Watch list for @{user_name}:\n\n")

		if user_id in user_dict.keys() and user_dict[user_id]:
				for index, anime in enumerate(user_dict[user_id]):
						anime_name = show_watchlist(anime)
						msg += (f'{index+1}. {anime_name}\n')
				bot.send_message(chat_id = update.message.chat_id, text = msg, reply_to_message_id = update.message.message_id, parse_mode='Markdown')
		else:
			bot.send_message(chat_id = update.message.chat_id, text = "You don't seem to have a watchlist. Add something to your watchlist using the /anime function.", reply_to_message_id = update.message.message_id)

		if user_id not in notif_dict.keys() or notif_dict[user_id] == 'off':
			bot.send_message(chat_id = update.message.chat_id, text = 'Btw, remember to turn /notif_on to get notifications.', reply_to_message_id = update.message.message_id)

showWatchlistHandler = CommandHandler("show_watchlist",show_watchlist)
dispatcher.add_handler(showWatchlistHandler)

def clear_watchlist(bot, update):
	user_id = update.message.from_user.id

	if user_id in user_dict.keys() and user_dict[user_id]:
		del user_dict[user_id]
		user_db = open('user_dict.db', 'wb')
		pickle.dump(user_dict, user_db)
		user_db.close()
		bot.send_message(chat_id = update.message.chat_id, text = "Successfully cleared watchlist!", reply_to_message_id = update.message.message_id)
	else:
		bot.send_message(chat_id = update.message.chat_id, text = "Your watchlist is already empty...", reply_to_message_id = update.message.message_id)

clearWatchlistHandler = CommandHandler('clear_watchlist', clear_watchlist)
dispatcher.add_handler(clearWatchlistHandler)

def update_anime_list(bot, job):
	from notif import anime_query
	anime_list = anime_query(7200)
	return callback(bot, job, anime_list)
job = j.run_repeating(update_anime_list, interval = 3600, first = 0)
 
def airing_today(bot, update):
	from notif import anime_query, today
	anime_list = anime_query(86400)

	msg = 'Anime airing today are:\n'
	for anime in anime_list:
		text = today(anime)
		msg += f'\n{text}\n'
	bot.send_message(chat_id = update.message.chat_id, text = msg)
airinghandler = CommandHandler('airing_today', airing_today)
dispatcher.add_handler(airinghandler)

def callback(bot, update, anime_list):
	from notif import anime_notification
	
	for anime in anime_list:
		text = anime_notification(anime)

		from notif import timeUntilAiring
		if timeUntilAiring > 0:
			sleep(timeUntilAiring)
		for person in user_dict.keys():
			if anime in user_dict[person]:
							if person in notif_dict.keys() and notif_dict[person] == 'on':
								try:
									bot.send_message(chat_id = person, text = text)
									print(f"Sent message to {person} about anime {anime}:")
									print(user_dict[person])
								except:
									print("COULDN'T SEND NOTIFICATION!")

def notif_on(bot, update):
	user_id = update.message.from_user.id
	if user_id not in notif_dict.keys() or notif_dict[user_id] == 'off':
		notif_dict[user_id] = 'on'
		notif_db = open('notif_dict.db', 'wb')
		pickle.dump(notif_dict, notif_db)
		notif_db.close()
		bot.send_message(chat_id = update.message.chat_id, text = "Your notifications have been enabled.", reply_to_message_id = update.message.message_id)
	elif notif_dict[user_id] == 'on':
		bot.send_message(chat_id = update.message.chat_id, text = "Your notifications are already enabled.", reply_to_message_id = update.message.message_id)
			
notif_on_handler = CommandHandler('notif_on', notif_on)
dispatcher.add_handler(notif_on_handler)

def notif_off(bot, update):
	user_id = update.message.from_user.id
	if user_id not in notif_dict.keys():
		bot.send_message(chat_id = update.message.chat_id, text = "You aren't registered in our database yet.", reply_to_message_id = update.message.message_id)
	elif notif_dict[user_id] == 'on':
		notif_dict[user_id] = 'off'
		notif_db = open('notif_dict.db', 'wb')
		pickle.dump(notif_dict, notif_db)
		notif_db.close()
		bot.send_message(chat_id=update.message.chat_id, text="Your notifications have been disabled", reply_to_message_id = update.message.message_id)
	elif notif_dict[user_id] == 'off':
		bot.send_message(chat_id=update.message.chat_id, text="Your notifications are already disabled", reply_to_message_id = update.message.message_id)
notif_off_handler = CommandHandler('notif_off', notif_off)
dispatcher.add_handler(notif_off_handler)

def inlinequery(bot, update):
	query = update.inline_query.query
	from main import anime_query, info
	from info_of_anime import info_anime
	data, anime_list, anime_dict, eng_dict = anime_query(query, 1, 10)
	results=[]

	for anime in anime_list:
		animes=anime_dict[anime]
		animeinfo=info_anime(animes)
		image=animeinfo['coverImage']['medium']
		status=animeinfo['status']
		typee=animeinfo['']
		text=info(animes)
		results.append(
            InlineQueryResultArticle(
            	id=str(uuid4()),
            	title=anime,
            	input_message_content=(InputTextMessageContent(text,parse_mode='MARKDOWN')),
            	thumb_url=image,
            	description=status))
	update.inline_query.answer(results)

dispatcher.add_handler(InlineQueryHandler(inlinequery))

updater.start_polling()
updater.idle()
