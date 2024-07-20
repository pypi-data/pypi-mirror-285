

class ReservoirNetwork():
    '''base class for reservoir network.
    Example shown in PyTorch'''
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.W_in = torch.randn(hidden_size, input_size)
        self.W = torch.randn(hidden_size, hidden_size)
        self.W_out = torch.randn(output_size, hidden_size)
        self.alpha = 0.5
        self.spectral_radius = 0.9
        self.W = self.W * self.spectral_radius / max(abs(np.linalg.eigvals(self.W)))

    def forward(self, x):
        self.x = x
        self.u = torch.tanh(self.W_in @ x + self.W @ self.x)
        self.y = self.W_out @ self.u
        return self.y
    
    def train(self, x, y):
        self.y_hat = self.forward(x)
        self.error = y - self.y_hat
        self.W_out += self.alpha * self.error * self.u
        return self.error
    
    def test(self, x, y):
        self.y_hat = self.forward(x)
        self.error = y - self.y_hat
        return self.error
    
    def predict(self, x):
        return self.forward(x)
    
