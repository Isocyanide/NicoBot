import requests
import pprint
import time

pp = pprint.PrettyPrinter(indent = 4)

url = 'https://graphql.anilist.co'

def anime_title(eng, rom):
	if eng:
		return (f'{eng}\n({rom})')
	else:
		return rom

def anime_query(search, curr_page, per_page = 5):
	query = '''
	query($search : String, $curr_page : Int, $per_page : Int) { 
		Page(page : $curr_page, perPage : $per_page) {
			media(search: $search, type : ANIME) {
				id
				title {
					romaji
					english
				}
			}
			pageInfo {
				total
				lastPage
				hasNextPage
			}
		}
	}
	'''

	variables = {
		'search' : search,
		'curr_page'	: curr_page,
		'per_page' : per_page
	}

	response = requests.post(url, json={'query': query, 'variables': variables})
	data = response.json()

	# pp.pprint(data)

	anime_dict = {}
	eng_dict = {}
	for media in data['data']['Page']['media']:
		anime_name = media['title']['romaji']
		anime_eng = media['title']['english']
		if anime_name not in anime_dict.keys() or media['id'] > anime_dict[anime_name]:
			anime_dict[anime_name] = media['id']
			eng_dict[anime_name] = anime_eng

	anime_list = list(anime_dict.keys())
	return data, anime_list, anime_dict, eng_dict

def info(anime_id):

	media_query = '''
	query($anime_id: Int) {
		Media(id : $anime_id, type : ANIME) {
			id
			title {
				romaji
				english
			}
			startDate {
				year
			}
			season
			type
			format
			status
			episodes
			duration
			averageScore
			popularity
			genres
			description
			coverImage{
				medium
				large
			}
			bannerImage
			siteUrl
			trailer{
				id
				site
			}
			studios{
				nodes{
					name
				}
			}
		}
	}
	'''

	airing_query = '''
	query ($curr_time : Int, $anime_id : Int) {
		AiringSchedule(mediaId : $anime_id, airingAt_greater : $curr_time) {
			episode
			timeUntilAiring
		}
	}
	'''
	variables = {
		'anime_id' : anime_id,
		'curr_time' : int(time.time())
	}

	media_response = requests.post(url, json={'query': media_query, 'variables': variables})
	media_data = media_response.json()
	airing_response = requests.post(url, json={'query': airing_query, 'variables': variables})
	airing_data = airing_response.json()

	airing_days = ''

	if airing_data['data'] and airing_data['data']['AiringSchedule']:
		airing_episode = airing_data['data']['AiringSchedule']['episode']
		time_until_airing = airing_data['data']['AiringSchedule']['timeUntilAiring']
		from misc import airing_time
		airs_in = airing_time(time_until_airing)[0] or airing_time(time_until_airing)[1] + airing_time(time_until_airing)[2]
		airing_days += f"_Airs in {airs_in}\n_"

	anime_data = media_data['data']['Media']
	status = anime_data['status']
	if status:
		status = status.capitalize()
	average_score = anime_data['averageScore']
	season = anime_data['season']
	if season:
		season = season.capitalize()
	start_date = f"{season} {anime_data['startDate']['year']}"
	episodes = anime_data['episodes']

	genres = ''
	genre_list = anime_data['genres']
	for index, genre in enumerate(genre_list):
		genres += (f'{genre}') if (index == len(genre_list) - 1) else (f'{genre}, ')

	title_eng = anime_data['title']['english']
	title_rom = anime_data['title']['romaji']
	title = anime_title(title_eng, title_rom)

	description = anime_data['description'] or "No description available"
	description = description.replace('*', '\*').replace('_','\_').replace('#', '\#')
	if len(description) >= 200:
		description = description[:200] + '...'

	if not anime_data['bannerImage']:
		banner = anime_data['coverImage']['large']
	else:
		banner = anime_data['bannerImage']

	site_url = anime_data['siteUrl']

	trailer = None
	if anime_data['trailer']:
		trailer = anime_data['trailer']['site'] + ".com/video/" + anime_data['trailer']['id']
	
	studio_list = anime_data['studios']['nodes']
	studio = ''
	for index, studios in enumerate(studio_list):
		studios = studios['name']
		if index == len(studio_list)-1:
			studio += (f'{studios}')
		else:
			studio += (f'{studios}, ')

	msg = (
f'''*{title}*
{airing_days}
*Studios:* {studio}
*Status:* {status}
*Started in:* {start_date}
*Episodes:* {episodes}
*Average Score:* {average_score}
*Genres:* {genres}

*Synopsis:*
_{description}_
[\u200B]({banner})
''')

	return msg, site_url, trailer

