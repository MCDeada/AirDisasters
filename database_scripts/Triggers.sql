delimiter $$
CREATE TRIGGER disasters_before_insert
BEFORE INSERT ON disasters 
	FOR EACH ROW BEGIN 
		DECLARE message varchar(1000) default '';
		DECLARE max_crew float;
        DECLARE max_passengers float;
        DECLARE first_flight date;
        DECLARE last_flight date;
        DECLARE developed_in date;
        IF (NEW.departure_date is not null and NEW.departure_date > now()) THEN
			SET message = CONCAT(message, 'tr_dis00');
		END IF;
        IF (NEW.destination_date is not null and NEW.destination_date > now()) THEN
			SET message = CONCAT(message, 'tr_dis01');
		END IF;
		IF (NEW.departure_date is not null and
			NEW.destination_date is not null and
		    NEW.departure_date > NEW.destination_date) THEN 
				SET message = CONCAT(message, 'tr_dis1');
		END IF;
        IF not exists (select * from Engines_types_to_aircraft_types where id_aircraft_type = new.aircraft_model_type and id_engine_type = new.engine_model_type) THEN 
			SET message = CONCAT(message, 'tr_dis2');
		END IF;
        select att.max_crew into max_crew from Aircraft_types as att where id = new.aircraft_model_type;
        IF (max_crew < new.crew_survived + new.crew_fatalities) THEN 
			SET message = CONCAT(message, 'tr_dis3');
		END IF;
        select att.max_passengers into max_passengers from Aircraft_types as att where id = new.aircraft_model_type;
        IF (max_passengers < new.passengers_survived + new.passengers_fatalities) THEN 
			SET message = CONCAT(message, 'tr_dis4'); 
		END IF;
        select att.first_flight into first_flight from Aircraft_types as att where id = new.aircraft_model_type;
        select att.last_flight into last_flight from Aircraft_types as att where id = new.aircraft_model_type;
        select ett.developed_in into developed_in from Engine_types as ett where id = new.engine_model_type;
        IF (first_flight is not null and first_flight > new.disaster_datetime) THEN 
			SET message = CONCAT(message, 'tr_dis5'); /* Дата катастрофы не должна быть меньше даты первого полета модели */
		END IF;
        IF (last_flight is not null and last_flight < new.disaster_datetime) THEN 
			SET message = CONCAT(message, 'tr_dis6'); /* Дата катастрофы не должна быть больше даты последнего полета модели */
		END IF;
        IF (NEW.departure_place is not null and NEW.destination_place is not null and NEW.departure_place = NEW.destination_place) THEN 
			SET message = CONCAT(message, 'tr_dis7'); /* Место отправления не должно совпадать с место прибытия */
		END IF;
        IF (first_flight is not null and NEW.departure_date is not null and NEW.departure_date < first_flight) THEN 
			SET message = CONCAT(message, 'tr_dis8'); /* Дата отправления не должна быть раньше чем дата первого полета у модели */
		END IF;
        IF message != '' THEN
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = message;
		END IF;
	END
$$

delimiter $$
CREATE TRIGGER disasters_before_update
BEFORE UPDATE ON disasters 
	FOR EACH ROW BEGIN 
		DECLARE message varchar(1000) default '';
		DECLARE max_crew float;
        DECLARE max_passengers float;
        DECLARE first_flight date;
        DECLARE last_flight date;
        DECLARE developed_in date;
		IF (NEW.departure_date is not null and
			NEW.destination_date is not null and
		    NEW.departure_date > NEW.destination_date) THEN 
				SET message = CONCAT(message, 'tr_dis1');
		END IF;
        IF not exists (select * from Engines_types_to_aircraft_types where id_aircraft_type = new.aircraft_model_type and id_engine_type = new.engine_model_type) THEN 
			SET message = CONCAT(message, 'tr_dis2');
		END IF;
        select att.max_crew into max_crew from Aircraft_types as att where id = new.aircraft_model_type;
        IF (max_crew < new.crew_survived + new.crew_fatalities) THEN 
			SET message = CONCAT(message, 'tr_dis3');
		END IF;
        select att.max_passengers into max_passengers from Aircraft_types as att where id = new.aircraft_model_type;
        IF (max_passengers < new.passengers_survived + new.passengers_fatalities) THEN 
			SET message = CONCAT(message, 'tr_dis4'); 
		END IF;
        select att.first_flight into first_flight from Aircraft_types as att where id = new.aircraft_model_type;
        select att.last_flight into last_flight from Aircraft_types as att where id = new.aircraft_model_type;
        select ett.developed_in into developed_in from Engine_types as ett where id = new.engine_model_type;
        IF (first_flight is not null and first_flight > new.disaster_datetime) THEN 
			SET message = CONCAT(message, 'tr_dis5'); /* Дата катастрофы не должна быть меньше даты первого полета модели */
		END IF;
        IF (last_flight is not null and last_flight < new.disaster_datetime) THEN 
			SET message = CONCAT(message, 'tr_dis6'); /* Дата катастрофы не должна быть больше даты последнего полета модели */
		END IF;
        IF (NEW.departure_place is not null and NEW.destination_place is not null and NEW.departure_place = NEW.destination_place) THEN 
			SET message = CONCAT(message, 'tr_dis7'); /* Место отправления не должно совпадать с место прибытия */
		END IF;
        IF (first_flight is not null and NEW.departure_date is not null and NEW.departure_date < first_flight) THEN 
			SET message = CONCAT(message, 'tr_dis8'); /* Дата отправления не должна быть раньше чем дата первого полета у модели */
		END IF;
        IF message != '' THEN
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = message;
		END IF;
	END
