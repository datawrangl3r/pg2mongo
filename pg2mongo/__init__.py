import re
import ast
from asteval import Interpreter
import psycopg2 as pg2
from pymongo import MongoClient
from config_reader import config_reader

aeval = Interpreter()

class Migrator():
	def __init__(self):
		self.output = config_reader.load_config()
		return None

	def ext_connection(self):
		try:
			database = self.output['EXTRACTION']
			client = pg2.connect(database=database['DATABASE'],user=database['USER'], password=database['PASSWORD'], host=database['HOST'])
			cur = client.cursor()
			return cur
		except Exception as e:
			result_ = {'Success':False, 'Response': 'Extraction Failure', 'Message': str(e)}
			return result_

	def com_connection(self):
		try:
			database = self.output['COMMIT']
			try:
				if database['USER'] != '' and database['USER'] != None:
					uri = "mongodb://%s:%s@%s:27017" % (database['USER'], database['PASSWORD'], database['HOST'])
				else:
					uri = "mongodb://localhost:27017"
			except:
				uri = "mongodb://localhost:27017"
			client = MongoClient(uri)
			cur = client[database['DATABASE']]
			return cur
		except Exception as e:
			result_ = {'Success':False, 'Response': 'Commit Failure', 'Message': str(e)}
			return result_

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
			rows = cursor.execute("""SELECT array_to_json(array_agg(t)) FROM (SELECT * from TABLE where COND)t""".replace('TABLE', table).replace('COND', cond))
		else:
			rows = cursor.execute("""SELECT array_to_json(array_agg(t)) FROM (SELECT * from TABLE)t""".replace('TABLE', table))
		result_set = cursor.fetchall()
		return result_set[0][0]

	def skeleton_reload(self):
		self.skeleton = self.output['MIGRATION']['SKELETON']
		for each_skeleton in self.skeleton:
			try:
				key_ = each_skeleton.split('=')[0].strip()
				self.each_skeleton = exec('self.'+each_skeleton)
			except Exception as e:
				return 'JSON Format Incorrect'		

	def validate_conf(self):
		try:
			cur = self.ext_connection()
		except Exception as e:
			return 'Something is wrong with the connection. Check your connection/config file'

		try:
			self.table_order = self.output['MIGRATION']['TABLES_ORDER']
		except Exception as e:
			return 'TABLES_ORDER key is not found. Check the config file'

		try:
			self.init_table = self.output['MIGRATION']['INIT_TABLE']
		except Exception:
			return 'INIT_TABLE key is not found. Check the config file'

		try:
			self.init_keys = self.output['MIGRATION']['INIT_KEYS']
		except Exception:
			return 'INIT_KEYS key is not found. Check the config file'

		try:
			self.init_keys = self.output['MIGRATION']['INIT_KEYS']
		except Exception:
			return 'INIT_KEYS key is not found. Check the config file'

		try:
			self.skeleton_reload()
		except Exception as e:
			return 'SKELETON key is not found. Check the config file'

		try:
			self.tables = self.output['MIGRATION']['TABLES']
		except Exception:
			return 'TABLES key is not found. Check the config file'

		try:
			self.collections = self.output['MIGRATION']['COLLECTIONS']
		except Exception:
			return 'COLLECTIONS key is not found. Check the config file'

	def init_migration(self):
		ext_curs = self.ext_connection()
		com_curs = self.com_connection()
		source_ext_query = "SELECT array_to_json(array_agg(t)) FROM (select %s from %s)t"%(', '.join(self.init_keys), self.init_table)
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
				dest_collection = com_curs[each_collection]
				com_curs[each_collection].insert_one(eval('self.'+self.collections[each_collection]))

if __name__ == "__main__":
	mig_obj = Migrator()
	if mig_obj.validate_conf() == None:
		print (mig_obj.init_migration())