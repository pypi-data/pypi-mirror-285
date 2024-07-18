#IMPORT STATEMENTS:


"""----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------"""
def str_int(input, u_data):
 for char in input:
    if char == 'a':
        u_data.append(1)
    elif char == 'b':
        u_data.append(2)
    elif char == 'c':
        u_data.append(3)
    elif char == 'd':
        u_data.append(4)
    elif char == 'e':
        u_data.append(5)
    elif char == 'f':
        u_data.append(6)
    elif char == 'g':
        u_data.append(7)
    elif char == 'h':
        u_data.append(8)
    elif char == 'i':
        u_data.append(9)
    elif char == 'j':
        u_data.append(10)
    elif char == 'k':
        u_data.append(11)
    elif char == 'l':
        u_data.append(12)
    elif char == 'm':
        u_data.append(13)
    elif char == 'n':
        u_data.append(14)
    elif char == 'o':
        u_data.append(15)
    elif char == 'p':
        u_data.append(16)
    elif char == 'q':
        u_data.append(17)
    elif char == 'r':
        u_data.append(18)
    elif char == 's':
        u_data.append(19)
    elif char == 't':
        u_data.append(20)
    elif char == 'u':
        u_data.append(21)
    elif char == 'v':
        u_data.append(22)
    elif char == 'w':
        u_data.append(23)
    elif char == 'x':
        u_data.append(24)
    elif char == 'y':
        u_data.append(25)
    elif char == 'z':
        u_data.append(26)


def sim(trained_Data, tuple_data):
    trainvalue = []
    str_int(trained_Data, u_data=trainvalue) 
    fedvalue = []
    str_int(tuple_data, u_data=fedvalue)

    trainvalue_sim_increase = 100 / len(trainvalue)
    fedvalue_sim_increase = 100 / len(fedvalue)
    sim = 0
    runTime = -1
    anomaly =[]
    for i in fedvalue:
        runTime = runTime + 1
        if len(trainvalue) < len(fedvalue):
         required_len_Array = len(trainvalue) - len(fedvalue)
         trainvalue.append(0)
        else:
         if i == trainvalue[runTime]:
            sim = sim + fedvalue_sim_increase
         else:
            anomaly.append(fedvalue.index(i))
    if len(anomaly) == 0:
        return sim
    else:

        return sim

def sim_anomaly(trained_Data, tuple_data):
    trainvalue = []
    str_int(trained_Data, u_data=trainvalue) 
    fedvalue = []
    str_int(tuple_data, u_data=fedvalue)

    trainvalue_sim_increase = 100 / len(trainvalue)
    fedvalue_sim_increase = 100 / len(fedvalue)
    sim = 0
    runTime = -1
    anomaly =[]
    for i in fedvalue:
        runTime = runTime + 1
        if i == trainvalue[runTime]:
            sim = sim + fedvalue_sim_increase
        else:
            anomaly.append(fedvalue.index(i))
    if len(anomaly) == 0:
        return f"Similarity: {sim}"
    else:

        return f"Similarity: {sim}\nAnomalies on index(es) {anomaly}"
    
