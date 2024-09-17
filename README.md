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

# Modifications Needed

Ship movement changes. 
    - should keep track of ship movement within a hex (from region to region)
    - ships should be in metaspace while travelling, rather than waiting at one hex and teleporting to the next 
    - When two ships/fleets pass between the same region, an interaction between them should be decided 
    - *fleets* should move around and be composed of ships. 
    - ships shouldn't be deleted after arriving somewhere, they instead should just decide on a new destination. The destination should be based on where it expects to sell its goods for the most profit. 
    - sufficiently damaged fleets someties will return to a friendly port to repair. Military ones will always do so, and this is free. Privately owned ships instead must pay. 
    - Fleets keep track of their owner's finances. 
    - A station's category decides the maximum Credits/day worth of work can be done. Ships need regular maintenance, and so this is a soft cap on the number of ships a sector can support 
    - Update the route-finding to be able to make larger steps depending on the drive rating. Cost should be number of days to get somewhere and dependent on drive rating, fuel bunkers, and fuel scoops. The route will be mapped out on the HexID level, and then intermediate steps will be inserted added after that

Starports are now separate from planets, but really be interlinked. I think the starport should have an associated planet that it draws desireability/tags from. 
A `Terminal` will be some entity, also tied to a planet, from which passengers and trade goods are drawn. 
There could therefore be a terminal on a planets surface or a spaceport. 

# station work speed factor
    A 10
    B 4
    C 2
    D 1
    E 0
    X 0