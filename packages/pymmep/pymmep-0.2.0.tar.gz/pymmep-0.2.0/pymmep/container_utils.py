"""
The point of this module is to hold functions that are repeatedly
used for container manipulation.
"""

import pymmep
from pathlib import Path
import pandas as pd
import numpy as np
from collections import Counter




def pickle_iterator(pickle_dir="./pickled_containers"):
    """
    yields all pickles in a folder
    """
    pickles = Path(pickle_dir)
    for pickle in sorted(pickles.glob("*.pickle")):
        yield str(pickle.relative_to("."))
        
        
        
        
def calculate_translation_perc(container, language_code):
    """
    This function takes a container and a language code and returns
    the language's Kaldi estimation of the percentage of translated 
    and non-translated speech in a touple of two floats.
    
    input: container (with eaf info), language_code
    output: If eaf_duration = 0: None
            If no segment with translation value: None
            Else: (Float, Float)
            The first float is the % of translated speech.
            The second float is the % of non translated speech.
            (This does not necessarily add up to 100% because
            of silence)
    """
    # if the eaf_duration is 0 then no decision can be made.
    if container._eaf_data['eaf_duration'] == 0:
        return None
    
    # if there is at least one segment with a value then measure the %age.
    if container.language_data[language_code]['df_is_translation']['Value'].count() != 0:
        # calculate duration of segments
        evaluation_series = pd.DataFrame(container.language_data[language_code]['df_transcription']['Time_End'] - 
                                         container.language_data[language_code]['df_transcription']['Time_Start'])
        evaluation_df = pd.concat([evaluation_series, container.language_data[language_code]['df_is_translation']['Value']], axis=1)
        evaluation_df.columns = ['Duration', 'Value']
        # if segment translated: +duration/eaf_duration
        # if segment not translated: -duration/eaf_duration
        evaluation_df['Result'] = np.where(evaluation_df['Value'],
                                           evaluation_df['Duration'] / container._eaf_data['eaf_duration'],
                                           -evaluation_df['Duration'] / container._eaf_data['eaf_duration'])
        return round(evaluation_df[evaluation_df['Result'] >= 0]['Result'].sum(),2), round(evaluation_df[evaluation_df['Result'] < 0]['Result'].sum(), 2)
    
    # if there is no segment with a value then no decision can be made.
    else:
        return None




def set_orig_lang_kaldi(container):
    """
    This function takes a container, iterates over all languages and collects
    all is_translation_perc values. It stores these values in kaldi_data and
    sets orig_lang_kaldi according to the winner with an added reliability 
    measure.
    
    input: container (with eaf info and is_translated_perc set)
    output: (tuple, string, float) 
            Sorted tuple of all languages' is_translation_perc and 
            The language string with the highest percentage of non-translated 
            segments and 
            the distance to number two.
    """
    perc_list = []
    for language_code in container.language_data.keys():
        if container.language_data[language_code]['is_translation_perc'] is not None:
            perc_list.append((language_code, container.language_data[language_code]['is_translation_perc']))
    output_base = sorted(perc_list, key=lambda x: x[1][1])
    return output_base, output_base[0][0], output_base[0][1][1] - output_base[1][1][1]




def calculate_zcr_reliability(zcr_data):
    """
    This returns true if "und" and the best estimate are closer than
    the the second best estimate and either "und" or the best estimate.
    (It was established that "und" has to be in the top 2.)
    
    Input: Entry of zcr-dictionary of the form [(estimate), [(), (), ...]]
    Output: True or False
    """
    # get und-value, estimate-value and data-values without those two values.
    und = [x for x in zcr_data[1] if x[0] == 'und']
    estimate = zcr_data[0]
    cleaned = [x for x in zcr_data[1] if x[0] != 'und' and x[0] != zcr_data[0][0]]
    
    # calculate difference between "und" and estimate
    control = und[0][1] - estimate[1]

    # calculate difference between the lower of the two and the number3
    # if order is und-lang-number3
    if control >= 0:
        # lang - number3
        compare = estimate[1] - cleaned[-1][1]
        # difference between control and compare 
        result = control - compare
    # if order is lang-und-number3
    if control < 0:
        # und - number3
        compare = und[0][1] - cleaned[-1][1]
        # difference between control and compare (- replaces abs, compare can never be negative)
        result = -control - compare

    # evaluate if best estimate and "und" are closer than either and the second best estimate
    if result < 0:
        return True
    else:
        return False




