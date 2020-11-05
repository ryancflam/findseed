from time import time
from asyncio import TimeoutError
from random import randint, choice
from string import ascii_lowercase

from discord import Embed
from discord.ext import commands

import funcs
from game_models.bulls_and_cows import BullsAndCows
from game_models.card_trick import CardTrick, PlayingCards
from game_models.minesweeper import Minesweeper
from game_models.battleship import Battleship
from game_models.hangman import Hangman


class ChatGames(commands.Cog, name="Chat Games"):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.gameChannels = []

    async def checkGameInChannel(self, ctx):
        if ctx.channel.id in self.gameChannels:
            await ctx.channel.send(
                embed=funcs.errorEmbed(
                    None, "A game is already in progress in this channel, please be patient or use another channel!")
            )
            return True
        return False

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="guessthenumber", description="Play Guess the Number.", aliases=["gtn", "gn"])
    async def guessthenumber(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.channel.send("**Welcome to Guess the Number. A random number between " + \
                               "1-10000 will be generated and your job is to guess it. " + \
                               "Input `time` to see total elapsed time, or `quit` to quit the game.**")
        self.gameChannels.append(ctx.channel.id)
        starttime = time()
        number = randint(1, 10000)
        attempts = 0
        guess = ""
        while guess != number:
            await ctx.channel.send(f"`Attempt {attempts+1} for {ctx.author.name}. Please guess a number between 1-10000.`")
            try:
                message = await self.client.wait_for(
                    "message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=30
                )
            except TimeoutError:
                await ctx.channel.send(f"`{ctx.author.name} has left Guess the Number for idling too long.`")
                break
            try:
                guess = int(message.content)
                if not 1 <= guess <= 10000:
                    await ctx.channel.send(embed=funcs.errorEmbed(None, "Input must be 1-10000 inclusive."))
                else:
                    attempts += 1
                    if guess < number:
                        await ctx.channel.send("`The number is larger than your guess. Guess higher!`")
                    elif guess > number:
                        await ctx.channel.send("`The number is smaller than your guess. Guess lower!`")
                    else:
                        await ctx.channel.send("`You have found the number!`")
            except ValueError:
                if message.content.casefold() == "quit" or message.content.casefold() == "exit" or message.content.casefold() == "stop":
                    break
                elif message.content.casefold() == "time":
                    _, m, s, _ = funcs.timeDifferenceStr(time(), starttime, noStr=True)
                    await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
                else:
                    await ctx.channel.send(embed=funcs.errorEmbed(None, "Invalid input."))
        await ctx.channel.send(f"```The number was {number}.\n\nTotal attempts: {attempts}\n\n" + \
                               f"Thanks for playing, {ctx.author.name}!```")
        _, m, s, _ = funcs.timeDifferenceStr(time(), starttime, noStr=True)
        await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="bullsandcows", description="Play Bulls and Cows.", aliases=["bc", "bulls", "cows"])
    async def bullsandcows(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.channel.send("**Welcome to Bulls and Cows. Input `help` for help, " + \
                               "`time` to see total elapsed time, or `quit` to quit the game.**")
        self.gameChannels.append(ctx.channel.id)
        game = BullsAndCows()
        while not game.getStoppedBool():
            await ctx.channel.send(f"`Attempt {game.getAttempts()+1} for {ctx.author.name}. " + \
                                   "Please guess a four-digit number with no duplicates.`")
            try:
                message = await self.client.wait_for(
                    "message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=90
                )
            except TimeoutError:
                await ctx.channel.send(f"`{ctx.author.name} has left Bulls and Cows for idling too long.`")
                break
            try:
                guess = message.content
                bulls, cows = game.guess(guess)
                if guess.casefold() == "time":
                    m, s = game.getTime()
                    await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
                elif guess.casefold() == "help":
                    await ctx.channel.send(
                        "```== Bulls and Cows ==\n\nBulls and Cows is a code-breaking logic-based game, " + \
                        "originally played using pencil and paper, where one tries to guess a number that" + \
                        " has been randomly generated by the bot. This game has inspired the commercially" + \
                        " marketed board game Mastermind and possibly predates it by over a century.\n\n" + \
                        "The randomly generated number contains exactly four digits between 0 and 9, and" + \
                        " unlike Guess the Number, the digits have no repeats.\n\nExample of a valid guess:" + \
                        " 1234\nExample of an invalid guess: 1244 (The digit 4 has been used twice when it " + \
                        "can only be used once.)\n\nIn the game, the player is asked to enter a four-digit " + \
                        "number which is then compared to the randomly generated four-digit number; each " + \
                        "individual digit entered by the player is compared to each digit within the randomly" + \
                        " generated number. If a digit in the player's guess is in the randomly generated " + \
                        "number and is in the same position in it as it was in their number, then it is " + \
                        "scored as a 'bull'. If that same digit is in a different position, then it is marked" + \
                        " as a 'cow'.\n\nThe goal of this particular version of the game is to find all four " + \
                        "bulls in the shortest amount of time, using as few attempts as possible. If " + \
                        "victorious, the player wins 300 experience points.\n\nExample:\nRandomly generated " + \
                        "number: 1234\nGuess: 1325\nResult: 1 bull and 2 cows. (1 is the bull, whereas 2 " + \
                        "and 3 are the cows. 5 is not in the randomly generated number, hence it is " + \
                        "disregarded and not scored.)```"
                    )
                elif guess.casefold() == "quit" or guess.casefold() == "exit" or guess.casefold() == "stop":
                    continue
                else:
                    await ctx.channel.send(f"`Result: {bulls} bull{'' if bulls == 1 else 's'} and " + \
                                           f"{cows} cow{'' if cows == 1 else 's'}." + \
                                           f"{'' if bulls != 4 else ' You have found the number!'}`")
            except Exception as ex:
                await ctx.channel.send(embed=funcs.errorEmbed(None, str(ex)))
        await ctx.channel.send(f"```The number was {game.getNumber()}.\n\nTotal attempts: {game.getAttempts()}\n\n" + \
                               f"Thanks for playing, {ctx.author.name}!```")
        m, s = game.getTime()
        await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="21cardtrick", description="Play the 21 Card Trick.", aliases=["ct", "21", "cardtrick"])
    async def cardtrick(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.channel.send("**Welcome to the 21 Card Trick. " + \
                               "Pick a card from one of the three piles and I will try to guess it.**")
        self.gameChannels.append(ctx.channel.id)
        game = CardTrick()
        cardSample = game.getSample()
        count = 0
        while count != 3:
            count += 1
            p1, p2, p3 = game.piles(cardSample)
            await ctx.channel.send(f"```{game.showCards(p1, p2, p3)}```")
            while True:
                await ctx.channel.send(f"`Which pile is your card in, {ctx.author.name}? " + \
                                       "Enter either 1, 2, or 3 to pick a pile, or 'quit' quit the game.`")
                try:
                    message = await self.client.wait_for(
                        "message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=30
                    )
                    content = message.content
                    if content.casefold() == "quit" or content.casefold() == "exit" or content.casefold() == "stop":
                        await ctx.channel.send(f"`{ctx.author.name} has left the 21 Card Trick.`")
                        self.gameChannels.remove(ctx.channel.id)
                        return
                    choice = int(content)
                    if not 1 <= choice <= 3:
                        await ctx.channel.send(embed=funcs.errorEmbed(None, "Input must be 1-3 inclusive."))
                    else:
                        cardSample = game.shuffle(choice, p1, p2, p3)
                        break
                except TimeoutError:
                    await ctx.channel.send(f"`{ctx.author.name} has left the 21 Card Trick for idling too long.`")
                    self.gameChannels.remove(ctx.channel.id)
                    return
                except ValueError:
                    await ctx.channel.send(embed=funcs.errorEmbed(None, "Invalid input."))
        yourCard = cardSample[10]
        e = Embed(title="21 Card Trick")
        e.add_field(name=f"{ctx.author.name}'s Card", value=f"`{PlayingCards().returnCardName(yourCard)}`")
        e.set_image(url=PlayingCards().returnCardImage(yourCard))
        e.set_footer(text="Have I guessed it correctly?")
        await ctx.channel.send(embed=e)
        self.gameChannels.remove(ctx.channel.id)

    async def gameIdle(self, ctx, game, ms):
        if ms:
            title = "Minesweeper"
            game.revealSquares()
        else:
            title = "Battleship"
        await ctx.channel.send(f"`{ctx.author.name} has left {title} for idling too long.`")

    async def rowOrCol(self, ctx, game, choice, ms):
        if choice:
            rolCol = "vertical row number between 0-9. (set of numbers on the left)"
        else:
            rolCol = "horizontal column number between 0-9. (set of numbers at the top)"
        await ctx.channel.send(f"`Please enter a {rolCol}`")
        try:
            msg = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.message.channel and m.author == ctx.author, timeout=120
            )
        except TimeoutError:
            await self.gameIdle(ctx, game, ms)
            return "quit"
        yy = msg.content
        while yy.casefold() != "time" and yy.casefold() != "quit" and yy.casefold() != "stop" and yy.casefold() != "exit":
            try:
                yy = int(yy)
                if not 0 <= yy <= 9:
                    pass
                else:
                    break
            except ValueError:
                pass
            await ctx.channel.send(embed=funcs.errorEmbed(None, "Invalid input."))
            await ctx.channel.send(f"`Please enter a {rolCol}`")
            try:
                msg = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.message.channel and m.author == ctx.author, timeout=120
                )
            except TimeoutError:
                await self.gameIdle(ctx, game, ms)
                return "quit"
            yy = msg.content
        if str(yy).casefold() == "quit" or str(yy).casefold() == "exit" or str(yy).casefold() == "stop":
            if ms:
                game.revealSquares()
            return "quit"
        elif str(yy).casefold() == "time":
            m, s = game.getTime()
            await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
            return None
        else:
            return yy

    async def gameOptions(self, ctx, game):
        squaresLeft = 90 - game.getUncovered()
        await ctx.channel.send(
            f"`{ctx.author.name} has {90 - game.getUncovered()} square{'' if squaresLeft==1 else 's'} left to uncover.`"
        )
        await ctx.channel.send("`Would you like to reveal, flag, or unflag a location?`")
        try:
            msg = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.message.channel and m.author == ctx.author, timeout=120
            )
        except TimeoutError:
            await self.gameIdle(ctx, game, True)
            return
        decision = msg.content
        while decision.casefold() != "f" and decision.casefold() != "flag" \
                and decision.casefold() != "time" and decision.casefold() != "r" \
                and decision.casefold() != "reveal" and decision.casefold() != "u" \
                and decision.casefold() != "unflag" and decision.casefold() != "exit" \
                and decision.casefold() != "quit" and decision.casefold() != "stop":
            await ctx.channel.send(embed=funcs.errorEmbed(None, "Invalid input."))
            await ctx.channel.send("`Would you like to reveal, flag, or unflag a location?`")
            try:
                msg = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.message.channel and m.author == ctx.author, timeout=120
                )
            except TimeoutError:
                await self.gameIdle(ctx, game, True)
                return
            decision = msg.content
        if decision.casefold() == "quit" or decision.casefold() == "exit" or decision.casefold() == "stop":
            game.revealSquares()
            return
        if decision.casefold() == "time":
            m, s = game.getTime()
            await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
            return
        yy = await self.rowOrCol(ctx, game, True, True)
        if yy == "quit" or yy is None:
            return
        else:
            yy = int(yy)
        xx = await self.rowOrCol(ctx, game, False, True)
        if xx == "quit" or xx is None:
            return
        else:
            xx = int(xx)
        if decision.casefold() == "f" or decision.casefold() == "flag":
            if game.getDispboard()[yy][xx] != ".":
                if game.getDispboard()[yy][xx] == "F":
                    game.getDispboard()[yy][xx] = "."
                else:
                    await ctx.channel.send(embed=funcs.errorEmbed(None, "This location has already been revealed before."))
                    return
            else:
                game.getDispboard()[yy][xx] = "F"
        elif decision.casefold() == "u" or decision.casefold() == "unflag":
            if game.getDispboard()[yy][xx] != "F":
                await ctx.channel.send(embed=funcs.errorEmbed(None, "This location is not flagged."))
                return
            else:
                game.getDispboard()[yy][xx] = "."
        elif decision.casefold() == "r" or decision.casefold() == "reveal":
            if game.getDispboard()[yy][xx] != ".":
                if game.getDispboard()[yy][xx] == "F":
                    await ctx.channel.send("`Watch out, you have previously flagged this location before!`")
                    return
                else:
                    await ctx.channel.send(embed=funcs.errorEmbed(None, "This location has already been revealed before."))
                    return
            else:
                game.uncoverSquares(xx, yy)
                game.incrementAttempts()
        return

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="minesweeper", description="Play Minesweeper.", aliases=["ms", "mines"])
    async def minesweeper(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.channel.send("**Welcome to Minesweeper. Input `time` to see total elapsed time, or `quit` to quit the game.**")
        self.gameChannels.append(ctx.channel.id)
        game = Minesweeper()
        won = False
        while not game.getGameEnd():
            await ctx.channel.send(f"```Attempt {game.getAttempts()+1} for {ctx.author.name}. " + \
                                   f"Current board:\n\n{game.displayBoard()}```")
            await self.gameOptions(ctx, game)
            won = game.winLose()
        await ctx.channel.send(f"```Current board:\n\n{game.displayBoard()}```")
        m, s = game.getTime()
        await ctx.channel.send(f"```You have {'won' if won else 'lost'} Minesweeper!\n\nTotal attempts: {game.getAttempts()}" + \
                               f"\n\nThanks for playing, {ctx.author.name}!```")
        await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="battleship", description="Play Battleship.", aliases=["bs", "battleshit"])
    async def battleship(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.channel.send("**Welcome to Battleship. Input `time` to see total elapsed time, " + \
                               "or `quit` to quit the game.**")
        self.gameChannels.append(ctx.channel.id)
        game = Battleship()
        while game.getShipcount() > 0:
            await ctx.channel.send(
                f"```Attempt {game.getAttempts()+1} for {ctx.author.name}. {game.displayBoard(False)}```"
            )
            await ctx.channel.send(
                f"`{ctx.author.name} has {game.getShipcount()} ship{'' if game.getShipcount()==1 else 's'} left to find.`"
            )
            yy = await self.rowOrCol(ctx, game, True, False)
            if yy == "quit":
                await ctx.channel.send(f"```{game.displayBoard(True)}```")
                break
            elif yy is None:
                continue
            else:
                yy = int(yy)
            xx = await self.rowOrCol(ctx, game, False, False)
            if xx == "quit":
                await ctx.channel.send(f"```{game.displayBoard(True)}```")
                break
            elif xx is None:
                continue
            else:
                xx = int(xx)
            await ctx.channel.send(f"`{ctx.author.name} has {game.takeTurn(yy, xx)}.`")
        m, s = game.getTime()
        await ctx.channel.send(f"```You have {'won' if game.getWonBool() else 'lost'} Battleship!\n\n" + \
                               f"Total attempts: {game.getAttempts()}\n\nThanks for playing, {ctx.author.name}!```")
        await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="rps", description="Play Rock Paper Scissors.",
                      aliases=["rockpaperscissors", "rsp", "psr", "prs", "srp", "spr"])
    async def rps(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        self.gameChannels.append(ctx.channel.id)
        while True:
            aic = choice(["Rock", "Paper", "Scissors"])
            if aic == "Rock":
                aiclist = ["Scissors", "Rock", "Paper"]
            elif aic == "Paper":
                aiclist = ["Rock", "Paper", "Scissors"]
            else:
                aiclist = ["Paper", "Scissors", "Rock"]
            listindex = aiclist.index(aic)
            await ctx.channel.send("`Rock, paper, or scissors?`")
            try:
                msg = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.message.channel and m.author == ctx.author, timeout=60
                )
            except TimeoutError:
                await ctx.channel.send(f"`{ctx.author.name} has feft Rock Paper Scissors for idling too long.`")
                self.gameChannels.remove(ctx.channel.id)
                return
            if msg.content.casefold().startswith("r") or msg.content.casefold().startswith("p") \
                    or msg.content.casefold().startswith("s"):
                if msg.content.casefold().startswith("r"):
                    answer = "Rock"
                elif msg.content.casefold().startswith("p"):
                    answer = "Paper"
                else:
                    answer = "Scissors"
            else:
                await ctx.channel.send(embed=funcs.errorEmbed(None, "Invalid input."))
                continue
            await ctx.channel.send(f"`{self.client.user.name} bot chose: {aic}`")
            if answer == aic:
                await ctx.channel.send(f"`It's a tie! {ctx.author.name} gets to play again.`")
                continue
            else:
                getindex = aiclist.index(answer)
                if getindex < listindex:
                    await ctx.channel.send(f"`{ctx.author.name} has lost Rock Paper Scissors!`")
                else:
                    await ctx.channel.send(f"`{ctx.author.name} has won Rock Paper Scissors!`")
                self.gameChannels.remove(ctx.channel.id)
                return

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="hangman", description="Play Hangman.", aliases=["hm", "hangyourself", "hang"])
    async def hangman(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.channel.send(
            "**Welcome to Hangman. You have 10 lives. Guess one letter at a time. " + \
            "Input `lives` to see how many lives you have left, `time` to see total elapsed time, or `quit` to quit the game.**"
        )
        self.gameChannels.append(ctx.channel.id)
        game = Hangman()
        while game.getLives() > 0 and not game.getDashes() == game.getWord():
            await ctx.channel.send(f"```{ctx.author.name}'s word:\n\n{game.getDashes()}```")
            await ctx.channel.send("`Please guess a letter.`")
            try:
                guess = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.message.channel and m.author == ctx.author, timeout=120
                )
            except TimeoutError:
                await ctx.channel.send(f"`{ctx.author.name} has left Hangman for idling too long.`")
                await ctx.channel.send(f"`{ctx.author.name}'s word was {game.getWord()}.`")
                self.gameChannels.remove(ctx.channel.id)
                return
            content = guess.content
            if len(content) != 1:
                if content.casefold() == "quit" or content.casefold() == "exit" or content.casefold() == "stop":
                    await ctx.channel.send(f"`{ctx.author.name} has left Hangman.`")
                    await ctx.channel.send(f"`{ctx.author.name}'s word was {game.getWord()}.`")
                    self.gameChannels.remove(ctx.channel.id)
                    return
                elif content.casefold().startswith("live"):
                    lives = game.getLives()
                    await ctx.channel.send(f"`{ctx.author.name} has {game.getLives()} live{'s' if lives!=1 else ''} left.`")
                elif content.casefold().startswith("time"):
                    m, s = game.getTime()
                    await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
                else:
                    await ctx.channel.send(embed=funcs.errorEmbed(None, "You may only enter one letter at a time."))
            elif content.lower() not in ascii_lowercase:
                await ctx.channel.send(embed=funcs.errorEmbed(None, "Invalid character(s)."))
                continue
            else:
                try:
                    result = game.makeGuess(content)
                    if result:
                        await ctx.channel.send("`Letter found!`")
                    else:
                        await ctx.channel.send("`Letter not found...`")
                        await ctx.channel.send(f"```{game.hangmanPic()}```")
                except Exception as ex:
                    await ctx.channel.send(embed=funcs.errorEmbed(None, str(ex)))
        if game.getLives() == 0:
            await ctx.channel.send(f"`{ctx.author.name} has lost Hangman. Their word was {game.getWord()}.`")
        else:
            lives = game.getLives()
            await ctx.channel.send(
                f"`{ctx.author.name} has won Hangman with " + \
                f"{'' if lives!=10 else 'all '}{lives} li{'ves' if lives!=1 else 'fe'} left!`"
            )
        m, s = game.getTime()
        await ctx.channel.send(f"`Elapsed time: {m}m {s}s`")
        self.gameChannels.remove(ctx.channel.id)


def setup(client):
    client.add_cog(ChatGames(client))
