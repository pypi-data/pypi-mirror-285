from typing import Any, List
import os
import torch
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import OneHotEncoder

class HeliosMedPrep:
    def __init__(
            self,
            dataset="MIMICIV",
            raw_folder: str = None,
            preprocessing_folder: str = None,
            external_folder: str = None,
            triplet: bool = True,
            top_k: int = 256,
            ) -> None:
        
        self.dataset = dataset
        self.raw_folder = raw_folder
        self.preprocessing_folder = preprocessing_folder
        self.top_k = top_k
        self.triplet = triplet
        self.ndc_rxnorm_file = f"{external_folder}/ndc2rxnorm_mapping.txt"
        self.ndc2atc_file = f"{external_folder}/ndc2atc_level4.csv"
        self.ddi_path = f"{external_folder}/drug-DDI.csv"
        self.cid_atc_path = f"{external_folder}/drug-atc.csv"


        
        if dataset == "MIMICIV":
            self.retrieve_dict = {
                "clinical": {
                    "1_digits_icd_code": ['R', 'S', 'T', 'V', 'W', 'X', 'Y', 'U', 'Z'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                    },
                "resistance_to_antimicrobial_drugs": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": ['Z16']
                    },
                "body_mass_index": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": ['Z68']
                    },
                "long_term_current_drug_therapy": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": ['Z79']
                    },
                "allergy_status_to_drugs": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": ['Z88']
                    }
            }
            categories = {
                "Certain infectious and parasitic diseases": {
                    "1_digits_icd_code": ['A', 'B'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Neoplasms": {
                    "1_digits_icd_code": ['C'],
                    "2_digits_icd_code": ['D0', 'D1', 'D2', 'D3', 'D4'],
                    "3_digits_icd_code": []
                },
                "Diseases of the blood and blood-forming organs and certain disorders involving the immune mechanism": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['D5', 'D6', 'D7', 'D8', 'D9'],
                    "3_digits_icd_code": []
                },
                "Endocrine, nutritional and metabolic diseases": {
                    "1_digits_icd_code": ['E'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Mental, Behavioral and Neurodevelopmental disorders": {
                    "1_digits_icd_code": ['F'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Diseases of the nervous system": {
                    "1_digits_icd_code": ['G'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Diseases of the eye and adnexa": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['H0', 'H1', 'H2', 'H3', 'H4', 'H5'],
                    "3_digits_icd_code": []
                },
                "Diseases of the ear and mastoid process": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['H6', 'H7', 'H8', 'H9'],
                    "3_digits_icd_code": []
                },
                "Diseases of the circulatory system": {
                    "1_digits_icd_code": ['I'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Diseases of the respiratory system": {
                    "1_digits_icd_code": ['J'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Diseases of the digestive system": {
                    "1_digits_icd_code": ['K'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Diseases of the skin and subcutaneous tissue": {
                    "1_digits_icd_code": ['L'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Diseases of the musculoskeletal system and connective tissue": {
                    "1_digits_icd_code": ['M'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Diseases of the genitourinary system": {
                    "1_digits_icd_code": ['N'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Pregnancy, childbirth and the puerperium": {
                    "1_digits_icd_code": ['O'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Certain conditions originating in the perinatal period": {
                    "1_digits_icd_code": ['P'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Congenital malformations, deformations and chromosomal abnormalities": {
                    "1_digits_icd_code": ['Q'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Symptoms, signs and abnormal clinical and laboratory findings, not elsewhere classified": {
                    "1_digits_icd_code": ['R'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Injury, poisoning and certain other consequences of external causes": {
                    "1_digits_icd_code": ['S', 'T'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Codes for special purposes": {
                    "1_digits_icd_code": ['U'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "External causes of morbidity": {
                    "1_digits_icd_code": ['V', 'W', 'X', 'Y'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Factors influencing health status and contact with health services": {
                    "1_digits_icd_code": ['Z'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
            }

            self.icd9toicd10cmgem = load_dataframe_from_url("https://drive.google.com/file/d/1vkBfT2Tcss46ZZvHRtKSyCMx3To6SzgM/view?usp=sharing")
            self.icd9toicd10pcsgem = load_dataframe_from_url("https://drive.google.com/file/d/1KZz45yI7_Jarkb_tc7Sj-Y16fakJ6qgW/view?usp=sharing")

            # print(self.icd9toicd10cmgem.columns)
            self.icd9toicd10cmgem['icd9cm'] = self.icd9toicd10cmgem['icd9cm'].astype(str)
            self.icd9toicd10cmgem['icd10cm'] = self.icd9toicd10cmgem['icd10cm'].astype(str)
            self.icd9toicd10cmgem['icd9'] = self.icd9toicd10cmgem['icd9cm'].str[:3]
            self.icd9toicd10cmgem['icd10'] = self.icd9toicd10cmgem['icd10cm'].str[:3]
            self.icd9toicd10cmgem = self.icd9toicd10cmgem[['icd9cm', 'icd10cm', 'icd9', 'icd10']]
            self.icd9toicd10pcsgem['icd9cm'] = self.icd9toicd10pcsgem['icd9cm'].astype(str)
            self.icd9toicd10pcsgem['icd10cm'] = self.icd9toicd10pcsgem['icd10cm'].astype(str)
            self.icd9toicd10pcsgem['icd9'] = self.icd9toicd10pcsgem['icd9cm'].str[:3]
            self.icd9toicd10pcsgem['icd10'] = self.icd9toicd10pcsgem['icd10cm'].str[:3]
            self.icd9toicd10pcsgem = self.icd9toicd10pcsgem[['icd9cm', 'icd10cm', 'icd9', 'icd10']]

        elif dataset == "MIMICIII":
            self.retrieve_dict = {
                "clinical": {
                    "1_digits_icd_code": ['8', '9', 'V', 'E'],
                    "2_digits_icd_code": ['78' ,'79'],
                    "3_digits_icd_code": []
                    },
                "resistance_to_antimicrobial_drugs": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": ['V09']
                    },
                "body_mass_index": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": ['V85']
                    },
                "long_term_current_drug_therapy": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": ['V58']
                    },
                "allergy_status_to_drugs": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": ['V14']
                    }
            }
            categories = {
                "Infectious And Parasitic Diseasess": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13'],
                    "3_digits_icd_code": []
                },
                "Neoplasms": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['14', '15', '16', '17', '18', '19', '20', '21', '22', '23'],
                    "3_digits_icd_code": []
                },
                "Endocrine, Nutritional And Metabolic Diseases, And Immunity Disorders": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['24', '25', '26', '27'],
                    "3_digits_icd_code": []
                },
                "Diseases Of The Blood And Blood-Forming Organs": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['28'],
                    "3_digits_icd_code": []
                },
                "Mental Disorders": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['29', '30', '31'],
                    "3_digits_icd_code": []
                },
                "Diseases Of The Nervous System And Sense Organs": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['32', '33', '34', '35', '36', '37', '38'],
                    "3_digits_icd_code": []
                },
                "Diseases Of The Circulatory System": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['39', '40', '41', '42', '43', '44', '45'],
                    "3_digits_icd_code": []
                },
                "Diseases Of The Respiratory System": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['46', '47', '48', '49', '50', '51'],
                    "3_digits_icd_code": []
                },
                "Diseases Of The Digestive System": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['52', '53', '54', '55', '56', '57'],
                    "3_digits_icd_code": []
                },
                "Diseases Of The Genitourinary System": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['58', '59', '60', '61', '62'],
                    "3_digits_icd_code": []
                },
                "Complications Of Pregnancy, Childbirth, And The Puerperium": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['63', '64', '65', '66', '67'],
                    "3_digits_icd_code": []
                },
                "Diseases Of The Skin And Subcutaneous Tissue": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['68', '69', '70'],
                    "3_digits_icd_code": []
                },
                "Diseases Of The Musculoskeletal System And Connective Tissue": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['71', '72', '73'],
                    "3_digits_icd_code": []
                },
                "Congenital Anomalies": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['74', '75'],
                    "3_digits_icd_code": []
                },
                "Certain Conditions Originating In The Perinatal Period": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['76', '77'],
                    "3_digits_icd_code": []
                },
                "Symptoms, Signs, And Ill-Defined Conditions": {
                    "1_digits_icd_code": [],
                    "2_digits_icd_code": ['78', '79'],
                    "3_digits_icd_code": []
                },
                "Injury And Poisoning": {
                    "1_digits_icd_code": ['8', '9'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Supplementary Classification Of Factors Influencing Health Status And Contact With Health Services": {
                    "1_digits_icd_code": ['V'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
                "Supplementary Classification Of External Causes Of Injury And Poisoning": {
                    "1_digits_icd_code": ['E'],
                    "2_digits_icd_code": [],
                    "3_digits_icd_code": []
                },
            }

        self.categories = generate_categories_df(categories)
        pass

    def __call__(
            self, 
            train_valid_test_split: List[float] = [0.75, 0.1, 0.15],
            *args: Any, 
            **kwds: Any
            ) -> Any:
        
        file_dict = self.load_dataset_function(self.raw_folder)
        preprocessing_data_dict = {}
        preprocessing_data_dict.update(self.preprocess_hospitalizations(admissions_df=file_dict['admissions'], patients_df=file_dict['patients']))
        preprocessing_data_dict.update(self.preprocess_diagnoses(diagnoses_icd_df=file_dict['diagnoses_icd'], d_icd_diagnoses_df=file_dict['d_icd_diagnoses']))
        preprocessing_data_dict.update(self.preprocess_procedures(procedures_icd_df=file_dict['procedures_icd'], d_icd_procedures_df=file_dict['d_icd_procedures']))
        preprocessing_data_dict.update(self.preprocess_prescriptions(prescriptions_df=file_dict['prescriptions']))
        preprocessing_data_dict.update(self.preprocess_labevents(labevents_df=file_dict['labevents'], d_labitems_df=file_dict['labevents']))
        preprocessing_data_dict.update(select_sample(preprocessing_data_dict['admissions']))



        train_dict_df, valid_dict_df, test_dict_df = self.split(preprocessing_data_dict, train_valid_test_split)
        print(f"Save preprocessing dataset")
        mkdir(f"{self.preprocessing_folder}/{self.dataset}/train")
        mkdir(f"{self.preprocessing_folder}/{self.dataset}/valid")
        mkdir(f"{self.preprocessing_folder}/{self.dataset}/test")
        for k in train_dict_df.keys():
            print(k)
            train_dict_df[k].to_csv(f'{self.preprocessing_folder}/{self.dataset}/train/{k}.csv.gz', index=False, compression='gzip', encoding='utf-8')
        for k in valid_dict_df.keys():
            print(k)
            valid_dict_df[k].to_csv(f'{self.preprocessing_folder}/{self.dataset}/valid/{k}.csv.gz', index=False, compression='gzip', encoding='utf-8')
        for k in test_dict_df.keys():
            print(k)
            test_dict_df[k].to_csv(f'{self.preprocessing_folder}/{self.dataset}/test/{k}.csv.gz', index=False, compression='gzip', encoding='utf-8')

        for k in preprocessing_data_dict.keys():
            print(k)
            if k.startswith('d_'):
                preprocessing_data_dict[k].to_csv(f'{self.preprocessing_folder}/{self.dataset}/{k}.csv.gz', index=False, compression='gzip', encoding='utf-8')
        
        pass

    def split(self, dict_df, train_valid_test_split):
        print(dict_df['admissions'])
        subject_id_list = dict_df['admissions']['subject_id'].drop_duplicates().to_list()

        np.random.shuffle(subject_id_list)

        # Xác định số lượng phần tử cho mỗi tập
        n = len(subject_id_list)
        train_size = int(train_valid_test_split[0] * n)
        valid_size = int(train_valid_test_split[1] * n)

        # Chia danh sách thành các tập
        train_subject_id_list = subject_id_list[:train_size]
        valid_subject_id_list = subject_id_list[train_size:train_size + valid_size]
        test_subject_id_list = subject_id_list[train_size + valid_size:]

        train_dict_df = {}
        valid_dict_df = {}
        test_dict_df = {}

        for k in dict_df.keys():
            if not k.startswith('d_'):
                print(dict_df[k])
                train_dict_df[k] = dict_df[k][dict_df[k]['subject_id'].isin(train_subject_id_list)]
                valid_dict_df[k] = dict_df[k][dict_df[k]['subject_id'].isin(valid_subject_id_list)]
                test_dict_df[k] = dict_df[k][dict_df[k]['subject_id'].isin(test_subject_id_list)]

        return train_dict_df, valid_dict_df, test_dict_df
    
    def load_dataset_function(
            self,
            folder
            ):
        folder_list = os.listdir(f"{folder}/hosp")
        dict = {}
        for file in folder_list:
            name, extension, zip_= str.split(file, sep='.')
            dict[name.lower()] = read_csv_gz_function(f"{folder}/hosp/{file}")
        return dict
    
    def preprocess_hospitalizations(
            self,
            admissions_df,
            patients_df,
            ):
        
        print("".center(100, "-"))
        print("".center(100, "-"))
        print(f" {self.dataset} ".center(100, "-"))
        print("".center(100, "-"))
        print(" Preprocessing demographic data in the DataFrame: admissions.csv and patients.csv ".center(100, "-"))
        print("".center(100, "-"))
        print(" Statistics Before Preprocessing ".center(100, "-"))

        if self.dataset == "MIMICIII":
            patients_df = patients_df.rename(columns={"dob": "anchor_year"})
            admissions_df = admissions_df.rename(columns={"ethnicity": "race"})
            patients_df["anchor_age"] = 0
        patients_df = patients_df[['subject_id','gender','anchor_year', 'anchor_age']]
        admissions_df = admissions_df[['subject_id', 'hadm_id', 'admittime', 'dischtime',
            'deathtime', 'admission_type', 'admission_location',
            'discharge_location',
            'marital_status', 'race']]
        distinct_patients_df = pd.merge(patients_df, admissions_df[['subject_id']], how='inner', on='subject_id').drop_duplicates()
        admissions_df = pd.merge(admissions_df, distinct_patients_df, how='inner', on='subject_id').drop_duplicates()
        admissions_df['death'] = np.where(admissions_df['deathtime'].isna(), False, admissions_df['deathtime'] <= admissions_df['dischtime'])

        if self.dataset == "MIMICIII":
            admissions_df['age'] = admissions_df.apply(lambda x: x['anchor_age'] + (int(x['admittime'][:4]) - int(x['anchor_year'][:4])), axis=1)
        elif self.dataset == "MIMICIV":
            admissions_df['age'] = admissions_df.apply(lambda x: x['anchor_age'] + (int(x['admittime'][:4]) - x['anchor_year']), axis=1)
        

        self.preprocess_info_hospitalizations(admissions_df)


        admissions_df['admittime'] = pd.to_datetime(admissions_df['admittime'], errors='coerce')
        if admissions_df['admittime'].isnull().any():
            print("There are conversion errors in 'admittime' column.")
        admissions_df['latest_admittime'] = admissions_df.groupby('subject_id')['admittime'].transform('max')
        admissions_df['time'] = (admissions_df['latest_admittime'] - admissions_df['admittime']).dt.days
        admissions_df = admissions_df.drop(columns=['latest_admittime']).sort_values(['subject_id', 'admittime'])
        


        print(" Statistics After Preprocessing ".center(100, "-"))
        self.preprocess_info_hospitalizations(admissions_df)

        return {
            "admissions": admissions_df[['subject_id', 'hadm_id', 'admittime', 'marital_status', 'admission_location', 'race', 'admission_type', 'gender', 'age', 'time']].drop_duplicates(), 
            "admittime": admissions_df[['subject_id', 'hadm_id', 'admittime']].drop_duplicates(), 
            "patients": admissions_df[['subject_id']].drop_duplicates()
        }
    
    def preprocess_info_hospitalizations(
            self,
            admissions_df
            ):
        distinct_patients = len(admissions_df['subject_id'].drop_duplicates())
        admission_per_patients = admissions_df[['subject_id', 'hadm_id']].drop_duplicates().groupby('subject_id').count().reset_index()
        sum_admission_per_patients = admission_per_patients['hadm_id'].sum()
        mean_admission_per_patients = admission_per_patients['hadm_id'].mean()
        max_admission_per_patients = admission_per_patients['hadm_id'].max()
        min_admission_per_patients = admission_per_patients['hadm_id'].min()

        distinct_gender_df = len(admissions_df['gender'].drop_duplicates())
        distinct_age_df = len(admissions_df['age'].drop_duplicates())
        distinct_admission_type_df = len(admissions_df['admission_type'].drop_duplicates())
        distinct_admission_location_df = len(admissions_df['admission_location'].drop_duplicates())
        distinct_marital_status_df = len(admissions_df['marital_status'].drop_duplicates())
        distinct_race_df = len(admissions_df['race'].drop_duplicates())

        print(f"Distinct patients: {distinct_patients}")
        print(f"Distinct admission: {sum_admission_per_patients}")
        print(f"per Patient - Avg: {mean_admission_per_patients}")
        print(f"per Patient - Max: {max_admission_per_patients}")
        print(f"per Patient - Min: {min_admission_per_patients}")

        print(f"Distinct Gender: {distinct_gender_df}")
        print(f"Distinct Age: {distinct_age_df}")
        print(f"Distinct Admission type: {distinct_admission_type_df}")
        print(f"Distinct Admission location: {distinct_admission_location_df}")
        print(f"Distinct Marital status: {distinct_marital_status_df}")
        print(f"Distinct Race: {distinct_race_df}")
        print(f"Sum feature: {distinct_gender_df + distinct_age_df + distinct_admission_type_df + distinct_admission_location_df + distinct_marital_status_df + distinct_race_df}")
    
    def preprocess_labevents(
            self,
            labevents_df,
            d_labitems_df
            ):
        
        print("".center(100, "-"))
        print("".center(100, "-"))
        print(f" {self.dataset} ".center(100, "-"))
        print("".center(100, "-"))
        print(" Preprocessing labevents data in the DataFrame: labevents.csv ".center(100, "-"))
        print("".center(100, "-"))
        print(" Statistics Before Preprocessing ".center(100, "-"))
        if self.dataset == "MIMICIII":
            labevents_df = labevents_df.rename(columns={"row_id": "labevent_id"})

        self.preprocess_info_labevents(labevents_df)
        labevents_df = labevents_df.dropna(subset=['hadm_id'])
        labevents_df = labevents_df.dropna(subset=['valuenum'])
        labevents_df['hadm_id'] = labevents_df['hadm_id'].astype(int)
        labevents_df = labevents_df[['subject_id', 'hadm_id', 'itemid', 'charttime', 'valuenum']].drop_duplicates()
        d_labitems_df = pd.merge(d_labitems_df, labevents_df['itemid'].drop_duplicates())

        distinct_labevents = labevents_df[['subject_id', 'hadm_id', 'charttime']]
        distinct_labevents = distinct_labevents.drop_duplicates().groupby(['subject_id', 'hadm_id'], group_keys=True, sort=True).apply(lambda x: (x[['charttime']])[-64:])
        distinct_labevents = distinct_labevents.reset_index()[['subject_id', 'hadm_id', 'charttime']].drop_duplicates()
        labevents_df = pd.merge(distinct_labevents, labevents_df).drop_duplicates()
        d_labitems_df = pd.merge(d_labitems_df, labevents_df['itemid'].drop_duplicates())

        labevents_df['itemid'] = labevents_df['itemid'].astype(int)
        # print(labevents_df["itemid"].value_counts().reset_index().sort_values(by=['count'], ascending=False))
        top_k_code_labevents_df = labevents_df["itemid"].value_counts().reset_index().sort_values(by=['count'], ascending=False)[:self.top_k][["itemid"]]
        labevents_df = pd.merge(labevents_df, top_k_code_labevents_df, how='inner', on='itemid')
        d_labitems_df = pd.merge(d_labitems_df, top_k_code_labevents_df, how='inner', on='itemid')[['itemid']]
    
        
        print(" Statistics After Preprocessing ".center(100, "-"))
        self.preprocess_info_labevents(labevents_df)

        return {
            "labevents": labevents_df, 
            "d_labitems": d_labitems_df['itemid'].drop_duplicates()
        }
    
    def preprocess_info_labevents(
            self,
            labevents_df
            ):
        distinct_patients = len(labevents_df['subject_id'].drop_duplicates())
        distinct_cases = len(labevents_df[['subject_id', 'hadm_id']].drop_duplicates())
        distinct_itemids = len(labevents_df['itemid'].drop_duplicates())
        cases_per_patients = labevents_df[['subject_id', 'hadm_id']].drop_duplicates().groupby(['subject_id']).count().reset_index()
        charttime_per_cases = labevents_df[['subject_id', 'hadm_id', 'charttime']].drop_duplicates().groupby(['subject_id', 'hadm_id']).count().reset_index()
        paraclinicals_per_charttimes = labevents_df[['subject_id', 'hadm_id', 'charttime', 'itemid']].drop_duplicates().groupby(['subject_id', 'hadm_id', 'charttime']).count().reset_index()

        sum_admission_per_patients = cases_per_patients['hadm_id'].sum()
        mean_admission_per_patients = cases_per_patients['hadm_id'].mean()
        max_admission_per_patients = cases_per_patients['hadm_id'].max()
        min_admission_per_patients = cases_per_patients['hadm_id'].min()

        sum_admission_per_cases = charttime_per_cases['charttime'].sum()
        mean_admission_per_cases = charttime_per_cases['charttime'].mean()
        max_admission_per_cases = charttime_per_cases['charttime'].max()
        min_admission_per_cases = charttime_per_cases['charttime'].min()

        sum_admission_per_tests = paraclinicals_per_charttimes['itemid'].sum()
        mean_admission_per_tests = paraclinicals_per_charttimes['itemid'].mean()
        max_admission_per_tests = paraclinicals_per_charttimes['itemid'].max()
        min_admission_per_tests = paraclinicals_per_charttimes['itemid'].min()

        print(f"Distinct patients: {distinct_patients}")
        print(f"Distinct cases: {distinct_cases}")
        print(f"Distinct paraclinical: {distinct_itemids}")
        print(f"Cases - per Patient - Sum: {sum_admission_per_patients}")
        print(f"Cases - per Patient - Avg: {mean_admission_per_patients}")
        print(f"Cases - per Patient - Max: {max_admission_per_patients}")
        print(f"Cases - per Patient - Min: {min_admission_per_patients}")
        print(f"Charttime - per Case - Sum: {sum_admission_per_cases}")
        print(f"Charttime - per Case - Avg: {mean_admission_per_cases}")
        print(f"Charttime - per Case - Max: {max_admission_per_cases}")
        print(f"Charttime - per Case - Min: {min_admission_per_cases}")
        print(f"Paraclinicals - per Charttime - Sum: {sum_admission_per_tests}")
        print(f"Paraclinicals - per Charttime - Avg: {mean_admission_per_tests}")
        print(f"Paraclinicals - per Charttime - Max: {max_admission_per_tests}")
        print(f"Paraclinicals - per Charttime - Min: {min_admission_per_tests}")
        

    def preprocess_prescriptions(
            self,
            prescriptions_df
            ):
        """
        Preprocess the prescriptions DataFrame by cleaning and filtering data, converting dosage values to numeric, 
        and extracting high-frequency drug codes.

        Parameters:
            prescriptions_df (DataFrame): The input DataFrame containing prescription data.

        Returns:
            dict: A dictionary containing the processed prescriptions DataFrame and the extracted high-frequency drug codes DataFrame.
        """
        
        print("".center(100, "-"))
        print("".center(100, "-"))
        print(f" {self.dataset} ".center(100, "-"))
        print("".center(100, "-"))
        print(" Preprocessing prescription data in the DataFrame: prescriptions.csv ".center(100, "-"))
        print("".center(100, "-"))
        print(" Statistics Before Preprocessing ".center(100, "-"))
        prescriptions_df = prescriptions_df[['subject_id', 'hadm_id', 'ndc', 'dose_val_rx']].drop_duplicates()

        # Convert the 'dose_val_rx' column to numeric, coercing errors to NaN
        prescriptions_df['dose_val_rx'] = pd.to_numeric(prescriptions_df['dose_val_rx'], errors='coerce')
        # Drop rows where 'dose_val_rx' is NaN (ambiguous prescriptions)
        prescriptions_df = prescriptions_df.dropna(subset=['dose_val_rx'])
        prescriptions_df = prescriptions_df.dropna(subset=['ndc'])
    
        prescriptions_df['ndc'] = prescriptions_df['ndc'].astype(int)
        prescriptions_df['ndc'] = prescriptions_df['ndc'].astype(str).apply(lambda x: x.zfill(11))
        prescriptions_df = ndc2atc4(self.ndc_rxnorm_file, self.ndc2atc_file, prescriptions_df)
        atc, ddi_df = self.preprocessing_atc(prescriptions_df['atc'].drop_duplicates(), self.ddi_path, self.cid_atc_path)

        prescriptions_df = pd.merge(prescriptions_df, atc['atc'].drop_duplicates())
        
        
        df = prescriptions_df
        self.preprocess_info_codes(prescriptions_df, columns="atc")
        # Extract the top 1024 most frequent drug codes
        # print(prescriptions_df["atc"].value_counts().reset_index().sort_values(by=['count'], ascending=False))
        top_k_code_prescriptions_df = prescriptions_df["atc"].value_counts().reset_index().sort_values(by=['count'], ascending=False)[:self.top_k][['atc']]

        filtered_prescriptions_df = pd.merge(prescriptions_df, top_k_code_prescriptions_df, how='inner', on='atc').drop_duplicates()
        unique_drug_codes_df = top_k_code_prescriptions_df[['atc']].drop_duplicates()
    
        # print(len(top_k_code_prescriptions_df))
        # print(len(filtered_prescriptions_df))

        print(" Statistics After Preprocessing ".center(100, "-"))
        df = filtered_prescriptions_df
        self.preprocess_info_codes(df, columns="atc")

        ddi_df = ddi_df.rename(columns={"atc_1" : "atc"})
        ddi_df = pd.merge(ddi_df, filtered_prescriptions_df, how='inner')
        ddi_df = ddi_df.rename(columns={"atc" : "atc_1"})
        ddi_df = ddi_df.rename(columns={"atc_2" : "atc"})
        ddi_df = pd.merge(ddi_df, filtered_prescriptions_df, how='inner')
        ddi_df = ddi_df.rename(columns={"atc" : "atc_2"})

        return {
            "prescriptions": filtered_prescriptions_df,
            "d_prescriptions": unique_drug_codes_df,
            "d_ddi": ddi_df
        }

    def preprocess_procedures(
            self, 
            procedures_icd_df, 
            d_icd_procedures_df
            ):
        print("".center(100, "-"))
        print("".center(100, "-"))
        print(f" {self.dataset} ".center(100, "-"))
        print("".center(100, "-"))
        print(" Preprocessing procedures data in the DataFrame: procedures_icd.csv ".center(100, "-"))
        print("".center(100, "-"))
  
        if self.dataset == "MIMICIII":
            procedures_icd_df = procedures_icd_df.rename(columns={'icd9_code': 'icd_code'})
            d_icd_procedures_df = d_icd_procedures_df.rename(columns={'icd9_code': 'icd_code'})
            procedures_icd_df['icd_version'] = 9

        procedures_icd_df = procedures_icd_df[['subject_id', 'hadm_id', 'icd_code', 'icd_version']].drop_duplicates()
        
        print(" ICD 9 ".center(100, "-"))
        print(" Procedures ".center(100, "-"))
        self.preprocess_info_codes(procedures_icd_df[procedures_icd_df['icd_version']==9], columns="icd_code") 
        print(" ICD 10 ".center(100, "-"))
        print(" Procedures ".center(100, "-"))
        self.preprocess_info_codes(procedures_icd_df[procedures_icd_df['icd_version']==10], columns="icd_code") 

        if self.dataset == "MIMICIV":
            procedures_icd_df, d_icd_procedures_df = self.convert_icd_function(procedures_icd_df, d_icd_procedures_df, self.icd9toicd10pcsgem)
        elif self.dataset == "MIMICIII":
            procedures_icd_df = procedures_icd_df.rename(columns={'icd9_code': 'icd_code'})
            d_icd_procedures_df = d_icd_procedures_df.rename(columns={'icd9_code': 'icd_code'})

            procedures_icd_df = procedures_icd_df[['subject_id', 'hadm_id', 'icd_code']].drop_duplicates()
            procedures_icd_df = pd.merge(procedures_icd_df, d_icd_procedures_df).drop_duplicates()
            d_icd_procedures_df = pd.merge(d_icd_procedures_df, procedures_icd_df, how='inner')[d_icd_procedures_df.columns].drop_duplicates()
            procedures_icd_df['icd_code'] = procedures_icd_df['icd_code'].astype(str)
            d_icd_procedures_df['icd_code'] = d_icd_procedures_df['icd_code'].astype(str)

        procedures_icd_df["3_digit_icd_code"] = procedures_icd_df["icd_code"].str[:3]
        d_icd_procedures_df["3_digit_icd_code"] = d_icd_procedures_df["icd_code"].str[:3]
        # print(procedures_icd_df["3_digit_icd_code"].value_counts().reset_index().sort_values(by=['count'], ascending=False))
        top_k_code_procedures_df = procedures_icd_df["3_digit_icd_code"].value_counts().reset_index().sort_values(by=['count'], ascending=False)[:self.top_k][["3_digit_icd_code"]]
        procedures_icd_df = pd.merge(procedures_icd_df, top_k_code_procedures_df, how='inner').drop(columns=['3_digit_icd_code'])
        d_icd_procedures_df = pd.merge(d_icd_procedures_df, top_k_code_procedures_df, how='inner').drop(columns=['3_digit_icd_code'])
        
        print(" Statistics After Preprocessing ".center(100, "-"))
        print(" Procedures ".center(100, "-"))
        self.preprocess_info_codes(procedures_icd_df, columns="icd_code") 

        procedures_icd_df['icd_code'] = procedures_icd_df['icd_code'].str[:3]
        d_icd_procedures_df['icd_code'] = d_icd_procedures_df['icd_code'].str[:3]
        procedures_icd_df = procedures_icd_df.drop_duplicates()
        d_icd_procedures_df = d_icd_procedures_df.drop_duplicates()


        return {
            "procedures_icd": procedures_icd_df.drop_duplicates(), 
            "d_icd_procedures": d_icd_procedures_df["icd_code"].drop_duplicates()
        }

    def convert_icd_function(self, diagnosed_df, distinct_df, convert_df):
        # Merge to find icd_version in diagnosed_df
        diagnosed_df = pd.merge(diagnosed_df, distinct_df)

        # Split to icd9 dataframe and icd 10 dataframe
        diagnosed_icd_9_df = diagnosed_df[diagnosed_df['icd_version']==9][['subject_id', 'hadm_id', 'icd_code']].drop_duplicates()
        diagnosed_icd_10_df = diagnosed_df[diagnosed_df['icd_version']==10][['subject_id', 'hadm_id', 'icd_code']].drop_duplicates()

        distinct_icd_9_df = distinct_df[distinct_df['icd_version']==9]
        distinct_icd_10_df = distinct_df[distinct_df['icd_version']==10]

        # Change name of column to match with convert_df
        diagnosed_icd_9_df = diagnosed_icd_9_df.rename(columns={'icd_code': 'icd9cm'})
        distinct_icd_9_df = distinct_icd_9_df.rename(columns={'icd_code': 'icd9cm'})

        # Delete all icd 9 that have more 1 icd 10
        one_icd9_to_icd10_df = convert_df[['icd9cm', 'icd10']].drop_duplicates()
        one_icd9_to_icd10_df = one_icd9_to_icd10_df.groupby(['icd9cm']).count().reset_index()
        one_icd9_to_icd10_df = one_icd9_to_icd10_df[one_icd9_to_icd10_df['icd10']==1]

        convert_df = pd.merge(convert_df, one_icd9_to_icd10_df[['icd9cm']], how='inner')
        # Match convert_df
        distinct_icd_9_df = pd.merge(distinct_icd_9_df, convert_df, how='inner', on=['icd9cm'])[['icd9cm', 'icd10cm', 'icd9', 'icd10']].drop_duplicates()
        
        # Filter co-occurance code
        # distinct_icd_9_df = pd.merge(convert_df['icd9cm'], distinct_icd_9_df[['icd9cm', 'icd10cm']].drop_duplicates())

        # Delete "NoD" code
        distinct_icd_9_df = distinct_icd_9_df[distinct_icd_9_df['icd10cm']!='NoD']

        # Re-generate icd 9 dataframe
        diagnosed_icd_9_df = pd.merge(diagnosed_icd_9_df, distinct_icd_9_df, how='inner', on=['icd9cm'])
        diagnosed_icd_9_df = diagnosed_icd_9_df[['subject_id', 'hadm_id', 'icd10cm']].rename(columns={'icd10cm': 'icd_code'})
        distinct_icd_9_df = distinct_icd_9_df.rename(columns={'icd9cm': 'icd_code'})

        distinct_df = pd.concat([distinct_icd_9_df, distinct_icd_10_df], ignore_index=True)[['icd_code']].drop_duplicates()
        diagnosed_df = pd.concat([diagnosed_icd_9_df, diagnosed_icd_10_df], ignore_index=True).sort_values(['subject_id', 'hadm_id']).drop_duplicates()
        distinct_df = pd.merge(distinct_df, diagnosed_df)[distinct_df.columns].drop_duplicates()
        diagnosed_df = pd.merge(distinct_df, diagnosed_df)[diagnosed_df.columns].drop_duplicates()

        return diagnosed_df, distinct_df
    
    def preprocess_diagnoses(
            self, 
            diagnoses_icd_df, 
            d_icd_diagnoses_df
            ):
        print("".center(100, "-"))
        print("".center(100, "-"))
        print(f" {self.dataset} ".center(100, "-"))
        print("".center(100, "-"))
        print(" Preprocessing diagnoses data in the DataFrame: diagnoses_icd.csv ".center(100, "-"))
        print("".center(100, "-"))
  
        if self.dataset == "MIMICIII":
            diagnoses_icd_df = diagnoses_icd_df.rename(columns={'icd9_code': 'icd_code'})
            d_icd_diagnoses_df = d_icd_diagnoses_df.rename(columns={'icd9_code': 'icd_code'})
            diagnoses_icd_df['icd_version'] = 9
            diagnoses_icd_df['icd_code'] = diagnoses_icd_df['icd_code'].astype(str)
            d_icd_diagnoses_df['icd_code'] = d_icd_diagnoses_df['icd_code'].astype(str)

        diagnoses_icd_df = diagnoses_icd_df[['subject_id', 'hadm_id', 'icd_code', 'icd_version']].drop_duplicates()
        # diagnoses_icd_df["icd_code"] = diagnoses_icd_df["icd_code"].astype(str)
        print(" ICD 9 ".center(100, "-"))
        df = diagnoses_icd_df[diagnoses_icd_df['icd_version']==9]
        self.preprocess_info_codes(df, columns="icd_code")
        print(" ICD 10 ".center(100, "-"))
        df = diagnoses_icd_df[diagnoses_icd_df['icd_version']==10]
        self.preprocess_info_codes(df, columns="icd_code")

        if self.dataset == "MIMICIV":
            diagnoses_icd_df, d_icd_diagnoses_df = self.convert_icd_function(diagnoses_icd_df, d_icd_diagnoses_df, self.icd9toicd10cmgem)
        elif self.dataset == "MIMICIII":
            diagnoses_icd_df = diagnoses_icd_df.rename(columns={'icd9_code': 'icd_code'})
            d_icd_diagnoses_df = d_icd_diagnoses_df.rename(columns={'icd9_code': 'icd_code'})

            diagnoses_icd_df = diagnoses_icd_df[['subject_id', 'hadm_id', 'icd_code']].drop_duplicates()
            diagnoses_icd_df = pd.merge(diagnoses_icd_df, d_icd_diagnoses_df)

        d_icd_diagnoses_df = pd.merge(d_icd_diagnoses_df, diagnoses_icd_df, how='inner')[d_icd_diagnoses_df.columns].drop_duplicates()
        d_icd_diagnoses_df['1_digits_icd_code'] = d_icd_diagnoses_df['icd_code'].str[:1]
        d_icd_diagnoses_df['2_digits_icd_code'] = d_icd_diagnoses_df['icd_code'].str[:2]
        d_icd_diagnoses_df['3_digits_icd_code'] = d_icd_diagnoses_df['icd_code'].str[:3]
        diagnoses_icd_df['1_digits_icd_code'] = diagnoses_icd_df['icd_code'].str[:1]
        diagnoses_icd_df['2_digits_icd_code'] = diagnoses_icd_df['icd_code'].str[:2]
        diagnoses_icd_df['3_digits_icd_code'] = diagnoses_icd_df['icd_code'].str[:3] 
        

        clinical_df, post_paraclinical_df                       = self.retrieve(diagnoses_icd_df, "clinical")
        d_clinical_df, d_post_paraclinical_df                   = self.retrieve(d_icd_diagnoses_df, "clinical")
        resistance_to_antimicrobial_drugs_df, clinical_df       = self.retrieve(clinical_df, "resistance_to_antimicrobial_drugs")
        d_resistance_to_antimicrobial_drugs_df, d_clinical_df   = self.retrieve(d_clinical_df, "resistance_to_antimicrobial_drugs")
        body_mass_index_df, clinical_df                         = self.retrieve(clinical_df, "body_mass_index")
        d_body_mass_index_df, d_clinical_df                     = self.retrieve(d_clinical_df, "body_mass_index")
        long_term_current_drug_therapy_df, clinical_df          = self.retrieve(clinical_df, "long_term_current_drug_therapy")
        d_long_term_current_drug_therapy_df, d_clinical_df      = self.retrieve(d_clinical_df, "long_term_current_drug_therapy")
        allergy_status_to_drugs_df, clinical_df                 = self.retrieve(clinical_df, "allergy_status_to_drugs")
        d_allergy_status_to_drugs_df, d_clinical_df             = self.retrieve(d_clinical_df, "allergy_status_to_drugs")


        clinical_df                                             = clinical_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates()
        d_clinical_df                                           = d_clinical_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates(['icd_code'])
        resistance_to_antimicrobial_drugs_df                    = resistance_to_antimicrobial_drugs_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates()
        d_resistance_to_antimicrobial_drugs_df                  = d_resistance_to_antimicrobial_drugs_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates(['icd_code'])
        body_mass_index_df                                      = body_mass_index_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates()
        d_body_mass_index_df                                    = d_body_mass_index_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates(['icd_code'])
        long_term_current_drug_therapy_df                       = long_term_current_drug_therapy_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates()
        d_long_term_current_drug_therapy_df                     = d_long_term_current_drug_therapy_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates(['icd_code'])
        allergy_status_to_drugs_df                              = allergy_status_to_drugs_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates()
        d_allergy_status_to_drugs_df                            = d_allergy_status_to_drugs_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates(['icd_code'])
        internal_medicine_history_df                            = diagnoses_icd_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates()
        d_internal_medicine_history                             = d_icd_diagnoses_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates(['icd_code'])
        post_paraclinical_df                                    = post_paraclinical_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates()
        d_post_paraclinical_df                                  = d_post_paraclinical_df.drop(columns=['3_digits_icd_code', '2_digits_icd_code', '1_digits_icd_code']).drop_duplicates(['icd_code'])

        if self.triplet == True:
            clinical_df["3_digit_icd_code"] = clinical_df["icd_code"].str[:3]
            d_clinical_df["3_digit_icd_code"] = d_clinical_df["icd_code"].str[:3]
            top_k_code_clinical_df = clinical_df["3_digit_icd_code"].value_counts().reset_index().sort_values(by=['count'], ascending=False)[:self.top_k][["3_digit_icd_code"]]
            clinical_df = pd.merge(clinical_df, top_k_code_clinical_df, how='inner', on='3_digit_icd_code')
            d_clinical_df = pd.merge(d_clinical_df, top_k_code_clinical_df, how='inner', on='3_digit_icd_code')
            
            internal_medicine_history_df["3_digit_icd_code"] = internal_medicine_history_df["icd_code"].str[:3]
            d_internal_medicine_history["3_digit_icd_code"] = d_internal_medicine_history["icd_code"].str[:3]
            top_k_code_internal_medicine_history_df = internal_medicine_history_df["3_digit_icd_code"].value_counts().reset_index().sort_values(by=['count'], ascending=False)[:self.top_k][["3_digit_icd_code"]]
            internal_medicine_history_df = pd.merge(internal_medicine_history_df, top_k_code_internal_medicine_history_df, how='inner', on='3_digit_icd_code')
            d_internal_medicine_history = pd.merge(d_internal_medicine_history, top_k_code_internal_medicine_history_df, how='inner', on='3_digit_icd_code')
            
            post_paraclinical_df["3_digit_icd_code"] = post_paraclinical_df["icd_code"].str[:3]
            d_post_paraclinical_df["3_digit_icd_code"] = d_post_paraclinical_df["icd_code"].str[:3]
            top_k_code_post_paraclinical_df = post_paraclinical_df["3_digit_icd_code"].value_counts().reset_index().sort_values(by=['count'], ascending=False)[:self.top_k][["3_digit_icd_code"]]
            post_paraclinical_df = pd.merge(post_paraclinical_df, top_k_code_post_paraclinical_df, how='inner', on='3_digit_icd_code')
            d_post_paraclinical_df = pd.merge(d_post_paraclinical_df, top_k_code_post_paraclinical_df, how='inner', on='3_digit_icd_code')
        else:
            clinical_df["3_digit_icd_code"] = clinical_df["icd_code"].str[:3]
            d_clinical_df["3_digit_icd_code"] = d_clinical_df["icd_code"].str[:3]
            top_k_code_clinical_df = clinical_df["icd_code"].value_counts().reset_index().sort_values(by=['count'], ascending=False)[:self.top_k][["icd_code"]]
            clinical_df = pd.merge(clinical_df, top_k_code_clinical_df, how='inner', on='icd_code')
            d_clinical_df = pd.merge(d_clinical_df, top_k_code_clinical_df, how='inner', on='icd_code')
            
            internal_medicine_history_df["3_digit_icd_code"] = internal_medicine_history_df["icd_code"].str[:3]
            d_internal_medicine_history["3_digit_icd_code"] = d_internal_medicine_history["icd_code"].str[:3]
            top_k_code_internal_medicine_history_df = internal_medicine_history_df["icd_code"].value_counts().reset_index().sort_values(by=['count'], ascending=False)[:self.top_k][["icd_code"]]
            internal_medicine_history_df = pd.merge(internal_medicine_history_df, top_k_code_internal_medicine_history_df, how='inner', on='icd_code')
            d_internal_medicine_history = pd.merge(d_internal_medicine_history, top_k_code_internal_medicine_history_df, how='inner', on='icd_code')
            
            post_paraclinical_df["3_digit_icd_code"] = post_paraclinical_df["icd_code"].str[:3]
            d_post_paraclinical_df["3_digit_icd_code"] = d_post_paraclinical_df["icd_code"].str[:3]
            top_k_code_post_paraclinical_df = post_paraclinical_df["icd_code"].value_counts().reset_index().sort_values(by=['count'], ascending=False)[:self.top_k][["icd_code"]]
            post_paraclinical_df = pd.merge(post_paraclinical_df, top_k_code_post_paraclinical_df, how='inner', on='icd_code')
            d_post_paraclinical_df = pd.merge(d_post_paraclinical_df, top_k_code_post_paraclinical_df, how='inner', on='icd_code')
        
        print(" Statistics After Preprocessing ".center(100, "-"))
        print(" Diagnosis Label ".center(100, "-"))
        self.preprocess_info_codes(post_paraclinical_df, columns="icd_code")
        print(" Internal Medicine History ".center(100, "-"))
        self.preprocess_info_codes(internal_medicine_history_df, columns="icd_code")
        print(" Clinical ".center(100, "-"))
        self.preprocess_info_codes(clinical_df, columns="icd_code")
        print(" Drug Resistance ".center(100, "-"))
        self.preprocess_info_codes(resistance_to_antimicrobial_drugs_df, columns="icd_code")
        print(" Body Mass Index (BMI) ".center(100, "-"))
        self.preprocess_info_codes(body_mass_index_df, columns="icd_code")
        print(" Long-term Drug Use ".center(100, "-"))
        self.preprocess_info_codes(long_term_current_drug_therapy_df, columns="icd_code")
        print(" Drug Allergy ".center(100, "-"))
        self.preprocess_info_codes(allergy_status_to_drugs_df, columns="icd_code")
        
        if self.triplet == True:
            d_internal_medicine_history = d_internal_medicine_history.drop(columns=['icd_code'])
            d_internal_medicine_history = d_internal_medicine_history.rename(columns={"3_digit_icd_code": "icd_code"})
            internal_medicine_history_df = internal_medicine_history_df.drop(columns=['icd_code'])
            internal_medicine_history_df = internal_medicine_history_df.rename(columns={"3_digit_icd_code": "icd_code"})
            d_clinical_df = d_clinical_df.drop(columns=['icd_code'])
            d_clinical_df = d_clinical_df.rename(columns={"3_digit_icd_code": "icd_code"})
            clinical_df = clinical_df.drop(columns=['icd_code'])
            clinical_df = clinical_df.rename(columns={"3_digit_icd_code": "icd_code"})
            d_post_paraclinical_df = d_post_paraclinical_df.drop(columns=['icd_code'])
            d_post_paraclinical_df = d_post_paraclinical_df.rename(columns={"3_digit_icd_code": "icd_code"})
            post_paraclinical_df = post_paraclinical_df.drop(columns=['icd_code'])
            post_paraclinical_df = post_paraclinical_df.rename(columns={"3_digit_icd_code": "icd_code"})
        else:
            
            d_internal_medicine_history = d_internal_medicine_history.drop(columns=['3_digit_icd_code'])
            internal_medicine_history_df = internal_medicine_history_df.drop(columns=['3_digit_icd_code'])
            d_clinical_df = d_clinical_df.drop(columns=['3_digit_icd_code'])
            clinical_df = clinical_df.drop(columns=['3_digit_icd_code'])
            d_post_paraclinical_df = d_post_paraclinical_df.drop(columns=['3_digit_icd_code'])
            post_paraclinical_df = post_paraclinical_df.drop(columns=['3_digit_icd_code'])

        clinical_df['icd_code'] = clinical_df['icd_code'].astype(str)
        d_clinical_df['icd_code'] = d_clinical_df['icd_code'].astype(str)
        internal_medicine_history_df['icd_code'] = internal_medicine_history_df['icd_code'].astype(str)
        d_internal_medicine_history['icd_code'] = d_internal_medicine_history['icd_code'].astype(str)
        post_paraclinical_df['icd_code'] = post_paraclinical_df['icd_code'].astype(str)
        d_post_paraclinical_df['icd_code'] = d_post_paraclinical_df['icd_code'].astype(str)
        clinical_df['icd_code'] = clinical_df['icd_code'].apply(lambda x: x.zfill(3))
        d_clinical_df['icd_code'] = d_clinical_df['icd_code'].apply(lambda x: x.zfill(3))
        internal_medicine_history_df['icd_code'] = internal_medicine_history_df['icd_code'].apply(lambda x: x.zfill(3))
        d_internal_medicine_history['icd_code'] = d_internal_medicine_history['icd_code'].apply(lambda x: x.zfill(3))
        post_paraclinical_df['icd_code'] = post_paraclinical_df['icd_code'].apply(lambda x: x.zfill(3))
        d_post_paraclinical_df['icd_code'] = d_post_paraclinical_df['icd_code'].apply(lambda x: x.zfill(3))

        # category_internal_medicine_history = retrieve_categories(internal_medicine_history_df, self.categories)
        # d_category_internal_medicine_historyretrieve_categories = retrieve_categories(d_internal_medicine_history, self.categories)
        # category_ablation_internal_medicine_history = retrieve_categories(post_paraclinical_df, self.categories)
        # d_category_ablation_internal_medicine_historyretrieve_categories = retrieve_categories(d_post_paraclinical_df, self.categories)
        # print(" Category Diagnosis ".center(100, "-"))
        # self.preprocess_info_codes(category_internal_medicine_history, columns="icd_code")
        # print(" Category Ablation Diagnosis ".center(100, "-"))
        # self.preprocess_info_codes(category_ablation_internal_medicine_history, columns="icd_code")

        return {
            "clinical": clinical_df.drop_duplicates(),
            "d_clinical": d_clinical_df["icd_code"].drop_duplicates(),
            "resistance_to_antimicrobial_drugs": resistance_to_antimicrobial_drugs_df.drop_duplicates(),
            "d_resistance_to_antimicrobial_drugs": d_resistance_to_antimicrobial_drugs_df["icd_code"].drop_duplicates(),
            "body_mass_index": body_mass_index_df.drop_duplicates(),
            "d_body_mass_index": d_body_mass_index_df["icd_code"].drop_duplicates(),
            "long_term_current_drug_therapy": long_term_current_drug_therapy_df.drop_duplicates(),
            "d_long_term_current_drug_therapy": d_long_term_current_drug_therapy_df["icd_code"].drop_duplicates(),
            "allergy_status_to_drugs": allergy_status_to_drugs_df.drop_duplicates(),
            "d_allergy_status_to_drugs": d_allergy_status_to_drugs_df["icd_code"].drop_duplicates(),
            "internal_medicine_history": internal_medicine_history_df.drop_duplicates(),
            "d_internal_medicine_history": d_internal_medicine_history["icd_code"].drop_duplicates(),
            "ablation_diagnoses": post_paraclinical_df.drop_duplicates(),
            "d_ablation_diagnoses": d_post_paraclinical_df["icd_code"].drop_duplicates(),
            # "category_internal_medicine_history": category_internal_medicine_history.drop_duplicates(),
            # "d_category_internal_medicine_history": d_category_internal_medicine_historyretrieve_categories["icd_code"].drop_duplicates(),
            # "ablation_category_diagnoses": category_ablation_internal_medicine_history.drop_duplicates(),
            # "d_ablation_category_diagnoses": d_category_ablation_internal_medicine_historyretrieve_categories["icd_code"].drop_duplicates(),
        }

    def preprocessing_atc(self, atc_ehr_df, ddi_path, cid_atc_path):
        def clean_df(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Analyze the data to find the maximum number of fields
            max_fields = max([len(line.split(',')) for line in lines])

            # Process each line to ensure they have the same number of fields
            processed_lines = []
            for line in lines:
                fields = line.strip().split(',')
                if len(fields) < max_fields:
                    fields.extend([''] * (max_fields - len(fields)))  # Fill missing fields with empty strings
                processed_lines.append(fields)

            # Create a DataFrame from the processed data
            df = pd.DataFrame(processed_lines)
            return df
        
        def ddi(ddi_file, clean_atc_df):
            ddi_df = pd.read_csv(ddi_file)
            sti_1_ddi_df = ddi_df['STITCH 1'].reset_index().drop_duplicates()
            sti_1_ddi_df = sti_1_ddi_df.rename(columns={"STITCH 1": "drug"})
            sti_2_ddi_df = ddi_df['STITCH 2'].reset_index().drop_duplicates()
            sti_2_ddi_df = sti_2_ddi_df.rename(columns={"STITCH 1": "drug"})
            sti_1_ddi_df = pd.merge(sti_1_ddi_df, clean_atc_df)[['drug', 'atc']].drop_duplicates()
            sti_2_ddi_df = pd.merge(sti_1_ddi_df, clean_atc_df)[['drug', 'atc']].drop_duplicates()
            sti_1_ddi_df = sti_1_ddi_df.rename(columns={"drug": "STITCH 1", "atc": "atc_1"})
            sti_2_ddi_df = sti_2_ddi_df.rename(columns={"drug": "STITCH 2", "atc": "atc_2"})
            ddi_df = pd.merge(ddi_df, sti_1_ddi_df)
            ddi_df = pd.merge(ddi_df, sti_2_ddi_df)
            ddi_df = ddi_df[['atc_1', 'atc_2']].drop_duplicates().reset_index()
            return ddi_df
        
        atc_df = clean_df(cid_atc_path)
        dict = {
            "atc": [],
            "drug": []
        }
        for index, row in atc_df.iterrows():
            for column in atc_df.columns:
                if column != 0:
                    if len(row[column]) > 0:
                        dict['atc'].append(row[column])
                        dict['drug'].append(row[0])
        clean_df = pd.DataFrame(dict)
        clean_df['atc'] = clean_df['atc'].str[:5]
        clean_df = clean_df.dropna()
        clean_atc_df = clean_df.drop_duplicates(subset=['atc'])
        clean_atc_df = pd.merge(clean_atc_df, atc_ehr_df.drop_duplicates())
        ddi_df = ddi(ddi_path, clean_atc_df)[['atc_1', 'atc_2']].drop_duplicates()
        return clean_atc_df, ddi_df

    def preprocess_codes(self, df, columns):
        total_diagnosed_codes = len(df)
        distinct_codes = len(df[columns].drop_duplicates())

        per_Patient = df[['subject_id', 'counts']].groupby(['subject_id']).sum().reset_index()
        per_Patient_avg_codes = per_Patient['counts'].mean()
        per_Patient_max_codes = per_Patient['counts'].max()
        per_Patient_min_codes = per_Patient['counts'].min()
        
        per_Case = df[['subject_id', 'hadm_id', 'counts']].groupby(['subject_id', 'hadm_id']).sum().reset_index()
        per_Case_avg_codes = per_Case['counts'].mean()
        per_Case_max_codes = per_Case['counts'].max()
        per_Case_min_codes = per_Case['counts'].min()

        print(f"Distinct codes: {distinct_codes}")
        print(f"Total diagnosed codes: {total_diagnosed_codes}")
        print(f"per Patient - Avg. codes: {per_Patient_avg_codes}")
        print(f"per Patient - Max. codes: {per_Patient_max_codes}")
        print(f"per Patient - Min. codes: {per_Patient_min_codes}")
        print(f"per Case - Avg. codes: {per_Case_avg_codes}")
        print(f"per Case - Max. codes: {per_Case_max_codes}")
        print(f"per Case - Min. codes: {per_Case_min_codes}")

    def preprocess_detail_codes(self, df, columns):
        df = df.copy()
        df['counts'] = 1
        column_list = ['subject_id', 'hadm_id', 'counts']
        column_list.append(columns)
        df = df[column_list].drop_duplicates()

        self.preprocess_codes(df, columns)


    def preprocess_triplet_codes(self, df, columns):
        df = df.copy()
        df['counts'] = 1
        df[columns] = df[columns].astype(str)
        df[columns] = df[columns].str[:3]
        column_list = ['subject_id', 'hadm_id', 'counts']
        column_list.append(columns)
        # print(column_list)
        df = df[column_list].drop_duplicates()
        self.preprocess_codes(df, columns)

    def preprocess_info_codes(self, df, columns):
        print(" Detail Code ".center(100, "-"))
        self.preprocess_detail_codes(df, columns=columns)
        print(" Triplet Code ".center(100, "-"))

        self.preprocess_triplet_codes(df, columns=columns)
        print("".center(100, "-"))


    def retrieve(self, df, attribute):
        return df[df["1_digits_icd_code"].isin(self.retrieve_dict[attribute]["1_digits_icd_code"]) | df["2_digits_icd_code"].isin(self.retrieve_dict[attribute]["2_digits_icd_code"]) | df["3_digits_icd_code"].isin(self.retrieve_dict[attribute]["3_digits_icd_code"])], \
            df[~df["1_digits_icd_code"].isin(self.retrieve_dict[attribute]["1_digits_icd_code"]) & ~df["2_digits_icd_code"].isin(self.retrieve_dict[attribute]["2_digits_icd_code"]) & ~df["3_digits_icd_code"].isin(self.retrieve_dict[attribute]["3_digits_icd_code"])]

    def retrieve_categories(self, label_diagnosis_df):
        label_diagnosis_df['category'] = label_diagnosis_df.ap

        
def select_sample(df):
    # Xác định các cột đặc trưng cần bao quát
    feature_columns = ['marital_status', 'admission_location', 'race', 'admission_type', 'gender', 'age']
    # Tạo một dictionary để lưu trữ tất cả các giá trị duy nhất cho mỗi cột đặc trưng
    unique_values = {col: set(df[col]) for col in feature_columns}
    # Tạo một danh sách các giá trị cần được bao quát
    values_to_cover = {col: set(values) for col, values in unique_values.items()}
    print(f"Sum Feature: {np.sum([len(values_to_cover[col]) for col in values_to_cover])}")
    
    # Khởi tạo một danh sách các hàng đã chọn
    selected_rows = []

    for index, row in df.iterrows():
        check = 0
        for col, value in row[feature_columns].items():
            for v in values_to_cover[col]:
                if v == value:
                    check+=1
                    values_to_cover[col].remove(v)
                    break
        if check > 0:
            selected_rows.append(index)
        if np.sum([len(values_to_cover[col]) for col in values_to_cover.keys()]) == 0:
            break
    # Lấy dataframe chỉ chứa các hàng đã chọn
    result_df = df.loc[selected_rows]
    return {
        "d_patient": result_df
    }

def padding_medical_history(input_tensor, dim=64):
    if dim <= input_tensor.size(0):
        input_tensor = input_tensor[-dim:]
        return input_tensor
    if len(input_tensor.shape) == 2:
        padding = torch.zeros((dim-input_tensor.size(0), input_tensor.size(1)))
    elif len(input_tensor.shape) == 1:
        padding = torch.zeros((dim-input_tensor.size(0)), dtype=torch.float32)
    input_tensor = torch.cat([padding, input_tensor], dim=0)
    return input_tensor


def convert(data, folder):
    print(f"{folder}")
    dict = {}
    for key in data[0].keys():
        dict[key] = []
    data_loader = DataLoader(data, batch_size=48, num_workers=24)
    for i, sample in enumerate(data_loader):
        print(f"{i}")

        for key in sample.keys():
            dict[key].append(sample[key])
    for key in dict.keys():
        dict[key] = np.concatenate(dict[key])
        np.savez_compressed(f"{folder}/{key}.npz", arr=dict[key])
    return dict

def save_json(data, folder_path):
    for k, v in data.items():
        list_numbers = v.dict.columns.to_list()
        dict_numbers = {index: value for index, value in enumerate(list_numbers)}
        file_path = f"{folder_path}/{k}.json"
        with open(file_path, 'w') as file:
            json.dump(dict_numbers, file)

def read_csv_gz_function(path):
    file_size = os.path.getsize(path)
    file_size_MB = file_size / (1024 * 1024)

    print(f"Read file {path}")
    print(f'File size: {file_size_MB:.2f} MB')

    if file_size_MB > 100: 
        chunk_size = 10000 

        chunk_list = []
        for chunk in pd.read_csv(path, chunksize=chunk_size, compression='gzip'):
            chunk_list.append(chunk)
        df = pd.concat(chunk_list)
        df.columns = df.columns.str.lower()
        return df 
    else:
        df = pd.read_csv(path, compression='gzip')
        df.columns = df.columns.str.lower()
        return df

def load_dataframe_from_url(url):
    url='https://drive.google.com/uc?id=' + url.split('/')[-2]
    return pd.read_csv(url)


def mkdir(path):
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("The new directory is created!")


def ndc2atc4(ndc_rxnorm_file, ndc2atc_file, med_pd):
    with open(ndc_rxnorm_file, 'r') as f:
        ndc2rxnorm = eval(f.read())
    # return ndc2rxnorm
    med_pd['rxcui'] = med_pd['ndc'].map(ndc2rxnorm)
    med_pd.dropna(inplace=True)

    rxnorm2atc = pd.read_csv(ndc2atc_file)
    rxnorm2atc.columns = rxnorm2atc.columns.str.lower()
    rxnorm2atc = rxnorm2atc.drop(columns=['year','month','ndc'])
    rxnorm2atc.drop_duplicates(subset=['rxcui'], inplace=True)
    med_pd.drop(index = med_pd[med_pd['rxcui'].isin([''])].index, axis=0, inplace=True)
    
    med_pd['rxcui'] = med_pd['rxcui'].astype('int64')
    med_pd = med_pd.reset_index(drop=True)
    med_pd = med_pd.merge(rxnorm2atc, on=['rxcui'])
    med_pd.drop(columns=['ndc', 'rxcui'], inplace=True)
    med_pd = med_pd.rename(columns={'atc4':'atc'}) 
    # med_pd['ndc'] = med_pd['ndc'].map(lambda x: x[:4])
    med_pd = med_pd.drop_duplicates()    
    med_pd = med_pd.reset_index(drop=True)
    return med_pd

def generate_categories_df(categories):
    # Create an empty list to store rows
    rows = []

    # Iterate over each category and its codes
    for major_category, codes in categories.items():
        # Combine codes into strings
        # icd_1_digits = ', '.join(codes['1_digits_icd_code'])
        # icd_2_digits = ', '.join(codes['2_digits_icd_code'])
        # icd_3_digits = ', '.join(codes['3_digits_icd_code'])
        if len(codes['1_digits_icd_code']) > 0:
            for code in codes['1_digits_icd_code']:
                # Append a dictionary representing each row
                rows.append({
                    'Major Category': major_category,
                    '1_digits_icd_code': code,
                    '2_digits_icd_code': '',
                    '3_digits_icd_code': ''
                })
        if len(codes['2_digits_icd_code']) > 0:
            for code in codes['2_digits_icd_code']:
                # Append a dictionary representing each row
                rows.append({
                    'Major Category': major_category,
                    '1_digits_icd_code': '',
                    '2_digits_icd_code': code,
                    '3_digits_icd_code': ''
                })
        if len(codes['3_digits_icd_code']) > 0:
            for code in codes['3_digits_icd_code']:
                # Append a dictionary representing each row
                rows.append({
                    'Major Category': major_category,
                    'icd_code': '',
                    '2_digits_icd_code': '',
                    '3_digits_icd_code': code
                })

    # Create DataFrame from the list of rows
    df = pd.DataFrame(rows)
    return df

def retrieve_categories(ablation_diagnoses_df, df):
    label_df = ablation_diagnoses_df.copy()
    label_df['1_digits_icd_code'] = label_df['icd_code'].str[:1]
    df_1 = pd.merge(label_df, df, how='inner', on=['1_digits_icd_code'])[['icd_code', 'Major Category']]
    label_df = ablation_diagnoses_df.copy()
    label_df['2_digits_icd_code'] = label_df['icd_code'].str[:2]
    df_2 = pd.merge(label_df, df, how='inner', on=['2_digits_icd_code'])[['icd_code', 'Major Category']]
    label_df = ablation_diagnoses_df.copy()
    label_df['3_digits_icd_code'] = label_df['icd_code'].str[:3]
    df_3 = pd.merge(label_df, df, how='inner', on=['3_digits_icd_code'])[['icd_code', 'Major Category']]
    df = pd.concat((df_1, df_2, df_3))
    df = pd.merge(ablation_diagnoses_df, df).drop(columns=['icd_code']).drop_duplicates()
    df = df.rename(columns={"Major Category": "icd_code"})
    return df


def convert(data, folder, batch_size, num_workers):
    print(f"{folder}")
    dict = {}
    for key in data[0].keys():
        dict[key] = []
    data_loader = DataLoader(data, batch_size=batch_size, num_workers=num_workers, pin_memory=True, drop_last=False)
    data_iterator = tqdm(data_loader, desc=f"Transfer to numpy step: ")
    for sample in data_iterator:
        for key in sample.keys():
            dict[key].append(sample[key])
        sample  = None
        del sample
    for key in dict.keys():
        dict[key] = np.concatenate(dict[key])
        np.savez_compressed(f"{folder}/{key}.npz", arr=dict[key])
    return dict
def generate_weight(data, folder_path):
    def save_weight(data, path):
        np.savez_compressed(path, arr=np.sum(data, axis=0))

    for file in data.keys():
        if file.startswith("label"):
            path = f"{folder_path}/weighted_{file}.npz"
            save_weight(data[file], path)

def mkdir(path):
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("The new directory is created!")
class ADJ_Dataset(Dataset):
    def __init__(
        self,
        numpy_folder,
        ):
        train_ehr_df = np.load(f"{numpy_folder}/train/internal_medicine_history.npz")['arr']
        valid_ehr_df = np.load(f"{numpy_folder}/valid/internal_medicine_history.npz")['arr']
        test_ehr_df = np.load(f"{numpy_folder}/test/internal_medicine_history.npz")['arr']
        ehr = np.concatenate((train_ehr_df, valid_ehr_df, test_ehr_df))
        train_ehr_df = None
        valid_ehr_df = None
        test_ehr_df = None
        self.ehr = ehr.reshape( ehr.shape[0] * ehr.shape[1] , -1, 1)
        self.ehr_len = len(self.ehr)
        
    def last_shape(self):
        return self.ehr.shape[-2]
    
    def __len__(self):
        return self.ehr_len
    
    def __getitem__(self, index):
        return self.ehr[index]
    
def generate_ehr_adj(numpy_folder, batch_size, num_workers):
    dataset =  ADJ_Dataset(numpy_folder=numpy_folder)
    data = DataLoader(
            dataset = dataset, 
            batch_size=batch_size,
            num_workers=num_workers,
            drop_last=False,
            pin_memory=True
        )
    matrix = np.zeros((dataset.last_shape(), dataset.last_shape()))
    for sample in tqdm(data):
        # print(sample.shape)
        matrix += np.sum(np.transpose(sample.numpy(), (0,2,1)) *sample.numpy(), 0)
    return matrix

class Tokenizer():
    def __init__(self, df):
        if 'icd_code' in df.columns:
            self.label = 'icd_code'
        else:
            self.label = 'atc'
        self.dict = self.build_tokenizer(df)
        self.df = df
        self.len_dict = len(self.dict.columns)

    def keys(self):
        return self.dict.columns
    
    def build_tokenizer(self, df):
        dummies = pd.get_dummies(df[self.label])
        return dummies

    def __len__(self):
        return self.len_dict
        
    def __call__(self, icd_code):
        # print(icd_code)
        if isinstance(icd_code, str):
            return self.dict[icd_code]
        elif isinstance(icd_code, list):
            zeros_array = np.zeros(len(self.dict))
            
            for code in icd_code:
                zeros_array = np.logical_or(zeros_array, self.dict[code])
            return zeros_array
    def decode(self, icd_code):
        list_code = []
        for k, v in enumerate(icd_code):
            if v == 1:
                list_code.append(self.dict.keys()[k])
        return list_code

    def array_info(self, icd_code):
        list_code = self.decode(icd_code)
        filtered_df = self.df[self.df[self.label].isin(list_code)]
        return filtered_df['long_title'].to_list()
    
    def info(self, icd_code):
        if isinstance(icd_code, str):
            filtered_df = self.df[self.df[self.label].isin([icd_code])]
            return filtered_df['long_title'].to_list() 
        elif isinstance(icd_code, list):
            filtered_df = self.df[self.df[self.label].isin(icd_code)]
            return filtered_df['long_title'].to_list()

class NumTokenizer():
    def __init__(self, df):
        self.dict = self.build_tokenizer(df)
        self.df = df
        self.len_dict = len(self.dict.columns)
    def __len__(self):
        return self.len_dict
        
    def build_tokenizer(self, df):
        dummies = pd.get_dummies(df['itemid'])
        return dummies
        
    def __call__(self, icd_code):
        zeros_array = np.zeros(len(self.dict))
        
        for code in icd_code:
            zeros_array = zeros_array + self.dict[code[0]] * code[1]
        return zeros_array
    def decode(self, icd_code):
        list_code = []
        for k, v in enumerate(icd_code):
            if v != 0:
                list_code.append([self.dict.keys()[k], v])
        return list_code

    def array_info(self, icd_code):
        list_code = self.decode(icd_code)
        list_co = [v[0] for v in list_code]
        filtered_df = self.df[self.df['itemid'].isin(list_co)]
        return filtered_df['label'].to_list()
    
    def info(self, icd_code):
        
        list_co = [v[0] for v in icd_code]
        filtered_df = self.df[self.df['itemid'].isin(list_co)]
        return filtered_df['label'].to_list()


def padding_medical_history(input_tensor, dim=64):
    if dim <= input_tensor.size(0):
        input_tensor = input_tensor[-dim:]
        return input_tensor
    if len(input_tensor.shape) == 2:
        padding = torch.zeros((dim-input_tensor.size(0), input_tensor.size(1)))
    elif len(input_tensor.shape) == 1:
        padding = torch.zeros((dim-input_tensor.size(0)), dtype=torch.float32)
    input_tensor = torch.cat([padding, input_tensor], dim=0)
    return input_tensor

def save_json(data, folder_path):
    for k, v in data.items():
        list_numbers = v.dict.columns.to_list()
        dict_numbers = {index: value for index, value in enumerate(list_numbers)}
        file_path = f"{folder_path}/{k}.json"
        with open(file_path, 'w') as file:
            json.dump(dict_numbers, file)

def read_csv_gz_function(path):
    file_size = os.path.getsize(path)
    file_size_MB = file_size / (1024 * 1024)

    print(f"Read file {path}")
    print(f'File size: {file_size_MB:.2f} MB')

    if file_size_MB > 100: 
        chunk_size = 10000 

        chunk_list = []
        for chunk in pd.read_csv(path, chunksize=chunk_size, compression='gzip'):
            chunk_list.append(chunk)
        df = pd.concat(chunk_list)
        df.columns = df.columns.str.lower()
        return df 
    else:
        df = pd.read_csv(path, compression='gzip')
        df.columns = df.columns.str.lower()
        return df

def load_dataframe_from_url(url):
    url='https://drive.google.com/uc?id=' + url.split('/')[-2]
    return pd.read_csv(url)

def load_preprocessing_dataset(preprocessed_folder):
    all_items = os.listdir(preprocessed_folder)
    preprocessed_filedict = [item for item in all_items if os.path.isfile(os.path.join(preprocessed_folder, item))]

    dict_df = {}
    # for k in all_items:
    #     if len(str.split(k, sep='.'))==3:
    #         name, _, _ = str.split(k, sep='.')
    #         dict_df[name] = read_csv_gz_function(f"{preprocessed_folder}/{k}")
    for k in preprocessed_filedict:
        if len(str.split(k, sep='.'))==3:
            name, _, _ = str.split(k, sep='.')
            dict_df[name] = read_csv_gz_function(f"{preprocessed_folder}/{k}")
            
    return dict_df

def mkdir(path):
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("The new directory is created!")


class HeliosMedDataset(Dataset):
    def __init__(
            self, 
            preprocessing_folder: str = None,
            numpy_folder: str = None,
            external_folder: str = None,
            mode: str = None,
            *args, 
            **kwargs
            ) -> None:
        super(HeliosMedDataset, self).__init__(*args, **kwargs)
        self.ccsr_file = f"{external_folder}/DXCCSR_v2024-1.csv"
        
        self.dict_df = load_preprocessing_dataset(preprocessing_folder)
        self.dict_df.update(load_preprocessing_dataset(f"{preprocessing_folder}/{mode}"))

        self.dict_df['labevents']['itemid'] = self.dict_df['labevents']['itemid'].astype(int)

        self.seq_len = 64
        self.subject_id_list = self.dict_df['admittime']['subject_id'].drop_duplicates().to_list()
        self.len_d_labitems = len(self.dict_df['d_labitems'])

        self.tokenizers = {}
        self.tokenizers['labevents']                            = NumTokenizer(self.dict_df['d_labitems'].drop_duplicates(subset=['itemid']).sort_values(by=['itemid']))
        self.tokenizers['internal_medicine_history']            = Tokenizer(self.dict_df['d_internal_medicine_history'].drop_duplicates(subset=['icd_code']).sort_values(by=['icd_code']))
        self.tokenizers['procedures']                           = Tokenizer(self.dict_df['d_icd_procedures'].drop_duplicates(subset=['icd_code']).sort_values(by=['icd_code']))
        self.tokenizers['prescriptions']                        = Tokenizer(self.dict_df['d_prescriptions'].drop_duplicates(subset=['atc']).sort_values(by=['atc']))
        self.tokenizers['clinical']                             = Tokenizer(self.dict_df['d_clinical'].drop_duplicates(subset=['icd_code']).sort_values(by=['icd_code']))
        self.tokenizers['ablation_diagnoses']                   = Tokenizer(self.dict_df['d_ablation_diagnoses'].drop_duplicates(subset=['icd_code']).sort_values(by=['icd_code']))
        self.tokenizers['resistance_to_antimicrobial_drugs']    = Tokenizer(self.dict_df['d_resistance_to_antimicrobial_drugs'].drop_duplicates(subset=['icd_code']).sort_values(by=['icd_code']))
        self.tokenizers['body_mass_index']                      = Tokenizer(self.dict_df['d_body_mass_index'].drop_duplicates(subset=['icd_code']).sort_values(by=['icd_code']))
        self.tokenizers['long_term_current_drug_therapy']       = Tokenizer(self.dict_df['d_long_term_current_drug_therapy'].drop_duplicates(subset=['icd_code']).sort_values(by=['icd_code']))
        self.tokenizers['allergy_status_to_drugs']              = Tokenizer(self.dict_df['d_allergy_status_to_drugs'].drop_duplicates(subset=['icd_code']).sort_values(by=['icd_code']))
        self.tokenizers['ddi']                                  = Tokenizer(self.dict_df['d_prescriptions'].drop_duplicates(subset=['atc']).sort_values(by=['atc']))
        # self.tokenizers['category_internal_medicine_history']   = Tokenizer(self.dict_df['d_category_internal_medicine_history'].drop_duplicates(subset=['icd_code']))
        # self.tokenizers['ablation_category_diagnoses']          = Tokenizer(self.dict_df['d_ablation_category_diagnoses'].drop_duplicates(subset=['icd_code']))

        categorical_cols = ['marital_status', 'admission_location', 'race', 'admission_type', 'gender', 'age']

        self.time_df = self.dict_df['admissions'][['subject_id', 'hadm_id', 'time']].drop_duplicates()
        patient_infom_df = self.dict_df['d_patient'][['subject_id', 'hadm_id', 'marital_status', 'admission_location', 'race', 'admission_type', 'gender', 'age']]
        patient_info_df = self.dict_df['admissions'][['subject_id', 'hadm_id', 'marital_status', 'admission_location', 'race', 'admission_type', 'gender', 'age']]
        # Tạo OneHotEncoder và mã hóa các thuộc tính phân loại
        self.encoder = OneHotEncoder(sparse_output=False)
        self.encoder.fit(patient_infom_df[categorical_cols])
        encoded_features = self.encoder.transform(patient_info_df[categorical_cols])
        # Tạo DataFrame từ các đặc trưng đã mã hóa
        encoded_df = pd.DataFrame(encoded_features, columns=self.encoder.get_feature_names_out(categorical_cols))

        # Kết hợp các cột không phân loại và các cột đã mã hóa lại
        self.patient_info_df = pd.concat([patient_info_df.drop(columns=categorical_cols), encoded_df], axis=1)

        if numpy_folder != None:
            self.matrix = self.co_occurence(self.dict_df['d_ddi'], self.tokenizers['ddi'])
            np.savez_compressed(f"{numpy_folder}/ddi_adj.npz", arr=self.matrix)
            
            df_encoded_category, icd_code = self.preprocess_ccsr(self.ccsr_file, self.dict_df['d_internal_medicine_history'].drop_duplicates(subset=['icd_code']).sort_values(by=['icd_code']))
            np.savez_compressed(f"{numpy_folder}/ccsr_adj.npz", arr=df_encoded_category)

    def __len__(self):
        return len(self.subject_id_list)

    def __getitem__(self, index):
        # print("1")
        subject_id = self.subject_id_list[index]
        hadm_id = self.dict_df['admittime'][self.dict_df['admittime']['subject_id']==subject_id]['hadm_id'].drop_duplicates().to_list()
        time = self.time_df[self.time_df['subject_id']==subject_id]['time'].to_numpy()[-65:-1]
        patient_info = self.patient_info_df[self.patient_info_df['subject_id']==subject_id].drop(columns=['subject_id', 'hadm_id']).to_numpy()[-1]

        # print("2")
        # History
        # Tiền căn nội khoa đến thời điểm t-1
        internal_medicine_history = self.tokenize('internal_medicine_history',
                                            self.tokenizers['internal_medicine_history'],
                                            subject_id,
                                            hadm_id)
        # category_internal_medicine_history = self.tokenize('category_internal_medicine_history',
        #                                     self.tokenizers['category_internal_medicine_history'],
        #                                     subject_id,
        #                                     hadm_id)
        # print("3")
        # Tiền căn ngoại khoa đến thời điểm t-1
        treatment_history = self.tokenize('procedures_icd',
                                    self.tokenizers['procedures'],
                                    subject_id,
                                    hadm_id)
        # print("4")
        # Thuốc đến thời điểm t-1
        prescriptions = self.tokenize('prescriptions',
                                    self.tokenizers['prescriptions'],
                                    subject_id,
                                    hadm_id)
        # print("5")
        
        # Realtime
        # Tình trạng kháng thuốc thời điểm t
        resistance_to_antimicrobial_drugs = self.tokenize('resistance_to_antimicrobial_drugs',
                                                            self.tokenizers['resistance_to_antimicrobial_drugs'],
                                                            subject_id,
                                                            hadm_id)[-1]
        # print("6")
        # Chỉ số BMI thời điểm t
        body_mass_index = self.tokenize('body_mass_index',
                                        self.tokenizers['body_mass_index'],
                                        subject_id,
                                        hadm_id)[-1]
        # print("7")
        # Tình trạng sử dụng thuốc dài hạn thời điểm t
        long_term_current_drug_therapy = self.tokenize('long_term_current_drug_therapy',
                                                        self.tokenizers['long_term_current_drug_therapy'],
                                                        subject_id,
                                                        hadm_id)[-1]
        # print("8")
        # Tình trạng dị ứng thuốc thời điểm t
        allergy_status_to_drugs = self.tokenize('allergy_status_to_drugs',
                                                self.tokenizers['allergy_status_to_drugs'],
                                                subject_id,
                                                hadm_id)[-1]
        # print("9")
        # Triệu chứng lâm sàng thời điểm t
        clinical = self.tokenize('clinical',
                                    self.tokenizers['clinical'],
                                    subject_id,
                                    hadm_id)[-1]
        # print("10")
        
        # Label
        # Nhãn thời điểm t
        label_ablation_diagnoses = self.tokenize('ablation_diagnoses',
                                            self.tokenizers['ablation_diagnoses'],
                                            subject_id,
                                            hadm_id)[-1]
        
        # label_ablation_category_diagnoses = self.tokenize('ablation_category_diagnoses',
        #                                     self.tokenizers['ablation_category_diagnoses'],
        #                                     subject_id,
        #                                     hadm_id)[-1]
        # print("11")
        # label_category_diagnoses = category_internal_medicine_history[-1]
        # category_internal_medicine_history = category_internal_medicine_history[-65:-1]
        label_diagnoses = internal_medicine_history[-1]
        internal_medicine_history = internal_medicine_history[-65:-1]
        label_treatment = treatment_history[-1]
        treatment_history = treatment_history[-65:-1]
        label_prescriptions = prescriptions[-1]
        prescriptions = prescriptions[-65:-1]
        # print("12")

        # Kết quả cận lâm sàng thời điểm t
        df = self.dict_df['labevents'][self.dict_df['labevents']['subject_id']==subject_id]
        df = df[df['hadm_id']==hadm_id[-1]]
        time_list = df['charttime'].drop_duplicates().sort_values().to_list()[-64:]
        labevents = np.zeros((64, self.len_d_labitems))
        # print("13")
        for k, index in enumerate(time_list):
            temp = self.tokenizers['labevents'](df[df['charttime']==index].apply(lambda x: [x['itemid'], x['valuenum']], axis=1).to_list()).to_numpy()
            labevents[-k-1] = temp

        label_labevents = np.where(np.sum(labevents, axis=0) != 0, 1, 0) #
        # print("14")

        clinical = torch.FloatTensor(clinical)
        internal_medicine_history = torch.FloatTensor(internal_medicine_history)
        treatment_history = torch.FloatTensor(treatment_history)
        prescriptions = torch.FloatTensor(prescriptions)
        resistance_to_antimicrobial_drugs = torch.FloatTensor(resistance_to_antimicrobial_drugs)
        body_mass_index = torch.FloatTensor(body_mass_index)
        long_term_current_drug_therapy = torch.FloatTensor(long_term_current_drug_therapy)
        allergy_status_to_drugs = torch.FloatTensor(allergy_status_to_drugs)
        labevents = torch.FloatTensor(labevents)
        time = torch.FloatTensor(time)
        patient_info = torch.FloatTensor(patient_info)

        label_treatment = torch.FloatTensor(label_treatment)
        label_prescriptions = torch.FloatTensor(label_prescriptions)
        label_ablation_diagnoses = torch.FloatTensor(label_ablation_diagnoses)
        label_labevents = torch.FloatTensor(label_labevents)
        label_diagnoses = torch.FloatTensor(label_diagnoses)
        # label_category_diagnoses = torch.FloatTensor(label_category_diagnoses)
        # label_ablation_category_diagnoses = torch.FloatTensor(label_ablation_category_diagnoses)

        internal_medicine_history = padding_medical_history(internal_medicine_history, dim=self.seq_len)
        treatment_history = padding_medical_history(treatment_history, dim=self.seq_len)
        prescriptions = padding_medical_history(prescriptions, dim=self.seq_len)
        labevents = padding_medical_history(labevents, dim=self.seq_len)
        time = padding_medical_history(time, dim=self.seq_len)
        input = {
            "subject_id": subject_id,
            "clinical": clinical.numpy(), # (batch_size, feature_size)
            "internal_medicine_history": internal_medicine_history.numpy(), # (batch_size, seq_len, feature_size)
            "treatment_history": treatment_history.numpy(), # (batch_size, seq_len, feature_size)
            "prescriptions": prescriptions.numpy(),
            "resistance_to_antimicrobial_drugs": resistance_to_antimicrobial_drugs.numpy(), # (batch_size, feature_size)
            "body_mass_index": body_mass_index.numpy(), # (batch_size, feature_size)
            "long_term_current_drug_therapy": long_term_current_drug_therapy.numpy(), # (batch_size, feature_size)
            "allergy_status_to_drugs": allergy_status_to_drugs.numpy(), # (batch_size, feature_size)
            "labevents": labevents.numpy(), # (batch_size, seq_len, feature_size)
            "time": time.numpy(), # (batch_size, seq_len)
            "patient_info": patient_info.numpy(), # (batch_size, feature_size)
            "label_treatment": label_treatment.numpy(), # (batch_size, feature_size)
            "label_prescriptions": label_prescriptions.numpy(), # (batch_size, feature_size)
            "label_diagnoses": label_diagnoses.numpy(), # (batch_size, feature_size)
            "label_ablation_diagnoses": label_ablation_diagnoses.numpy(), # (batch_size, feature_size)
            "label_paraclinical_request": label_labevents.numpy(), # (batch_size, feature_size)
            # "label_category_diagnoses": label_category_diagnoses.numpy(), # (batch_size, feature_size)
            # "label_ablation_category_diagnoses": label_ablation_category_diagnoses.numpy(), # (batch_size, feature_size)
        }
        return input
    def tokenize(self, name_df, tokenizer, subject_id, hadm_id):
        if name_df == 'prescriptions':
            column = 'atc'
        else:
            column = 'icd_code'
        list = np.zeros((max(65, len(hadm_id)), len(tokenizer)))
        df = self.dict_df[name_df][self.dict_df[name_df]['subject_id']==subject_id]
        for k, index in enumerate(hadm_id):
            list[-k-1] = tokenizer(df[df['hadm_id']==index].apply(lambda x: x[column], axis=1).to_list())
        return list
    
    def save_tokenizer(self, folder):
        mkdir(folder)
        hyperparameters = {}
        for k in self.tokenizers.keys():
            # print(self.tokenizers[k].dict)
            hyperparameters[f"{k}_dim"] = len(self.tokenizers[k].dict)
            path = f"{folder}/{k}.csv.gz"
            self.tokenizers[k].dict.to_csv(path, index=False, compression='gzip', encoding='utf-8')
        

        hyperparameters['ddi_dim'] = self.matrix.shape[0]
        hyperparameters['patients_info_dim'] = len(self.patient_info_df.columns) - 2
        path = f"{folder}/hyperparameters.json"
        with open(path, 'w') as file:
            json.dump(hyperparameters, file)

    def co_occurence(self, df, tokenizer):
        atc_columns = tokenizer.keys()

        matrix = np.zeros((len(atc_columns), len(atc_columns)))

        for _, row in df.iterrows():
            # print("===")
            atc_1 = row['atc_1']
            atc_2 = row['atc_2']
            # print(f"atc_1 {atc_1} atc_2 {atc_2}")
            atc_1_position = atc_columns.get_loc(atc_1)
            # print(f"atc_1_position {atc_1_position}")
            atc_2_position = atc_columns.get_loc(atc_2)
            # print(f"atc_2_position {atc_2_position}")
            matrix[atc_1_position][atc_2_position] = 1
        return matrix
    
    def preprocess_ccsr(self, ccsr_file, d_icd_code_df):
        df = pd.read_csv(ccsr_file)
        df = df.rename(columns={"\'ICD-10-CM CODE\'": 'ICD-10-CM CODE',
                                                        "\'ICD-10-CM CODE DESCRIPTION\'": 'ICD-10-CM CODE DESCRIPTION',
                                                        "\'Default CCSR CATEGORY IP\'": 'Default CCSR CATEGORY IP',
                                                        "\'Default CCSR CATEGORY DESCRIPTION IP\'": 'Default CCSR CATEGORY DESCRIPTION IP',
                                                        "\'Default CCSR CATEGORY OP\'": 'Default CCSR CATEGORY OP',
                                                        "\'Default CCSR CATEGORY DESCRIPTION OP\'": 'Default CCSR CATEGORY DESCRIPTION OP',
                                                        "\'CCSR CATEGORY 1\'": 'CCSR CATEGORY 1',
                                                        "\'CCSR CATEGORY 1 DESCRIPTION\'": 'CCSR CATEGORY 1 DESCRIPTION',
                                                        "\'CCSR CATEGORY 2\'": 'CCSR CATEGORY 2',
                                                        "\'CCSR CATEGORY 2 DESCRIPTION\'": 'CCSR CATEGORY 2 DESCRIPTION',
                                                        "\'CCSR CATEGORY 3\'": 'CCSR CATEGORY 3',
                                                        "\'CCSR CATEGORY 3 DESCRIPTION\'": 'CCSR CATEGORY 3 DESCRIPTION',
                                                        "\'CCSR CATEGORY 4\'": 'CCSR CATEGORY 4',
                                                        "\'CCSR CATEGORY 4 DESCRIPTION\'": 'CCSR CATEGORY 4 DESCRIPTION',
                                                        "\'CCSR CATEGORY 5\'": 'CCSR CATEGORY 5',
                                                        "\'CCSR CATEGORY 5 DESCRIPTION\'": 'CCSR CATEGORY 5 DESCRIPTION',
                                                        "\'CCSR CATEGORY 6\'": 'CCSR CATEGORY 6',
                                                        "\'CCSR CATEGORY 6 DESCRIPTION\'": 'CCSR CATEGORY 6 DESCRIPTION',})
        df = df.applymap(lambda x: x.lstrip("\'") if isinstance(x, str) else x)
        df = df.applymap(lambda x: x.rstrip("\'") if isinstance(x, str) else x)
        df = df[[   'ICD-10-CM CODE',
                    'CCSR CATEGORY 1', 
                    'CCSR CATEGORY 2',
                    'CCSR CATEGORY 3',
                    'CCSR CATEGORY 4',
                    'CCSR CATEGORY 5',
                    'CCSR CATEGORY 6']]
        df = df.rename(columns={
        "ICD-10-CM CODE": "icd_code",
        })
        print(df.columns)
        print(d_icd_code_df.columns)
        df = pd.merge(d_icd_code_df, df, how='inner')
        top = len(df)
        df_melted = df[:top].melt(value_vars=[
            'CCSR CATEGORY 1', 
            'CCSR CATEGORY 2', 
            'CCSR CATEGORY 3', 
            'CCSR CATEGORY 4', 
            'CCSR CATEGORY 5', 
            'CCSR CATEGORY 6'
        ], var_name='Category', value_name='Code')

        # Thực hiện One-Hot Encoding trên cột 'Code'
        df_encoded = pd.get_dummies(df_melted['Code']).drop(columns=[' ']).astype(bool)
        df_final = df_encoded.groupby(df_melted.index // (len(df[:top]))).max().reset_index(drop=True)

        df_encoded_category_1 = df_encoded[:top]
        df_encoded_category_2 = df_encoded[top:2*top].reset_index(drop=True)
        df_encoded_category_3 = df_encoded[2*top:3*top].reset_index(drop=True)
        df_encoded_category_4 = df_encoded[3*top:4*top].reset_index(drop=True)
        df_encoded_category_5 = df_encoded[4*top:5*top].reset_index(drop=True)
        df_encoded_category_6 = df_encoded[5*top:6*top].reset_index(drop=True)

        df_encoded_category = df_encoded_category_1 | df_encoded_category_2 | df_encoded_category_3 | df_encoded_category_4 | df_encoded_category_5 | df_encoded_category_6
        return df_encoded_category.to_numpy(), df['icd_code']
    
class HeliosMedNumpy:
    def __init__(
            self,
            preprocessing_folder : str = None,
            numpy_folder : str = None,
            external_folder: str = None,
            dataset : str = None,
            tokenize_folder : str = None,
            batch_size : int = 32,
            num_workers : int = 32
            ) -> None:
        self.numpy_folder = numpy_folder
        self.ehr_adj_path = f"{numpy_folder}/{dataset}/ehr_adj.npz"
        self.dataset = dataset
        self.batch_size = batch_size
        self.num_workers = num_workers

        
        mkdir(f"{numpy_folder}/{dataset}")
        self.train_data = HeliosMedDataset(
            preprocessing_folder=f"{preprocessing_folder}/{dataset}",
            numpy_folder=f"{numpy_folder}/{dataset}",
            external_folder=external_folder,
            mode="train",
        )
        self.valid_data = HeliosMedDataset(
            preprocessing_folder=f"{preprocessing_folder}/{dataset}",
            mode="valid",
        )
        self.test_data = HeliosMedDataset(
            preprocessing_folder=f"{preprocessing_folder}/{dataset}",
            mode="test",
        )
        
        self.train_data.save_tokenizer(f"{tokenize_folder}/{dataset}")
        
        pass

    def __call__(
            self, 
            *args: Any, 
            **kwds: Any
            ) -> Any:
        
        mkdir(f"{self.numpy_folder}/{self.dataset}/train")
        mkdir(f"{self.numpy_folder}/{self.dataset}/valid")
        mkdir(f"{self.numpy_folder}/{self.dataset}/test")
        mkdir(f"{self.numpy_folder}/{self.dataset}/weights")

        train_dict = convert(self.train_data, f"{self.numpy_folder}/{self.dataset}/train", batch_size=self.batch_size, num_workers=self.num_workers)
        valid_dict = convert(self.valid_data, f"{self.numpy_folder}/{self.dataset}/valid", batch_size=self.batch_size, num_workers=self.num_workers)
        test_dict = convert(self.test_data, f"{self.numpy_folder}/{self.dataset}/test", batch_size=self.batch_size, num_workers=self.num_workers)

        dict = {}
        for k in test_dict.keys():
            print(k)
            print(train_dict[k].shape)
            print(valid_dict[k].shape)
            print(test_dict[k].shape)
            dict[k] = np.concatenate([train_dict[k], valid_dict[k], test_dict[k]])
            print(dict[k].shape)
        generate_weight(dict, f"{self.numpy_folder}/{self.dataset}/weights")
        matrix = generate_ehr_adj(numpy_folder=f"{self.numpy_folder}/{self.dataset}", 
                          batch_size=2048, 
                          num_workers=12)
        np.savez_compressed(self.ehr_adj_path, arr=(matrix !=0))
        pass
    
    
