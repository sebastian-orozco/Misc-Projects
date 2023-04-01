# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

# The name of the second character has been replaced with "person" to protect their identity.
define s = Character("Sebastian", image = "sebastian")
define p = Character("Person", image = "person")


# The game starts here.

label start:

    # Show a background. This uses a placeholder by default, but you can
    # add a file (named either "bg room.png" or "bg room.jpg") to the
    # images directory to show it.

    scene bg mountain2

    # This shows a character sprite. A placeholder is used, but you can
    # replace it by adding a file named "eileen happy.png" to the images
    # directory.


    # These display lines of dialogue.

    s smile "Welcome to Hiking Hotties! I'm your host, Sebastian."

    label choices_1:
        s smile "We're going on a hike in Morse Meadows, want to join?"
    menu:
        "Yes.":
            jump choices_1_common

        "Yes but in a British accent.":
            jump choices_1_common

    label choices_1_common:
        s full-smile"Awesome!"

    scene bg flower-field

    s smile "Ah, what a lovely day..."
    s surprised "Wait, what's that?"

    scene bg grass-book

    label choices_2:
        s surprised "A math textbook?"
    menu: 
        "Take it!":
            jump choices_2a
        "Leave it!":
            jump choices_2b

    label choices_2a:
        s full-smile "Alright! We could read it as a bedtime story to Mediocrates later."
        jump choices_2_common

    label choices_2b:
        s wink "Nahhh, we could read it as a bedtime story to Mediocrates later."
        jump choices_2_common

    label choices_2_common:
        s neutral "I wonder what else we'll find on our hike..."
    
    scene bg forest

    s nervy "Woah, it's getting dark."
    s surprised "Huh, what's that?"

    scene bg wide

    s neutral "Looks like some sort of summoning ritual."
    s "There's blueberries & cream cheese..."
    s "A violin..."
    s "A flag of Hong Kong..."
    s "Sugar (must be really sweet)..."

    label choices_3:
        s "And an empty space."
    menu: 
        "Place the textbook.":
            jump choices_3_common

    label choices_3_common:
        s smile "Good idea!"

    scene bg wide_all with Pause(2)

    scene bg explosion with Pause(2)

    scene bg hearts with Pause(0.5)
    
    p smile "Hey ;)"

    s heartthrob "<3"

    scene bg sunset

    "And they lived happily ever after."
    "Happy 100 Days."

    # This ends the game.

    return

