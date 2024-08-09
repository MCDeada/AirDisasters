create database AirDisasters;
use AirDisasters;

create table Roles(
	id        int not null auto_increment primary key,
    role_name varchar(40) not null unique check (role_name != '')
);

create table Users(
	id              int not null auto_increment primary key,
    user_name       varchar(40) not null check (user_name != ''),
    user_surname    varchar(40) not null check (user_surname != ''),
    user_patronymic varchar(40) not null check (user_patronymic != ''),
    login           varchar(40) not null unique check (login != ''),
    user_password   varchar(40) not null check (user_password != ''),
    user_key        varchar(40) not null unique check (user_key != ''),
    id_role         int not null,
    
    constraint users_role_fk
    foreign key (id_role) references Roles(id)
    on delete cascade
);

create table Users_actions(
	id              int not null auto_increment primary key,
    action_name     varchar(40) not null unique check (action_name != '')
);

create table History_of_users(
	id          int not null auto_increment primary key,
    user_id  int not null,
    user_action int not null,
    related_table varchar(100),
    row_before_action json,
    row_after_action json,
    action_datetime datetime not null,
    
    constraint history_of_users_login_fk
    foreign key (user_id) references Users(id)
    on delete cascade, 
    
    constraint history_of_users_action_fk
    foreign key (user_action) references Users_actions(id)
    on delete cascade
);

create table Weather_conditions(
	id            int not null auto_increment primary key,
    condition_name varchar(30) not null unique check (condition_name != '')
);

create table Flight_phases(
	id         int not null auto_increment primary key,
    phase_name varchar(40) not null unique check (phase_name != '')
);

create table Aircraft_conditions(
	id             int not null auto_increment primary key,
    condition_name varchar(40) not null unique check (condition_name != '')
);

create table Aviation_accident_types(
	id            int not null auto_increment primary key,
    accident_type varchar(80) not null unique check (accident_type != '')
);

create table Countries(
	id           int not null auto_increment primary key,
    country_name varchar(80) not null check (country_name != '')
);

create table Flight_types(
	id          int not null auto_increment primary key,
    flight_type varchar(70) not null unique check (flight_type != '')
);

create table Airports(
	id            int not null auto_increment primary key,
    airport_name  varchar(80) not null check (airport_name != ''),
    ICAO_code	  varchar(10) not null unique check (ICAO_code != ''),
    country       int not null,
    latitude  	  float check (-90 <= latitude <= 90),
    longitude 	  float check (-180 <= longitude <= 180),
    height    	  float check (-433 <= height <= 15000),
    
    constraint airports_fk 
    foreign key (country) references Countries(id)
    on delete cascade
);

create table Aircraft_types(
	id              int not null auto_increment primary key,
    model_name      varchar(80) not null unique check (model_name != ''),
    first_flight    date,
    last_flight     date,
    max_mass        float check (1 <= max_mass <= 650),
    max_crew        int not null check (1 <= max_crew <= 10),
    max_passengers  int not null check (0 <= max_passengers <= 1000),
    length          float check (3.5 <= length <= 85),
    height          float check (1 <= height <= 30),
    wingspan        float check (4 <= wingspan <= 120),
    wing_area       float check (4 <= wing_area <= 550),
    fuselage_width  float check (0.5 <= fuselage_width <= 10),
    interior_width  float check (0.5 <= interior_width <= 10),
    cruising_speed  float check (160 <= cruising_speed <= 3000),
    runaway_range   float check (350 <= runaway_range <= 12000),
    max_flight_altitude float check (1000 <= max_flight_altitude <= 20000)
);

create table Engine_types(
	id            int not null auto_increment primary key,
    model_name    varchar(50) not null unique check (model_name != ''),
    static_thrust float check (0.1 <= static_thrust <= 570),
    mass          float check (0.1 <= mass <= 10000),
    length        float check (250 <= length <= 15000),
    diameter      float check (100 <= diameter <= 4500),
    developed_in  date
);

create table Engines_types_to_aircraft_types(
	id               int not null auto_increment primary key,
    id_engine_type   int not null,
    id_aircraft_type int not null,
    
    constraint eta_engine_type_fk
    foreign key (id_engine_type) references Engine_types(id)
    on delete cascade,
    
    constraint eta_aircraft_type_fk
    foreign key (id_aircraft_type) references Aircraft_types(id)
    on delete cascade
);

create table Operators(
	id            int not null auto_increment primary key,
    operator_name varchar(80) not null unique check (operator_name != ''),
    country		  int not null,
    ICAO_code	  varchar(10) not null unique check (ICAO_code != ''),
    
    constraint operators_country_fk
    foreign key (country) references Countries(id)
    on delete cascade
);

create table Disasters(
	id                    int not null auto_increment primary key,
    disaster_datetime     datetime not null,
    flight_type		  	  int,
    flight_number     	  varchar(30) check (flight_number != ''),
    operator          	  int,
    aircraft_model_type   int not null,
    engine_model_type     int not null,
    registration_code     varchar(40) not null check (registration_code != ''),
    departure_place   	  int,
    departure_date    	  datetime,
    destination_place 	  int,
    destination_date  	  datetime,
    crew_survived         int not null check (0 <= crew_survived <= 10),
    crew_fatalities       int not null check (0 <= crew_fatalities <= 10),
    passengers_survived   int not null check (0 <= passengers_survived <= 1000),
    passengers_fatalities int not null check (0 <= passengers_fatalities <= 1000),
    temperature    		  float check (-100 <= temperature <= 100),
    pressure       		  float check (0 <= pressure <= 850),
    weather_condition 	  int not null,
    wind_speed     		  float check (0 <= wind_speed <= 100),
    country				  int not null,
    latitude  			  float check (-90 <= latitude <= 90),
    longitude 			  float check (-180 <= longitude <= 180),
    height    			  float check (-433 <= height <= 15000),
    flight_phase          int not null,
    aircraft_condition    int not null,
    disaster_accident     int not null,
    location_description  text check (location_description != ''),
    accident_description  text check (accident_description != ''),
    photo_of_result       mediumblob,
    
    constraint disasters_flight_type_fk
    foreign key (flight_type) references Flight_types(id)
    on delete cascade,
    
    constraint disasters_operator_fk
    foreign key (operator) references Operators(id)
    on delete cascade,
    
    constraint aircraft_model_type_fk
    foreign key (aircraft_model_type) references Aircraft_types(id)
    on delete cascade,
    
    constraint engine_model_type_fk
    foreign key (engine_model_type) references Engine_types(id)
    on delete cascade,
    
    constraint disasters_departure_place_fk
    foreign key (departure_place) references Airports(id)
    on delete cascade,
    
    constraint disasters_destination_place_fk
    foreign key (destination_place) references Airports(id)
    on delete cascade,
    
    constraint disasters_country_fk
    foreign key (country) references Countries(id)
    on delete cascade,
    
    constraint disasters_weather_conditions_fk
    foreign key (weather_condition) references Weather_conditions(id)
    on delete cascade,
    
    constraint disasters_phase_fk
    foreign key (flight_phase) references Flight_phases(id)
    on delete cascade,
    
    constraint disasters_aircraft_condition_fk
    foreign key (aircraft_condition) references Aircraft_conditions(id)
    on delete cascade,
    
    constraint disasters_accident_fk
    foreign key (disaster_accident) references Aviation_accident_types(id)
    on delete cascade
);
