create table warcs
(
    id               uuid default gen_random_uuid() not null
        constraint pk
            unique,
    record_id        integer,
    url              varchar(1000)
        constraint unique_url
            unique,
    title            text,
    timestamp        date,
    path             varchar(255),
    pre_cleaned_text text,
    html_text        text,
    batch_number     integer
);

alter table warcs
    owner to app;

grant select on warcs to eiji;

