from discord import Embed
from discord.ext import commands

from other_utils import funcs
from other_utils import morse_data
from other_utils.brainfuck_interpreter import BrainfuckInterpreter


class Conversion(commands.Cog, name="Conversion"):
    def __init__(self, client:commands.Bot):
        self.client = client

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="texttobrainfuck", description="Converts plain text to Brainfuck.",
                      aliases=["ttbf", "t2bf"])
    async def texttobrainfuck(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                old = 0
                output = ""
                for character in text:
                    ordd = ord(character)
                    if old == ordd:
                        output += "."
                        continue
                    deviation = ordd - old
                    root = int((abs(deviation)) ** (1 / 2))
                    rest = abs(deviation) - (root ** 2)
                    mult = root, rest
                    if 0 < deviation:
                        if deviation < 6:
                            output += "{}.".format("+" * deviation)
                        else:
                            output += ">{}[<{}>-]<{}.".format("+" * mult[0], "+" * mult[0], "+" * mult[1])
                    else:
                        if deviation >- 6:
                            output += "{}.".format("-" * abs(deviation))
                        else:
                            output += ">{}[<{}>-]<{}.".format("+" * mult[0], "-" * mult[0], "-" * mult[1])
                    old = ordd
                e = Embed(
                    title="Text to Brainfuck",
                    description=funcs.formatting(output)
                )
            except Exception:
                e = funcs.errorEmbed(None,"Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="brainfucktotext", description="Converts Brainfuck to plain text.",
                      aliases=["bftt", "bf2t"])
    async def brainfucktotext(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                interpreter = BrainfuckInterpreter(text)
                while interpreter.available():
                    interpreter.step()
                e = Embed(
                    title="Brainfuck to Text",
                    description=funcs.formatting(interpreter.output.read())
                )
            except Exception as ex:
                e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="texttomorse", description="Converts plain text to Morse code.",
                      aliases=["ttmc", "t2mc", "texttomorsecode", "ttm", "t2m"])
    async def texttomorse(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                output = ""
                for char in text:
                    try:
                        output += morse_data.morse[char.upper()] + " "
                    except:
                        continue
                output = output[:-1]
                e = Embed(
                    title="Text to Morse Code",
                    description=funcs.formatting(output)
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="morsetotext", description="Converts Morse code to plain text.",
                      aliases=["mctt", "mc2t", "morsecodetotext", "mtt", "m2t"])
    async def morsetotext(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                text += " "
                output = ""
                ctext = ""
                spaces = 0
                for char in text:
                    if char != " ":
                        if char != "-" and char != ".":
                            if char == "·":
                                char = "."
                            else:
                                continue
                        spaces = 0
                        ctext += char
                    else:
                        spaces += 1
                        if spaces == 2:
                            output += " "
                        else:
                            output += list(morse_data.morse.keys())[list(morse_data.morse.values()).index(ctext)]
                            ctext = ""
                e = Embed(
                    title="Text to Morse Code",
                    description=funcs.formatting(output)
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="texttohex", description="Converts plain text to hexadecimal.",
                      aliases=["tth", "t2h", "texttohexadecimal"])
    async def texttohex(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                e = Embed(
                    title="Text to Hexadecimal",
                    description=funcs.formatting(text.encode('utf-8').hex())
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="hextotext", description="Converts hexadecimal to plain text.",
                      aliases=["htt", "h2t", "hexadecimaltotext"])
    async def hextotext(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                e = Embed(
                    title="Hexadecimal to Text",
                    description=funcs.formatting(bytes.fromhex(text).decode("utf-8"))
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="texttobinary", description="Converts plain text to binary.",
                      aliases=["ttb", "t2b"])
    async def texttobinary(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                e = Embed(
                    title="Text to Binary",
                    description=funcs.formatting(str("".join(f"{ord(i):08b}" for i in text)))
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="binarytotext", description="Converts binary to plain text.",
                      aliases=["btt", "b2t"])
    async def binarytotext(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                e = Embed(
                    title="Binary to Text",
                    description=funcs.formatting("".join(chr(int(text[i*8:i*8+8], 2)) for i in range(len(text)//8)))
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="decimaltobinary", description="Converts decimal to binary.",
                      aliases=["dtb", "d2b"])
    async def decimaltobinary(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                number = text.replace(" ", "")
                e = Embed(
                    title="Binary to Decimal",
                    description=funcs.formatting(bin(int(number)).replace("0b", ""))
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="binarytodecimal", description="Converts binary to decimal.",
                      aliases=["btd", "b2d"])
    async def binarytodecimal(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                binnumber = text.replace(" ", "")
                e = Embed(
                    title="Binary to Decimal",
                    description=funcs.formatting(str(int(binnumber, 2)))
                )
            except ValueError:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="binarytohex", description="Converts binary to hexadecimal.",
                      aliases=["bth", "b2h", "binarytohexadecimal"])
    async def binarytohex(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                text = text.replace(" ", "")
                hstr = "%0*X" % ((len(text) + 3) // 4, int(text, 2))
                e = Embed(
                    title="Binary to Hexadecimal",
                    description=funcs.formatting(hstr)
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="hextobinary", description="Converts hexadecimal to binary.",
                      aliases=["htb", "h2b", "hexadecimaltobinary"])
    async def hextobinary(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                n = int(text.replace(" ", ""), 16)
                bstr = ""
                while n > 0:
                    bstr = str(n % 2) + bstr
                    n = n >> 1
                e = Embed(
                    title="Hexadecimal to Binary",
                    description=funcs.formatting(str(bstr))
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="hextodecimal", description="Converts hexadecimal to decimal.",
                      aliases=["htd", "h2d"])
    async def hextodecimal(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                hexnumber = text.replace(" ", "")
                e = Embed(
                    title="Hexadecimal to Decimal",
                    description=funcs.formatting(str(int(hexnumber, 16)))
                )
            except ValueError:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="decimaltohex", description="Converts decimal to hexadecimal.",
                      aliases=["dth", "d2h"])
    async def decimaltohex(self, ctx, *, text:str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                number = int(text.replace(" ", ""))
                e = Embed(
                    title="Decimal to Hexadecimal",
                    description=funcs.formatting(hex(number).split("x")[-1])
                )
            except ValueError:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)


def setup(client:commands.Bot):
    client.add_cog(Conversion(client))
