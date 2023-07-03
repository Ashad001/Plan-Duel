### PLANE DUEL
The game is a Space Invaders clone built using Pygame. It includes a player who can move and shoot bullets,
enemies who move across the screen, obstacles that block the player's bullets and a mysterious ship that flies across the screen from either side.

The player is controlled using the arrow keys to move left and right, and up and down to change the player's height. 
The player shoots bullets using the rigth shift and second player can move by w,s,a,d, up,down,left,rigth respectivly.
it can shoots bullet using space bar.

The enemies move back and forth across the screen and drop bombs that can destroy the player. The player has three lives,
and the game ends when all three lives are lost.

The obstacles are blocks that the player's bullets cannot pass through, forcing the player to avoid them or shoot around them.
The mysterious ship flies across the screen from either side and drops power-ups that can give the player extra lives or a more powerful weapon

total 6 classes are used:
 
1) Player class: Represents the player's plane, which can move in four directions and shoo bullets.

2) Bullet class: Represents the bullets that the player can shoot.

3) Blocker class: Represents the obstacles that the player needs to avoid.

4) Enemy class: Represents the enemies that the player needs to defeat.

5) Mystery class: Represents a mystery object that appears on the screen at random intervals.

6) Game class: class: Represents the game itself, which contains the main game loop and handles the creation of game elements.

Each class defines its own methods and attributes. The Player class, for example, has a get_input() method that checks the player's key presses and moves the player's plane accordingly. It also has attributes like up_key, down_key, and speed that define the keys that the player needs to press and the speed at which the player's plane moves.

The Game class is responsible for creating instances of all the other classes and managing their behavior. It creates instances of the Player, Bullet, Blocker, Enemy, and Mystery classes and adds them to groups. It also defines methods for updating the game state, detecting collisions between game elements, and handling events like key presses.

Overall, the code uses object-oriented programming principles like encapsulation (each class defines its own behavior and data), inheritance (the Player, Bullet, Blocker, Enemy, and Mystery classes all inherit from the pygame.sprite.Sprite class), and polymorphism (each class has its own unique behavior and attributes).
