# Milestone 3 README

### Why did you choose to test the code you did
The code I tested ensured that the right code executes given the conditions. Many of them were socket emits and database commits. The functionality of my chat box application involves displaying the correct messages, names, pictures, etc. It was important to make sure the sockets are emitted what pertains to the given user/message. If the proper message was not saved in the database, then anything the sockets emit would not be the right data either. I also tested the logic of my bot commands. There is a lot of room for edge cases and error, given that a user is typing them, so it was important to make sure the bot correctly handles any type of message it recieves.

### What more would I test
I would test so that there is 100% test coverage. I could test more with my database table creations and commits, to ensure all the information going into them is correct. I would also test my google authorization code and ensure the correct icon, user, and email is getting saved and that the correct sequence of events happens after a user signs in. Also, it would be beneficial to test the visuals of my code. Checking whether lengths of certain links/images/text will cause it to display weirdly or if the database table chat log gets too large, what happens to the scroll bar.
