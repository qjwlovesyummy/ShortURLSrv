create table tb_control
(
	id int auto_increment primary key,
	type varchar(10) default '' not null,
	value bigint default 1 not null
);

create table tb_record_20190629
(
	id binary(16) not null primary key,
	short_url varchar(50) default '' not null,
	ip int not null,
	agent varchar(200) not null,
	visit_count int default 0 not null
);

create table tb_url_N
(
	id bigint not null primary key,
	short_url varchar(50) default '' not null,
	full_url text not null,
	expire bigint default 0 null,
	visited bigint default 0 not null
);

create index tb_url_N_expire on shorturlsrv.tb_url_N (expire);



