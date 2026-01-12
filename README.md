# AutoBots

## Placed 3rd at the Fall Clark hackathon 2025!

## What it Does

AutoBots is an online interface to create 'bots' in Python to compete in 1v1 competition with someone else's creation in fun games like Connect4 and TicTacToe. Users can also create their own games!

## Inspiration

As avid programmers, we are always looking for fun ways to improve our skills. Programming problems are often tedious and abstract, and it can be difficult to find the time to start a project. 
We were familiar with bot programming competitions, but despite having interesting problems and being adaptable to a wide range of programming levels and time constraints, there are no on demand options for these competitions.

## Tech Stack

- Python
- JavaScript
- FastAPI
- React
- Websockets
- CodeMirror
- Pyodide
- Piston
- MongoDB

## My contribution

I was primarily responsible for the backend, working with Websockets to create real-time communication between users and the server, integrating Pyodide to run user-submitted Python code in the browser sandbox on their end, and utilizing Piston to securely run user submitted game logic server-side.

## Challenges we ran into
The key challenge we ran into is security. By allowing users to make their own games and write their own bots we knew we could not allow that code to be ran on our server, nor on our user's devices. To solve this, users run their own bots on their machines, responding to the current game state when the server requests. The game logic is ran by the server in Piston, an external secure code execution engine, and the board front end for games is run isolated in an iframe.

## Accomplishments that we're proud of
We are proud of how fun our project ended up being and how scalable it is to add more games, languages, and features such as player statistics or AI made games in the future. We also picked up a lot of new skills throughout this weekend.

## What we learned
We learned about networking with websockets, asynchronous actions, security with code isolation, managing git, and MongoDB.

## What's next for AutoBots
Next for AutoBots is player statistics, AI generated games, training against pre set bots, historically best bots, and larger lobbies for tournaments or battle royales.
