from rdkit import Chem, RDLogger
import pandas as pd
import sys
import os


class Sdf:
    def __init__(self):
        pass

    def process_sdf(self, input_file, database, batch_size, affinity_cutoff=None):
        if not os.path.exists("SDFs"):
            os.makedirs("SDFs")
        try:
            with open(input_file, 'r') as file:
                lines = file.readlines()
        except:
            return print('\nFILE NOT FOUND\n')

        current_molecule = []
        current_affinity = None
        first_database_name = None

        def save_batch(batch, index):
            with open(os.path.join("SDFs", f"{database}_{index:04d}.sdf"), 'w') as f:
                f.writelines(batch)

        batch = []
        file_index = 1
        molecule_count = 0

        for i, line in enumerate(lines):
            if not current_molecule:
                first_database_name = line.split()[0] if line.strip() else None
                if first_database_name:
                    current_molecule.append(first_database_name + '\n')
            else:
                current_molecule.append(line)

            if line.startswith('>  <minimizedAffinity>'):
                current_affinity = float(lines[i + 1].strip())

            if line.strip() == '$$$$':
                if affinity_cutoff is None or (current_affinity is not None and current_affinity <= affinity_cutoff):
                    batch.extend(current_molecule)
                    molecule_count += 1

                current_molecule = []
                current_affinity = None
                first_database_name = None

                if molecule_count == batch_size:
                    save_batch(batch, file_index)
                    file_index += 1
                    batch = []
                    molecule_count = 0

        if batch:
            save_batch(batch, file_index)

        print(f"\nProcessing finished. \n{file_index} batch(es) saved in folder 'SDFs'.\n")

