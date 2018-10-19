# Greedy_bot

Its a bot that focus on early aggro, then tries to make a transition

**Change log:**

_Style changes_

- Adding todo comments for refactoring on army_control, expansion

- Cleaning unused stuff on jack_bot

- Follow variable style convention on distribute_workers, block_expansions

- Fix too many booleans on a single if statement pylint error on train/overlord, expansion

- Small reformatting changes on army_control

_Optimization and micro-optimization_ 

- Exchanging list for the much faster sets or tuples on jack_bot, defend_worker_rush, defend_rush_buildings,
 upgrades/evochamber
 
 _Bug fixes_
 
 - Prevent errors using checks on spines