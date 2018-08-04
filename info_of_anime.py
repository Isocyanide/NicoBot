import requests
import pprint
import time

pp = pprint.PrettyPrinter(indent = 4)

url = 'https://graphql.anilist.co'

def info_anime(anime_id):
	query = '''
	query($id: Int) {
		Media(id : $id) {
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
	animeinfo=data['data']['Media']
	return animeinfo

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