class AdmetSpreadsheet:

    ''' Analyzes the AdmetLab 3.0 spreadsheet '''

    def __init__(self, input = None, weights=None):
        self.input = input
        self.df = None
        self.df_analysis = None
        self.weights = weights
        self.new_cols_to_move = ['SCORE', 'ABSORTION', 'DISTRIBUTION', 'TOXICITY', 'TOX21_PATHWAY', 'METABOLISM', 'TOXICOPHORE_RULES', 'EXCRETION', 'MEDICINAL_CHEMISTRY']
        self.required_columns = ['smiles', 'MW', 'Vol', 'Dense', 'nHA', 'nHD', 'TPSA', 'nRot', 'nRing', 'MaxRing','nHet', 'fChar', 'nRig', 'Flex', 'nStereo', 'gasa', 'QED', 'Synth', 'Fsp3', 'MCE-18', 'Natural Product-likeness', 'Alarm_NMR', 'BMS', 'Chelating', 'PAINS', 'Lipinski', 'Pfizer', 'GSK', 'GoldenTriangle', 'logS', 'logD', 'logP', 'mp', 'bp', 'pka_acidic', 'pka_basic', 'caco2', 'MDCK', 'PAMPA', 'pgp_inh', 'pgp_sub', 'hia', 'f20', 'f30', 'f50', 'OATP1B1', 'OATP1B3', 'BCRP', 'BSEP', 'BBB', 'MRP1', 'PPB', 'logVDss', 'Fu', 'CYP1A2-inh', 'CYP1A2-sub', 'CYP2C19-inh', 'CYP2C19-sub', 'CYP2C9-inh', 'CYP2C9-sub', 'CYP2D6-inh', 'CYP2D6-sub', 'CYP3A4-inh', 'CYP3A4-sub', 'CYP2B6-inh', 'CYP2B6-sub', 'CYP2C8-inh', 'LM-human', 'cl-plasma', 't0.5', 'BCF', 'IGC50', 'LC50DM', 'LC50FM', 'hERG', 'hERG-10um', 'DILI', 'Ames', 'ROA', 'FDAMDD', 'SkinSen', 'Carcinogenicity', 'EC', 'EI', 'Respiratory', 'H-HT', 'Neurotoxicity-DI', 'Ototoxicity', 'Hematotoxicity', 'Nephrotoxicity-DI', 'Genotoxicity', 'RPMI-8226', 'A549', 'HEK293', 'NR-AhR', 'NR-AR', 'NR-AR-LBD', 'NR-Aromatase', 'NR-ER', 'NR-ER-LBD', 'NR-PPAR-gamma', 'SR-ARE', 'SR-ATAD5', 'SR-HSE', 'SR-MMP', 'SR-p53', 'NonBiodegradable', 'NonGenotoxic_Carcinogenicity', 'SureChEMBL', 'LD50_oral', 'Skin_Sensitization', 'Acute_Aquatic_Toxicity', 'molstr', 'Genotoxic_Carcinogenicity_Mutagenicity', 'Aggregators', 'Fluc', 'Blue_fluorescence', 'Green_fluorescence','Reactive', 'Other_assay_interference', 'Promiscuous']
        self.weights = weights

    def replace_interval(self, valor, intervals, values):
        for interval, valor_substituido in zip(intervals, values):
            if interval[0] <= valor <= interval[1]:
                return valor_substituido
        return valor

    def replace_values(self, df, columns, intervals, values):
        replace = lambda x: self.replace_interval(pd.to_numeric(x, errors='coerce'), intervals, values)
        for col in columns:
            df[col] = df[col].apply(replace)
        return df

    def substituir_string(self, valor, string, valor1, valor2):
        return valor1 if valor == string else valor2

    def process_data(self, df, weights):
        
        self.df = df
        self.weights = weights if weights is not None else {
            "ABSORTION": 2,
            "DISTRIBUTION": 1,
            "TOXICITY": 8,
            "TOX21_PATHWAY": 3,
            "METABOLISM": 2,
            "TOXICOPHORE_RULES": 3,
            "EXCRETION": 1,
            "MEDICINAL_CHEMISTRY": 5
        }

        self.df = df.rename(columns={
            'cl-plasma': 'cl_plasma',
            't0.5': 't_0_5',
            'MCE-18': 'MCE_18',
            })

        out_of_analysis = ['BCF', 'bp', 'Dense', 'fChar', 'Flex', 'IGC50', 'LC50DM', 'LC50FM', 'LD50_oral', 'logD', 'logP', 'logS', 'logVDss', 'MaxRing', 'MDCK', 'mp', 'MW', 'Natural Product-likeness', 'nHA', 'nHD', 'nHet', 'nRig', 'nRing', 'nRot', 'nStereo', 'Other_assay_interference', 'pka_acidic', 'pka_basic', 'molstr', 'TPSA', 'Vol']
        absorption_columns = ['PAMPA', 'pgp_inh', 'pgp_sub', 'hia', 'f20', 'f30', 'f50']
        distribution_columns = ['OATP1B1', 'OATP1B3', 'BCRP', 'BSEP', 'BBB', 'MRP1']
        toxicity_columns = ['hERG', 'hERG-10um', 'DILI', 'Ames', 'ROA', 'FDAMDD', 'SkinSen', 'Carcinogenicity', 'EC', 'EI', 'Respiratory', 'H-HT', 'Neurotoxicity-DI', 'Ototoxicity', 'Hematotoxicity', 'Nephrotoxicity-DI', 'Genotoxicity', 'RPMI-8226', 'A549', 'HEK293']
        tox21_columns = ['NR-AhR', 'NR-AR', 'NR-AR-LBD', 'NR-Aromatase', 'NR-ER', 'NR-ER-LBD', 'NR-PPAR-gamma', 'SR-ARE', 'SR-ATAD5', 'SR-HSE', 'SR-MMP', 'SR-p53']
        metabolism_columns = ['CYP1A2-inh', 'CYP1A2-sub', 'CYP2C19-inh', 'CYP2C19-sub', 'CYP2C9-inh', 'CYP2C9-sub', 'CYP2D6-inh', 'CYP2D6-sub', 'CYP3A4-inh', 'CYP3A4-sub', 'CYP2B6-inh', 'CYP2B6-sub', 'CYP2C8-inh', 'LM-human']
        toxicophore_columns = ['NonBiodegradable', 'NonGenotoxic_Carcinogenicity', 'SureChEMBL', 'Skin_Sensitization', 'Acute_Aquatic_Toxicity', 'Genotoxic_Carcinogenicity_Mutagenicity']
        medicinal_chemistry_columns_str = ['Alarm_NMR', 'BMS', 'Chelating', 'PAINS']
        medicinal_chemistry_columns_float_divergent = ['gasa', 'QED', 'Synth', 'Fsp3', 'MCE_18', 'Lipinski', 'Pfizer', 'GSK', 'GoldenTriangle']
        medicinal_chemistry_columns_float_similar = ['Aggregators', 'Fluc', 'Blue_fluorescence', 'Green_fluorescence', 'Reactive', 'Promiscuous']
        medicinal_chemistry = medicinal_chemistry_columns_str + medicinal_chemistry_columns_float_divergent + medicinal_chemistry_columns_float_similar

        self.df = self.replace_values(self.df, absorption_columns, [(0, 0.3), (0.3, 0.7), (0.7, 1.0)], [1.25, 0.62, 0.0])
        self.df = self.replace_values(self.df, distribution_columns, [(0, 0.3), (0.3, 0.7), (0.7, 1.0)], [1.25, 0.62, 0.0])
        self.df = self.replace_values(self.df, toxicity_columns, [(0, 0.3), (0.3, 0.7), (0.7, 1.0)], [0.5, 0.25, 0.0])
        self.df = self.replace_values(self.df, tox21_columns, [(0, 0.3), (0.3, 0.7), (0.7, 1.0)], [0.83, 0.41, 0.0])
        self.df = self.replace_values(self.df, metabolism_columns, [(0, 0.3), (0.3, 0.7), (0.7, 1.0)], [0.71, 0.35, 0.0])

        for col in toxicophore_columns:
            self.df[col] = self.df[col].apply(self.substituir_string, args=("['-']", 1.6, 0))

        for col in medicinal_chemistry_columns_str:
            self.df[col] = self.df[col].apply(self.substituir_string, args=("['-']", 0.5, 0))

        self.df = (
            self.df.assign(
                caco2=pd.to_numeric(self.df['caco2'], errors='coerce').apply(lambda x: 1.25 if x > -5.15 else 0),
                PPB=pd.to_numeric(self.df['PPB'], errors='coerce').apply(lambda x: 1.25 if x <= 90 else 0),
                Fu=pd.to_numeric(self.df['Fu'], errors='coerce').apply(lambda x: 1.25 if x >= 5 else 0),
                cl_plasma=pd.to_numeric(self.df['cl_plasma'], errors='coerce').apply(lambda x: 5 if 0 <= x <= 5 else (2.5 if 5 < x <= 15 else 0)),
                t_0_5=pd.to_numeric(self.df['t_0_5'], errors='coerce').apply(lambda x: 5 if x > 8 else (2.5 if 1 <= x <= 8 else 0)),
                Lipinski=pd.to_numeric(self.df['Lipinski'], errors='coerce').apply(lambda x: 0.5 if x < 2 else 0),
                Pfizer=pd.to_numeric(self.df['Pfizer'], errors='coerce').apply(lambda x: 1 if x < 2 else 0),
                GSK=pd.to_numeric(self.df['GSK'], errors='coerce').apply(lambda x: 0.5 if x == 0 else 0),
                GoldenTriangle=pd.to_numeric(self.df['GoldenTriangle'], errors='coerce').apply(lambda x: 0.5 if x == 0 else 0),
                gasa=pd.to_numeric(self.df['gasa'], errors='coerce').apply(lambda x: 0.5 if x == 1 else 0),
                QED=pd.to_numeric(self.df['QED'], errors='coerce').apply(lambda x: 0.5 if x > 670 else 0),
                Synth=pd.to_numeric(self.df['Synth'], errors='coerce').apply(lambda x: 0.5 if x <= 6.000 else 0),
                Fsp3=pd.to_numeric(self.df['Fsp3'], errors='coerce').apply(lambda x: 0.5 if x >= 420 else 0),
                MCE_18=pd.to_numeric(self.df['MCE_18'], errors='coerce').apply(lambda x: 0.5 if x >= 45.000 else 0)
            )
        )

        for col in medicinal_chemistry_columns_float_similar:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce').apply(lambda x: 0.5 if x < 1.000 else 0)

        new_cols = pd.DataFrame({
            'ABSORTION': self.df[absorption_columns + ['caco2']].sum(axis=1, skipna=True),
            'DISTRIBUTION': self.df[['PPB', 'Fu'] + distribution_columns].sum(axis=1, skipna=True),
            'TOXICITY': self.df[toxicity_columns].sum(axis=1, skipna=True),
            'TOX21_PATHWAY': self.df[tox21_columns].sum(axis=1, skipna=True),
            'METABOLISM': self.df[metabolism_columns].sum(axis=1, skipna=True),
            'TOXICOPHORE_RULES': self.df[toxicophore_columns].sum(axis=1, skipna=True),
            'EXCRETION': self.df[['cl_plasma', 't_0_5']].sum(axis=1, skipna=True),
            'MEDICINAL_CHEMISTRY': self.df[medicinal_chemistry].sum(axis=1, skipna=True)
        })

        self.df_analysis = pd.concat([self.df, new_cols], axis=1)
        self.df_analysis = self.df_analysis.drop(columns=out_of_analysis)

        self.df_analysis['SCORE'] = (self.df_analysis['ABSORTION'] * self.weights['ABSORTION'] +
                                     self.df_analysis['DISTRIBUTION'] * self.weights ['DISTRIBUTION'] +
                                     self.df_analysis['TOXICITY'] * self.weights ['TOXICITY'] +
                                     self.df_analysis['TOX21_PATHWAY'] * self.weights ['TOX21_PATHWAY'] +
                                     self.df_analysis['METABOLISM'] * self.weights['METABOLISM'] +
                                     self.df_analysis['TOXICOPHORE_RULES'] * self.weights ['TOXICOPHORE_RULES'] +
                                     self.df_analysis['EXCRETION'] * self.weights['EXCRETION'] +
                                     self.df_analysis['MEDICINAL_CHEMISTRY'] * self.weights['MEDICINAL_CHEMISTRY']) / sum(self.weights.values())

        analysis_df = pd.merge(df, self.df_analysis[['smiles'] + self.new_cols_to_move], on='smiles', how='left')
        new_cols = ['ID_Molecula', 'Afinidade'] + self.new_cols_to_move + ['smiles'] + [col for col in analysis_df.columns if col not in self.new_cols_to_move and col not in ['ID_Molecula', 'Afinidade', 'smiles']]

        analysis_df = analysis_df[new_cols]
        analysis_df[self.new_cols_to_move] = analysis_df[self.new_cols_to_move].round(2)

        self.analysis_df = analysis_df

        print('\nAnalysis completed\n')
        return self.analysis_df

