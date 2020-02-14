### BACKEND SIDE OF THE CHAT APPLICATION

Over the course of the last month, I've been putting this application together with a
Django powered backend and a React.js powered frontend, having never made a SPA before.
I like to think I learned a lot. At this point, which is my stopping point, here are
some of my notes:

- User authentication via the /signup and /login and /logout endpoints
- Realtime chat messaging with the ability for users to add new groups,
leave groups, add other users to groups, change group names, and perform
commands within the scope of a group conversation.
- Unfortunately, I made some questionable design decisions and at the
interaction between the client and server sides on the WebSocket side
could use some (understatement) ironing out.
- There is CSRF protection, which took me a little too long to figure out.
- The app requires a running instance of Redis to work with the channel
layers.
- I have tests set up to cover basic model methods, but I quickly grew
tired of working on this project so testing coverage is limited.
- The application is viewed best on desktop
- I know this (as a whole) is pretty unprofessional, but I'm a kinda
proud.