$$


/*----------------Engine_types------------------*/
delimiter $$
CREATE TRIGGER engine_types_before_insert
BEFORE INSERT ON engine_types 
	FOR EACH ROW BEGIN 
        IF (NEW.developed_in is not null and new.developed_in > now()) THEN
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'tr_engtyp1';
		END IF;
	END
$$

delimiter $$
CREATE TRIGGER engine_types_before_update
BEFORE UPDATE ON engine_types 
	FOR EACH ROW BEGIN 
        IF (NEW.developed_in is not null and new.developed_in > now()) THEN
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'tr_engtyp1';
		END IF;
	END
$$


/*----------------Aircraft_types------------------*/
delimiter $$
CREATE TRIGGER aircraft_types_before_insert
BEFORE INSERT ON aircraft_types 
	FOR EACH ROW BEGIN 
		DECLARE message varchar(1000) default '';
        IF (NEW.first_flight is not null and NEW.first_flight > now()) THEN
			SET message = CONCAT(message, 'tr_airtyp1');
		END IF;
        IF (NEW.last_flight is not null and NEW.last_flight > now()) THEN
			SET message = CONCAT(message, 'tr_airtyp2');
		END IF;
        IF (NEW.last_flight is not null and NEW.first_flight is not null and NEW.first_flight > NEW.last_flight) THEN
			SET message = CONCAT(message, 'tr_airtyp3');
		END IF;
        IF message != '' THEN
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = message;
		END IF;
	END
$$

delimiter $$
CREATE TRIGGER aircraft_types_before_update
BEFORE UPDATE ON aircraft_types 
	FOR EACH ROW BEGIN 
		DECLARE message varchar(1000) default '';
        IF (NEW.first_flight is not null and NEW.first_flight > now()) THEN
			SET message = CONCAT(message, 'tr_airtyp1');
		END IF;
        IF (NEW.last_flight is not null and NEW.last_flight > now()) THEN
			SET message = CONCAT(message, 'tr_airtyp2');
		END IF;
        IF (NEW.last_flight is not null and NEW.first_flight is not null and NEW.first_flight > NEW.last_flight) THEN
			SET message = CONCAT(message, 'tr_airtyp3');
		END IF;
        IF message != '' THEN
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = message;
		END IF;
	END
$$

/*----------------Engines_types_to_aircraft_types------------------*/
delimiter $$
CREATE TRIGGER engines_to_aircraft_before_insert
BEFORE INSERT ON Engines_types_to_aircraft_types 
	FOR EACH ROW BEGIN 
		DECLARE message varchar(1000) default '';
        DECLARE last_flight date;
        DECLARE developed_in date;
        select att.last_flight into last_flight from Aircraft_types as att where id = new.id_aircraft_type;
        select ett.developed_in into developed_in from Engine_types as ett where id = new.id_engine_type;
		IF (developed_in is not null) THEN
			IF (last_flight is not null and last_flight < developed_in) THEN
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'tr_ettatt3';
			END IF;
		END IF;
	END
$$

delimiter $$
CREATE TRIGGER engines_to_aircraft_before_update
BEFORE UPDATE ON Engines_types_to_aircraft_types 
	FOR EACH ROW BEGIN 
		DECLARE message varchar(1000) default '';
        DECLARE last_flight date;
        DECLARE developed_in date;
        select att.last_flight into last_flight from Aircraft_types as att where id = new.id_aircraft_type;
        select ett.developed_in into developed_in from Engine_types as ett where id = new.id_engine_type;
		IF (developed_in is not null) THEN
			IF (last_flight is not null and last_flight < developed_in) THEN
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'tr_ettatt3';
			END IF;
		END IF;
	END
$$
