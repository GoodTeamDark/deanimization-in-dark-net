select "user"."login","Station"."name" from "Station" 
join "User_to_stations"
on "Station"."id"="User_to_stations"."Station_id"
join "user" on
"user"."id"="User_to_stations"."User_id"
where "user"."login"='test'
order by "user"."login","Station"."name"