class Extract:

    def __init__(self):
        pass

    RDLogger.DisableLog('rdApp.*')

    def extract_ids_affinities_from_sdf(self, sdf_file):
        ids_affinity = []
        with Chem.SDMolSupplier(sdf_file) as suppl:
            for mol in suppl:
                if mol is not None:
                    mol_id = mol.GetProp('_Name')
                    affinity = mol.GetDoubleProp('minimizedAffinity')
                    smiles = Chem.MolToSmiles(mol)
                    ids_affinity.append((mol_id, affinity, smiles))
        df = pd.DataFrame(ids_affinity, columns=['ID_Molecula', 'Afinidade', 'smiles'])
        return df

    def extract (self,csv_file, sdf_file ):

        try:
            df_final = self.extract_ids_affinities_from_sdf(sdf_file)
        except:
            print('\nSDF NOT FOUND\n')
            sys.exit()

        try:
            df_csv = pd.read_csv(csv_file)
        except:
            print('\nCSV NOT FOUND\n')
            sys.exit()
    
        df_merged = pd.merge(df_final, df_csv, on='smiles', how='left')

        df_merged.drop_duplicates(subset=['smiles'], inplace=True)
        
        return df_merged

class Spreadsheet:

    def __init__(self):
        pass

    def spreadsheet_output(self, df):

        if not os.path.exists('score'):
            os.makedirs('score')

        csv_path = os.path.join('score', 'scoreadmet.csv')

        if os.path.exists(csv_path):
            existing_df = pd.read_csv(csv_path)
            updated_df = pd.concat([existing_df, df], ignore_index=True)
        else:
            updated_df = df

        updated_df = updated_df.sort_values(by='SCORE', ascending=False)

        updated_df.to_csv(csv_path, index=False)

        return updated_df
