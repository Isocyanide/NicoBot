import pprint
import requests
import time

pp = pprint.PrettyPrinter(indent = 4)


timeUntilAiring = 0

url = 'https://graphql.anilist.co'

def airing_time(time):
	days, hours, minutes = range(3)

	day_count = time // 86400
	hour_count = (time // 3600) % 24
	minute_count = (time // 60) % 60

	days = f'{time // 86400} days ' if day_count else ''
	hours = f'{(time // 3600) % 24} hours and ' if (hour_count or day_count) else ''
	minutes = f'{(time // 60) % 60} minutes'

	return (f"{days}{hours}{minutes}")

def anime_query(times):
	anime_list = []

	query = '''
	query($time_ahead : Int) {
  		Page(perPage:50) {
      		airingSchedules(notYetAired : true, airingAt_lesser : $time_ahead) {
          		id
          		airingAt
          		episode
          		mediaId
        	}
        pageInfo {
          total
          lastPage
        }
    }
}
'''

	variables = {
  		'time_ahead' : int(time.time() + times)
	}
	
	response = requests.post(url, json={'query': query, 'variables': variables})
	data = response.json()

	if data['data']:
		for schedules in data['data']['Page']['airingSchedules']:
			mediaId= schedules['mediaId']
			anime_list.append(mediaId)
	return anime_list

def today(anime):
	global timeUntilAiring

	airing_query='''
	query($id: Int, $curr_time: Int){
		AiringSchedule(mediaId:$id, airingAt_greater: $curr_time){
			timeUntilAiring
			episode
		}
	}
	'''
	media_query='''
	query($id : Int){
		Media(id:$id){
			title{
				romaji
				english
			}
		}
	}
	'''
	variables2={
		'id' : anime,
		'curr_time':int(time.time())
	}
	variables1={
	'id':  anime
	}

	response = requests.post(url, json={'query': airing_query, 'variables': variables2})
	airing_data = response.json()

	response = requests.post(url, json={'query': media_query, 'variables': variables1})
	media_data = response.json()

	airing=airing_data['data']['AiringSchedule']
	media=media_data['data']['Media']
	timeUntilAiring=airing['timeUntilAiring']
	episode = airing['episode']
	title_eng = media['title']['english']
	title_rom = media['title']['romaji']
	from main import anime_title
	title = anime_title(title_eng, title_rom)

	airtime = airing_time(timeUntilAiring)

	return(f'`{title}` - {airtime}')

def anime_title(eng, rom):
	if eng:
		return (f'{eng}\n({rom})')
	else:
		return (f'{rom}')

def anime_notification(anime):
	global timeUntilAiring

	airing_query = '''
	query($id: Int, $curr_time: Int){
		AiringSchedule(mediaId:$id, airingAt_greater: $curr_time){
			timeUntilAiring
			episode
		}
	}
	'''
	media_query = '''
	query($id : Int){
		Media(id:$id){
			title{
				romaji
				english
			}
		}
	}
	'''

	airing_variables = {
		'id': anime,
		'curr_time':int(time.time())
	}

	media_variables = {
	'id':  anime
	}

	airing_response = requests.post(url, json={'query': airing_query, 'variables': airing_variables})
	airing_data = airing_response.json()

	media_response = requests.post(url, json={'query': media_query, 'variables': media_variables})
	media_data = media_response.json()

	airing = airing_data['data']['AiringSchedule']
	media = media_data['data']['Media']

	timeUntilAiring = airing['timeUntilAiring']
	episode = airing['episode']

	title_eng = media['title']['english']
	title_rom = media['title']['romaji']
	title = anime_title(title_eng, title_rom)
	
	if int(episode) % 10 == 1 and int(episode) % 100 != 11:
		episode = f'{episode}st'
	elif int(episode) % 10 == 2 and int(episode) % 100 != 12:
		episode = f'{episode}nd'
	elif int(episode) % 10 == 3 and int(episode) % 100 != 13:
		episode = f'{episode}rd'
	else:
		episode = f'{episode}th'

	return(f'{title}\'s {episode} episode has aired!!')
