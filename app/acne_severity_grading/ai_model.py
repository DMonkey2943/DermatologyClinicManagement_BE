import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import io

class AcneClassifier:
    def __init__(self, model_path: str):
        # Tải mô hình ResNet-18
        self.model = models.resnet18()
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, 4)  # 4 lớp
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()  # Chế độ đánh giá
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

        # Transform cho ảnh đầu vào
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Danh sách lớp
        self.classes = ['Mild', 'Moderate', 'Severe', 'Very Severe']

    def predict(self, image_bytes: bytes) -> str:
        # Đọc ảnh từ bytes
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        # Áp dụng transform
        image = self.transform(image).unsqueeze(0).to(self.device)
        # Dự đoán
        with torch.no_grad():
            output = self.model(image)
            _, predicted = torch.max(output, 1)
        return self.classes[predicted.item()]

# Khởi tạo mô hình
acne_classifier = AcneClassifier(model_path='app/acne_severity_grading/models/acne_severity_grading_model_v3.pth')