import os
import re
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from unsloth import FastLanguageModel


# ---------------------------------------------------------------------------
# Paths (relative to this file's location)
# ---------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
LORA_ADAPTERS_PATH = PROJECT_ROOT / "lora_adapters"
DATABASE_PATH = PROJECT_ROOT / "sales_data.db"


# ---------------------------------------------------------------------------
# Prompt template with few-shot example
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
Convert the following question to a SQL query for a SQLite database. Only output the SQL query, nothing else.

Example:
Question: How many products are there?
SQL: SELECT COUNT(*) FROM products

Question: {question}

### Input:
Database schema:
{context}

### Response:
"""


# ---------------------------------------------------------------------------
# Simple rule-based SQL generator for common queries (fallback/demo mode)
# ---------------------------------------------------------------------------
def rule_based_sql(question: str) -> str | None:
    """
    Generate SQL for common question patterns using simple rules.
    Returns None if no rule matches (then use the model).
    """
    q = question.lower().strip()
    
    # Count queries
    if "how many products" in q or "count" in q and "product" in q:
        return "SELECT COUNT(*) as product_count FROM products"
    
    if "how many sales" in q or "count" in q and "sales" in q:
        return "SELECT COUNT(*) as sales_count FROM sales"
    
    # List all
    if "show all products" in q or "list all products" in q or "all products" in q:
        return "SELECT * FROM products"
    
    if "show all sales" in q or "list all sales" in q or "all sales" in q:
        return "SELECT * FROM sales LIMIT 20"
    
    # Price queries
    if "price" in q:
        # Extract product name if mentioned
        products = ["gaming laptop", "mechanical keyboard", "wireless mouse", "monitor", 
                    "headphones", "smartphone", "smartwatch", "router", "chair", "desk",
                    "lamp", "bookshelf", "coffee table", "water bottle", "backpack",
                    "phone case", "running shoes", "hoodie", "ssd", "docking station"]
        for product in products:
            if product in q:
                return f"SELECT name, price FROM products WHERE LOWER(name) LIKE '%{product}%'"
        # If no specific product, show all prices
        if "highest" in q or "most expensive" in q:
            return "SELECT name, price FROM products ORDER BY price DESC LIMIT 5"
        if "lowest" in q or "cheapest" in q:
            return "SELECT name, price FROM products ORDER BY price ASC LIMIT 5"
        return "SELECT name, price FROM products ORDER BY price DESC"
    
    # Category queries
    if "category" in q or "categories" in q:
        if "how many" in q or "count" in q:
            return "SELECT category, COUNT(*) as count FROM products GROUP BY category"
        return "SELECT DISTINCT category FROM products"
    
    # Region queries
    if "region" in q:
        if "sales" in q or "most" in q or "highest" in q:
            return "SELECT region, SUM(quantity) as total_sales FROM sales GROUP BY region ORDER BY total_sales DESC"
        return "SELECT DISTINCT region FROM sales"
    
    # Total sales
    if "total sales" in q or "total quantity" in q:
        return "SELECT SUM(quantity) as total_quantity FROM sales"
    
    # Top products
    if "top" in q and "product" in q:
        return """SELECT p.name, SUM(s.quantity) as total_sold 
                  FROM products p 
                  JOIN sales s ON p.id = s.product_id 
                  GROUP BY p.id 
                  ORDER BY total_sold DESC 
                  LIMIT 5"""
    
    # Revenue
    if "revenue" in q or "money" in q or "earned" in q:
        return """SELECT SUM(p.price * s.quantity) as total_revenue 
                  FROM products p 
                  JOIN sales s ON p.id = s.product_id"""
    
    # Average
    if "average price" in q:
        return "SELECT AVG(price) as average_price FROM products"
    
    if "average" in q and "sales" in q:
        return "SELECT AVG(quantity) as average_quantity FROM sales"
    
    # No rule matched
    return None


# ---------------------------------------------------------------------------
# Global model / tokenizer (loaded once at startup)
# ---------------------------------------------------------------------------
model = None
tokenizer = None


# ---------------------------------------------------------------------------
# Lifespan: load model on startup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, tokenizer
    print(f"Loading model from {LORA_ADAPTERS_PATH} ...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(LORA_ADAPTERS_PATH),
        max_seq_length=2048,
        load_in_4bit=True,
    )
    # Enable faster inference mode
    FastLanguageModel.for_inference(model)
    print("Model loaded and ready for inference.")
    yield
    # Cleanup (if needed) on shutdown
    model = None
    tokenizer = None


app = FastAPI(title="NL-to-SQL API", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Pydantic request model
# ---------------------------------------------------------------------------
class QueryRequest(BaseModel):
    question: str


# ---------------------------------------------------------------------------
# Helper: get CREATE TABLE statements from the database
# ---------------------------------------------------------------------------
def get_database_schema(db_path: Path) -> str:
    """Return all CREATE TABLE statements from the SQLite database."""
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL"
        )
        rows = cursor.fetchall()
        return "\n\n".join(row[0] for row in rows)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Helper: extract SQL from model output
# ---------------------------------------------------------------------------
def extract_sql(text: str) -> str:
    """
    Extract the FIRST SQL query from the model's response.
    """
    # First, try to get text after "### Response:"
    response_match = re.search(r"###\s*Response:\s*(.*)", text, re.DOTALL | re.IGNORECASE)
    if response_match:
        text = response_match.group(1).strip()
    
    # Try to match SQL inside code fences
    fence_match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()

    # Get just the first line or first statement
    lines = text.strip().split('\n')
    first_line = lines[0].strip() if lines else text.strip()
    
    # If first line starts with SQL keyword, use it
    if re.match(r'^(SELECT|INSERT|UPDATE|DELETE|WITH)\b', first_line, re.IGNORECASE):
        # Stop at UNION if present
        union_pos = first_line.upper().find(' UNION ')
        if union_pos > 0:
            first_line = first_line[:union_pos].strip()
        return first_line.rstrip(';').strip()

    # Try to find any SQL statement in the text
    sql_match = re.search(
        r"(SELECT\s+.*?\s+FROM\s+\w+(?:\s+(?:WHERE|JOIN|GROUP BY|ORDER BY|LIMIT|HAVING)[^;]*)?)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if sql_match:
        sql = sql_match.group(1).strip()
        # Stop at UNION
        union_pos = sql.upper().find(' UNION ')
        if union_pos > 0:
            sql = sql[:union_pos].strip()
        return sql.rstrip(';').strip()

    return first_line.rstrip(';').strip() if first_line else text.strip()


# ---------------------------------------------------------------------------
# Helper: execute SQL and return rows as list of dicts
# ---------------------------------------------------------------------------
def execute_sql(db_path: Path, sql: str) -> list[dict[str, Any]]:
    """Execute a read-only SQL query and return results as JSON-serializable dicts."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# POST /ask endpoint
