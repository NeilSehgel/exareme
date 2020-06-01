
requirevars 'defaultDB' 'input_local_DB' 'db_query' 'x' 'y' 'xlevels' 'hypothesis';
--x: a vector of strings naming the variables of interest in data
--testValue: a number specifying the value of the null hypothesis

attach database '%{defaultDB}' as defaultDB;
attach database '%{input_local_DB}' as localDB;


-- ErrorHandling
select categoricalparameter_inputerrorchecking('hypothesis', '%{hypothesis}', 'different,greaterthan,lessthan');


--Read dataset and Cast values of columns using cast function.
var 'cast_y' from select create_complex_query("","tonumber(?) as ?", "," , "" , '%{y}');
drop table if exists defaultDB.localinputtblflat;
create table defaultDB.localinputtblflat as
select %{cast_y}, cast(%{x} as text) as '%{x}' from (select * from (%{db_query}))
where  %{x} is not null and %{x}  <>'NA' and %{x}  <>''
       and  %{x} in (select strsplitv('%{xlevels}','delimiter:,'));

--Independent or Unpaired T-test
var 'localstats' from select create_complex_query("","insert into  localstatistics
select '?' as colname, %{x} as groupval, sum(?) as S1, sum(?*?) as S2, count(?) as N from localinputtblflat
where ? is not null and ? <>'NA' and ? <>'' group by %{x};" , "" , "" , '%{y}');
drop table if exists localstatistics;
create temp table localstatistics (colname text, groupval text, S1 real, S2 real, N int);
%{localstats};

-- drop table if exists defaultDB.privacychecking; -- For error handling
-- create table defaultDB.privacychecking as
--ErrorChecking
select privacychecking(N) from (select count(*) as N from defaultDB.localinputtblflat);
select privacychecking(N) from localstatistics;

select variableshouldbebinary_inputerrorchecking('%{x}', val)
from (select count(distinct %{x}) as val from defaultDB.localinputtblflat)
where '%{xlevels}' <> '';
select variabledistinctvalues_inputerrorchecking('%{x}', val, '%{xlevels}')
from (select group_concat(distinct %{x}) as val from defaultDB.localinputtblflat)
where '%{xlevels}' <> '';


select * from localstatistics;

-- --Independent T-tests
-- var 'localstats' from select create_complex_query("","insert into  defaultDB.localstatistics
-- select '?' as colname, %{group_var} as group, sum(?) as S1, sum(?*?) as S2, count(?) as N from localinputtblflat
-- where ? is not null and ? <>'NA' and ? <>'' group by %{group_var};" , "" , "" , '%{localstats}');

--Paired T-test
-- var 'localstats' from select create_complex_query("","insert into  defaultDB.localstatistics
-- select strsplit('?','delimiter:-'), sum(?) as S1, sum(?*?) as S2, count(?) as N from localinputtblflat
-- where ? is not null and ? <>'NA' and ? <>'';" , "" , "" , '%{pairs}');
-- select C1 as colname1, C2 as colname2, sum(C1-C2) as S1, sum((C1-C2)*(C1-C2)) as S2, count(C1) from localinputtblflat, select strsplit('?','delimiter:-')
