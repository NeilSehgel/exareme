requirevars 'defaultDB' 'input_global_tbl' ;
attach database '%{defaultDB}' as defaultDB;

drop table if exists defaultdb.globaltree;
create table defaultdb.globaltree(no int, colname text, colval text, nextnode int, leafval text, samplesperclass text);

drop table if exists defaultdb.globalpathforsplittree;
create table defaultdb.globalpathforsplittree (no int, colname text, colval text, nextnode int, leafval text);

select 'ok';
