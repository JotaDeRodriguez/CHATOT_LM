### TODOs

Give variables more consistent names
Integrate battle history into the prompt - DONE
integrate full team data and observations into prompt
improve the prompt - DONE
add more models

Store battle data
Enable verbosity toggles - DONE
Make proper logging
Token counting

Try catch for failed actions and logging them
make concurrent
Create system prompt - DONE

Try double battles:
Excellent! Now I have a clear picture. Here's what you need to know about adapting for double battles:

  Key Differences for Double Battles:

  1. Battle Type: In doubles, battle.active_pokemon is a list of 2 Pokemon (your 2 active mons)
  2. Available moves/switches: These become lists of lists - battle.available_moves[0] for first mon, battle.available_moves[1] for second
  3. Force switch: battle.force_switch is a list of 2 booleans
  4. Return value: You return a DoubleBattleOrder containing two SingleBattleOrder objects (one for each Pokemon)
  5. Targeting: You need to specify move_target when creating orders (e.g., -1 for opponent's left mon, -2 for right)

  To implement this:

  Option 1: Quick adaptation - Modify your existing classes to check if it's a doubles battle and handle accordingly:

  async def choose_move(self, battle):
      if battle.format_is_doubles:
          return await self.choose_doubles_move(battle)
      else:
          # existing single battle logic
          ...

  Option 2: Separate classes - Create Local_DoublesAIPlayer and Router_DoublesAIPlayer classes specifically for doubles

  The AI prompt would need to return actions for both Pokemon, like:
  {
    "reasoning": "...",
    "first_action": "Move name or Pokemon species",
    "first_target": -1,  // -1 = opponent left, -2 = opponent right
    "second_action": "Move name or Pokemon species",
    "second_target": -2
  }

  Would you like me to implement the double battles functionality? If so, which approach would you prefer - modifying existing classes or creating separate ones?  

  - Write Readme