def predict_string(input_string):
    input_array_ofstr = list(input_string)    
    common_words = [
    "apple",
    "animal",
    "amazing",
    "art",
    "adventure",
    "always",
    "active",
    "answer",
    "area",
    "allow",
    "arrange",
    "atmosphere",
    "approach",
    "adapt",
    "achieve",
    "advanced",
    "argument",
    "analyze",
    "aspect",
    "association",
    "assess",
    "assistance",
    "academic",
    "authority",
    "architecture",
    "acknowledge",
    "account",
    "actor",
    "access",
    "adjust",
    "accelerate",
    "appliance",
    "anthem",
    "agile",
    "abandon",
    "affection",
    "angle",
    "audition",
    "anticipate",
    "ambition",
    "artisan",
    "alert",
    "assemble",
    "artisanal",
    "ascent",
    "anchor",
    "astronomy",
    "angel",
    "arrow",
    "audit",
    "attire",
    "arcade",
    "alliance",
    "ally",
    "almond",
    "amplify",
    "algae",
    "ambient",
    "amend",
    "arsenal",
    "attic",
    "adoration",
    "auction",
    "aroma",
    "affirm",
    "appraisal",
    "asset",
    "affirmative",
    "acclaim",
    "atlas",
    "apricot",
    "affidavit",
    "afghan",
    "aperture",
    "amulet",
    "anomaly",
    "apprentice",
    "adobe",
    "asterisk",
    "avatar",
    "albino",
    "archive",
    "abode",
    "absolve",
    "amass",
    "aphid",
    "algebra",
    "arctic",
    "artichoke",
    "abyss",
    "ad-lib",
    "annex",
    "aorta",
    "assail",
    "animate",
    "amnesia",
    "alto",
    "adorn",
    "autograph",
    "alloy",
    "align",
    "alligator",
    "audition",
    "amiable",
    "amplify",
    "affix",
    "abacus",
    "abdomen",
    "abdicate",
    "abduction",
    "abet",
    "abhor",
    "abnormal",
    "abode",
    "abreast",
    "abroad",
    "absent",
    "absorb",
    "abstract",
    "abundance",
    "abuse",
    "abut",
    "abyss",
    "academy",
    "accede",
    "accent",
    "accept",
    "access",
    "accident",
    "acclaim",
    "acclimate",
    "accompany",
    "accomplish",
    "accord",
    "account",
    "accrue",
    "accumulate",
    "accurate",
    "accuse",
    "accustom",
    "acerbic",
    "ache",
    "achieve",
    "acid",
    "acknowledge",
    "acoustic",
    "acquaint",
    "acquire",
    "acquit",
    "acre",
    "acrobat",
    "acronym",
    "across",
    "act",
    "action",
    "active",
    "actor",
    "actress",
    "actual",
    "acumen",
    "acute",
    "adapt",
    "add",
    "addict",
    "address",
    "adept",
    "adequate",
    "adhere",
    "adjacent",
    "adjective",
    "adjust",
    "admiral",
    "admire",
    "admit",
    "adobe",
    "adopt",
    "adore",
    "adorn",
    "adult",
    "advance",
    "adventure",
    "advert",
    "advice",
    "advise",
    "advocate",
    "aerial",
    "affect",
    "affiliate",
    "affirm",
    "affix",
    "afflict",
    "afford",
    "afraid",
    "after",
    "again",
    "against",
    "age",
    "agency",
    "agenda",
    "agent",
    "agile",
    "agitate",
    "agonize",
    "agree",
    "ahead",
    "aid",
    "ail",
    "aim",
    "air",
    "airplane",
    "airport",
    "ajar",
    "alarm",
    "album",
    "alcohol",
    "alert",
    "alien",
    "alight",
    "align",
    "alike",
    "alive",
    "all",
    "alley",
    "allot",
    "allow",
    "alloy",
    "allude",
    "ally",
    "almost",
    "alone",
    "along",
    "aloof",
    "already",
    "also",
    "alter",
    "always",
    "amaze",
    "ambition",
    "amble",
    "ambush",
    "amen",
    "amend",
    "amid",
    "amiss",
    "among",
    "amount",
    "ample",
    "amuse",
    "anchor",
    "ancient",
    "and",
    "anew",
    "angel",
    "anger",
    "angle",
    "angry",
    "animal",
    "ankle",
    "annoy",
    "annual",
    "answer",
    "ant",
    "antenna",
    "anti",
    "antics",
    "antique",
    "anvil",
    "anxiety",
    "any",
    "apart",
    "apathy",
    "apex",
    "aphid",
    "apiece",
    "aplomb",
    "apology",
    "apparel",
    "appear",
    "apple",
    "apply",
    "appraise",
    "apricot",
    "apt",
    "aquatic",
    "arcade",
    "arch",
    "archer",
    "archive",
    "area",
    "argue",
    "arid",
    "arise",
    "arm",
    "armed",
    "armor",
    "army",
    "aroma",
    "around",
    "arouse",
    "array",
    "arrive",
    "arrow",
    "art",
    "artist",
    "ascent",
    "ash",
    "aside",
    "ask",
    "asleep",
    "aspire",
    "assay",
    "assent",
    "assert",
    "assign",
    "assist",
    "assume",
    "assure",
    "astute",
    "asylum",
    "athlete",
    "atlas",
    "atom",
    "atone",
    "at"]
    similarity_array = []
    runtime = -1
    for y in common_words:
        runtime = runtime +1
        similarity =sim(y, input_string)
        similarity_array.append(similarity)
        
    print(similarity_array)
    return max(similarity_array), common_words[similarity_array.index(max(similarity_array))]
"""-------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------"""
