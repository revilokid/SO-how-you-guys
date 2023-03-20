import discord
from discord.ext import commands
import numpy as np
import random
import logging
import csv
logging.basicConfig(level=logging.INFO)

class Markov(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chains = self.import_chains()

    @commands.command(description="simple markov sentence generator: >markov {person} {length}")
    async def markov(self, ctx, person="suj", length=20):
        logging.info("Received markov command for: {}".format(person))
        sentence = self.generate_sentence(person.lower(), length)
        await ctx.reply("**{}**: {}".format(person, sentence))

    @commands.command(description="markov quiz")
    async def markovquiz(self, ctx, length=25):
        logging.info("Recieved markovquiz command")
        person, sentence = self.random_sentence(length)
        dd = DropdownView(person)
        await ctx.reply(sentence, view=dd)

    def import_chains(self):
        logging.info("Importing chains...")
        sujchain = Chain("suj", "suj.csv")
        pedrochain = Chain("pedro", "pedro.csv")
        danchain = Chain("dan", "dan.csv")
        woochain = Chain("woo", "woo.csv")
        benchain = Chain("ben", "ben.csv")
        edchain = Chain("ed", "ed.csv")
        pohlchain = Chain("pohl", "pohl.csv")
        logging.info("Chains imported")
        return {"suj": sujchain, "pedro": pedrochain, "dan": danchain, "woo": woochain, "ben": benchain, "ed": edchain, "pohl": pohlchain}

    def generate_sentence(self, person, length):
        if length > 100:
            length = 100

        if person in self.chains.keys():
            return self.chains[person].get_sentence(length)
        else:
            logging.error("User requested does not exist: {}".format(person))
            return "This user does not have a chain created"

    def random_sentence(self, length):
        person = random.choice(list(self.chains.keys()))
        sentence = self.generate_sentence(person, length)
        return person, sentence



class Chain():
    def __init__ (self, name, file):
        self.name = name
        self.starts, self.chain_map = self.create_chain(file)

    def create_chain(self, file):
        logging.info("Creating chain from file: {}".format(file))
        sentences = []

        with open('{}.csv'.format(self.name), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                content = [word.lower() for word in row['Content'].split()]
                if (len(content) > 5):
                    sentences+=content


        starts = [sentence[0] for sentence in sentences]

        pairs = self.make_pairs(sentences)
        chain_map = {}

        for word1, word2 in pairs:
            if word1 in chain_map.keys():
                chain_map[word1].append(word2)
            else:
                chain_map[word1] = [word2]
        logging.info("Finished chain from file: {}".format(file))
        return starts, chain_map

    def make_pairs(self, sentences):
        for i in range(len(sentences)-1):
            yield (sentences[i], sentences[i+1])

    def get_sentence(self, length):
        start = np.random.choice(self.starts)
        sentence = [start]
        for i in range(length-1):
            try:
                word = np.random.choice(self.chain_map[(sentence[-1])])
            except:
                word = random.choice(self.starts)
            sentence.append(word)
        logging.info("Generated {} sentence: {}".format(self.name, sentence))
        return " ".join(sentence)


class Dropdown(discord.ui.Select):
    def __init__(self, person):
        self.person = person

        options = [
            discord.SelectOption(label='ben'),
            discord.SelectOption(label='dan'),
            discord.SelectOption(label='ed'),
            discord.SelectOption(label='pedro'),
            discord.SelectOption(label='pohl'),
            discord.SelectOption(label='suj'),
            discord.SelectOption(label='woo')
        ]
        super().__init__(placeholder='Choose the person', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == self.person:
            await interaction.response.send_message("{} Correct! It was {}!".format(interaction.user.mention, self.person))
        else:
            await interaction.response.send_message("{} Wrong. It wasn't {}, It was {}!".format(interaction.user.mention, self.values[0], self.person))
        self.view.stop()
        

class DropdownView(discord.ui.View):
    def __init__(self, person):
        super().__init__()
        self.add_item(Dropdown(person))
