import json

def read_settings(settings_file):
	with open(settings_file, 'r') as f:
		settings = json.load(f)
	default = settings.get('default')
	front_left = settings.get('front_left')
	front_right = settings.get('front_right')
	rear_left = settings.get('rear_left')
	rear_right = settings.get('rear_right')
	return settings, default, front_left, front_right, rear_left, rear_right


if __name__ == '__main__':
	settings_file = 'settings.json'
	settings = read_settings(settings_file)
	for s in settings:
		print(s)