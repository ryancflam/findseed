from time import time
from json import load
from datetime import datetime
from asyncio import TimeoutError
from string import ascii_lowercase
from random import randint, choice, shuffle
from akinator import CantGoBackAnyFurther
from akinator.async_aki import Akinator

from discord import Embed, Colour, File
from discord.ext import commands

from other_utils import funcs
from game_models.uno import Uno
from game_models.bulls_and_cows import BullsAndCows
from game_models.card_trick import CardTrick
from game_models.minesweeper import Minesweeper
from game_models.battleship import Battleship
from game_models.hangman import Hangman


class ChatGames(commands.Cog, name="Chat Games"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.gameChannels = []

    async def checkGameInChannel(self, ctx):
        if ctx.channel.id in self.gameChannels:
            await ctx.send(
                embed=funcs.errorEmbed(
                    None,
                    "A game is already in progress in this channel, please be patient or use another channel!"
                )
            )
            return True
        return False

    @staticmethod
    async def sendTime(ctx, m, s):
        await ctx.send(f"`Elapsed time: {m}m {s}s`")

    @commands.command(name="cleargamechannels", description="Resets the game channel list.",
                      aliases=["resetgamechannels", "rgc", "cgc"])
    @commands.is_owner()
    async def cleargamechannels(self, ctx):
        self.gameChannels = []
        await ctx.send(":ok_hand:")

    async def unoDraw(self, user, drawn):
        if drawn is None:
            return False
        await user.send("**== Uno ==**\n\nYou have just drawn the following card(s): " + \
                        f"`{', '.join(card for card in drawn)}`")
        return True

    async def unoCallout(self, ctx, game, caller, victim):
        await caller.send(f"**== Uno ==**\n\nPsst, **{victim.name}** " + \
                          "has not said 'uno' yet! Say `call` in this channel to make" + \
                          " them draw two cards before this turn ends!")
        while game.getCallout():
            try:
                await self.client.wait_for(
                    "message", check=lambda m: m.author == caller and m.content.casefold() == "call", timeout=1
                )
            except TimeoutError:
                continue
            if victim == game.getPreviousPlayer():
                await ctx.send(f"`Uh oh! {victim.name} has been caught not yelling 'uno' by {caller.name}!" + \
                               f" As punishment, {victim.name} has been forced to draw two extra cards. " + \
                               "Better luck next time!`")
                if not await self.unoDraw(victim, game.callout()):
                    await ctx.send("`No more cards available to draw.`")
                return

    async def unoAwaitInput(self, ctx, game, user):
        while user in game.getPlayerList() and not game.getGameEndBool():
            try:
                var = await self.client.wait_for(
                    "message", check=lambda m: m.author == user, timeout=1
                )
                if var.content.casefold() == "time":
                    m, s = game.getTime()
                    await var.channel.send(f"`Elapsed time: {m}m {s}s`")
                elif var.content.casefold() == "hand" or var.content.casefold() == "h":
                    hand = game.getHand(user)
                    msg = f"`{', '.join(card for card in hand)}` ({len(hand)} left)"
                    await user.send(f"**== Uno ==**\n\nYour hand: {msg}")
                    await var.channel.send("`Please check DMs.`")
                elif var.content.casefold().startswith("uno"):
                    if game.getCallout() and len(game.getHand(user)) == 1 and game.getPreviousPlayer() == user:
                        await ctx.send(f"`Uno! {user.name} has only one card left!`")
                        game.saidUno()
                else:
                    continue
            except:
                continue

    @staticmethod
    def unoEmbedColour(card):
        if card.startswith("B"):
            return Colour.blue()
        if card.startswith("G"):
            return Colour.green()
        if card.startswith("R"):
            return Colour.red()
        if card.startswith("Y"):
            return Colour.orange()
        return Colour(0x23272A)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="uno", description="Play Uno.")
    @commands.guild_only()
    async def uno(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        self.gameChannels.append(ctx.channel.id)
        await ctx.send("**A game of Uno is starting in one minute in this channel! " + \
                       "Say `join` to join. The game requires a minimum of 2 players and a maximum of 4.**")
        game = Uno()
        game.addPlayer(ctx.author)
        waiting = time()
        while time() - waiting < 60:
            try:
                joinGame = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.content.casefold() == "join", timeout=1
                )
            except TimeoutError:
                continue
            with open(
                    f"{funcs.getPath()}/blacklist.json", "r", encoding="utf-8"
            ) as f:
                data = load(f)
            f.close()
            if joinGame.author.bot or joinGame.author in game.getPlayerList() or joinGame.author.id in list(data["users"]):
                continue
            else:
                game.addPlayer(joinGame.author)
                await ctx.send(f"`{joinGame.author.name} has joined Uno.`")
                if len(game.getPlayerList()) == 4:
                    break
        if len(game.getPlayerList()) < 2:
            self.gameChannels.remove(ctx.channel.id)
            return await ctx.send("**Not enough players for Uno; stopping current game.**")
        await ctx.send(
            f"**Starting a game of Uno with {len(game.getPlayerList())} players. " + \
            "Input `hand` to see your hand of cards, `time` to see total elapsed time, or " + \
            "`quit` to quit the game (Note: You may only quit when it is your turn). " + \
            "Remember to say `uno` when you only have one card left!**"
        )
        game.startGame()
        drawn, playable, wildCard, lastCard = [], False, False, False
        count = 1
        for player in game.getPlayerList():
            self.client.loop.create_task(self.unoAwaitInput(ctx, game, player))
            hand = game.getHand(player)
            msg = f"`{', '.join(card for card in hand)}` ({len(hand)} left)"
            await player.send(f"**== Uno ==**\n\nWelcome to Uno. You are player {str(count)}." + \
                              f" Active channel: <#{ctx.channel.id}>\n\nYour hand: {msg}\n\n" + \
                              "**Remember to say `uno` as soon as you play your second to last card!**")
            count += 1
        logo = "https://media.discordapp.net/attachments/668552771120791563/775240814636171324/logo.png"
        await ctx.send(f"`Say the name of a card in your hand to play it. " + \
                       "Say 'draw' to draw a card. Inputs are case insensitive, and you may " + \
                       "enter the first letter of the card colour and card value (e.g. r 5).`")
        while not game.getGameEndBool():
            if len(game.getPlayerList()) < 2:
                break
            try:
                playerCards = ""
                discard = game.getDiscardPileCard()
                colour = self.unoEmbedColour(discard)
                e = Embed(
                    title="Uno",
                    description=f"**{game.getCurrentPlayer().name}'s turn!**",
                    colour=colour
                )
                file = File(
                    f"{funcs.getPath()}/assets/uno_cards/" + \
                    f"{'Xmas_' if datetime.now().month == 12 else ''}{discard.replace(' ', '_')}.png",
                    filename="card.png"
                )
                e.set_image(url="attachment://card.png")
                e.set_thumbnail(url=logo)
                for player in game.getPlayerList():
                    playerCards += f"{player.name} - {len(game.getHand(player))}\n"
                e.add_field(name="Total Player Cards", value=f"```{playerCards[:-1]}```")
                e.add_field(name="Discard Pile Card", value=f"`{game.getDiscardPileCard()}`")
                await ctx.send(embed=e, file=file)
                while True:
                    currentPlayer = game.getCurrentPlayer()
                    try:
                        waitForInput = await self.client.wait_for(
                            "message", check=lambda m: m.author == currentPlayer, timeout=120
                        )
                        decision = waitForInput.content
                        if decision.casefold().startswith("d"):
                            await ctx.send(f"`{currentPlayer.name} has drawn a card.`")
                            drawn, affectedPlayer, playable, wildCard = game.drawCard()
                        elif decision.casefold() == "quit":
                            await ctx.send(f"`{currentPlayer.name} has left Uno.`")
                            game.removePlayer(currentPlayer)
                            if len(game.getPlayerList()) < 2:
                                await ctx.send("**Not enough players for Uno; stopping current game.**")
                            break
                        elif decision.casefold().startswith("w ") or decision.casefold() == "w" \
                                or decision.casefold().startswith("wild"):
                            await waitForInput.channel.send("`What colour would you like to use? " + \
                                                            "Please say the first letter of your preferred colour.`")
                            try:
                                waitForColour = await self.client.wait_for(
                                    "message", check=lambda m: m.author == currentPlayer, timeout=120
                                )
                            except TimeoutError:
                                await ctx.send(f"`{currentPlayer.name} has left Uno for idling too long.`")
                                game.removePlayer(currentPlayer)
                                break
                            colour = waitForColour.content
                            drawn, affectedPlayer, lastCard = game.playWildCard(colour, "+4" in decision)
                            await ctx.send(f"`{waitForInput.author.name} has played a wild card.`")
                        elif not decision.casefold().startswith("b") and not decision.casefold().startswith("g") \
                                and not decision.casefold().startswith("r") and not decision.casefold().startswith("y"):
                            break
                        else:
                            drawn, affectedPlayer, lastCard = game.playColouredCard(decision)
                            await ctx.send(f"`{waitForInput.author.name} has played a card.`")
                        if lastCard:
                            for player in game.getPlayerList():
                                if player == waitForInput.author:
                                    continue
                                self.client.loop.create_task(self.unoCallout(ctx, game, player, waitForInput.author))
                            lastCard = False
                        if playable:
                            _ = await self.unoDraw(affectedPlayer, drawn)
                            await affectedPlayer.send("**== Uno ==**\n\nYour drawn card is playable! Would you like " + \
                                                      "to play it? Input `y` to play it, or anything else to keep it.")
                            try:
                                waitForOption = await self.client.wait_for(
                                    "message", check=lambda m: m.author == affectedPlayer, timeout=120
                                )
                                playCard = waitForOption.content
                                if playCard.casefold().startswith("y"):
                                    await ctx.send(f"`{waitForOption.author.name} has played the drawn card.`")
                                    if wildCard:
                                        await waitForOption.author.send("`What colour do you want? Please say " + \
                                                                        "the first letter of your preferred colour.`")
                                        await ctx.send(f"`{waitForOption.author.name} has played a wild card.`")
                                        try:
                                            waitForColour = await self.client.wait_for(
                                                "message", check=lambda m: m.author == waitForOption.author, timeout=120
                                            )
                                        except TimeoutError:
                                            await ctx.send(f"`{waitForOption.author.name} has left Uno for idling too long.`")
                                            game.removePlayer(waitForOption.author)
                                            break
                                        colour = waitForColour.content
                                        drawn, affectedPlayer, lastCard = game.playWildCard(colour, "+4" in drawn[0], True)
                                    else:
                                        drawn, affectedPlayer, lastCard = game.playColouredCard(drawn[0], True)
                                    if lastCard:
                                        for player in game.getPlayerList():
                                            if player == waitForOption.author:
                                                continue
                                            self.client.loop.create_task(self.unoCallout(ctx, game, player, waitForOption.author))
                                        lastCard = False
                                else:
                                    await waitForOption.author.send("**== Uno ==**\n\nYou are keeping the card.")
                            except TimeoutError:
                                await affectedPlayer.send(f"**== Uno ==**\n\nYou have been idling for too long. " + \
                                                          "You will now proceed to keep the card.")
                            playable, wildCard = False, False
                        if drawn is None:
                            await affectedPlayer.send("**== Uno ==**\n\nYou are about to be the victim of a Wild +4 card!" + \
                                                      " Do you think it may be an illegal move? If so, you may input `y` to " + \
                                                      "challenge the player.\n```== Wild +4 Challenges ==\n\nAccording to " + \
                                                      "the official Uno rules, it is considered illegal for a player to use " + \
                                                      "a Wild +4 card if there are still cards on their hand that match " + \
                                                      "the colour of the current card on top of the discard pile. Once a Wild" + \
                                                      " +4 card is played, the victim may choose to challenge the player; if " + \
                                                      "challenged, the player of the Wild +4 card must then show their hand " + \
                                                      "of cards to the victim.\n\nIf guilty, the challenged player draws four" + \
                                                      " cards instead of the accuser as punishment whilst the accuser remains" + \
                                                      " safe from drawing additional cards. However, if not guilty, then the " + \
                                                      "accuser must draw a total of six cards.```\nReply with `y` if you " + \
                                                      "would like to challenge the Wild +4 card play (*You may risk drawing " + \
                                                      "six cards!*), or any other input to decline.")
                            try:
                                waitForOption = await self.client.wait_for(
                                    "message", check=lambda m: m.author == affectedPlayer, timeout=120
                                )
                                decision = waitForOption.content
                            except TimeoutError:
                                await affectedPlayer.send(f"**== Uno ==**\n\nYou have been idling for too long. " + \
                                                          "You will now proceed to draw four cards.")
                            decision = decision.casefold().startswith("y")
                            if decision:
                                await ctx.send(f"`{affectedPlayer.name} suspects that the Wild +4 card is being " + \
                                               f"played illegally! {currentPlayer.name} will now show their hand " + \
                                               f"of cards to {affectedPlayer.name}.`")
                                msg = f"`{', '.join(card for card in game.getHand(currentPlayer))}` " + \
                                      f"({len(game.getHand(currentPlayer))} left)"
                                await affectedPlayer.send(f"**== Uno ==**\n\n{currentPlayer.name}'s hand: {msg}")
                            drawn, affectedPlayer, guilty = game.challengePlayer(decision)
                            if guilty:
                                await ctx.send(f"`Uh oh! {affectedPlayer.name} has been caught illegally playing " + \
                                               f"the Wild +4 card by {game.getCurrentPlayer().name}! As " + \
                                               f"punishment, {affectedPlayer.name} has been forced to draw " + \
                                               f"four cards. {game.getCurrentPlayer().name} is " + \
                                               "now safe from drawing.`")
                            if decision and not guilty:
                                await ctx.send("`It looks like the Wild +4 card has been played legally " + \
                                               f"after all. Because of that, {affectedPlayer.name} will now " + \
                                               "have to draw a total of six cards! Better luck next time.`")
                        if len(drawn) != 0:
                            _ = await self.unoDraw(affectedPlayer, drawn)
                            break
                        break
                    except TimeoutError:
                        await ctx.send(f"`{currentPlayer.name} has left Uno for idling too long.`")
                        game.removePlayer(currentPlayer)
                        break
            except Exception as ex:
                error = str(ex)
                if error.startswith("not enough values to unpack"):
                    error = "Invalid card."
                await ctx.send(embed=funcs.errorEmbed(None, error))
        first, second, third, fourth = game.getPlayerRanking()
        m, s = game.getTime()
        msg = ""
        if first:
            msg += f"1st - {first.name}\n"
            discard = game.getDiscardPileCard()
            colour = self.unoEmbedColour(discard)
            e = Embed(title="Uno", description=f"The final card - `{discard}`", colour=colour)
            file = File(
                f"{funcs.getPath()}/assets/uno_cards/" + \
                f"{'Xmas_' if datetime.now().month == 12 else ''}{discard.replace(' ', '_')}.png",
                filename="card.png"
            )
            e.set_image(url="attachment://card.png")
            e.set_thumbnail(url=logo)
            await ctx.send(embed=e, file=file)
        if second:
            msg += f"2nd - {second.name}\n"
        if third:
            msg += f"3rd - {third.name}\n"
        if fourth:
            msg += f"4th - {fourth.name}\n"
        if first:
            await ctx.send(f"```== Uno ==\n\n{msg}\nThanks for playing!```")
        await self.sendTime(ctx, m, s)
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="akinator", description="Play Akinator.", aliases=["ak", "akin", "aki"])
    async def akinator(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        self.gameChannels.append(ctx.channel.id)
        akimage = "https://i.pinimg.com/originals/02/e3/02/02e3021cfd7210e2ebd2faac8ce289ba.png"
        await ctx.send("Starting Akinator instance...")
        aki = Akinator()
        game = await aki.start_game()
        while aki.progression <= 80:
            try:
                await ctx.send(embed=Embed(title="Akinator", description=game).set_image(url=akimage).set_footer(
                    text=f"Progress: {round(aki.progression / 80 * 100, 2)}% | Called by: {ctx.author.name}"))
                resp = await self.client.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=60
                )
            except TimeoutError:
                self.gameChannels.remove(ctx.channel.id)
                return await ctx.send(f"`{ctx.author.name} has left Akinator for idling too long.`")
            if resp.content.casefold() == "b":
                try:
                    game = await aki.back()
                except CantGoBackAnyFurther:
                    await ctx.send(embed=funcs.errorEmbed(None, "Cannot go back any further."))
            elif resp.content.casefold().startswith("q"):
                self.gameChannels.remove(ctx.channel.id)
                return await ctx.send(f"`{ctx.author.name} has left Akinator.`")
            else:
                try:
                    game = await aki.answer(resp.content)
                except:
                    await ctx.send(embed=funcs.errorEmbed("Invalid answer!",
                        "Valid options:\n\n`y` or `yes` for yes;\n`n` or `no` for no;\n" + \
                        "`i` or `idk` for I don't know;\n`p` or `probably` for probably;\n" + \
                        "`pn` or `probably not` for probably not;\n`b` for back;\n`q` or `quit` to quit the game."))
        await aki.win()
        e = Embed(
            title="Akinator",
            description="I think it is **{0.first_guess[name]} - {0.first_guess[description]}**\n\nWas I right?".format(aki)
        )
        e.set_footer(text=f"Thanks for playing, {ctx.author.name}!")
        e.set_image(url=aki.first_guess["absolute_picture_path"])
        e.set_thumbnail(url=akimage)
        await ctx.send(embed=e)
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="guessthenumber", description="Play Guess the Number.", aliases=["gtn", "gn"])
    async def guessthenumber(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.send("**Welcome to Guess the Number. A random number between " + \
                       "1-10000 will be generated and your job is to guess it. " + \
                       "Input `time` to see total elapsed time, or `quit` to quit the game.**")
        self.gameChannels.append(ctx.channel.id)
        starttime = time()
        number = randint(1, 10000)
        attempts = 0
        guess = ""
        while guess != number:
            await ctx.send(f"`Attempt {attempts+1} for {ctx.author.name}. Please guess a number between 1-10000.`")
            try:
                message = await self.client.wait_for(
                    "message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=30
                )
            except TimeoutError:
                await ctx.send(f"`{ctx.author.name} has left Guess the Number for idling too long.`")
                break
            try:
                guess = int(message.content)
                if not 1 <= guess <= 10000:
                    await ctx.send(embed=funcs.errorEmbed(None, "Input must be 1-10000 inclusive."))
                else:
                    attempts += 1
                    if guess < number:
                        await ctx.send("`The number is larger than your guess. Guess higher!`")
                    elif guess > number:
                        await ctx.send("`The number is smaller than your guess. Guess lower!`")
                    else:
                        await ctx.send("`You have found the number!`")
            except ValueError:
                if message.content.casefold() == "quit" or message.content.casefold() == "exit" \
                        or message.content.casefold() == "stop":
                    break
                elif message.content.casefold() == "time":
                    _, m, s, _ = funcs.timeDifferenceStr(time(), starttime, noStr=True)
                    await self.sendTime(ctx, m, s)
                else:
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
        await ctx.send(f"```The number was {number}.\n\nTotal attempts: {attempts}\n\n" + \
                               f"Thanks for playing, {ctx.author.name}!```")
        _, m, s, _ = funcs.timeDifferenceStr(time(), starttime, noStr=True)
        await self.sendTime(ctx, m, s)
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="bullsandcows", description="Play Bulls and Cows.", aliases=["bc", "bulls", "cows"])
    async def bullsandcows(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.send("**Welcome to Bulls and Cows. Input `help` for help, " + \
                               "`time` to see total elapsed time, or `quit` to quit the game.**")
        self.gameChannels.append(ctx.channel.id)
        game = BullsAndCows()
        while not game.getStoppedBool():
            await ctx.send(f"`Attempt {game.getAttempts()+1} for {ctx.author.name}. " + \
                                   "Please guess a four-digit number with no duplicates.`")
            try:
                message = await self.client.wait_for(
                    "message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=90
                )
            except TimeoutError:
                await ctx.send(f"`{ctx.author.name} has left Bulls and Cows for idling too long.`")
                break
            try:
                guess = message.content
                bulls, cows = game.guess(guess)
                if guess.casefold() == "time":
                    m, s = game.getTime()
                    await self.sendTime(ctx, m, s)
                elif guess.casefold() == "help":
                    await ctx.send(
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
                    await ctx.send(f"`Result: {bulls} bull{'' if bulls == 1 else 's'} and " + \
                                           f"{cows} cow{'' if cows == 1 else 's'}." + \
                                           f"{'' if bulls != 4 else ' You have found the number!'}`")
            except Exception as ex:
                await ctx.send(embed=funcs.errorEmbed(None, str(ex)))
        await ctx.send(f"```The number was {game.getNumber()}.\n\nTotal attempts: {game.getAttempts()}\n\n" + \
                               f"Thanks for playing, {ctx.author.name}!```")
        m, s = game.getTime()
        await self.sendTime(ctx, m, s)
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="21cardtrick", description="Play the 21 Card Trick.", aliases=["ct", "21", "cardtrick"])
    async def cardtrick(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.send("**Welcome to the 21 Card Trick. " + \
                               "Pick a card from one of the three piles and I will try to guess it.**")
        self.gameChannels.append(ctx.channel.id)
        game = CardTrick()
        cardSample = game.getSample()
        for _ in range(3):
            p1, p2, p3 = game.piles(cardSample)
            await ctx.send(f"```{game.showCards(p1, p2, p3)}```")
            while True:
                await ctx.send(f"`Which pile is your card in, {ctx.author.name}? " + \
                                       "Enter either 1, 2, or 3 to pick a pile, or 'quit' quit the game.`")
                try:
                    message = await self.client.wait_for(
                        "message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=30
                    )
                    content = message.content
                    if content.casefold() == "quit" or content.casefold() == "exit" or content.casefold() == "stop":
                        self.gameChannels.remove(ctx.channel.id)
                        return await ctx.send(f"`{ctx.author.name} has left the 21 Card Trick.`")
                    choice = int(content)
                    if not 1 <= choice <= 3:
                        await ctx.send(embed=funcs.errorEmbed(None, "Input must be 1-3 inclusive."))
                    else:
                        cardSample = game.shuffle(choice, p1, p2, p3)
                        break
                except TimeoutError:
                    self.gameChannels.remove(ctx.channel.id)
                    return await ctx.send(f"`{ctx.author.name} has left the 21 Card Trick for idling too long.`")
                except ValueError:
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
        cardName, cardImg = game.getCardNameImg(cardSample[10])
        e = Embed(title="21 Card Trick")
        e.add_field(name=f"{ctx.author.name}'s Card", value=f"`{cardName}`")
        e.set_image(url=cardImg)
        e.set_footer(text="Have I guessed it correctly?")
        await ctx.send(embed=e)
        self.gameChannels.remove(ctx.channel.id)

    async def gameIdle(self, ctx, game, ms):
        if ms:
            title = "Minesweeper"
            game.revealDots()
        else:
            title = "Battleship"
        await ctx.send(f"`{ctx.author.name} has left {title} for idling too long.`")

    async def rowOrCol(self, ctx, game, choice, ms):
        if choice:
            rolCol = "vertical row number between 0-9. (set of numbers on the left)"
        else:
            rolCol = "horizontal column number between 0-9. (set of numbers at the top)"
        await ctx.send(f"`Please enter a {rolCol}`")
        try:
            msg = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=120
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
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
            await ctx.send(f"`Please enter a {rolCol}`")
            try:
                msg = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=120
                )
            except TimeoutError:
                await self.gameIdle(ctx, game, ms)
                return "quit"
            yy = msg.content
        if str(yy).casefold() == "quit" or str(yy).casefold() == "exit" or str(yy).casefold() == "stop":
            if ms:
                game.revealDots()
            return "quit"
        elif str(yy).casefold() == "time":
            m, s = game.getTime()
            await self.sendTime(ctx, m, s)
            return None
        else:
            return yy

    async def gameOptions(self, ctx, game):
        dotsLeft = 90 - game.getUncovered()
        await ctx.send(
            f"`{ctx.author.name} has {90 - game.getUncovered()} dot{'' if dotsLeft==1 else 's'} left to uncover.`"
        )
        await ctx.send("`Would you like to reveal, flag, or unflag a location?`")
        try:
            msg = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=120
            )
        except TimeoutError:
            return await self.gameIdle(ctx, game, True)
        decision = msg.content
        while decision.casefold() != "f" and decision.casefold() != "flag" \
                and decision.casefold() != "time" and decision.casefold() != "r" \
                and decision.casefold() != "reveal" and decision.casefold() != "u" \
                and decision.casefold() != "unflag" and decision.casefold() != "exit" \
                and decision.casefold() != "quit" and decision.casefold() != "stop":
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
            await ctx.send("`Would you like to reveal, flag, or unflag a location?`")
            try:
                msg = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=120
                )
            except TimeoutError:
                return await self.gameIdle(ctx, game, True)
            decision = msg.content
        if decision.casefold() == "quit" or decision.casefold() == "exit" or decision.casefold() == "stop":
            return game.revealDots()
        if decision.casefold() == "time":
            m, s = game.getTime()
            return await self.sendTime(ctx, m, s)
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
                    await ctx.send(embed=funcs.errorEmbed(None, "This location has already been revealed before."))
            else:
                game.getDispboard()[yy][xx] = "F"
        elif decision.casefold() == "u" or decision.casefold() == "unflag":
            if game.getDispboard()[yy][xx] != "F":
                await ctx.send(embed=funcs.errorEmbed(None, "This location is not flagged."))
            else:
                game.getDispboard()[yy][xx] = "."
        elif decision.casefold() == "r" or decision.casefold() == "reveal":
            if game.getDispboard()[yy][xx] != ".":
                if game.getDispboard()[yy][xx] == "F":
                    await ctx.send("`Watch out, you have previously flagged this location before!`")
                else:
                    await ctx.send(embed=funcs.errorEmbed(None, "This location has already been revealed before."))
            else:
                game.uncoverDots(xx, yy)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="minesweeper", description="Play Minesweeper.", aliases=["ms", "mines"])
    async def minesweeper(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.send("**Welcome to Minesweeper. Input `time` to see total elapsed time, or `quit` to quit the game.**")
        self.gameChannels.append(ctx.channel.id)
        game = Minesweeper()
        won = False
        while not game.getGameEnd():
            await ctx.send(f"```Attempt {game.getAttempts()+1} for {ctx.author.name}. " + \
                                   f"Current board:\n\n{game.displayBoard()}```")
            await self.gameOptions(ctx, game)
            won = game.winLose()
        await ctx.send(f"```Current board:\n\n{game.displayBoard()}```")
        m, s = game.getTime()
        await ctx.send(f"```You have {'won' if won else 'lost'} Minesweeper!\n\nTotal attempts: {game.getAttempts()}" + \
                               f"\n\nThanks for playing, {ctx.author.name}!```")
        await self.sendTime(ctx, m, s)
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="battleship", description="Play Battleship.", aliases=["bs", "battleshit"])
    async def battleship(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.send("**Welcome to Battleship. Input `time` to see total elapsed time, " + \
                               "or `quit` to quit the game.**")
        self.gameChannels.append(ctx.channel.id)
        game = Battleship()
        while game.getShipcount() > 0:
            await ctx.send(
                f"```Attempt {game.getAttempts()+1} for {ctx.author.name}. {game.displayBoard()}```"
            )
            await ctx.send(
                f"`{ctx.author.name} has {game.getShipcount()} ship{'' if game.getShipcount()==1 else 's'} left to find.`"
            )
            yy = await self.rowOrCol(ctx, game, True, False)
            if yy == "quit":
                await ctx.send(f"```{game.displayBoard(True)}```")
                break
            elif yy is None:
                continue
            else:
                yy = int(yy)
            xx = await self.rowOrCol(ctx, game, False, False)
            if xx == "quit":
                await ctx.send(f"```{game.displayBoard(True)}```")
                break
            elif xx is None:
                continue
            else:
                xx = int(xx)
            await ctx.send(f"`{ctx.author.name} has {game.takeTurn(yy, xx)}.`")
        m, s = game.getTime()
        await ctx.send(f"```You have {'won' if game.getWonBool() else 'lost'} Battleship!\n\n" + \
                               f"Total attempts: {game.getAttempts()}\n\nThanks for playing, {ctx.author.name}!```")
        await self.sendTime(ctx, m, s)
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
            await ctx.send("`Rock, paper, or scissors?`")
            try:
                msg = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=60
                )
            except TimeoutError:
                self.gameChannels.remove(ctx.channel.id)
                return await ctx.send(f"`{ctx.author.name} has feft Rock Paper Scissors for idling too long.`")
            if msg.content.casefold().startswith("r") or msg.content.casefold().startswith("p") \
                    or msg.content.casefold().startswith("s"):
                if msg.content.casefold().startswith("r"):
                    answer = "Rock"
                elif msg.content.casefold().startswith("p"):
                    answer = "Paper"
                else:
                    answer = "Scissors"
            else:
                await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
                continue
            await ctx.send(f"`{self.client.user.name} chose: {aic}`")
            if answer == aic:
                await ctx.send(f"`It's a tie! {ctx.author.name} gets to play again.`")
                continue
            else:
                getindex = aiclist.index(answer)
                if getindex < listindex:
                    await ctx.send(f"`{ctx.author.name} has lost Rock Paper Scissors!`")
                else:
                    await ctx.send(f"`{ctx.author.name} has won Rock Paper Scissors!`")
                self.gameChannels.remove(ctx.channel.id)
                return

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="hangman", description="Play Hangman.", aliases=["hm", "hangyourself", "hang"])
    async def hangman(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.send(
            "**Welcome to Hangman. You have 10 lives. Guess one letter at a time. " + \
            "Input `lives` to see how many lives you have left, `time` to see total elapsed time, or `quit` to quit the game.**"
        )
        self.gameChannels.append(ctx.channel.id)
        game = Hangman()
        while game.getLives() > 0 and not game.getDashes() == game.getWord():
            await ctx.send(f"```{ctx.author.name}'s word:\n\n{game.getDashes()}```")
            await ctx.send("`Please guess a letter.`")
            try:
                guess = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=120
                )
            except TimeoutError:
                await ctx.send(f"`{ctx.author.name} has left Hangman for idling too long.`")
                self.gameChannels.remove(ctx.channel.id)
                return await ctx.send(f"`{ctx.author.name}'s word was {game.getWord()}.`")
            content = guess.content
            if len(content) != 1:
                if content.casefold() == "quit" or content.casefold() == "exit" or content.casefold() == "stop":
                    await ctx.send(f"`{ctx.author.name} has left Hangman.`")
                    self.gameChannels.remove(ctx.channel.id)
                    return await ctx.send(f"`{ctx.author.name}'s word was {game.getWord()}.`")
                elif content.casefold().startswith("live"):
                    lives = game.getLives()
                    await ctx.send(f"`{ctx.author.name} has {game.getLives()} live{'s' if lives!=1 else ''} left.`")
                elif content.casefold().startswith("time"):
                    m, s = game.getTime()
                    await self.sendTime(ctx, m, s)
                else:
                    await ctx.send(embed=funcs.errorEmbed(None, "You may only enter one letter at a time."))
            elif content.lower() not in ascii_lowercase:
                await ctx.send(embed=funcs.errorEmbed(None, "Invalid character(s)."))
                continue
            else:
                try:
                    result = game.makeGuess(content)
                    if result:
                        await ctx.send("`Letter found!`")
                    else:
                        await ctx.send("`Letter not found...`")
                        await ctx.send(f"```{game.hangmanPic()}```")
                except Exception as ex:
                    await ctx.send(embed=funcs.errorEmbed(None, str(ex)))
        if game.getLives() == 0:
            await ctx.send(f"`{ctx.author.name} has lost Hangman. Their word was {game.getWord()}.`")
        else:
            lives = game.getLives()
            await ctx.send(
                f"`{ctx.author.name} has won Hangman with " + \
                f"{'' if lives!=10 else 'all '}{lives} li{'ves' if lives!=1 else 'fe'} left!`"
            )
        m, s = game.getTime()
        await self.sendTime(ctx, m, s)
        self.gameChannels.remove(ctx.channel.id)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="trivia", description="Play Trivia.", aliases=["quiz"])
    async def trivia(self, ctx):
        if await self.checkGameInChannel(ctx):
            return
        await ctx.send(
            "**Welcome to Trivia. Try to answer as many questions in a row as possible. Input `quit` to quit the game.**"
        )
        self.gameChannels.append(ctx.channel.id)
        url = "https://opentdb.com/api.php"
        rightcount = -1
        starttime = time()
        while True:
            rightcount += 1
            try:
                res = await funcs.getRequest(url, params={"amount": "1"})
                data = res.json()
                category = data["results"][0]["category"]
                difficulty = data["results"][0]["difficulty"]
                question = data["results"][0]["question"]
                correct = data["results"][0]["correct_answer"]
                possibleanswers = data["results"][0]["incorrect_answers"]
                possibleanswers.append(correct)
                if data["results"][0]["type"] == "boolean":
                    possibleanswers = ["True", "False"]
                else:
                    shuffle(possibleanswers)
                answerindex = int(possibleanswers.index(correct)) + 1
                e = Embed(
                    title=f"Trivia Question {str(rightcount + 1)} ({difficulty.title()})",
                    description="```{}```".format(question.replace('&lt;', '<').replace(
                    '&gt;', '>').replace('&amp;', '&').replace('<br>', '').replace(
                    '&quot;', '"').replace('&#039;', "'").replace('&eacute;', 'é'))
                )
                answerchoices = ""
                choiceno = 1
                for i in possibleanswers:
                    answerchoices += f"{choiceno}) {i}\n"
                    choiceno += 1
                e.add_field(name="Choices", value="```{}```".format(answerchoices[:-1].replace('&lt;', '<').replace(
                    '&gt;', '>').replace('&amp;', '&').replace('<br>', '').replace(
                    '&quot;', '"').replace('&#039;', "'").replace('&eacute;', 'é')))
                e.add_field(name="Category", value=f"`{category.title()}`")
                e.set_footer(text=f"Please enter a value between 1-{len(possibleanswers)} " + \
                                  "corresponding to an answer above. You have 30 seconds.")
                await ctx.send(embed=e)
                while True:
                    try:
                        useranswer = await self.client.wait_for(
                            "message", timeout=30,
                            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                        )
                    except TimeoutError:
                        await ctx.send(f"`Inactivity; the correct answer was: {answerindex}) {correct}`")
                        await ctx.send(
                            f"`Game over! You got {rightcount} question{'' if rightcount == 1 else 's'} right in a row.`"
                        )
                        self.gameChannels.remove(ctx.channel.id)
                        _, m, s, _ = funcs.timeDifferenceStr(time(), starttime, noStr=True)
                        return await self.sendTime(ctx, m, s)
                    try:
                        intuserans = int(useranswer.content)
                        if intuserans < 1 or intuserans > len(possibleanswers):
                            await ctx.send(
                                embed=funcs.errorEmbed(None, f"Answer number must be 1-{len(possibleanswers)} inclusive.")
                            )
                            continue
                        else:
                            if intuserans == answerindex:
                                await ctx.send("`Correct! Moving on to next question...`")
                            else:
                                await ctx.send(f"`Incorrect! The correct answer was: {answerindex}) {correct}`")
                                await ctx.send(
                                    f"`Game over! You got {rightcount} question{'' if rightcount == 1 else 's'} right in a row.`"
                                )
                                self.gameChannels.remove(ctx.channel.id)
                                _, m, s, _ = funcs.timeDifferenceStr(time(), starttime, noStr=True)
                                return await self.sendTime(ctx, m, s)
                            break
                    except ValueError:
                        if useranswer.content.casefold() == correct.casefold() \
                                or useranswer.content.casefold().startswith("t") and correct == "True" \
                                or useranswer.content.casefold().startswith("f") and correct == "False":
                            await ctx.send("`Correct! Moving on to next question...`")
                            break
                        else:
                            await ctx.send(
                                f"`{'' if useranswer.content.casefold().startswith('quit') else 'Incorrect! '}" + \
                                f"The correct answer was: {answerindex}) {correct}`"
                            )
                            await ctx.send(
                                f"`Game over! You got {rightcount} question{'' if rightcount == 1 else 's'} right in a row.`"
                            )
                            self.gameChannels.remove(ctx.channel.id)
                            _, m, s, _ = funcs.timeDifferenceStr(time(), starttime, noStr=True)
                            return await self.sendTime(ctx, m, s)
            except Exception:
                self.gameChannels.remove(ctx.channel.id)
                return await ctx.send(embed=funcs.errorEmbed(None, "Possible server error, stopping game."))


def setup(client: commands.Bot):
    client.add_cog(ChatGames(client))
