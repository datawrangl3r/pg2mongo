import os.path, yaml

class config_reader():
	def load_config():
		search_paths = ['/etc/pg2mongo/pg2mongo.yml']
		for file_loc in search_paths:
			if os.path.isfile(file_loc) == False:
				return "Configuration File not found"
			else:
				with open(file_loc) as f:
					# use safe_load instead load
					Config = yaml.safe_load(f)
					print (Config.keys())
					if 'EXTRACTION' and 'COMMIT' in Config.keys():
						return Config 	#Returning the handler
					else:
						if 'EXTRACTION' in Config.keys() and 'COMMIT' not in Config.keys():
							return 'Commit configuration is unavailable'
						elif 'EXTRACTION' not in Config.keys() and 'COMMIT' in Config.keys():
							return 'Extraction configuration is unavailable'
						else:
							return 'Extraction and Commit Configurations Unavailable'

