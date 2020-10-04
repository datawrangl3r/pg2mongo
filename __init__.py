import re
import ast
import logging
import psycopg2 as pg2
from pymongo import MongoClient
from config_reader import config_reader

class Migrator():
	def __init__(self):
		self.output = config_reader.load_config()
		return None

	def ext_connection(self):
		try:
			database = self.output['EXTRACTION']
			client = pg2.connect(database=database['DATABASE'],user=database['USER'], password=database['PASSWORD'], host=database['HOST'])
			cur = client.cursor()
			return cur, None
		except Exception as e:
			return None, str(e)

	def com_connection(self):
		try:
			database = self.output['COMMIT']
			try:
				if database['USER'] != '' and database['USER'] != None:
					uri = "mongodb://{USER}:{PASSWORD}@{HOST}:27017".format(USER=database['USER'], PASSWORD=database['PASSWORD'], HOST=database['HOST'])
				else:
					uri = "mongodb://localhost:27017"
			except:
				uri = "mongodb://localhost:27017"
			client = MongoClient(uri)
			cur = client[database['DATABASE']]
			return cur, None
		except Exception as e:
			return None, str(e)

	def parse_dict(self, each_result, each_mapping):
		if each_mapping.find('{}')==-1:
			try:
				exec('self.'+each_mapping%('each_result'))
			except TypeError:
				exec('self.'+each_mapping)
		else:
			exec('self.'+each_mapping)
		return {}

	def parse_list(self, each_result, each_mapping):
		for sub_mapping in each_mapping:
			if 'list' not in sub_mapping:
				self.parse_dict(each_result, sub_mapping)
			else:
				self.parse_list(each_result, sub_mapping['list'])
		return {}

	def parse_skeleton(self, tables, table_name, result_set):
		for each_result in result_set:
			mappings = tables[table_name]['mapping']
			if mappings != None:
				for each_mapping in mappings:
					if 'list' not in each_mapping:
						self.parse_dict(each_result, each_mapping)
					else:
						self.parse_list(each_result, each_mapping['list'])
		return {}

	def retrieve_rows(self, cursor, table, cond):
		if cond != None:
			cursor.execute("""SELECT array_to_json(array_agg(t)) FROM (SELECT * from TABLE where COND)t""".replace('TABLE', table).replace('COND', cond))
		else:
			cursor.execute("""SELECT array_to_json(array_agg(t)) FROM (SELECT * from TABLE)t""".replace('TABLE', table))
		result_set = cursor.fetchall()
		return result_set[0][0]

	def skeleton_reload(self):
		self.skeleton = self.output['MIGRATION']['SKELETON']
		for each_skeleton in self.skeleton:
			try:
				each_skeleton.split('=')[0].strip()
				self.each_skeleton = exec('self.'+each_skeleton)
			except Exception:
				return 'JSON Format Incorrect'		

	def validate_conf(self):
		validation_checks = [] #len should be equal to 7
		try:
			self.ext_connection()
			validation_checks.append(1)
		except Exception:
			logging.error('Something is wrong with the connection. Check your connection/config file')

		try:
			self.table_order = self.output['MIGRATION']['TABLES_ORDER']
			validation_checks.append(1)
		except Exception:
			logging.error('TABLES_ORDER key is not found. Check the config file')

		try:
			self.init_table = self.output['MIGRATION']['INIT_TABLE']
			validation_checks.append(1)
		except Exception:
			logging.error('INIT_TABLE key is not found. Check the config file')

		try:
			self.init_keys = self.output['MIGRATION']['INIT_KEYS']
			validation_checks.append(1)
		except Exception:
			logging.error('INIT_KEYS key is not found. Check the config file')

		try:
			self.skeleton_reload()
			validation_checks.append(1)
		except Exception:
			logging.error('SKELETON key is not found. Check the config file')

		try:
			self.tables = self.output['MIGRATION']['TABLES']
			validation_checks.append(1)
		except Exception:
			logging.error('TABLES key is not found. Check the config file')

		try:
			self.collections = self.output['MIGRATION']['COLLECTIONS']
			validation_checks.append(1)
		except Exception:
			logging.error('COLLECTIONS key is not found. Check the config file')

		if len(validation_checks) == 7:
			return None

	def init_migration(self):
		ext_curs, error_ = self.ext_connection()
		if error_ != None:
			logging.error(error_)
			return None
		com_curs, error_ = self.com_connection()
		if error_ != None:
			logging.error(error_)
			return None
		source_ext_query = "SELECT array_to_json(array_agg(t)) FROM (SELECT {KEYS} FROM {TABLE})t".format(KEYS=', '.join(self.init_keys), TABLE=self.init_table)
		ext_curs.execute(source_ext_query)
		result_set = ext_curs.fetchall()
		for each_set in result_set[0][0]:
			for x in each_set:
				each_set[x] = str(each_set[x])
			self.skeleton_reload()
			for table_name in self.table_order:
				each_table = self.tables[table_name]
				condition = each_table['condition']
				if condition != None:
					if condition.find("['")==-1:
						pattern = re.compile('|'.join(each_set.keys()))
						condition = pattern.sub(lambda x: each_set[x.group()],  condition)
					else:
						cond_split = condition.split('=')
						condition  = ' = '.join([cond_split[0], str(eval('self.'+cond_split[-1].strip()))])
				result_set = self.retrieve_rows(ext_curs, table_name, condition)
				if result_set != None:
					self.parse_skeleton(self.tables, table_name, result_set)

			for each_collection in self.collections:
				print (eval('self.'+self.collections[each_collection]))
				com_curs[each_collection].insert_one(eval('self.'+self.collections[each_collection]))

if __name__ == "__main__":
	mig_obj = Migrator()
	# print(mig_obj.validate_conf())
	if mig_obj.validate_conf() == None:
		mig_obj.init_migration()