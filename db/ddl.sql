create table tickets (

    id serial primary key,

    event_id integer not null,

    gates_open datetime not null,
    gate_id varchar(50),

    row_id varchar(50),
    seat_id varchar(100),
    sector_id varchar(100),

    ticket_type varchar(250) not null,
    state boolean not null,

    foreign key (event_id) references events(id)
);

create table events (

    id serial primary key,
    event_name varchar(100) not null,
    event_date datetime not null

);