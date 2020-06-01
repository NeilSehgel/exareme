-- ------------------Input for testing
-- ------------------------------------------------------------------------------
-- hidden var 'defaultDB' defaultDB_TTEST;
-- hidden var 'x' 'righthippocampus,lefthippocampus';
-- hidden var 'outputformat' 'pfa';
-- hidden var 'testvalue' 3.0;
-- hidden var 'effectsize' 1;

-- hidden var 'ci'  0;
-- hidden var 'meandiff'  0;
-- hidden var 'hypothesis'  'different';
--
--
-- drop table if exists inputdata;
-- create table inputdata as
-- select %{y}
-- from (file header:t '/home/eleni/Desktop/HBP/exareme/Exareme-Docker/src/mip-algorithms/unit_tests/datasets/CSVs/desd-synthdata.csv');

--http://www.sthda.com/english/wiki/t-test-formula


------------------ End input for testing
------------------------------------------------------------------------------

requirevars 'defaultDB' 'input_local_DB' 'db_query' 'y' 'hypothesis';

attach database '%{defaultDB}' as defaultDB;
attach database '%{input_local_DB}' as localDB;

-- ErrorHandling
select categoricalparameter_inputerrorchecking('hypothesis', '%{hypothesis}', 'different,greaterthan,lessthan');

--Read dataset
drop table if exists inputdata;
create temp table inputdata as select * from (%{db_query});

-- Cast values of columns using cast function.
var 'cast_x' from select create_complex_query("","tonumber(?) as ?", "," , "" , '%{y}');
drop table if exists localinputtblflat;
create temp table localinputtblflat as
select %{cast_x} from inputdata;

--One Sample T-test
var 'localstats' from select create_complex_query("","insert into  localstatistics
select '?' as colname, sum(?) as S1, sum(?*?) as S2, count(?) as N from localinputtblflat
where ? is not null and ? <>'NA' and ? <>'';" , "" , "" , '%{y}');
drop table if exists localstatistics;
create temp table localstatistics (colname text, S1 real, S2 real, N int);
%{localstats};

drop table if exists privacychecking; -- For error handling
create temp table privacychecking as
select privacychecking(N) from localstatistics;

select * from localstatistics;
