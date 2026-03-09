import os
import io
import logging
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)


class Sketch2PhotoService:
    """Lightweight wrapper for loading and running the sketch2photo model."""

    def __init__(self, weights_path: Optional[str] = None):
        self.model = None
        self.device = None
        self.transforms = None
        self.weights_path = weights_path
        self._torch_available = False
        try:
            import torch  # noqa: F401
            import torchvision.transforms as T  # noqa: F401
            self._torch_available = True
        except Exception as e:
            logger.warning(f"PyTorch not available: {e}")

        if self._torch_available and weights_path:
            self.load(weights_path)

    def load(self, weights_path: str) -> bool:
        if not self._torch_available:
            logger.warning("Cannot load sketch2photo model: PyTorch not installed")
            return False

        try:
            import torch
            import torchvision.transforms as T
            from models.pix2pix_model import UNetGenerator

            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = UNetGenerator().to(self.device)
            state = torch.load(weights_path, map_location=self.device)
            self.model.load_state_dict(state)
            self.model.eval()

            self.transforms = T.Compose([
                T.Resize((256, 256)),
                T.ToTensor(),
            ])

            self.weights_path = weights_path
            logger.info(f"Sketch2Photo model loaded from {weights_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load sketch2photo model: {e}")
            self.model = None
            return False

    def is_ready(self) -> bool:
        return self.model is not None and self.transforms is not None

    def generate_photo(self, image_bytes: bytes) -> Optional[bytes]:
        """Run inference: sketch (bytes) -> generated photo (JPEG bytes)."""
        if not self.is_ready():
            return None
        try:
            import torch
            sketch_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            inp = self.transforms(sketch_pil).unsqueeze(0).to(self.device)
            with torch.no_grad():
                out = self.model(inp)
            out = out.squeeze(0).cpu().clamp(-1, 1)

            # Map from [-1,1] to [0,255]
            out = ((out + 1) / 2.0).mul(255).byte()
            out_pil = Image.fromarray(out.permute(1, 2, 0).numpy())

            buf = io.BytesIO()
            out_pil.save(buf, format="JPEG", quality=90)
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Error generating photo from sketch: {e}")
            return None



