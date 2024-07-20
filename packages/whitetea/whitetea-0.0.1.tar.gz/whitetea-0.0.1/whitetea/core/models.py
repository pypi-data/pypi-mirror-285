from blacktea import TeaModel

class EhrTeaModel(BaseTeaModel):
    '''A class for the EHR-TEA model.'''
    def __init__(self, ehr_data_path, **kwargs):
        super().__init__(**kwargs)
        self.model_type = 'ehr-tea'
        self.model_name = 'EHR-TEA'
        self.load_ehr_data(ehr_data_path)

    def load_ehr_data(self, data_path):
        '''Load EHR data from a file.'''
        self.data_path = data_path
        self.data = pd.read_csv(data_path)
        self.data = self.data.dropna()
        self.data = self.data.reset_index(drop=True)
        self.data = self.data.drop_duplicates()
        self.data = self.data.reset_index(drop=True)

    def preprocess_ehr_data(self):
        '''Preprocess EHR data.'''
        pass

    def artifically_impute(self, X):
        '''Artificially impute missing values grouped 
        by patient id.'''
        #TODO specify patient id extraction
        pass

    def learn_imputation(self, X):
        '''Learn imputation model, but masking grouped 
        by patient id.'''
        #TODO specify patient id extraction
        pass
