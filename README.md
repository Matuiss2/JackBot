# Greedy_bot

Its a bot that focus on early aggro, then tries to make a transition

**Change log:**

_Style changes_

- Adding todo comments for refactoring on army_control, expansion

- Cleaning unused stuff on jack_bot

- Follow variable style convention on distribute_workers, block_expansions

- Fix too many booleans on a single if statement pylint error on train/overlord, expansion

- Small reformatting changes on army_control

- Fix typos on army_control

_Optimization and micro-optimization_ 

- Exchanging list for the much faster sets or tuples on defend_worker_rush, defend_rush_buildings,
 upgrades/evochamber
  
- Exchanging list-comp for the faster generators where we can on building_positioning, worker
 
- Simplify drones, remove double calculation

- Avoiding dots(methods or properties calls)on army_control, jack_bot, micro, queen_abilities

 _Bug fixes_
 
 - Prevent errors using checks on spines
 
 - Exchanging integers comparisons for boolean checks(==0 --> not) on jack_bot, distribute_workers
 
_Functional changes_

- Making the first scout earlier(drone)

