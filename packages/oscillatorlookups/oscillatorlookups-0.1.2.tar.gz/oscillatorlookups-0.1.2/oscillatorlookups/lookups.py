import asyncio
import itertools
import os.path
import time

from aiofiles import open as aio_open
import aiohttp
import requests
import msgspec

class Model(msgspec.Struct):
    """A new type describing a Model"""
    modelType: str
    path: str
    numSpecies: int
    numReactions: int


def request_metadata(checksum):
    data = requests.get(
        "https://raw.githubusercontent.com/epshteinmatthew/OscillatorDatabase/master/metadata.json").text
    with open("../../metadata.json", "w") as f:
        f.write(data)
    with open("../../checksum", "w") as f:
        f.write(checksum)
    return data


def get_metadata():
    checksum = requests.get(
        "https://raw.githubusercontent.com/epshteinmatthew/OscillatorDatabase/master/checksum").text
    if not os.path.isfile("../../checksum") or not os.path.isfile("../../metadata.json"):
        return request_metadata(checksum)
    with open("../../checksum", "r") as f:
        loadck = f.read()
    if checksum != loadck:
        return request_metadata(checksum)
    with open("../../metadata.json", "r") as f:
        return msgspec.json.decode(f.read(), type=list[Model])


async def downloadAntString(url, session, resultant_dir):
    try:
        async with session.get(url=url) as response:
            resp = await response.text()
            async with aio_open(os.path.join(resultant_dir, url.split("/")[-1]), 'w') as f:
                await f.write(resp)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def lookup(data, resultant_dir, num_species=None, num_reactions=None, model_type=None, ):
    paths = []
    for item in data:
        if (num_species is None or item.numSpecies == num_species) and \
                (num_reactions is None or item.numReactions == num_reactions) and \
                (model_type is None or item.modelType == model_type):
            paths.append(
                "https://raw.githubusercontent.com/epshteinmatthew/OscillatorDatabase/master/" + item.path)
    if not os.path.isdir(resultant_dir):
        os.mkdir(resultant_dir)
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*(
            downloadAntString(url, session,
                              resultant_dir) for url in paths))


def get_summary(data, asString = False):
    if (asString):
        summary = "Total amount of models: " + len(data).__str__()
    else:
        summary = {
            "total amount of models": len(data),
        }
    reaction_nums = {item.numReactions for item in data}
    species_nums = {item.numSpecies for item in data}
    model_types = {item.modelType for item in data}

    combinations = itertools.product(
        reaction_nums,
        species_nums,
        model_types
    )
    for nr, ns, mt in combinations:
        amnt = len([item.path for item in data if
                    item.numSpecies == ns and item.numReactions == nr and item.modelType == mt])
        if (amnt != 0):
            if (asString):
                summary += f"\nAmount of {mt} models with {nr} reactions and {ns} species: " + amnt.__str__()
            else:
                summary[f"\nAmount of ${mt} models with ${nr} reactions and ${ns} species"] = amnt
    return summary


def get_total_number_of_model_types(data):
    return len({item.modelType for item in data})


def get_number_of_models_with_attrib(data, num_species=None, num_reactions=None, model_type=None):
    count = 0

    for item in data:
        if (num_species is None or item.numSpecies == num_species) and \
                (num_reactions is None or item.numReactions == num_reactions) and \
                (model_type is None or item.modelType == model_type):
            count += 1

    return count


start = time.time()
metadata = get_metadata()
print(time.time() - start)

#example: print a summary of the dataset
print(get_summary(metadata, asString=True))


#example: print the amount of models with 3 species and of type oscillator
print(get_number_of_models_with_attrib(metadata, num_species=3, model_type="oscillator"))

#example: lookup models with 3 species and 3 reactions, and put them into the "osc123" directory
asyncio.run(lookup(metadata, "osc123/", 3, 4, "oscillator"))
end = time.time()
print(end - start)


