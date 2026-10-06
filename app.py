
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3, os, uuid, hmac
from datetime import datetime

app = Flask(__name__)
secret_key = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
app.secret_key = secret_key

# For a paid Render persistent disk, set DATA_DIR=/var/data.
DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(__file__))
os.makedirs(DATA_DIR, exist_ok=True)
DB = os.path.join(DATA_DIR, "store.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

PRODUCTS = [
    (1,"2-Tier Coffee Table",4299,"Furniture","https://images.unsplash.com/photo-1533090481720-856c6e3c1fdc?auto=format&fit=crop&w=700&q=80"),
    (2,"4 Seater Rattan Garden Set",25999,"Garden","https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=700&q=80"),
    (3,"Charcoal BBQ Grill",7499,"Outdoor","https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?auto=format&fit=crop&w=700&q=80"),
    (4,"Ottoman Storage Bed",21499,"Furniture","https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=700&q=80"),
    (5,"4 Drawer Chest",10999,"Furniture","https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=700&q=80"),
    (6,"Baby High Chair",5999,"Kids & Baby","https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?auto=format&fit=crop&w=700&q=80"),
]

def db():
    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row
    return con

def init_db():
    con=db()
    con.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT, order_no TEXT UNIQUE, name TEXT,
        email TEXT, phone TEXT, address TEXT, city TEXT, state TEXT, pincode TEXT,
        amount INTEGER, payment_method TEXT, payment_status TEXT, created_at TEXT)""")
    con.commit(); con.close()

def product(pid):
    return next((p for p in PRODUCTS if p[0]==pid),None)

@app.before_request
def secure_session_settings():
    app.config.update(
        SESSION_COOKIE_SECURE=(os.environ.get("COOKIE_SECURE", "1") == "1"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

@app.context_processor
def common():
    cart=session.get("cart",{})
    count=sum(cart.values())
    return {"cart_count":count}

@app.route("/")
def home():
    q=request.args.get("q","").strip().lower()
    items=[p for p in PRODUCTS if not q or q in p[1].lower() or q in p[3].lower()]
    return render_template("home.html", products=items, q=q)

@app.post("/cart/add/<int:pid>")
def add(pid):
    if not product(pid): return jsonify(ok=False),404
    cart=session.setdefault("cart",{})
    key=str(pid); cart[key]=cart.get(key,0)+1
    session.modified=True
    return jsonify(ok=True,count=sum(cart.values()))

@app.post("/cart/update")
def update():
    data=request.get_json() or {}
    cart={}
    for k,v in data.items():
        try:
            n=int(v)
            if n>0 and product(int(k)): cart[k]=n
        except: pass
    session["cart"]=cart
    return jsonify(ok=True)

@app.get("/cart")
def cart():
    items=[]
    total=0
    for k,qty in session.get("cart",{}).items():
        p=product(int(k))
        if p:
            subtotal=p[2]*qty; total+=subtotal
            items.append({"id":p[0],"name":p[1],"price":p[2],"qty":qty,"subtotal":subtotal,"image":p[4]})
    return render_template("cart.html",items=items,total=total)

@app.route("/checkout", methods=["GET","POST"])
def checkout():
    cart=session.get("cart",{})
    if not cart: return redirect(url_for("home"))
    total=sum(product(int(k))[2]*v for k,v in cart.items() if product(int(k)))
    if request.method=="POST":
        f=request.form
        required=["name","email","phone","address","city","state","pincode","payment_method"]
        if any(not f.get(x,"").strip() for x in required):
            return render_template("checkout.html",error="Please complete all required fields.",total=total)
        order_no="JMJ-"+datetime.now().strftime("%Y%m%d")+"-"+uuid.uuid4().hex[:6].upper()
        con=db()
        con.execute("""INSERT INTO orders(order_no,name,email,phone,address,city,state,pincode,amount,payment_method,payment_status,created_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (order_no,f["name"],f["email"],f["phone"],f["address"],f["city"],f["state"],f["pincode"],total,f["payment_method"],
                     "Payment Pending" if f["payment_method"]!="COD" else "Cash on Delivery",datetime.now().isoformat()))
        con.commit(); con.close()
        session["cart"]={}
        return render_template("success.html",order_no=order_no,total=total,payment=f["payment_method"])
    return render_template("checkout.html",total=total,error=None)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/admin/orders")
def orders():
    if not ADMIN_PASSWORD:
        return "Admin access is not configured.", 503
    supplied = request.authorization.password if request.authorization else None
    if not supplied or not hmac.compare_digest(supplied, ADMIN_PASSWORD):
        return ("Authentication required", 401, {"WWW-Authenticate": 'Basic realm="JMJ Enterprise Admin"'})
    con=db(); rows=con.execute("SELECT * FROM orders ORDER BY id DESC").fetchall(); con.close()
    return render_template("orders.html",orders=rows)

# Initialize the database when the module is loaded by Gunicorn.
init_db()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
