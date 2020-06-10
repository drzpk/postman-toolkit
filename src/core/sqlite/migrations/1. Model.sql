create table environment
(
    id   integer     not null primary key autoincrement,
    name varchar(64) not null
);

create table profile
(
    id             integer     not null primary key autoincrement,
    name           varchar(64) not null,
    priority       int         not null,
    enabled        int         not null,
    environment_id int         not null,
    foreign key (environment_id) references environment (id)
);

create table property
(
    id         integer     not null primary key autoincrement,
    name       varchar(64) not null,
    value      varchar(128),
    type       varchar(1)  not null,
    enabled    int         not null,
    profile_id int         not null,
    foreign key (profile_id) references profile (id)
);