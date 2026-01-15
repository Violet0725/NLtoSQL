# NL-to-SQL: Local LLM Project

A complete Natural Language to SQL system using fine-tuned Llama-3-8B with Unsloth, FastAPI backend, and React frontend.

## 🎯 Project Overview

This project demonstrates an end-to-end NL-to-SQL pipeline:
- **Training**: Fine-tune Llama-3-8B using Unsloth + LoRA on SQL datasets
- **Backend**: FastAPI service for model inference and SQL execution
- **Frontend**: React + Tailwind CSS interface for natural language queries
- **Database**: SQLite database with sales data (products and sales records)

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI    │────▶│   Llama-3   │────▶│  SQLite    │
│  Frontend   │     │   Backend    │     │  + LoRA     │     │  Database  │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
```

## 📁 Project Structure

```
sql-project/
├── app/                    # FastAPI backend
│   └── main.py            # Inference API with model loading
├── training/              # Model training scripts
│   └── train.py          # Unsloth + LoRA fine-tuning
├── frontend/             # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── SQLChat.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── lora_adapters/        # Trained LoRA adapters (Git LFS)
├── generate_data.py      # SQLite database generator
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+ (or use yarn)
- NVIDIA GPU with CUDA (for training and inference)
- 12GB+ VRAM recommended

### 1. Clone and Setup

```bash
git clone https://github.com/Violet0725/NLtoSQL.git
cd NLtoSQL
```

### 2. Generate Database

```bash
python3 generate_data.py
```

This creates `sales_data.db` with:
- 20 products (Gaming Laptop, Mechanical Keyboard, etc.)
- 50 sales records across 5 regions

### 3. Setup Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic
pip install unsloth transformers trl datasets accelerate peft bitsandbytes
```

### 4. Train Model (Optional)

If you want to retrain the model:

```bash
python training/train.py
```

This will:
- Load Llama-3-8B in 4-bit
- Apply LoRA adapters (r=16)
- Fine-tune on b-mc2/sql-create-context dataset
- Save adapters to `lora_adapters/`

**Note**: Pre-trained adapters are included via Git LFS.

### 5. Start Backend

```bash
source .venv/bin/activate
python -m uvicorn app.main:app
```

Wait for: `Model loaded and ready for inference.`

### 6. Start Frontend

```bash
cd frontend
yarn install  # or npm install
yarn dev      # or npm run dev
```

Open http://localhost:5173 in your browser.

## 💡 Usage

### Example Queries

**Rule-based (reliable):**
- "How many products do we have?"
- "What is the price of Gaming Laptop?"
- "Show all products"
- "Which region has the most sales?"

**Model-generated (may vary):**
- "Show products that cost more than 500 dollars"
- "What is the total revenue?"

### API Endpoints

- `POST /ask` - Submit natural language query
  ```json
  {
    "question": "How many products do we have?"
  }
  ```
  
  Response:
  ```json
  {
    "question": "How many products do we have?",
    "generated_sql": "SELECT COUNT(*) as product_count FROM products",
    "results": [{"product_count": 20}],
    "method": "rule-based"
  }
  ```

- `GET /health` - Check API status
- `GET /schema` - Get database schema

## 🔧 Technical Details

### Model Training

- **Base Model**: Llama-3-8B-Instruct (4-bit quantized)
- **Method**: LoRA (Low-Rank Adaptation) with r=16
- **Dataset**: b-mc2/sql-create-context (Hugging Face)
- **Training**: 1 epoch, batch size 2, gradient accumulation 4
- **Hardware**: Optimized for 12GB VRAM (RTX 4070)

### Hybrid System

The system uses a **hybrid approach**:
- **Rule-based engine**: Handles common, predictable queries (high reliability)
- **ML model**: Handles complex, open-ended queries (flexibility)

This balances accuracy and flexibility, a common pattern in production systems.

### Database Schema

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL CHECK(price >= 0)
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    sale_date TEXT NOT NULL,
    region TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## 🐛 Known Limitations

1. **Model Quality**: The model was trained on generic SQL datasets, not our specific schema. Results may vary.
2. **Training**: Only 1 epoch was used; more training would improve accuracy.
3. **Domain Mismatch**: Training data has different schemas than our sales database.

### Improvement Directions

- Create targeted training data for our schema
- Increase training epochs (3-5)
- Implement few-shot prompting
- Add RAG for dynamic schema retrieval
- Consider larger models (70B) if resources allow

## 📊 Project Status

- ✅ Database: Working (20 products, 50 sales records)
- ✅ Training: Completed (LoRA adapters saved)
- ✅ Backend API: Working (FastAPI + model inference)
- ✅ Frontend: Working (React + Tailwind UI)
- ⚠️ Model quality: Needs improvement (rule-based fallback implemented)
- ✅ End-to-end pipeline: Functional for demonstration

## 🛠️ Development

### Adding New Rule Patterns

Edit `app/main.py`, function `rule_based_sql()`:

```python
if "your pattern" in q:
    return "SELECT ... FROM ..."
```

### Modifying Training

Edit `training/train.py`:
- Adjust `num_train_epochs` for more training
- Change `r` for LoRA rank
- Modify `target_modules` for different adapter placement

## 📝 License

This project is for educational/demonstration purposes.

## 🙏 Acknowledgments

- [Unsloth](https://github.com/unslothai/unsloth) for fast fine-tuning
- [Hugging Face](https://huggingface.co/) for models and datasets
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://react.dev/) and [Tailwind CSS](https://tailwindcss.com/) for the frontend

## 📧 Contact

For questions or issues, please open an issue on GitHub.
