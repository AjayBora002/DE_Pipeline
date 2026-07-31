
    
    

select
    trip_id as unique_field,
    count(*) as n_records

from "neondb"."public_public"."silver_ridership"
where trip_id is not null
group by trip_id
having count(*) > 1


