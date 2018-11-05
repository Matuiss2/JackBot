# Greedy_bot

Its a bot that focus on early aggro, then tries to make a transition

**Change log:**

_Style changes_

- Big refactor on army control, \build and upgrades
 
- Small reformatting changes everywhere it could

- Replace protected attributes for public ones

- Removing outdated comments on army_control

- Reduce the code everywhere 

- Remove unnecessary spaces

_Optimization and micro-optimization_ 

- Remove unnecessary 'if' checks 

- Remove unnecessary 'not' checks 

 _Bug fixes_ 
 
 - Hydras now attack air units on the attack if its the closest
 
 - Hydraden doesnt queue upgrades anymore 

_Functional changes_

- Implement hydralisks 

- Implement range upgrades

- Major tweaks so hydras transitions go smoother 

- Close enemy triggers with 20 instead of 25 (more time to regroup and stronger counter attack)

- Rally point now only considers finished bases(it no longer leaves unnecessary openings on the defense early) 

- Zerglings mandatory train trigger with no zergling speed started changed from 170 to 150(usually zergling speed starts
140 so no need to wait more than 10 seconds for it)

- Minimum zergling amount for worker production reduced to 15 from 17 also include hydralisks count(better long term eco, with no cost for defense)

- Don't make hydras on hydradens or its upgrades vs terran bm(it usually locks the mutalisks)

- Requirements for 3rd base reduced drastically(No difference vs early pressure but huge difference vs macro)

- Include hydralisk count into the attack trigger

- Allow 6 bases to go up before the cavern(with hydras it cant support constant production and go hive with only 5 
bases)
