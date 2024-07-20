
class BaseTeaModel():
    '''Base class for tabular embedding alignment (TEA) models. 
    '''
    def __init__(self):
        pass
    
    def artifically_impute(self, X):
        '''Artificially impute missing values in the input data X.
        '''

    def learn_imputation(self, X):
        '''Learn to impute missing values in the input data X.
        '''
        pass

    def fit(self, X, Y):
        '''Fit the model with input data X and target Y.
        '''
        pass

    def transform(self, X):
        '''Transform the input data X.
        '''
        pass

    def fit_transform(self, X, Y):
        '''Fit the model with input data X and target Y, then transform X.
        '''
        pass

    def get_params(self, deep=True):
        '''Get parameters for this estimator.
        '''
        pass

    def set_params(self, **params):
        '''Set the parameters of this estimator.
        '''
        pass

def DeepTeaModel(BaseTeaModel):
    '''Deep tabular embedding alignment (DeepTEA) model.
    Example shown is a 2-layer neural network in PyTorch.
    It performs deep alignment of tabular embeddings to create 
    effective projections between different datasets in terms of 
    partially observable entries and columns in the datasets.
    '''
    def __init__(self):
        model = nn.Sequential(
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Linear(50, 10),
            nn.ReLU()
        )
        self.model = model
    
    def learn_imputation(self, X):
        '''Learn to impute missing values in the input data X.
        In this example, we iteratively create training and validation
        dataset splits of simulated missing values by masking the original
        dataset, and train the model on the training data, then validate
        on the validation data. We use the model to predict the missing
        values based on the original dataset. The example shown is based on
        PyTorch training and validation loops.
        The base method is deep Non-negative Matrix Factorization (NMF).
        '''
        X = torch.tensor(X.values, dtype=torch.float32)
        mask = torch.isnan(X)
        #TODO sort out best ways to randomize masking in the next version       

        X[mask] = 0
        model = self.model
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        for epoch in range(100):
            model.train()
            optimizer.zero_grad()
            output = model(X)
            loss = criterion(output[mask], X[mask])
            loss.backward()
            optimizer.step()
            model.eval()
            with torch.no_grad():
                output = model(X)
                X[mask] = output[mask]
        return self
        

    def artifically_impute(self, X):
        '''Artificially impute missing values in the input data X.
        '''
        # TODO merge this method with transform?
        model = self.model
        X = torch.tensor(X.values, dtype=torch.float32)
        mask = torch.isnan(X)
        X[mask] = 0
        model.eval()
        with torch.no_grad():
            output = model(X)
            X[mask] = output[mask]
        return X      
    
    def fit(self, X, Y):
        '''Fit the model with input data X and target Y.
        '''
        X = self.artifically_impute(X)
        self.learn_imputation(X)
        self.model.fit(X, Y)
        return self
    
    def transform(self, X):
        '''Transform the input data X.
        '''
        X = self.artifically_impute(X)
        return self.model.transform(X)
    
    def get_params(self, deep=True):
        '''Get parameters for this estimator.
        '''
        return self.model.get_params(deep=deep)
    
    def set_params(self, **params):
        '''Set the parameters of this estimator.
        '''
        return self.model.set_params(**params)
    
    def __repr__(self):
        return 'DeepTeaModel'
    
