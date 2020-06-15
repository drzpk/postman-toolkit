create table schema_versions
(
    id int primary key,
    name varchar(64) not null,
    created_at timestamp not null,
    execution_time int not null,
    success int not null
);