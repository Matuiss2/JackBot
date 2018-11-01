# Greedy_bot

Its a bot that focus on early aggro, then tries to make a transition

**Change log:**

_Style changes_

- Refactoring the main

- Adding todo comments for refactoring on army_control, expansion

- Cleaning unused stuff on jack_bot

- Follow variable style convention on distribute_workers, block_expansions

- Fix too many booleans on a single if statement pylint error on train/overlord, expansion, build/evochamber

- Small reformatting changes everywhere it could

- Fix typos on army_control

_Optimization and micro-optimization_ 

- Exchanging list for the much faster sets or tuples on defend_worker_rush, defend_rush_buildings,
 upgrades/evochamber
  
- Exchanging list-comp for the faster generators where we can on building_positioning, worker
 
- Simplify drones, remove double calculation

- Reducing dots(methods or properties calls) and make variable locals where I could 

- Exchanging integers comparisons for boolean checks(==0 --> not) on jack_bot, distribute_workers

 _Bug fixes_
 
 - Prevent errors using checks on spines, jack_bot
 
 - Lazy fix - make zerglings even with no zergling speed after 2:40
 
 - Fix a bug that prevented the zerglings to attack after holding a proxy    
 
_Functional changes_

- Making the first scout earlier(drone)

- Tweaks on values so it beat Hjax 90% of the time

- Make evochambers and lair when holding a proxy

- More scouting with overlords

- Don't target gateways with drones just the pylons (the gateways would be unpowered)

- Preventing errors with drone pulls by limiting it a bit

- Adding trigger for attacking when flying units with damage are close(needs improvements)