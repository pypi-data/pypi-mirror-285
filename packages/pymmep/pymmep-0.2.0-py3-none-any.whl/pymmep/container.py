"""
The point of this module is to hold the class SpeechContainer and as little
else as possible, so that it can run on as many platforms out of the box
as possible.
"""

import numpy as np
import pandas as pd
import pickle


class SpeechContainer:
    """
    Description:

    This class is intended to hold all important values for one speech.

    This is intended to be created with the functions from eaf_utils,
    to parse all .eaf information into this python structure
    and save it pickled for later use.

    > The initialiser takes one argument: A touple containing
    [0] path to eaf file
    [1] dictionary of time info from eaf 
    [2] dictionary of tier info from eaf
    [3] list of other eaf info
    from here all relevant information is extracted.
    This touple can be neatly prepared with extract_eaf() from eaf_utils
    which requires only the path of an eaf file.

    > Add more data as you please using the speech_container_utils module.

    > Call method .to_pickle(Path) to save the whole object.

    ====================
    Attributes (Top level overview):

    file_data : Dictionary of file paths.

    speech_data : Dictionary of information about the speech and the 
                  recording.

    speaker_data : Dictionary of information about the speaker.

    _eaf_data : Dictionary of eaf data for full reconstruction.

    language_data : One dictionary for each language containing potential
                    eaf tiers.

    -------------------

    file_data:
    (set by the constructor)
        mp3_paths : (Str) The path of the folder holding all mp3s.
        eaf_path : (Str) The path to the eaf.
        folder_name : (Str) The folder name for this recording without path.

    speech_data:
    (set by the constructor)
        None
    (set manually)
        samples : (Int) The number of samples of the original speech.
        sample_rate : (Int) The sample rate of the original speech.
        length : (Int) The length in milliseconds of the original speech.
        orig_lang : (Str) The original language of the speech.
            orig_lang_kaldi : Original language according to Kaldi,
            orig_lang_zcr : Original language according to ocr,
            zcr_data : Data the zcr decision is based on,
            orig_lang_whisper : Original language according to whisper,
            whisper_data : Data the whisper decision is based on,
            orig_lang_sub : Original language according to subtraction,
            sub_data : Data the sub decision is based on.
        window : (Tuple of 2 Int) The window the original language is likely
                 spoken.
        date : (Str) The date of the SESSION of the speech.
        time : (Str) The approximate ACTUAL time of the speech.
        session : (Int) The session number.
        location : (Str) The location (Brussels or Strasbourg).
        cycle : (Tuple of 2 Int) The numbers of the session and max sessions 
                within the cycle (Normally 4 in Strasbourg, 2 in Brussels).
        subject : (Str) The subject of the block the speech is a part of.
        chair: (Str) Person in the president's chair.

    speaker_data:
    (set by the constructor)
        None
    (set manually)
        name : (Str) The name of the speaker.
        group : (Str) The group the speaker is affiliated with.
        gender : (Str) The gender of the speaker.
        birthday : (Str) The date of birth of the speaker.
        age : (Int) The age of the speaker at the time of the speech.
        native : (Bool) Information whether the speaker is speaking his native
                 language or not.
        wiki : (Str) wikipedia link to the speaker's page. 

    _eaf_data:
    (set by the constructor)
        time_dictionary : (Dict of Str key and Int value) 
        eaf_duration : (Int)
        date : (Str)
        property_tag : (Str)

    language_data:
    (set by the constructor)
        22 dictionaries, each containing:
            df_transcription : The transcription tier from the eaf-file
                               transcribed with Kaldi.
            df_confidence : Kaldi's confidence in its transcription.
            df_is_translation : Kaldi's estimation whether this segment is 
                                a translation.
            df_manually_corrected : Info whether the segment has been manually
                                    corrected by a human.
    (set manually)
            df_transcription_whisper1 : Transcription of the audio by whisper.
            df_transcription_whisper2 : Transcription of the audio by whisper
                                        after more training.
            'relay_interp' : (Bool) Flag if this is a relay interpretation.
            'retour_interp': (Bool) Flag if this is a retour interpretation.
            'is_translation_perc' : (Float) Percentage of 
            'speech_duration' : (Int) Duration of the audio channel.
            'verbatim_file' : (Int) Number of speech in verbatim dictionary.
            'verbatim_speech' : (Str) Content of verbatim speech.
            'verbatim_ratio' : (Float)Sequence matcher ratio that led to this
                               match.
            'interpreter_window' : Estimated window when the interpreter has 
                                   his microphone active (based on channel
                                   subtraction).

    ====================
    Public Methods:

    to_pickle(directory = _output) : pickles the container, standard directory
                                     is ./_output, but another one may be set.

    migrate() : extracts the contents of the container into a folder of the 
                same name. This only affects the attributes declares in this
                module, but other attributes may be added to the folder after
                calling migrate(). 
                Warning: This is very unweildly, but allows migrating the 
                structure to R or C++ or whatever is popular in 10 years.

    ====================
    Example Usage:
    
    
    
    
    
    """

    ###############
    # Initialiser #
    ###############
    
    def __init__(self, eaf_extraction):

        # Dictionary of file paths relating to the speech.
        # Set by this constructor
        self.file_data = {'mp3_paths' : '/corpus/{}/'.format(eaf_extraction[0][76:-4]),
                          'eaf_path' : eaf_extraction[0],
                          'folder_name' : eaf_extraction[0][76:-4]}

        # Dictionary of information relating to speech as a whole and its recording.
        # Set manually; from scraped data and acoustic analysis
        self.speech_data = {'samples' : None,
                            'sample_rate' : None,
                            'length' : None,
                            'orig_lang' : None,
                            'orig_lang_kaldi' : None,
                            'kaldi_data' : None,
                            'orig_lang_zcr' : None,
                            'zcr_data' : None,
                            'orig_lang_whisper' : None,
                            'whisper_data' : None,
                            'orig_lang_sub' : None,
                            'sub_data' : None,
                            'window' : None,
                            'date' : None, # date of SESSION
                            'time' : None,
                            'session' : None,
                            'location' : None,
                            'cycle' : None,
                            'subject' : None,
                            'chair' : None}

        # Dictionary of information relating to the original speaker (not the interpreters!).
        # Set manually; from scraped data.
        self.speaker_data = {'name' : None,
                             'group' : None,
                             'gender' : None,
                             'birthday' : None,
                             'age' : None,
                             'native' : None,
                             'wiki' : None}

        # Dictionary of information required to rebuild a nice eaf file for Elan.
        # Set by this constructor
        self._eaf_data = {'time_dictionary' : eaf_extraction[1],
                          'eaf_duration' : max(eaf_extraction[1].values()),
                          'date' : eaf_extraction[3][0],
                          'property_tag' : eaf_extraction[3][1]}

        # Dictionary of information for each language, for each interpreter channel.
        # Set partially by this constructor, partially manually.
        self.language_data = self._make_language_dictionary(eaf_extraction[2], eaf_extraction[1])
        
        # This has to be called here, because the "True" and "False" from the eaf files can not be fixed on read.
        # Strictly speaking this is just a hack to save a bit of disc space and processing time later.
        self._fix_boolean_column_dtypes()


    ###################
    # Private Methods #
    ###################

    # This function creates the dictionary structure: 22 language dictionaries that contain what _add_meta_dictionary fills in
    def _make_language_dictionary(self, tier_dictionary, time_dictionary):
        tier_list = list(tier_dictionary.values())
        return {tier[-3:] : self._add_meta_dictionary(index, tier_list, time_dictionary) for index, tier in enumerate(tier_dictionary) if "transcription" in tier}


    # This function populates one of the 22 language dictionaries with dataframes (from eaf tiers)
    def _add_meta_dictionary(self, index, tier_list, time_dictionary):
        return {'df_transcription': self._parse_transcription_tier_into_df(index, tier_list, time_dictionary),
                'df_confidence': self._parse_dependent_tier_into_df(index+1, tier_list),
                'df_is_translation': self._parse_dependent_tier_into_df(index+2, tier_list),
                'df_manually_corrected': self._parse_dependent_tier_into_df(index+3, tier_list),
                'relay_interp' : None,
                'retour_interp': None,
                'is_translation_perc' : None,
                'speech_duration' : None,
                'verbatim_file' : None,
                'verbatim_speech' : None,
                'verbatim_ratio' : None,
                'interpreter_window' : None}

    # Parses the transcription tier of the eaf into a data frame.
    def _parse_transcription_tier_into_df(self, index, tier_list, time_dictionary):
        return pd.DataFrame({'Annotation_ID' : [annotations[0].attrib["ANNOTATION_ID"] for annotations in tier_list[index]], 
                             'Time_Start' : [time_dictionary[annotations[0].attrib["TIME_SLOT_REF1"]] for annotations in tier_list[index]], 
                             'Time_End' : [time_dictionary[annotations[0].attrib["TIME_SLOT_REF2"]] for annotations in tier_list[index]],
                             'Text' : [annotations[0][0].text for annotations in tier_list[index]]}) # passing dtypes here is a github issue for 10 years+ now: no.

    # Parses a dependent tier of the eaf into a data frame.
    def _parse_dependent_tier_into_df(self, index, tier_list):
        return pd.DataFrame({'Annotation_ID' : [annotations[0].attrib["ANNOTATION_ID"] for annotations in tier_list[index]],
                             'Annotation_REF': [annotations[0].attrib["ANNOTATION_REF"] for annotations in tier_list[index]],
                             'Value' : [annotations[0][0].text for annotations in tier_list[index]]}) # passing dtypes here is a github issue for 10 years+ now: no.  

    # This fixes the "True" and "False" read from the eaf file into boolean type for faster processing.
    # This is not strictly speaking necessary, but for our specific usecase this is advantageous.
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


    ##################
    # Public Methods #
    ##################

    def to_pickle(self, directory = '_output'):
        """
        This method pickles the instance of SpeechContainer into a directory
        that is its only parameter (standard is _output).
        """
        with open('./{}/{}.pickle'.format(directory, self.file_data['folder_name']), 'wb') as f:
            pickle.dump(self, f, protocol=5)
            
    @classmethod
    def from_nothing(cls):
        """
        This creates an empty container which can then be refilled
        from an older container. Used for reordering and addition
        of attributes and methods. Kind of private, because it is
        a little hacky with its use of strings.
        """
        return (cls(('None', {None: [None]}, {'None': [None]}, [None, None])))

    def migrate(self, directory = '_migration'):
        """
        This method extracts all information declared in this module into a
        folder and file structure, so that it may be accessed with whatever
        program or language anyone could want. 
        Its only parameter is the output folder (standard is _migration).
        """
        pass

    def get_file_info():
        pass

    def get_speech_info():
        pass

    def get_speaker_info():
        pass

    def get_eaf_info():
        pass
    
    def get_language_info():
        pass