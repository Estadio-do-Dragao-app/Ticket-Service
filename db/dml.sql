insert into events (event_name, event_date) values ('Jogo Demo', '2024-09-15 20:00:00');

insert into tickets (event_id, gates_open, gate_id, row_id, seat_id, sector_id, ticket_type, state)
values (

    1,
    '2024-09-15 19:00:00',
    'Gate A',
    'Row 5',
    'Seat 12',
    'Sector 1',
    'VIP',
    true
    
);

insert into tickets (event_id, gates_open, gate_id, row_id, seat_id, sector_id, ticket_type, state)
values (

    1,
    '2024-09-15 19:00:00',
    'Gate A',
    'Row 4',
    'Seat 7',
    'Sector 1',
    'VIP',
    true

);