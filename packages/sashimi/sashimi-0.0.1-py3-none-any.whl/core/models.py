
class saliency_model():
    '''default saliency model class. 
    PyTorch example with 2-layer neural network.
    '''
    def __init__(self):
        self.model = nn.Sequential(
            nn.Linear(2, 10),
            nn.ReLU(),
            nn.Linear(10, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.model(x)
    
    def train(self, X, y, epochs=1000):
        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        for epoch in range(epochs):
            optimizer.zero_grad()
            output = self.model(X)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
            if epoch % 100 == 0:
                print('Epoch:', epoch, 'Loss:', loss.item())


   