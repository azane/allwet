# allwet
This is a mobile game prototype I designed a couple years ago. I've learned much since then, like the benefits of not putting all the code in one file ;), but the core idea was nonetheless solid: a 'runner' depicted in this prototype as "Shy Guy" (over the image of which I claim no copyright), must navigate a field of sprinklers without getting wet. In this version, getting wet slows the runner down, eventually to a standstill.
Please view the [demo video](https://drive.google.com/file/d/0BwlfuOXPcIRnbWZnR3FEMk5XcFk/view?usp=sharing) to see the prototype in action! Additionally, watch for the geometry drawn to visualize the [collision detection process](#portfolio-considerations) (it exists for debugging purposes, but it visualizes the method as well!).
#### Potential Expansion
A full version would have multiple runners race under various kinds of sprinklers, manipulating puzzle elements involving a piping system with turnable valves and the ability to redirect water pressure, among other things.
#### License
I do retain copyright over these ideas; the benefit of their secrecy does not outwiegh the benefit of their being in my 'portfolio' :). If the reader has any interest in running with this prototype, do please contact me! 

## Portfolio Considerations
If the reader is perusing this as a part of my portfolio, I want to draw special attention to the collision detection strategies employed. The water from each sprinkler comprises segments, and it is contact with these segments that get the runner wet. First, it is determined which sprinklers the runner is in range of, then it is determined if the runner is in the minimum bounding triangle created by the segments. Finally, the segments are iterated until the one segment is found that the runner might collide with. This subdivision massively reduces the bodies that need to be considered for collision.
#### Known Shortcomings and Potential Improvements
Currently, the outermost loop determining which sprinklers the runner is within range of simply iterates the sprinklers. But if I were to do it again, and if there enough runners to warrant the effort, I would use the sweepline/sweepwindow method as specified in the note in the main drawing loop of the script, resulting in a best case of O(s), an average case of O(s\*r/k) and a worst case of O(s\*r), though I'm sure even that could greatly improved upon. This would replace the current O(s\*r) for every case. 's' is the number of sprinklers, 'r' is the number of runners, and 'k' is an integer representing the subsection of runners evaluated in a given window.

## Try it!
So long as it is not distributed, modified, or used commercially, the reader may download the script and run the prototype using a pygame-equipped Python 2.7 installation. The runner will run toward the cursor at a rate proportional to the runner's distance to the cursor, up to a constant. Pressing left shift resets the environment and the score. Enjoy!
