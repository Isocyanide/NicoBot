import requests
import pprint
import time

pp = pprint.PrettyPrinter(indent = 4)

url = 'https://graphql.anilist.co'

def info_anime(anime_id):
	query = '''
	query($id: Int) {
		Media(id : $id, type: ANIME) {
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
			type
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

	variables = {
		'id' : anime_id
	}

	response = requests.post(url, json={'query': query, 'variables': variables})
	data = response.json()
	try:
		animeinfo=data['data']['Media']
		return animeinfo
	except:
		pass

def genr(genre, curr_page,per_page=5):
	query = '''
	query($genre : String, $curr_page : Int, $per_page : Int) { 
		Page(page : $curr_page, perPage : $per_page) {
			media(genre:$genre, type : ANIME, sort: SCORE_DESC) {
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
		'genre' : genre,
		'curr_page' : curr_page,
		'per_page' : per_page
	}

	response = requests.post(url, json={'query': query, 'variables': variables})
	data = response.json()
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

def characters(name):
	query='''
	query($name:String)
	{
		Character(search:$name){
			name{
				first
				last
			}
			image{
				large
				medium
			}
			description
		}
	}
	'''
	variables = {
		'name':name
	}

	response = requests.post(url, json={'query': query, 'variables': variables})
	data = response.json()

	if data['data']:
		chr_info=data['data']['Character']
		name=chr_info['name']['first']+" "+chr_info['name']['last']
		image=chr_info['image']['large']
		description=chr_info['description']
		if len(description)>400:
			description=description[:400]
	return f'Name : {name}\nDescription : {description}\n{image}'