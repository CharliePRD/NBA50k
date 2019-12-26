**Users Table**
The first step in my process was creating the user’s database. Within this, I included 5 columns: ID (the user’s ID),
username (the user’s username), hash (the user’s password hashed), cash(the number of points the user has) and
networth(the user’s total net worth, calculated by points + the collection’s value).

**Players Table**
I underestimated the sheer amount of time which collecting and displaying the information needed for my player
database ended up taking. Players represent the cards from which users can pull from packs and keep in their collection.
Players has 5 columns: id (the NBA player’s unique ID), name (player’s name), team (player’s team), overall (player’s overall)
and image (a link to an image of the player’s card). I was able to find a database that, after much editing, contained all
of a player’s information aside from their image link. I then copied and pasted this database from numbers into google forms
and created an image column. For over 200 players, I manually pasted the image link into the table (there was no better way to
do this). Then, I converted the player table into a csv file and imported it into a SQL database.

**Collection Table**
The collection database is meant to represent the player cards which each user owns. It has 3 columns: id (the id of the
collection entry), player id (the id associated with the specific player card) and user_id (the id of the user which owns
this said card).

**register()**
Register begins with if statements confirming the user provided a username, password and confirmed password and that
the password and confirm password are matching. This information is received through a form. If the user fails to do
any of these tasks, they will be redirected to apology (see helpers.py below).  The password is hashed with a simple
generate_password_hash funciton, and stored in the user database along with the user’s username. Once this is finished,
the user is redirected to (“/”), the home page (see home() )

**login()**
Login is similarly structured to register. It has a forum that receives two pieces of data: the user’s username and
password. If either is not provided or if the user is not found, a customized error is provided ( see apology () ).
Once logged in, the user is redirected to (“/”), the home page.

**home()**
The homepage displays a lot of information, so it begins by selected the data it needs to show.
points: Selected from the user database under “cash”. This is in nearly every function (and thus will be the last I
mention of it) so that points may be passed over to each page’s html.

username: Select from the user database under “username”.
overalls: Selected all the overalls of players which the user owns from the collection table.
Collection_images: Selected all information from a joint table of players and collection where the user was the user
who was logged in. This was also ordered in descending order by overall.
Total overalls: total overalls sifted through the entire database of overalls which “overalls” held in a for loop and
added them together. That way, total_overalls was a summation of all the overalls of players which the collection held.
Total value: This is what collection_value is displayed as. It multiplies the total overalls by 65.
Networth: Networth is a sum of total_value and points.

Furthermore, a for loop is included in home.html which iterates through collection_images and displays the player
image as a form for each player. I displayed these as a hidden form so that, when clicked on and taken to the info page
(see info() ), the image link will allow data of the player to be passed through.

**openpacks()**
Openpacks simply redirects to the openpacks.html, which displays an image of a pack that, when clicked on, redirects to packs().

**packs()**
Packs conducts the opening of a pack. First, it checks if you have enough points to purchase the pack. If the user has enough
points, it subtracts 5000 from the user’s cash and runs an SQL command. This SQL command orders the database of players randomly
and selects all information from the top player on the list. Then, it inserts this player into the collection. Packs.html is
rendered which displays this player and this player’s information.

You will notice I included commented out code. This was code I originally made to not allow a player to get a duplicate card.
I spent a lot of time creating this code and making a function called refund() (also commented out) which would tell you you
pulled a duplicate player and give you a refund. This worked by creating a variable called player_found (either 1 or 0) that
confirmed whether or not the player was in the user’s database. However, I realized it made more sense to allow a player to
own multiple of one card as that’s how real-life card opening works. I kept the commented version in just because I spent a
lot of time on it and didn’t want to delete it all (plus, I could now bring it back if I wanted).

**info()**
The player’s image link is passed along from home into info() when the player is clicked because the image clicked is a form.
Then, the full information of the player can be selected where the image link passed over matches the one in the “player” table
and put into a dict called “player”. Then, we can display the player’s name, overall, team and image from this dict called “player”.
The value of the player is the overall * 65, and the selling value is the player’s value * 0.99 rounded (see “scoring” for more
information on this). There is also two buttons below, one to redirect to home and another which allows you to sell for the selling value.

**sell()**
If the button to sell a player is chosen, sell gets all the information of the player in the same way info() does (using the image link)
and puts it into a dict called player. The same variables of points, overall and value are collection as info(). In addition, the player id
is collected from the player dict. Then, the player’s points are increased by the selling value and the SQL database of “users” updates
this player’s cash. Furthermore, the player is deleted from the SQL database of “collection” where the player ids and user ids match--this
is so the player is no longer a part of the user’s collection and isn’t displayed or factored into their networth/collection worth.
Finally, it redirects home.

**leaderboard()**
Leaderboard displays the username, place and networth of every player. It does so by selecting all information (this includes username
and networth) from the “users” database and storing it in a list of dicts called “users” by descending order of networth. It also
initializes x--which will be the place of each user--at 1 and runs it through a for loop of how many users there are so that it may store
it in users under “place”. On the html, a table is iterated for the number of users there are a for loop while displaying the user’s place,
username, and networth.

**logout()**
Logout simply clears the session ID and redirects the user to login().

**helpers.py**
Apology, USD and Login Required are short and all essentially use finance’s code. Apology, however, instead links to a website that makes
a custom meme displaying Michael Jordan crying and the error’s text. USD converts points into a USD format so that it can be displayed in
dollar amounts for values and net worth. Finally, login required checks to see if there is a user logged in by checking if session.get("user_id") is None.

**Scoring**
The overalls of players span from 68 up to 99 with the median being a 78 (the mean is likely a bit higher, around 80). I knew I wanted
to deal with bigger numbers to represents points to give it a video-game feel, so I settled on starting each user with 50,000 points.
Furthermore, I wanted the average pack to be a straightforward number that on average broke-even, so I settled on 5,000. Then, since 78 is the median,
I chose to subtract 78 from the overall and multiple by 400. This would give a number ranging from -4000 to 8400. I would then add this to the price
of the pack, 5000, and that would be the player's worth.
Then, I wanted user’s to be incentivized to collect rather than sell everything and open packs so that there was strategy to the game, so I made the
sell price slightly lower at 99% of what the player’s value is. Furthermore, in order to incentivize user’s to
keep and not sell players I calculated the networth as the value of all the players collected + the points of the user rather than
just the points.

A final note on scoring: Because the mean is actually slightly higher than the median of 78, it’s more likely you make money
from opening a pack and thus users are incentivized to open packs and keep playing to get a higher net worth.
