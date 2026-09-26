from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Document
from dotenv import load_dotenv
import os 

load_dotenv()

# connect to Qdrant Cloud
client = QdrantClient(
    url=os.getenv("QDRANT_CLUSTER_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY"),
    cloud_inference=True
)

client.create_collection(
    collection_name="items",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

menu_items = [
    ("Pad Thai with Tofu", "Stir-fried rice noodles with tofu bean sprouts scallions and crushed peanuts in traditional tamarind sauce", "$13.95", "Noodles"),
    ("Grilled Salmon Fillet", "Wild-caught Atlantic salmon grilled with lemon butter and fresh herbs served with seasonal vegetables", "$24.50", "Seafood Entrees"),
    ("Mushroom Risotto", "Creamy arborio rice with mixed mushrooms parmesan truffle oil and fresh thyme", "$16.75", "Vegetarian"),
    ("Bibimbap Bowl", "Korean rice bowl with seasoned vegetables fried egg gochujang sauce and choice of protein", "$14.50", "Korean Bowls"),
    ("Falafel Wrap", "Crispy chickpea fritters with hummus tahini cucumber tomato and pickled vegetables in warm pita", "$11.25", "Mediterranean"),
    ("Shrimp Tacos", "Three soft tacos with grilled shrimp cabbage slaw chipotle aioli and fresh lime", "$13.00", "Tacos"),
    ("Vegetable Curry", "Mixed vegetables in aromatic coconut curry sauce with jasmine rice and naan bread", "$12.95", "Indian Curries")
]

# Upload the items to the Qdrant collection
points = []
for i, item in enumerate(menu_items):
    points.append(
        PointStruct(
            id=i,
            vector=Document(text=item[1], model="sentence-transformers/all-MiniLM-L6-v2"),
            payload={
                "item_name": item[0],
                "description": item[1],
                "price": item[2],
                "category": item[3]
            }
        )
    )

client.upsert(
    collection_name="items",
    points=points
)

query_text = "vegetarian dishes"

# search for similar menu items
results = client.query_points(
    collection_name="items",
    query=Document(text=query_text, model="sentence-transformers/all-MiniLM-L6-v2"),
    with_payload=True,
    limit=5
)

# print results
for result in results.points:
    print(f"Item: {result.payload.get('item_name', 'N/A')}")
    print(f"Score: {result.score}")
    print(f"Description: {result.payload['description'][:150]}...")
    print(f"Price: {result.payload.get('price', 'N/A')}")
    print("---")