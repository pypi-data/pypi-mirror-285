import pymmep.eaf_utils
import pandas as pd
import numpy as np

from pathlib import Path
from lxml import etree
import pickle
np.seterr(all='raise')




class Eaf_Container: # would it speed things up to make this a singleton...probably a horrible idea, but it would work around slow garbage collection?
    """
    This class is intended to hold all important values from an .eaf file.
    It will also hold a lot of additional information that would not fit neatly into an .eaf file.
    
    This is intended to be used with the iterator from eaf_utils,
    to parse all .eaf information into a python structure
    (and save it pickled for later use).
    
    The constructor takes four arguments: the path to the .eaf file, and the results of "prepare_eaf(path)", 
    from here all relevant information is extracted.
    Call method .to_pickle(Path) to save the whole object.
    
    ====================
    Parameters of Constructor: __init__(path, time_dictionary, tier_dictionary, deco)

    path : String

    slot_dic : Dictionary of eaf time data; provided by prepare_eaf(path)

    tier_dic : Dictionary of eaf tiers; provided by prepare_eaf(path)

    deco : List of two Strings; provided by prepare_eaf(path)

    ====================
    Attributes:
    
    lannguage_data : The dictionary that holds the language individual data <-- this is likely what you are here for. The keys are the 3-letter language codes.
    
        bul bulgarian
        cze czech
        dan danish
        dut dutch
        eng english
        est estonian
        fin finnish
        fra french
        ger german
        gre greek
        hun hungarian
        ita italian
        lav latvian
        lit lithuanian
        mlt maltese
        pol polish
        por portuguese
        rum romanian
        slo slovakian
        slv slovenian
        spa spanish
        swe swedish
        
        the value of each key is another dictionary that holds the transcriptions, verbatim_reports, metadata and everything else I can find. The UML contains all keys.

    path : The path to the .eaf file as Path

    time_dictionary : The TIME_ORDER block from the .eaf file (hash table for time values) as Dictionary.

    original_language : The language the speech was delivered in as 3 letter String. (determined by sequence matcher)
    
    speaker_name : The speaker's full name, speaker_name[0] being the first name, speaker_name[-1] being the last name.

    speaker_is_native : Info whether the speaker was considered speaking in his native language as Bool.
    
    speaker_birth : Info on the age of the speaker as Int.
    
    speaker_gender : Info on the gender of the speaker as 1 letter String.
    
    speaker_affiliation : Info on the group the speaker is speaking for as String.

    eaf_duration : Duration of the .eaf file in milliseconds as Int.

    mp3_paths : ---not implemented---
    
    _original_language_zcr : The language the speech was delivered in as 3 letter String. (determined by zcr)

    _filename : The filename without the .eaf as String

    _deco1 : ANNOTATION_DOCUMENT tag as String

    _deco2 : PROPERTY NAME="URN" tag as String
    ====================
    Methods:

    @staticmethod
    prepare_eaf(path) : This function calls several functions of pymmep.eaf_utils to prepare the data
        necessary to construct the Eaf_Container. The arguments can not be provided as list, so kindly
        write a[0], a[1], a[2] until I find a better way to only parse the xml once.
        
    describe() : Sums up the most important information about the speech (not yet implemented)

    ====================
    Example Usage:

    arguments = prepare_eaf("./files/file.eaf")
    eaf = Eaf_Container("./files/file.eaf", arguments[0], arguments[1], arguments[2])
    eaf.to_pickle()

    """
    def __init__(self, path, time_dictionary, tier_dictionary, deco):

        self.path = Path(path) # This holds the path to the source .eaf file as Path.

        self._filename = self.path.name[:-4]    # This holds the file name without the ".eaf" as String
                                                # Intended for export only - but seeing surprising amounts of use

        self.time_dictionary = time_dictionary # This holds the whole time information block from the .eaf file as Dictionary.

        self.eaf_duration = max(self.time_dictionary.values()) # This holds the duration of the .eaf file in milliseconds as Int.

        self.speaker_name = '' # holds the full name of the speaker, probably as Tuple of Strings. tuple[0] being the first name, tuple[-1] the last name.

        self.original_language = '' # This holds the original language of the speech as 3 letter String.

        self._speaker_original_language_zcr = "" # This holds the original language of the speech as assigned by the zero crossing rate method to detect interpreter voiceover as a 3 letter String.

        self.speaker_is_native = False # This holds whether the original speaker is considered native as Boolean. NOT IMPLEMENTED

        self.speaker_birth = 0 # holds the age in some way (see documentation of the function for the factors, probably just Wikipedia) as 4-8 digit Int or Date.

        self.speaker_gender = "" # holds the automatically determined gender (see documentation of the function for the factors) as 1 letter String.

        self.speaker_affiliation = "" # holds the automatically determined affiliation (group they are speaking for according to europarl verbatim) as varying length String.


        @property
        def mp3_paths(): # This will generate and return the relative 20 mp3 paths if they are ever needed
            return ["not yet implemented, sorry"]
        
        # These two attributes are only necessary if (for whatever reason) it is required to reconstruct the .eaf file.
        self._deco1 = deco[0] # This holds the ANNOTATION_DOCUMENT tag content as String
        self._deco2 = deco[1] # This holds the PROPERTY NAME="URN" tag content as String
        
        # This is the heart of the object, it contains all tiers data and meta information, some have to be set after making the DataFrames!
        self.language_data = self._make_language_dictionary(tier_dictionary) # This holds the .eaf tiers, ordered by language as Dictionary.
        
        self._fix_boolean_column_dtypes()
        
        self._language_list = list(self.language_data.keys())   # This just holds a list of the 3 letter language codes
                                                                # Inteded for looping only.
        
        # Now find and set the meta for the 22 dictionaries:
        self._find_and_set_speaker_name() # NOT IMPLEMENTED
        self._find_and_set_speaker_native() # NOT IMPLEMENTED
        self._find_and_set_translation_perc()
        self._find_and_set_speech_duration()
        

    # This function creates the dictionary structure: 22 language dictionaries that contain what _add_meta_dictionary fills in
    def _make_language_dictionary(self, tier_dictionary):
        tier_list = list(tier_dictionary.values())
        return {tier[-3:] : self._add_meta_dictionary(index, tier_list) for index, tier in enumerate(tier_dictionary) if "transcription" in tier} # kind of hacky way to count languages
    
    # This function populates one of the 22 language dictionaries with dataframes (from eaf tiers) and meta information
    def _add_meta_dictionary(self, index, tier_list):
        return {'df_transcription': self._parse_transcription_tier_into_df(index, tier_list), 
                'df_confidence': self._parse_dependent_tier_into_df(index+1, tier_list),
                'df_is_translation': self._parse_dependent_tier_into_df(index+2, tier_list),
                'df_manually_corrected': self._parse_dependent_tier_into_df(index+3, tier_list),
                #'df_aligned_pretty': # This approach will probably not work, I will write a method to add this later
                #'df_translation': # This approach will probably not work, I will write a method to add this later
                'speaker_name' : "", # NOT IMPLEMENTED
                'speaker_native': False,  # NOT IMPLEMENTED
                'is_translation_perc' : 0.0, # Will be set later
                'is_orig' : False, # Will be set later
                'speech_duration' : 0, # Will be set later, sum of segments, intensity > x (eventually) as Int
                'verbatim_file' : '', # name of europarl speech file as String
                'verbatim_speech' : '', # speech from verbatim with highest ratio
                'verbatim_ratio' : 0.0 # sequence matcher ratio
               }        

    def _parse_transcription_tier_into_df(self, index, tier_list):
        return pd.DataFrame({'Annotation_ID' : [annotations[0].attrib["ANNOTATION_ID"] for annotations in tier_list[index]], 
                             'Time_Start' : [self.time_dictionary[annotations[0].attrib["TIME_SLOT_REF1"]] for annotations in tier_list[index]], 
                             'Time_End' : [self.time_dictionary[annotations[0].attrib["TIME_SLOT_REF2"]] for annotations in tier_list[index]],
                             'Text' : [annotations[0][0].text for annotations in tier_list[index]]}) # passing dtypes here is a github issue for 10 years+ now: no.
        
    def _parse_dependent_tier_into_df(self, index, tier_list):
        return pd.DataFrame({'Annotation_ID' : [annotations[0].attrib["ANNOTATION_ID"] for annotations in tier_list[index]],
                             'Annotation_REF': [annotations[0].attrib["ANNOTATION_REF"] for annotations in tier_list[index]],
                             'Value' : [annotations[0][0].text for annotations in tier_list[index]]}) # passing dtypes here is a github issue for 10 years+ now: no.
    
    def _fix_boolean_column_dtypes(self):
        for language_code in self.language_data:
            self.language_data[language_code]['df_is_translation']['Value'] = np.where((self.language_data[language_code]['df_is_translation']['Value'] == "True"),
                                                                                       True,
                                                                                       False
                                                                                      )
            self.language_data[language_code]['df_manually_corrected']['Value'] = np.where((self.language_data[language_code]['df_manually_corrected']['Value'] == "True"),
                                                                                           True,
                                                                                           False
                                                                                          )
    ###############################################################
    # Functions to find and set the meta for the 22 dictionaries: #
    ###############################################################
    
    def _find_and_set_speaker_name(self):
        pass
    
    def _find_and_set_speaker_native(self):
        pass
    
    # Calculate how much % of the annotated time is labled as translation IF this means dividing by 0, then something is broken and I set it to 9999
    def _find_and_set_translation_perc(self):
        list_of_translation_percents = []
        for language_code in self._language_list:
            try:
                self.language_data[language_code]['is_translation_perc'] = self.language_data[language_code]['df_is_translation']['Value'].sum() / self.language_data[language_code]['df_is_translation']['Value'].count() # this line is the reason for np.seterr(all='raise')
            except:
                self.language_data[language_code]['is_translation_perc'] = 9999
            list_of_translation_percents.append(self.language_data[language_code]['is_translation_perc'])
            self._find_and_set_is_original(list_of_translation_percents)
        self._find_and_set_original_language(list_of_translation_percents)
    
    # The language with the lowest "is_translation_perc" should be the original.
    def _find_and_set_is_original(self, translation_percents):
        self.language_data[self._language_list[np.argmin(translation_percents)]]['is_orig'] == True
    
    # Add the language annotated time
    def _find_and_set_speech_duration(self):
        for language_code in self._language_list:
            self.language_data[language_code]['speech_duration'] = (self.language_data[language_code]['df_transcription']['Time_End']-self.language_data[language_code]['df_transcription']['Time_Start']).sum()
            
    
    ##############################################
    # Functions to find and set the global meta: #
    ##############################################
    
    #
    def _find_and_set_original_language(self, translation_percents):
        self.original_language = self._language_list[np.argmin(translation_percents)]
    
    def _find_and_set_speaker_is_native(self):
        pass
        
###########################

    @staticmethod
    def prepare_eaf(path):
        tree = pymmep.eaf_utils.parse_eaf(path)
        slots = pymmep.eaf_utils.get_time_slots(tree)
        slot_dic = pymmep.eaf_utils.make_time_slot_dictionary(slots)
        tiers = pymmep.eaf_utils.get_tiers(tree)
        tier_dic = pymmep.eaf_utils.make_tier_dictionary(tiers) 
        deco = pymmep.eaf_utils.get_decoration(tree)
        return [slot_dic, tier_dic, deco]
    
    @classmethod
    def make_dataframe_from_path_to_eaf(path): # Maybe implement later
        pass

    # I really have to see if I like to work with this to decide whether I want to improve this
    def make_big_dataframe(self, code):
        big_df = self.language_data[code]['df_transcription'].merge(self.language_data[code]['df_confidence'], left_on='Annotation_ID', right_on='Annotation_REF')
        big_df.rename(columns={'Annotation_ID_x':'Annotation_ID', 'Value':'Confidence'}, inplace=True)
        big_df.drop('Annotation_ID_y', axis=1, inplace=True)
        big_df.drop('Annotation_REF', axis=1, inplace=True)
        big_df = big_df.merge(self.language_data[code]['df_is_translation'], left_on='Annotation_ID', right_on='Annotation_REF')
        big_df.rename(columns={'Annotation_ID_x':'Annotation_ID', 'Value':'Translated'}, inplace=True)
        big_df.drop('Annotation_ID_y', axis=1, inplace=True)
        big_df.drop('Annotation_REF', axis=1, inplace=True)
        big_df = big_df.merge(self.language_data[code]['df_manually_corrected'], left_on='Annotation_ID', right_on='Annotation_REF')
        big_df.rename(columns={'Annotation_ID_x':'Annotation_ID', 'Value':'Man_Corrected'}, inplace=True)
        big_df.drop('Annotation_ID_y', axis=1, inplace=True)
        big_df.drop('Annotation_REF', axis=1, inplace=True)
        return big_df
    
    def make_duration_column(self): # It's 2 am and it's super simple, if I ever actually need this I'll write it and put it here.
        pass
    
    def to_pickle(self, outpath='./_output/{}.pickle'):
        with open(outpath.format(self._filename), 'wb') as f:
            pickle.dump(self, f, protocol=5)

    def remake_eaf(): # Maybe implement later
        pass  
    
    def describe(): #implement later, give key information quick
        pass