create database fandom;
	
DROP TABLE if exists universes;

CREATE TABLE universes (
	id serial NOT NULL,
	universe character varying(10),
	created_at timestamp(0) without time zone NOT NULL default now()
);

INSERT INTO universes (universe) values ('DC'), ('MARVEL');

DROP TABLE if exists heroes;

CREATE TABLE heroes (
	hero_id serial NOT NULL,
	universe_id int NOT NULL,
	name character varying(50) NOT NULL,
	created_at timestamp(0) without time zone NOT NULL default now()
);

INSERT INTO heroes (universe_id, name) values (1, 'BATMAN'), (1, 'SUPERMAN'), (2, 'WOLVERINE'), (2, 'IRONMAN');

DROP TABLE if exists weapons;

CREATE TABLE weapons (
	weapon_id serial NOT NULL,
	hero_id int NOT NULL,
	weapon_name character varying(50) NOT NULL,
	weapon_category int,
	created_at timestamp(0) without time zone NOT NULL default now()
);

INSERT INTO weapons (hero_id, weapon_name, weapon_category) values (1, 'BATARANG', 1), (1, 'BATMOBILE', 3), (2, 'LASER VISION', 3), (2, 'GOD-LIKE STRENGTH', 5), (3, 'ADAMANTIUM CLAWS', 4), (3, 'REGENERATION CAPABILITIES', 4), (4, 'AROMOURED SUIT', 4);