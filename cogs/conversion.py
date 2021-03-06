import hashlib

from discord import Embed
from discord.ext import commands

from other_utils import funcs
from other_utils.brainfuck_interpreter import BrainfuckInterpreter


class Conversion(commands.Cog, name="Conversion"):
    MORSE = {
        "A": ".-",
        "B": "-...",
        "C": "-.-.",
        "D": "-..",
        "E": ".",
        "F": "..-.",
        "G": "--.",
        "H": "....",
        "I": "..",
        "J": ".---",
        "K": "-.-",
        "L": ".-..",
        "M": "--",
        "N": "-.",
        "O": "---",
        "P": ".--.",
        "Q": "--.-",
        "R": ".-.",
        "S": "...",
        "T": "-",
        "U": "..-",
        "V": "...-",
        "W": ".--",
        "X": "-..-",
        "Y": "-.--",
        "Z": "--..",
        "0": "-----",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        " ": "/",
        ".": ".-.-.-",
        ",": "--..--",
        ":": "---...",
        "?": "..--..",
        '"':".-..-.",
        "'": ".----.",
        "-": "-....-",
        "/": "-..-.",
        "@": ".--.-.",
        "=": "-...-",
        "(": "-.--.",
        ")": "-.--.-",
        "+": ".-.-.",
        "&": ".-...",
        ";": "-.-.-.",
        "_": "..--.-",
        "$": "...-..-",
        "¿": "..-.-",
        "¡": "--...-"
    }

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="hash", description="Generates a hash from an input using an algorithm.",
                      aliases=["hashing", "hashbrown"], usage="<algorithm> [input]")
    async def hash(self, ctx, algo=None, *, msg=""):
        algorithms = [
            "md5", "blake2b", "blake2s", "sha1", "sha224", "sha256", "sha384", "sha512", "sha", "md"
        ]
        if not algo:
            e = funcs.errorEmbed(None, "Please select a hashing algorithm.")
        else:
            algo = algo.casefold().replace("-", "").replace("_", "").strip()
            if algo not in algorithms:
                e = funcs.errorEmbed(
                    "Invalid algorithm!",
                    "Valid options:\n\n`MD5`, `BLAKE2b`, `BLAKE2s`, " + \
                    "`SHA1`, `SHA224`, `SHA256`, `SHA384`, `SHA512`"
                )
            else:
                if algo.startswith("md"):
                    algo = "MD5"
                    output = str(hashlib.md5(msg.encode("utf-8")).hexdigest())
                elif algo == "blake2b":
                    algo = "BLAKE2b"
                    output = str(hashlib.blake2b(msg.encode("utf-8")).hexdigest())
                elif algo == "blake2s":
                    algo = "BLAKE2s"
                    output = str(hashlib.blake2s(msg.encode("utf-8")).hexdigest())
                elif algo == "sha1" or algo == "sha":
                    algo = "SHA1"
                    output = str(hashlib.sha1(msg.encode("utf-8")).hexdigest())
                elif algo == "sha224":
                    algo = "SHA224"
                    output = str(hashlib.sha224(msg.encode("utf-8")).hexdigest())
                elif algo == "sha256":
                    algo = "SHA256"
                    output = str(hashlib.sha256(msg.encode("utf-8")).hexdigest())
                elif algo == "sha384":
                    algo = "SHA384"
                    output = str(hashlib.sha384(msg.encode("utf-8")).hexdigest())
                else:
                    algo = "SHA512"
                    output = str(hashlib.sha512(msg.encode("utf-8")).hexdigest())
                e = Embed(title=algo, description=funcs.formatting(output))
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="texttobrainfuck", description="Converts plain text to Brainfuck.",
                      aliases=["ttbf", "t2bf"], usage="<input>")
    async def texttobrainfuck(self, ctx, *, text: str=""):
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
                        output += "{}.".format("+" * deviation) if deviation < 6 \
                            else ">{}[<{}>-]<{}.".format("+" * mult[0], "+" * mult[0], "+" * mult[1])
                    else:
                        output += "{}.".format("-" * abs(deviation)) if deviation > -6 \
                            else ">{}[<{}>-]<{}.".format("+" * mult[0], "-" * mult[0], "-" * mult[1])
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
                      aliases=["bftt", "bf2t"], usage="<input>")
    async def brainfucktotext(self, ctx, *, text: str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                interpreter = BrainfuckInterpreter(text)
                while interpreter.available():
                    interpreter.step()
                e = Embed(
                    title="Brainfuck to Text",
                    description=funcs.formatting(interpreter.getOutput().read())
                )
            except Exception as ex:
                e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="texttomorse", description="Converts plain text to Morse code.",
                      aliases=["ttmc", "t2mc", "texttomorsecode", "ttm", "t2m"], usage="<input>")
    async def texttomorse(self, ctx, *, text: str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                output = ""
                for char in text:
                    try:
                        output += self.MORSE[char.upper()] + " "
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
                      aliases=["mctt", "mc2t", "morsecodetotext", "mtt", "m2t"], usage="<input>")
    async def morsetotext(self, ctx, *, text: str=""):
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
                            output += list(self.MORSE.keys())[list(self.MORSE.values()).index(ctext)]
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
                      aliases=["tth", "t2h", "texttohexadecimal"], usage="<input>")
    async def texttohex(self, ctx, *, text: str=""):
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
                      aliases=["htt", "h2t", "hexadecimaltotext"], usage="<input>")
    async def hextotext(self, ctx, *, text: str=""):
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
                      aliases=["ttb", "t2b"], usage="<input>")
    async def texttobinary(self, ctx, *, text: str=""):
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
                      aliases=["btt", "b2t"], usage="<input>")
    async def binarytotext(self, ctx, *, text: str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                text = text.replace(" ", "")
                e = Embed(
                    title="Binary to Text",
                    description=funcs.formatting("".join(chr(int(text[i * 8:i * 8 + 8], 2)) \
                        for i in range(len(text) // 8)))
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="decimaltobinary", description="Converts decimal to binary.",
                      aliases=["dtb", "d2b"], usage="<input>")
    async def decimaltobinary(self, ctx, *, text: str=""):
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
                      aliases=["btd", "b2d"], usage="<input>")
    async def binarytodecimal(self, ctx, *, text: str=""):
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
                      aliases=["bth", "b2h", "binarytohexadecimal"], usage="<input>")
    async def binarytohex(self, ctx, *, text: str=""):
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
                      aliases=["htb", "h2b", "hexadecimaltobinary"], usage="<input>")
    async def hextobinary(self, ctx, *, text: str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                number = int(text.replace(" ", ""), 16)
                e = Embed(
                    title="Hexadecimal to Binary",
                    description=funcs.formatting(bin(int(number)).replace("0b", ""))
                )
            except Exception:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="hextodecimal", description="Converts hexadecimal to decimal.",
                      aliases=["htd", "h2d"], usage="<input>")
    async def hextodecimal(self, ctx, *, text: str=""):
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
                      aliases=["dth", "d2h"], usage="<input>")
    async def decimaltohex(self, ctx, *, text: str=""):
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

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="ctf", description="Converts Celsius to Fahrenheit.",
                      aliases=["c2f", "ctof", "fahrenheit"], usage="<input>")
    async def ctf(self, ctx, *, text: str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                number = float(text.replace(" ", "").replace(",", ""))
                e = Embed(
                    title="Celsius to Fahrenheit",
                    description=funcs.formatting(str(round(funcs.celsiusToFahrenheit(number), 3)) + "°F")
                )
            except ValueError:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="ftc", description="Converts Fahrenheit to Celsius.",
                      aliases=["f2c", "ftoc", "celsius"], usage="<input>")
    async def ftc(self, ctx, *, text: str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                number = float(text.replace(" ", "").replace(",", ""))
                value = round((number - 32) * 5 / 9, 3)
                e = Embed(
                    title="Fahrenheit to Celsius",
                    description=funcs.formatting(str(value) + "°C")
                )
            except ValueError:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="lbstokg", description="Converts pounds to kilograms.", usage="<input>",
                      aliases=["kg", "kilogram", "kgs", "kilograms", "kilo", "kilos", "lbs2kg"])
    async def lbstokg(self, ctx, *, text: str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                number = float(text.replace(" ", "").replace(",", ""))
                value = round(number * 0.45359237, 3)
                e = Embed(
                    title="Pounds to Kilograms",
                    description=funcs.formatting(str(value) + " kg")
                )
            except ValueError:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="kgtolbs", description="Converts kilograms to pounds.",
                      aliases=["lbs", "pound", "pounds", "kg2lbs"], usage="<input>")
    async def kgtolbs(self, ctx, *, text: str=""):
        if text == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                number = float(text.replace(" ", "").replace(",", ""))
                value = round(number * 2.2046226218, 3)
                e = Embed(
                    title="Kilograms to Pounds",
                    description=funcs.formatting(str(value) + " lbs")
                )
            except ValueError:
                e = funcs.errorEmbed(None, "Conversion failed. Invalid input?")
        await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(Conversion(client))
