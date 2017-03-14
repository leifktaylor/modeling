Dialogue (dlg) Templates:

    Dialogue files contain 'lines of dialogue' and 'triggers'
    'triggers' are enclosed in [brackets]
    
    Example syntax would be:
        [hail]
        How are you today?
    
    When the player character has the NPC tagetted and says 'hail',
        the NPC will respond with 'How are you today?'
    
    Actions can also be added to the 'lines of dialogue',
        each action must be on a separate line.
    
    (ALL dialogue must start with a [hail] trigger)
    Here is a fully formed example with dialogue and actions:
        [hail]
        Have you seen the [demon]?
        [demon]
        Yes, I swear I saw him on the top of the watch tower.
        Take this, it will protect you. I must be [going].
        {give gameobjects/weapon/longsword.itm}
        [going]
        Don't worry young one, you won't need me around any longer.
        {cast 23}  # This is a healing spell for the player
        {remove self}

    Actions:
        {need path/to/item.itm}            # Item needed for this trigger
        {dialogue path/to/dialogue.lfm}    # Change dialogue file
        
        {give path/to/item.itm}            # Give item to player
        {take path/to/item.itm}            # Take item from player
        
        {cast spellid}                     # Cast spell on player
        {teleport roomname x y}            # Teleport player
        
        {spawn path/to/lifeform.lfm x y}   # Spawn lifeform
        
        {remove self}                      # Delete self

Lifeform (lfm) Templates:

Item (itm) Templates:

Room (rm) Templates:

Spells: