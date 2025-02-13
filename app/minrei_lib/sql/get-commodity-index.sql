select cg.px_location, cg.commoditygroup, sc.supercommodity, cg.sensitivitybucket
from commoditygroup cg
left join supercommodity sc on cg.commoditygroup = sc.commoditygroup
order by cg.px_location