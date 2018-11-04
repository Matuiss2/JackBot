# Greedy_bot

Its a bot that focus on early aggro, then tries to make a transition

**Change log:**

_Style changes_

- Big refactor on army control, \build and upgrades
 
- Small reformatting changes everywhere it could

- Replace protected attributes for public ones

- Removing outdated comments on army_control

_Optimization and micro-optimization_ 

 _Bug fixes_ 
 
_Functional changes_

- Implement hydralisks 

- Implement range upgrades

- Major tweaks so hydras transitions go smoother 

- Close enemy triggers with 20 instead of 25 (more time to regroup and stronger counter attack)

- Rally point now only considers finished bases(it no longer leaves unnecessary openings on the defense early) 

- Zerglings mandatory train trigger with no zergling speed started changed from 170 to 150(usually zergling speed starts
140 so no need to wait more than 10 seconds for it)

- Minimum zergling amount for worker production reduced to 15 from 17(better long term eco, with no cost for defense)

- Don't make hydras on hydradens vs terran bm(it usually locks the mutalisks)

- Requirements for 3rd base reduced drastically(No difference vs early pressure but huge difference vs macro)