def status(anime_id):
	query = '''
	query ($id: Int) { 
		Media (id: $id, type: ANIME) {
			status
		}
	}
	'''

	variables = {
		'id' : anime_id
	}

	response = requests.post(url, json={'query': query, 'variables': variables})
	data = response.json()

	anime_status = data['data']['Media']['status']
	return anime_status

def airing(anime_id):

	airing_query = '''
	query ($curr_time : Int, $anime_id : Int) {
		AiringSchedule(mediaId : $anime_id, airingAt_greater : $curr_time) {
			id
			mediaId
			episode
			timeUntilAiring
			airingAt
		}
	}
	'''
	media_query = '''
	query($anime_id: Int) {
		Media(id : $anime_id, type : ANIME) {
			title {
				romaji
				english
			}
		}
	}
	'''

	variables = {
		'curr_time' : int(time.time()),
		'anime_id' : anime_id
	}

	airing_response = requests.post(url, json={'query': airing_query, 'variables': variables})
	airing_data = airing_response.json()
	media_response = requests.post(url, json={'query': media_query, 'variables': variables})
	media_data = media_response.json()

	title_eng = media_data['data']['Media']['title']['english']
	title_rom = media_data['data']['Media']['title']['romaji']
	title = anime_title(title_eng, title_rom)

	if not airing_data['data']['AiringSchedule']:
		anime_status = status(anime_id).replace('_',' ').lower()
		return (f"The anime has {anime_status}.")

	episode = airing_data['data']['AiringSchedule']['episode']
	epoch_diff = int(airing_data['data']['AiringSchedule']['timeUntilAiring'])

	days, hours, minutes = range(3)

	day_count = epoch_diff // 86400
	hour_count = (epoch_diff // 3600) % 24
	minute_count = (epoch_diff // 60) % 60

	days = f'{epoch_diff // 86400} days ' if day_count else ''
	hours = f'{(epoch_diff // 3600) % 24} hours and ' if (hour_count or day_count) else ''
	minutes = f'{(epoch_diff // 60) % 60} minutes'

	return (f"\nEpisode {episode} of {title} airs in {days}{hours}{minutes}.")

def show_watchlist(anime_id):

	query = '''
	query($id: Int) { 
		Media(id : $id, type : ANIME) {
			id
			title {
				romaji
				english
			}
			status
		}
	}
	'''

	query2 = '''
	query($id:Int, $curr_time:Int) {
		AiringSchedule(mediaId: $id, airingAt_greater:$curr_time) {
			episode
			timeUntilAiring
		}
	}
	'''

	variables = {
		'id' : anime_id
	}

	variables2 = {
		'curr_time' : int(time.time()),
		'id' : anime_id
	}
	
	response = requests.post(url, json={'query': query, 'variables': variables})
	data = response.json()

	response2 = requests.post(url, json={'query': query2, 'variables': variables2})
	data2 = response2.json()

	anime_info = data['data']['Media']

	title_eng = anime_info['title']['english']
	title_rom = anime_info['title']['romaji']
	title = anime_title(title_eng, title_rom)

	status = anime_info['status'].replace('_',' ').capitalize()

	if status == 'Releasing':
		episode = data2['data']['AiringSchedule']['episode']
		time_until_airing = data2['data']['AiringSchedule']['timeUntilAiring']
		from misc import airing_time
		airs_in = airing_time(time_until_airing)[0] or airing_time(time_until_airing)[1] + airing_time(time_until_airing)[2]
		animu = (f'*{title}*\n_{status} (Episode {episode} airs in {airs_in.strip()})_\n---------------------------------------')
	else:
		animu = (f'*{title}*\n_{status}_\n---------------------------------------')
	return animu


def main():
	curr_page = 1

	search = input("What anime would you like to search?: ")
	data, anime_list, anime_dict, eng_dict = airing(search)

	print("\nChoose anime:\n")

	for index, anime in enumerate(anime_dict, 1):
		if eng_dict[anime]:
			print(f"{index}. {eng_dict[anime]}\n   ({anime})")
		else:
			print(f"{index}. {anime}")
	if data['data']['Page']['pageInfo']['hasNextPage']:
		print(f"{len(anime_list) + 1}. More...")

	choice = int(input("\nEnter: ")) - 1
	if choice == len(anime_list):
		curr_page += 1
		anime_query(search, curr_page)
	else:
		anime_id = anime_dict[anime_list[choice]]
		print(airing(anime_id))

if __name__ == '__main__':
	main()