def estimate_orig_lang_whisper(current_whisper):
    """
    Returns a list of all languages reliably identified within the 
    recording, ordered by amount of window occurrences (first run
    used 10 second windows in 3 second steps.
    
    Input: List of whisper language estimates of the form
            ['language', reliable?, [full data]]
    Output: Ordered list of the sum of reliably identified 
            language sections.    
    """
    compare_list = []
    for segment in current_whisper:
        if segment[1] is True:
            compare_list.append(segment[0])
    return (Counter(compare_list).most_common())




def estimate_orig_lang_sub(action):
    """
    Takes second-wise estimate of interpreter activity and returns 
    the most likely main language, duration and confidence measure.
    
    Input: Dictionary of language:second_wise_interaction_boolean
    Output: Main language, Seconds of interpreter inactivity,
            confidence measure between 0 and 1, unlikely > 0.8
    """
    comparison_list = []
    for language, content in action.items():
        comparison_list.append((language, sum(content)))
    # True = Interpreter action, so lowest value is most likely original
    decision_base = sorted(comparison_list, key=lambda x: x[1])
    decision_confidence = (decision_base[1][1] - decision_base[0][1]) / len(content)
    return decision_base[0][0], len(content) - decision_base[0][1], decision_confidence




def set_session_data(container, session_list):
    """
    This sets the session specific information according to a session
    list provided.
    
    Input: Session list containing (session_start, session_end, 
            location code, and number of sessions in cycle.
    Output: None, sets attributes in container.
    """
    container_time = ''.join([container.file_data['folder_name'][8:16], 
                             container.file_data['folder_name'][17:-9]])
    for index, element in enumerate(session_list):
        if container_time >= element[0] and container_time <= element[1]:
            container.speech_data['date'] = element[0][:8]
            container.speech_data['time'] = container_time
            container.speech_data['session'] = index+1
            if element[2][0] == 'b':
                container.speech_data['location'] = 'Brussels'
            if element[2][0] == 's':
                container.speech_data['location'] = 'Strasbourg'
            container.speech_data['cycle'] = (int(element[2][1]), int(element[3]))
            break

            


def set_subject(container, subject_list):
    '''
    This sets the speech subject according to the time stamp
    from filename and a start + end + subject name list provided.
    
    Input: List containing (subject_start, subject_end, subject)            
    Output: None, sets attributes in container.
    '''
    # get container time
    container_session = container.speech_data['session']
    container_time_start = ''.join([container.file_data['folder_name'][8:16], 
                              container.file_data['folder_name'][17:-9]])[:-2]
    container_time_end = ''.join([container.file_data['folder_name'][8:16], 
                              container.file_data['folder_name'][-8:]])[:-2]

    # see if it fits the subject time
    for subject in subject_list[container_session]:
        if container_time_start >= subject[0] and container_time_start <= subject[1]:
            container.speech_data['subject'] = subject[2]

    # if nothing fits, then settle for a bad fit from ending time
    if container.speech_data['subject'] is None:
        for subject in subject_list[container_session]:
            if container_time_end >= subject[0] and container_time_end <= subject[1]:
                container.speech_data['subject'] = ('bad fit', subject[2])

    # if nothing fits, then send a message
    if container.speech_data['subject'] is None:
        print('{} has failed to find a timeslot'.format(container.file_data['folder_name']))




def set_chair_from_time(container, chair_list):
    '''
    This sets the person currently in the chair according
    to chair changes from the verbatim report time stamps.
    This is not precise !
    
    Input: container, list of chair changes            
    Output: person in chair
    '''
    container_session = container.speech_data['session']

    # if possible get subject number, else return None
    if (compare := container.speech_data['subject']) is not None:
        if type(compare) is not tuple:
            compare = int(compare[:3].replace('.', ''))
        else:
            compare = int(compare[1][:3].replace('.', ''))
    else:
        return None

    for index, president in enumerate(chair_list[container_session]):
        # if last entry, then don't try to check the next
        if index+1 == len(chair_list[container_session]):
            if compare > int(president[1][:3].replace('.', '')):
                return president[0][14:]
        # compare > president_start and compare < next_president_start = success
        else:
            if compare > int(president[1][:3].replace('.', '')) and compare <= int(chair_list[container_session][index+1][1][:3].replace('.', '')):
                return president[0][14:]




