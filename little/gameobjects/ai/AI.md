# Actions can be placed in the combat tab, or the idle tab

(<precondition>) <action> <target> (<condition>)

 
Combat Examples: (Command are execute by priority from top down)
 
    # Attack nearest enemy:
        attack nearest enemy
    
    # Heal ally if ally health falls below 50%
        cast heal ally any stat HP<50
    
    # The same as above, but only cast if user has more than 20% mana
        stat MP>20 cast heal any ally stat HP<50
    
    # Greet everyone every 60 seconds
        timer 60 say "Hello there!"
        
    # Cure blindness on self if status is blindness
        status blind cast vision self
    
    # Move to farthest player if user HP more than 50%
        stat HP>50 move farthest player
    
    # Attack ally if they forgot their potions!
        attack any ally lacks potion
        
    # Cure any ally who has poison status
        cast heal any ally status poison
  
Idle Examples: (Commands are executed sequentially on a loop)

    # Wander for 10 seconds, buff self, move to coordinates, speak
        wander 10
        cast shielding self
        move (10, 30)
        say "What a long walk!"
       
    # Follow nearest ally with Iron Covenant faction greater than 70
        follow nearest ally faction iron_covenant>70

    # Check for nearest players and buff up to 3 of them every 60 seconds
        timer 60
        cast shielding nearest player
        cast shielding nearest player status not shielding
        cast shielding nearest player status not shielding

# preconditions like: STAT<3 or STAT>5:
#  stat HP>10
#  status blind
#  random 30
#  timer 60

# actions:
#  cast spell_name
#  use item_name
#  move (3,4)
#  follow
#  flee
#  say "<message>"
#  wait <time>
#  wander

# targets
#  nearest <enemy/ally/player>
#  farthest <enemy/ally/player>
#  any <enemy/ally/player>
#  self

# conditions
#  stat MP>30
#  has long_sword
#  lacks potion
#  faction iron_covenent>40
#  status shielding
#  status not poison

Target Types:
    ally    - anyone the AI does not consider KOS 
    enemy   - anyone the AI considers KOS (faction of 0)
    player  - only player controlled Lifeform gameobjects