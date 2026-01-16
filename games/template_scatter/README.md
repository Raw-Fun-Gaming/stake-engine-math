# Scatter-Pays Game

#### Summary:

* A 6-reel, 5-row pay-anywhere tumbling (cascading) game.
* 8 paying total (4 high, 4 low)
* 2 special symbols (wild, scatter)

Symbols payouts are grouped by cluster-sizes (8-8), (9-10), (11,13), (14,36)

#### Base Game:

Minimum of 3 Scatter symbols needed for free game trigger.
2 free game spins are awarded for each Scatter.


#### Free Game rules
Every tumble increments the global multiplier by +1, which is persistent throughout the free game
The global multiplier is applied to the tumble win as they are removed from the board
After all tumbles have completed: multiply the cumulative tumble win by multipliers on board
(multipliers on board do not increment the global mult)
If there is a multiplier symbol on the board, this is added to the global multiplier before the final evaluation


#### Notes
Due to the potential for symbols to tumble into the active board area, there is no upper limit on the number of free game that can be awarded.
The total number of free game is 2 * (number of Scatters on board). To account for this the usual 'update_total_free_spin_amount' function is overridden
in the game_executables.py file.

#### Event descriptions
"winInfo" Summarises winning combinations. Includes multipliers, symbol positions, payInfo [passed for every tumble event]
"tumbleBanner" includes values from the cumulative tumble, with global mult applied
"setWin" this the result for the entire spin (from on Reveal to the next). Applied after board has stopped tumbling
"setTotalWin" the cumulative win for a round. In the base-game this will be equal to the set_win, but in the bonus it will incrementally increase
