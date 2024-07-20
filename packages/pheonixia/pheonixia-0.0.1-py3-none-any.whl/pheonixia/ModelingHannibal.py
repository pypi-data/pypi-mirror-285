from torch import nn
from huggingface_hub import PyTorchModelHubMixin


class Hannibal(nn.Module,
              PyTorchModelHubMixin,
              library_name = "PyTorchModelHubMixin-template",
              repo_url = "https://github.com/not-lain/phoenixia",
              tags=["visual-question-answering"],
              ):
    """an AI model for visual question answering"""

    def __init__(self, a=2, b=1):
        super().__init__()
        self.layer = nn.Linear(a, b, bias=False)

    def forward(self, input_ids):
        return self.layer(input_ids)
