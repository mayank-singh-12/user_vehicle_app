create table if not exists users (
   id       integer primary key,
   username text not null,
   password text not null
);

create table if not exists parking_lot (
   id                      integer primary key,
   prime_location_name     text not null,
   price                   real not null,
   address                 text not null,
   pin_code                integer not null,
   maximum_number_of_spots integer not null
);


create table if not exists parking_spot (
   id     integer primary key,
   lot_id integer not null,
   status text check ( status in ( "O",
                                   "A" ) ),
   foreign key ( lot_id )
      references parking_lot ( id )
);


create table if not exists reserve_parking_spot (
   id                integer primary key ,
   spot_id           integer not null,
   user_id           integer not null,
   parking_timestamp timestamp default current_timestamp not null,
   foreign key ( spot_id )
      references parking_spot ( id ),
   foreign key ( user_id )
      references users ( id )
);