def airing_time(time):

	days, hours, minutes = range(3)

	day_count = time // 86400
	hour_count = (time // 3600) % 24
	minute_count = (time // 60) % 60

	days = '' if not day_count else f'{day_count} day ' if day_count == 1 else  f'{day_count} days '
	hours = '' if not (hour_count or day_count) else  f'{hour_count} hour and ' if hour_count == 1 else  f'{hour_count} hours and '
	minutes = f'{minute_count} minute' if minute_count == 1 else f'{minute_count} minutes'

	return ([days, hours, minutes])