# 🔍 Fraud Lens — AI Insurance Claim Fraud Detection

An AI-powered system that detects fraudulent car damage 
photos in insurance claims using a two-layer detection approach.

## How It Works

**Layer 1 — ResNet50 (Deep Learning)**
- Pretrained on ImageNet
- Fine-tuned on 595 car damage images
- Detects pixel-level manipulation

**Layer 2 — Physical Plausibility**
- Lighting consistency check
- Camera noise pattern analysis
- Edge distribution analysis
- Shadow ratio check

**Layer 3 — XGBoost Ensemble**
- Combines ResNet score + plausibility features
- Learned decision boundary from data
- 87.64% test accuracy

## Dataset
- 300 real car damage images (CarDD dataset)
- 135 OpenCV manipulated fakes (5 techniques)
- 160 AI-generated Gemini fakes
- Total: 595 images

## Results
| Model | Val Accuracy | Test Accuracy |
|-------|-------------|---------------|
| Baseline ResNet50 | 86.67% | 83.00% |
| v3 (OpenCV + Gemini) | 79.78% | 87.64% |

## Tech Stack
- PyTorch + ResNet50
- XGBoost ensemble
- OpenCV for fake generation
- Streamlit for demo app
- Google Colab for training

## Project Structure
fraud-lens/
├── notebooks/          # Training notebook
├── src/                # Core modules
├── app/                # Streamlit demo
├── fake_generator/     # OpenCV fake generation
└── results/            # Training charts

## Setup
pip install -r requirements.txt

## Author
Juliya Sebastian — Final Year Project, April 2026