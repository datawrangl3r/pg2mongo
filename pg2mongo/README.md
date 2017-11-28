# pg2mongo
-----------
> version 1.0

A hassle-free postresql to mongo migration framework.

## Usage steps:
1. Clone the repository.
2. Locate to pg2mongo/pg2mongo/
3. Modify pg2mongo.yml based on your requirements.
4. invoke the migration by executing '\_\_init\_\_.py' as:
```sh
$ python3 __init__.py
```

## Configuring pg2mongo.yml:

The structure of pg2mongo.yml goes as follows (The yaml file provided over here is just an example provided along with the script):

```yml
EXTRACTION:
    HOST : localhost 
    USER : postgres
    PASSWORD : 
    DATABASE : fandom
COMMIT:
    HOST : localhost
    USER :
    PASSWORD :
    DATABASE : fandom
MIGRATION:
    INIT_TABLE: universes
    INIT_KEYS:
        - id as uv_id
        - universe as trax_universe
        - created_at as trax_created_at
    SKELETON : 
        - KEY1 = {}
        - KEY2 = {}
    TABLES_ORDER :
        - heroes
        - weapons
    TABLES :
        heroes :
            condition : universe_id = uv_id
                #Dictionary's key ==> Postgres Field of the corresponding schema.table1
            mapping   :
                - KEY1['hero_id'] = %s['hero_id']
                - KEY1['universe_id'] = %s['universe_id']
                - KEY1['name'] = %s['name']
                - KEY1['created_at'] = %s['created_at']
                - KEY1['weapons'] = []
        weapons :
            condition : hero_id = KEY1['hero_id']
            mapping   :
                - list:
                    - KEY1['weapons'].append({})
                    - KEY1['weapons'][-1]['weapon_name'] = %s['weapon_name']
                    - KEY1['weapons'][-1]['weapon_category'] = %s['weapon_category']
    COLLECTIONS :
        heroes : KEY1
        #Collection name <== skeleton
        
```

The preliminary sections such as **extraction** and **commit** are self expanatory, stating the configuration settings for the extraction and commit databases. The component **Migration** is where all the magic happens!

|Key name | Intended Function |
|---------|-------------------|
| INIT_TABLE | Inital table from which data needs to be migrated. This could be a prime table such as a transactions table with a primary key having multiple foreign constraints to other tables of the postgreSQL database. FOR EACH ENTRY IN THIS TABLE, THE LINKING OF OTHER TABLES WILL HAPPEN WHILE DEFINING THE ***TABLES***.
| INIT_KEYS | KEYS of the init_table (aliases can be given using 'as')|
| SKELETON | Skeleton is an empty raw python dictionary assignment which will transform to a mongodb document, upon migration |
| TABLES_ORDER | The order by which the TABLES section needs to be executed for each of the entry from INIT_TABLE |
| TABLES | Set of PostgreSQL tables enlisted along with condition and corresponding mapping. In the case of lists inside a dictionary, list can be mentioned. Mapping is where, the association of skeleton to the table keys is defined. The value assignments are python compatible; hence, they are defined by using '%s' and other python based variable transformation functions can be used over here.|
| COLLECTIONS | This is where the push of the skeleton to the corresponding MongoDB collection takes place. |
