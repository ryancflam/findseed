from asyncio import sleep
from random import randint
from time import time

from discord import ButtonStyle, ui

from other_utils.funcs import minSecs, printError

LEFT = "◀️"
RIGHT = "▶️"
ROTATE = "🔄"
SOFT_DROP = "🔽"
HARD_DROP = "⏬"
QUIT = "🗑️"
TETRIS_BLOCKS = [
    [
        [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
    ],
    [
        [[0, 0, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
        [[0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]]
    ],
    [
        [[0, 0, 0, 0], [0, 0, 1, 1], [0, 1, 1, 0], [0, 0, 0, 0]],
        [[0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
    ],
    [
        [[1, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 1, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]],
        [[0, 1, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0]]
    ],
    [
        [[0, 0, 0, 1], [0, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [0, 1, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0]],
        [[0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
    ],
    [
        [[0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 1, 0, 0], [0, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
        [[0, 1, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]]
    ],
    [[[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]]]
]


class Tetris:
    NEXT_BLOCK_IMAGES = [
        "https://i.imgur.com/OCQkjvl.jpg",
        "https://i.imgur.com/8DIq9pG.jpg",
        "https://i.imgur.com/IuzUG8y.jpg",
        "https://i.imgur.com/37KiWc1.jpg",
        "https://i.imgur.com/AbKmjsx.jpg",
        "https://i.imgur.com/Si3Uic2.jpg",
        "https://i.imgur.com/jVVeS1o.jpg",
        "https://i.imgur.com/WkbxL9l.jpg"
    ]

    def __init__(self, ctx, client):
        self.__ctx = ctx
        self.__client = client
        self.__startTime = time()
        self.__width = 10
        self.__height = 20
        self.__board = [[0 for _ in range(self.__width)] for _ in range(self.__height)]
        self.__ticks = 0
        self.__lines = 0
        self.__level = 0
        self.__gameEnd = False
        self.__message = None
        self.__nextBlock = TetrisBlock(self, randint(0, len(TETRIS_BLOCKS) - 1))
        self.__currentBlock = None
        self.__score = 0
        self.__tempPoints = 0
        self.__bnw = False

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, messageObject):
        self.__message = messageObject
        self.__client.loop.create_task(self.__message.edit(view=TetrisButtons(self.__ctx, self.__client, self)))

    async def tick(self):
        if self.__gameEnd:
            return
        self.__ticks += 10
        try:
            if not self.__ticks % (30 - self.__level * 2) and not self.__gameEnd:
                self.__currentBlock.fall()
                await self.updateBoard()
        except:
            pass

    async def updateBoard(self):
        e = self.__message.embeds[0]
        e.description = self.__endScreen() if self.__gameEnd else self.gameBoard()
        e.set_thumbnail(url=self.NEXT_BLOCK_IMAGES[-1 if self.__gameEnd else self.__nextBlock.getBlockType()])
        e.clear_fields()
        e.add_field(name="Lines", value="`{:,}`".format(self.__lines))
        e.add_field(name="Level", value="`{:,}`".format(self.__level))
        e.add_field(name="Score", value="`{:,}`".format(self.__score))
        await self.__message.edit(embed=e)

    def __endScreen(self):
        endScreen = "```"
        for _ in range(self.__height // 2 - 1):
            endScreen += "⬛" * self.__width + "\n"
        endScreen += "⬛" * (self.__width // 2 - 1) + "GAME " + "⬛" * (self.__width // 2 - 1) \
                     + "\n" + "⬛" * (self.__width // 2 - 1) + "OVER " + "⬛" * (self.__width // 2 - 1) + "\n"
        for _ in range(self.__height // 2 - 1):
            endScreen += "⬛" * self.__width + "\n"
        return endScreen[:-1] + "```"

    def __checkLines(self):
        lines = 0
        newGame = []
        rowIndex = 0
        for row in self.__board:
            lineClear = True
            for digit in row:
                if not digit:
                    lineClear = False
            if lineClear:
                lines += 1
            else:
                newGame.append(self.__board[rowIndex])
            rowIndex += 1
        for _ in range(lines):
            newGame.insert(0, [0 for _ in range(10)])
        self.__lines += lines
        score = self.__level + 1
        multipliers = [0, 40, 100, 300, 1200]
        score *= multipliers[lines]
        self.__score += score
        self.__level = int(self.__lines / 10)
        self.__board = newGame

    def __removeGhostBlock(self):
        newGame = []
        for row in self.__board:
            newRow = []
            for digit in row:
                newRow.append(0 if digit == 8 else digit)
            newGame.append(newRow)
        self.__board = newGame

    def newBlock(self):
        self.__ticks = 0
        self.__removeGhostBlock()
        self.__checkLines()
        self.__currentBlock = self.__nextBlock
        self.__currentBlock.moveY()
        if self.isOccupied(self.__currentBlock):
            self.__currentBlock.moveY(down=False)
        if self.isOccupied(self.__currentBlock):
            self.__currentBlock.rotation = self.__currentBlock.rotation + 1
            if self.__currentBlock.rotation >= len(TETRIS_BLOCKS[self.__currentBlock.getBlockType()]):
                self.__currentBlock.rotation = 0
            if self.isOccupied(self.__currentBlock):
                self.__gameEnd = True
        self.placeBlock(self.__currentBlock)
        self.__nextBlock = TetrisBlock(self, randint(0, len(TETRIS_BLOCKS) - 1))

    def placeBlock(self, blockObject):
        blockObject2 = TetrisBlock(
            game=self,
            blockType=blockObject.getBlockType(),
            rotation=blockObject.rotation,
            x=blockObject.getX(),
            y=blockObject.getY()
        )
        while not self.isOccupied(blockObject2):
            blockObject2.moveY(down=False)
        blockObject2.moveY()
        rowIndex = 0
        for row in blockObject2.getBlock():
            colIndex = 0
            for col in row:
                if col == 1:
                    self.__board[blockObject2.getY() + rowIndex][blockObject2.getX() + colIndex] = 8
                colIndex += 1
            rowIndex += 1
        block = blockObject.getBlock()
        rowIndex = 0
        for row in block:
            colIndex = 0
            for col in row:
                if col == 1:
                    self.__board[blockObject.getY() + rowIndex][blockObject.getX() + colIndex] \
                        = blockObject.getBlockType() + 1
                colIndex += 1
            rowIndex += 1

    def removeBlock(self, blockObject):
        self.__removeGhostBlock()
        block = blockObject.getBlock()
        rowIndex = 0
        for row in block:
            colIndex = 0
            for col in row:
                if col == 1:
                    self.__board[blockObject.getY() + rowIndex][blockObject.getX() + colIndex] = 0
                colIndex += 1
            rowIndex += 1

    def isOccupied(self, blockObject):
        block = blockObject.getBlock()
        rowIndex = 0
        for row in block:
            colIndex = 0
            for col in row:
                try:
                    if col == 1 and (
                        not 0 <= blockObject.getX() + colIndex < self.__width
                        or not 0 <= blockObject.getY() + rowIndex < self.__height
                        or (
                            0 < self.__board[blockObject.getY() + rowIndex][blockObject.getX() + colIndex]
                            < self.__width - 2
                        )
                    ):
                        return True
                except:
                    return True
                colIndex += 1
            rowIndex += 1
        return False

    def gameBoard(self):
        colours = ["⬛","⬜","⬜","⬜","⬜","⬜","⬜","⬜","🔳"] if self.__bnw \
                  else ["⬛","⬜","🟥","🟩","🟦","🟧","🟪","🟨","🔳"]
        text = "```"
        for row in self.__board:
            for digit in row:
                text += colours[digit]
            text += "\n"
        return text[:-1] + "```"

    def addTempPoints(self):
        self.__score += self.__tempPoints
        self.__tempPoints = 0

    def manualFall(self):
        self.__tempPoints += 1

    def gameEnd(self):
        self.__gameEnd = True

    def getGameEnd(self):
        return self.__gameEnd

    def setBnw(self):
        self.__bnw = not self.__bnw
        return self.__bnw

    def getTime(self):
        return minSecs(time(), self.__startTime)

    def getLinesLevelScore(self):
        return self.__lines, self.__level, self.__score

    def getNextBlock(self):
        return self.__nextBlock

    def getCurrentBlock(self):
        return self.__currentBlock


class TetrisBlock:
    def __init__(self, game: Tetris, blockType, rotation=0, x=3, y=0):
        self.__game = game
        self.__blockType = blockType
        self.__rotation = rotation
        self.__x = x
        self.__y = y

    @property
    def rotation(self):
        return self.__rotation

    @rotation.setter
    def rotation(self, value: int):
        self.__rotation = value

    def getBlock(self):
        return TETRIS_BLOCKS[self.__blockType][self.__rotation]

    def getBlockType(self):
        return self.__blockType

    def getX(self):
        return self.__x

    def getY(self):
        return self.__y

    def moveY(self, down=True):
        self.__y -= 1 if down else -1

    def rotate(self):
        self.__game.removeBlock(self)
        prevRotation = self.__rotation
        self.__rotation += 1
        if self.__rotation >= len(TETRIS_BLOCKS[self.__blockType]):
            self.__rotation = 0
        if self.__game.isOccupied(self):
            self.__x += 1
            if self.__game.isOccupied(self):
                self.__x -= 2
                if self.__game.isOccupied(self):
                    self.__x += 1
                    self.__y += 1
                    if self.__game.isOccupied(self):
                        self.__rotation = prevRotation
                        self.__y -= 1
        self.__game.placeBlock(self)

    def move(self, units):
        self.__game.removeBlock(self)
        prevX = self.__x
        self.__x += units
        if self.__game.isOccupied(self):
            self.__x = prevX
        self.__game.placeBlock(self)

    def fall(self, manual=False):
        if manual:
            self.__game.manualFall()
        self.__game.removeBlock(self)
        self.moveY(down=False)
        newBlock = False
        if self.__game.isOccupied(self):
            self.moveY()
            newBlock = True
        self.__game.placeBlock(self)
        if newBlock:
            self.__game.newBlock()
            self.__game.addTempPoints()

    def drop(self):
        self.__game.removeBlock(self)
        while not self.__game.isOccupied(self):
            self.__y += 1
        self.__y -= 1
        self.__game.placeBlock(self)
        self.__game.newBlock()
        self.__game.addTempPoints()


class TetrisButtons(ui.View):
    def __init__(self, ctx, client, game: Tetris):
        super().__init__()
        self.__ctx = ctx
        self.__client = client
        self.__game = game
        self.__client.loop.create_task(self.__whileNotGameEnd())

    async def interaction_check(self, interaction):
        return interaction.user == self.__ctx.author

    async def on_error(self, error, item, interaction):
        printError(self.__ctx, error)

    @ui.button(emoji=LEFT, style=ButtonStyle.primary)
    async def left(self, button, interaction):
        self.__game.getCurrentBlock().move(-1)
        await self.__game.updateBoard()

    @ui.button(emoji=RIGHT, style=ButtonStyle.primary)
    async def right(self, button, interaction):
        self.__game.getCurrentBlock().move(1)
        await self.__game.updateBoard()

    @ui.button(emoji=ROTATE, style=ButtonStyle.primary)
    async def rotate(self, button, interaction):
        self.__game.getCurrentBlock().rotate()
        await self.__game.updateBoard()

    @ui.button(emoji=SOFT_DROP, style=ButtonStyle.primary)
    async def softdrop(self, button, interaction):
        self.__game.getCurrentBlock().fall(manual=True)
        await self.__game.updateBoard()

    @ui.button(emoji=HARD_DROP, style=ButtonStyle.primary)
    async def harddrop(self, button, interaction):
        self.__game.getCurrentBlock().drop()
        await self.__game.updateBoard()

    @ui.button(emoji=QUIT, style=ButtonStyle.danger)
    async def quit(self, button, interaction):
        self.__game.gameEnd()
        await self.__ctx.send(f"`{self.__ctx.author.name} has left Tetris.`")

    async def __whileNotGameEnd(self):
        while not self.__game.getGameEnd():
            await sleep(1)
        await self.__game.message.edit(view=None)
