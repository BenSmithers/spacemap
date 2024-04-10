# Spacemap
A reference/utility map for Traveller or Stars Without Number games. Uses the traveller ruleset for system generation, and is based off a lot of the code from [MultiHex](https://github.com/bensmithers/MultiHex2). 

![an example map](https://raw.githubusercontent.com/BenSmithers/spacemap/main/wiki/galaxy.png)

# A few current features
 - generates a whole sector and rolls for all of the attributes of each of the main world
 - creates a government, its tech level, the law level, and all present factions for each system
 - "Retailers" can be generated as vendors and purchasers at each system. Retailers will have different prices for trade goods depending on (1) random chance representing their own feelings, (2) a provided brokerage skill, and (3) the characteristics of the world they live on.
 - A passenger list is provided at each system too, each of them will have a different desired destination and quality of cabin they require.
 - The lieges and vassals of each system is generated, and the territory of each soverign displayed.
 - Bases for each system are generated. TAS, naval bases, scout bases, etc
 - Trade routes between systems are generated for different trade goods.
 - AI ships populate the map. They will start from a system, sampled from how "wealthy" systems in the sector are, and choose some destination (preferring established routes). AI ships carry cargo based off their home world's availability.
 - AI ships will step towards their destination as you step the clock forwards. When they arrive at their destination, a new ship is generated after sampling from the world. 
