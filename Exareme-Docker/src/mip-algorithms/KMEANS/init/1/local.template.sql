requirevars 'defaultDB' 'input_local_DB' 'db_query' 'db_query' 'y' 'centers' 'k' 'dataset' ;
attach database '%{defaultDB}' as defaultDB;
attach database '%{input_local_DB}' as localDB;

var 'x' '%{y}';

-- Read dataset, Delete patients with null values (val is null or val = '' or val = 'NA'). Cast values of columns using cast function.
var 'nullCondition' from select create_complex_query(""," ? is not null and ? <>'NA' and ? <>'' ", "and" , "" , '%{x}');
var 'cast_x' from select create_complex_query("","tonumber(?) as ?", "," , "" , '%{x}');
drop table if exists defaultDB.localinputtbl;
create table defaultDB.localinputtbl as
select cast(rowid as text) as rid, %{cast_x}
from (select %{x} from (%{db_query})) where %{nullCondition};

var 'centersisempty' from select case when (select '%{centers}')='' or (select '%{centers}')='[]' or (select '%{centers}')='[{}]' or (select '%{centers}')='{}' then 1 else 0 end;
var 'privacy' from select privacychecking(no) from (select count(*) as no from defaultDB.localinputtbl);
var 'inputerrorchecking' from select kmeans_inputerrorchecking('%{centersisempty}','%{k}');

drop table if exists defaultDB.assignnearestcluster;
create table defaultDB.assignnearestcluster(rid int primary key, clid int, mindist real);

var 'schema' from select create_complex_query("clid int, clN int,","?_clS real",",","",'%{x}');
var 'partialSums' from select create_complex_query("clid, count(*) as clN,", "sum(?) as ?_clS" , "," , '' ,'%{x}');
var 'nulls' from select create_complex_query("null,null," , "null", ",","",'%{x}');

var 'k' from select case when  %{centersisempty}= 0 then 2 else tonumber(%{k}) end;

drop table if exists defaultDB.partialclustercenters;
create table defaultDB.partialclustercenters (%{schema});
insert into defaultDB.partialclustercenters
select  %{partialSums}
from (   select rid, clid, %{x}
         from defaultDB.localinputtbl,
              (select rid as rid1,idofset as clid from (sklearnkfold splits:%{k} select distinct rid from defaultDB.localinputtbl))
         where rid1 =rid)
where %{centersisempty} = 1
group by clid;

select * from defaultDB.partialclustercenters;
