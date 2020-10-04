import os.path, yaml

class config_reader():
	def load_config():
		search_paths = ['/etc/pg2mongo/pg2mongo.yml', './pg2mongo.yml']
		counter = 0
		for file_loc in search_paths:
			counter+=1
			if os.path.isfile(file_loc) == False:
				if counter == len(search_paths):
					return "Configuration File not found"
				else:
					continue
			else:
				with open(file_loc) as f:
					# use safe_load instead load
					Config = yaml.safe_load(f)
					if 'EXTRACTION' and 'COMMIT' in Config.keys():
						return Config 	#Returning the handler
					else:
						if 'EXTRACTION' in Config.keys() and 'COMMIT' not in Config.keys():
							return 'Commit configuration is unavailable'
						elif 'EXTRACTION' not in Config.keys() and 'COMMIT' in Config.keys():
							return 'Extraction configuration is unavailable'
						else:
							return 'Extraction and Commit Configurations Unavailable'

