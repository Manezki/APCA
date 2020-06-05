from programy.clients.embed.basic import EmbeddedDataFileBot
from sentiment import getSentiment, getEmoji
from mutate import mutateMessage, SynonymNotFound
from bot import generateExperimentGroupResponse

files = {'aiml': ['rosie-master/lib/aiml'],
         'properties': 'rosie-master/lib/system/rosie.properties',
         'defaults': 'rosie-master/lib/system/rosie.pdefaults',
         'sets': ['rosie-master/lib/sets'],
         'maps': ['rosie-master/lib/maps'],
         'denormals': 'rosie-master/lib/substitutions/denormal.substitution',
         'normals': 'rosie-master/lib/substitutions/normal.substitution',
         'genders': 'rosie-master/lib/substitutions/gender.substitution',
         'persons': 'rosie-master/lib/substitutions/person.substitution',
         'person2s': 'rosie-master/lib/substitutions/person2.substitution',
         }

my_bot = EmbeddedDataFileBot(files)

while True:
    user_message = input("Your message >>> ")
    
    response = generateExperimentGroupResponse(user_message, user_id=0)

    print(response)