# ---------------------------------------------------------------------------
@app.post("/ask")
def ask(request: QueryRequest):
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    # 1) Try rule-based SQL first (for demo reliability)
    sql = rule_based_sql(request.question)
    used_rules = sql is not None
    
    if sql:
        print(f"\n{'='*60}")
        print(f"Question: {request.question}")
        print(f"Using RULE-BASED SQL: {sql}")
        print(f"{'='*60}\n")
    else:
        # 2) Fall back to model generation
        schema = get_database_schema(DATABASE_PATH)
        prompt = PROMPT_TEMPLATE.format(question=request.question, context=schema)
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=False,
            temperature=0.1,
            repetition_penalty=1.2,
        )

        prompt_length = inputs['input_ids'].shape[1]
        generated_tokens = outputs[0][prompt_length:]
        generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        print(f"\n{'='*60}")
        print(f"Question: {request.question}")
        print(f"Using MODEL-GENERATED SQL")
        print(f"Generated text:\n{generated_text}")
        print(f"{'='*60}")

        sql = extract_sql(generated_text)
        print(f"Extracted SQL: {sql}")
        print(f"{'='*60}\n")
    
    # If SQL is empty, return error
    if not sql or len(sql) < 5:
        raise HTTPException(
            status_code=400, 
            detail="Could not generate valid SQL for this question."
        )

    # Execute SQL and get results
    try:
        results = execute_sql(DATABASE_PATH, sql)
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=400, 
            detail=f"SQL execution error: {e}. Generated SQL: {sql}"
        )

    return {
        "question": request.question,
        "generated_sql": sql,
        "results": results,
        "method": "rule-based" if used_rules else "model-generated"
    }


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


# ---------------------------------------------------------------------------
# Debug endpoint: test SQL extraction without model
# ---------------------------------------------------------------------------
@app.get("/schema")
def get_schema():
    """Return the database schema (for debugging)."""
    schema = get_database_schema(DATABASE_PATH)
    return {"schema": schema}
