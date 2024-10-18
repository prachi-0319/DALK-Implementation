import os
from tqdm import tqdm
import time
import json
from apis import *

# Reading the file to understand the structure of the pubtator files
# with open("/Users/prachikansal/Desktop/stuff/nus intern/DALK/My Implementation/LLM4KG/by_year/2011.pubtator") as f:
#     i =0
#     for line in f.readlines():
#         i+=1
#         if (i<50): # Printing only the first 50 lines
#             print(line) 

"""
Structure of the pubtator files
    19233513|t|Thiamine deficiency increases beta-secretase activity and accumulation of beta-amyloid peptides.
    19233513|a|Thiamine pyrophosphate (TPP) and the activities of thiamine-dependent enzymes are reduced in Alzheimer's disease (AD) patients. In this study, we analyzed the relationship between thiamine deficiency (TD) and amyloid precursor protein (APP) processing in both cellular and animal models of TD. In SH-SY5Y neuroblastoma cells overexpressing APP, TD promoted maturation of beta-site APP cleaving enzyme 1 (BACE1) and increased beta-secretase activity which resulted in elevated levels of beta-amyloid (Abeta) as well as beta-secretase cleaved C-terminal fragment (beta-CTF). An inhibitor of beta-secretase efficiently reduced TD-induced up-regulation of Abeta and beta-CTF. Importantly, thiamine supplementation reversed the TD-induced alterations. Furthermore, TD treatment caused a significant accumulation of reactive oxygen species (ROS); antioxidants suppressed ROS production and maturation of BACE1, as well as TD-induced Abeta accumulation. On the other hand, exogenous Abeta(1-40) enhanced TD-induced production of ROS. A study on mice indicated that TD also caused Abeta accumulation in the brain, which was reversed by thiamine supplementation. Taken together, our study suggests that TD could enhance Abeta generation by promoting beta-secretase activity, and the accumulation of Abeta subsequently exacerbated TD-induced oxidative stress.

    19233513        0       8       Thiamine        Chemical        MESH:D013831
    19233513        9       44      deficiency increases beta-secretase     Disease MESH:D012497
    19233513        97      119     Thiamine pyrophosphate  Chemical        MESH:D013835

From the look of it, it can be understoof that the first line contains the title t, foillow by an abstract and the extracted entities.
First column might correspond to the line number.
Second and third columns specify the start and end indices of the entity.
Fourth and fifth columns contain the entity name and type.
"""

# years = [2011,2012,2013,2014,2015,2016,2017,2018,2019,2020]
years = [2018] # Only considering 3 years for the sake of simiplicity

# Predefined tempalte
template = '''Read the following abstract, extract the relationships between each entity.
You can choose the relation from: (covaries, interacts, regulates, resembles, downregulates, upregulates, associates, binds, treats, palliates), or generate a new predicate to describe the relationship between the two entities.
Output all the extract triples in the format of "head | relation | tail". For example: "Alzheimer's disease | associates | memory deficits"

Abstract: {}
Entity: {}
Output: '''

# Extracting entity names from the extracted list
def get_entity_name(entity_names):
    if len(entity_names) == 1:
        return entity_names[0]
    else:
        return '{} ({})'.format(entity_names[0], ', '.join(entity_names[1:]))

# Function to extract information from the pubtator files
def read_literature():
    year2literatures = {year: [] for year in years}
    for year in years: # Only for the 3 years specified
        with open(os.path.join('by_year', '{}.pubtator'.format(year))) as f: # Reading their pubtator files
            
            # For the list of entities
            literature = {'entity': {}} 
            for line in f.readlines():
                line = line.strip()
                
                if line == '' and literature != {}:
                    for entity_id in literature['entity']:
                        literature['entity'][entity_id]['entity_name'] = list(literature['entity'][entity_id]['entity_name'])
                        # print(literature['entity'][entity_id]['entity_name'])
                    year2literatures[year].append(literature)
                    literature = {'entity': {}}
                    continue

                # Extracting the title and the abstract
                if '|t|' in line:
                    literature['title'] = line.split('|t|')[1]
                    #print("t\n",literature['title'])
                elif '|a|' in line:
                    literature['abstract'] = line.split('|a|')[1]
                    #print("a\n",literature['abstract'])
                      
                elif (len(line)>1): # Indicates that it contains the entity 
                    splitline = line.split('\t')
                    if len(splitline) != 6:
                        entity_name, entity_type, entity_id = splitline[3], splitline[4], None
                    else:
                        entity_name, entity_type, entity_id = splitline[3], splitline[4], splitline[5]

                    # Adding the entities to the literature of the particular file
                    if entity_id not in literature['entity']:
                        literature['entity'][entity_id] = {'entity_name':set(), 'entity_type': entity_type}
                    literature['entity'][entity_id]['entity_name'].add(entity_name)
            entity_type = set() # We will have all the entities of the same type together
        
        #year2literatures[year].append(literature)

    # For understanding the structure of year2literatures
    # for k,v in year2literatures.items():
    #     print(k)
    #     print(type(v)) 
    
    """
    type(v):
    2018
    <class 'list'>
    2019
    <class 'list'>
    2020
    <class 'list'>

    This shows that the dictionary year2literatures is a dictionary with key as the year and value a list containing all information in the pubtator file for that year
    """

    return year2literatures



def main():
    year2literatures = read_literature()

    for year, literatures in year2literatures.items():
        
        extracted = []
        for literature in tqdm(literatures):    
            title = literature['title']
            abstract = literature['abstract']
            item = {
                'title': title,
                'abstract': abstract,
                'triplet':[]
            }

            entity_names = ', '.join([get_entity_name(entity_info['entity_name']) for entity_info in literature['entity'].values()])
            message = template.format(abstract, entity_names)

            print("Message")
            print(message)
            print("--------------------------------")            
            
            # Getting a response from the LLM
            try:
                ret = request_llama(message)
                # ret = request_biomistral(message)
            except Exception as e:
                print(f"An error occurred: {e}")
            
            print("Response")
            print(ret)
            print("--------------------------------")

            if ret != []: # If the response is not null                 
                for triplet in ret.split('\n'):
                    if triplet == '':
                        continue
                    try:
                        entity1, relation, entity2 = triplet.split(' | ')
                    except:
                        continue
                
                item['triplet'].append({'entity1': { 'entity_name': entity1,}, 'entity2': {'entity_name': entity2,},'relation': relation})
            
            extracted.append(item)

        # Appending the title, abstract and extracted entities to a new json file
        # with open('extracted/{}.json'.format(year), 'w') as f:
        #     f.write(json.dumps(extracted, indent=2))


if __name__ == '__main__':
    main()