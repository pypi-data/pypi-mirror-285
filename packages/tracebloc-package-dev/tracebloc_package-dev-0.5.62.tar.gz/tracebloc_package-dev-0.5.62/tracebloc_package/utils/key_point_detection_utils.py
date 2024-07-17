import torch
from torch.utils.data import Dataset
from PIL import Image
import numpy as np


class FakeKeypointDetectionDataset(Dataset):
    def __init__(
        self, num_images, image_size, num_keypoints=4, num_classes=10, transform=None
    ):
        self.num_images = num_images
        self.image_size = image_size  # e.g., (2448, 2648)
        self.num_keypoints = num_keypoints
        self.num_classes = num_classes
        self.transform = transform

    def __len__(self):
        return self.num_images

    def __getitem__(self, idx):
        # Create a blank image
        image = Image.new("RGB", self.image_size, color="white")

        # Generate keypoints
        keypoints = self.generate_random_keypoints(self.num_keypoints, self.image_size)

        # Calculate bounding box
        bboxes = self.get_bbox(keypoints)

        # Transformation logic
        if self.transform:
            image = self.transform(image)

        # Create target dictionary
        target = {
            "boxes": torch.as_tensor([bboxes], dtype=torch.float32),
            "labels": torch.randint(
                0, self.num_classes, (1,)
            ),  # Random class for the object
            "image_id": torch.tensor([idx]),
            "area": torch.tensor([(bboxes[2] - bboxes[0]) * (bboxes[3] - bboxes[1])]),
            "iscrowd": torch.tensor([0]),
            "keypoints": torch.as_tensor(keypoints, dtype=torch.float32),
        }

        return image, target

    def generate_random_keypoints(self, num_keypoints, size):
        return [
            [np.random.randint(0, s) for s in size] + [1] for _ in range(num_keypoints)
        ]

    def get_bbox(self, keypoints):
        x_coords = [kp[0] for kp in keypoints]
        y_coords = [kp[1] for kp in keypoints]
        return [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
