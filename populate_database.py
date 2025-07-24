from sqlmodel import Session, select
from app.database import engine
from app.models import (
    User, Product, Order, OrderProduct, Tag, ProductTag, UserFavoriteTag
)
from datetime import datetime, timedelta
import random

def populate_database():
    with Session(engine) as session:
        # Clear existing data using modern SQLModel approach
        # Delete in correct order to respect foreign key constraints
        user_favorite_tags = session.exec(select(UserFavoriteTag)).all()
        for uft in user_favorite_tags:
            session.delete(uft)
            
        product_tags = session.exec(select(ProductTag)).all()
        for pt in product_tags:
            session.delete(pt)
            
        order_products = session.exec(select(OrderProduct)).all()
        for op in order_products:
            session.delete(op)
            
        orders = session.exec(select(Order)).all()
        for order in orders:
            session.delete(order)
            
        products = session.exec(select(Product)).all()
        for product in products:
            session.delete(product)
            
        users = session.exec(select(User)).all()
        for user in users:
            session.delete(user)
            
        tags = session.exec(select(Tag)).all()
        for tag in tags:
            session.delete(tag)
        session.commit()
        
        # Create brands (12 brands)
        brands = [
            "Logitech", "Razer", "Corsair", "SteelSeries", "HyperX", "ASUS",
            "MSI", "Gigabyte", "Samsung", "LG", "Dell", "HP", "Blue"
        ]
        
        brand_tags = []
        for brand in brands:
            tag = Tag(name=brand)
            session.add(tag)
            brand_tags.append(tag)
        
        # Create categories (24 categories)
        categories = [
            "Gaming", "Wireless", "RGB", "Mechanical", "Silent", "Ergonomic",
            "Ultra-wide", "4K", "144Hz", "Bluetooth", "USB-C", "Thunderbolt",
            "Noise-cancelling", "Streaming", "Professional", "Budget",
            "Premium", "Compact", "Portable", "Durable", "Waterproof",
            "Customizable", "Multi-device", "Low-latency"
        ]
        
        category_tags = []
        for category in categories:
            tag = Tag(name=category)
            session.add(tag)
            category_tags.append(tag)
        
        session.commit()
        
        # Create products (computer peripherals)
        # Note: 2 products will be out of stock (stock_quantity = 0)
        # 1 product will be below low-stock margin (stock_quantity < min_stock_level)
        products_data = [
            # Mice
            ("Logitech G Pro X Superlight", "Mouse", "Logitech", 149.99, 50, 10, ["Logitech", "Gaming", "Wireless", "Lightweight"]),
            ("Razer DeathAdder V3 Pro", "Mouse", "Razer", 159.99, 45, 8, ["Razer", "Gaming", "Wireless", "Ergonomic"]),
            ("Corsair M65 RGB Ultra", "Mouse", "Corsair", 89.99, 60, 12, ["Corsair", "Gaming", "RGB", "Durable"]),
            ("SteelSeries Prime Wireless", "Mouse", "SteelSeries", 129.99, 40, 8, ["SteelSeries", "Gaming", "Wireless", "Professional"]),
            ("Logitech MX Master 3S", "Mouse", "Logitech", 99.99, 70, 15, ["Logitech", "Professional", "Silent", "Multi-device"]),
            
            # Keyboards
            ("Razer BlackWidow V3 Pro", "Keyboard", "Razer", 229.99, 35, 8, ["Razer", "Gaming", "Wireless", "Mechanical"]),
            ("Corsair K100 RGB", "Keyboard", "Corsair", 249.99, 30, 6, ["Corsair", "Gaming", "RGB", "Premium"]),
            ("SteelSeries Apex Pro", "Keyboard", "SteelSeries", 199.99, 40, 8, ["SteelSeries", "Gaming", "Customizable", "Professional"]),
            ("HyperX Alloy Origins", "Keyboard", "HyperX", 89.99, 55, 12, ["HyperX", "Gaming", "Compact", "Budget"]),
            ("Logitech G915 TKL", "Keyboard", "Logitech", 179.99, 45, 10, ["Logitech", "Gaming", "Wireless", "RGB"]),
            
            # Headsets
            ("HyperX Cloud Alpha", "Headset", "HyperX", 99.99, 65, 15, ["HyperX", "Gaming", "Noise-cancelling", "Durable"]),
            ("Razer BlackShark V2 Pro", "Headset", "Razer", 179.99, 40, 8, ["Razer", "Gaming", "Wireless", "Noise-cancelling"]),
            ("SteelSeries Arctis Pro", "Headset", "SteelSeries", 199.99, 35, 8, ["SteelSeries", "Gaming", "Premium", "Streaming"]),
            ("Corsair Virtuoso RGB", "Headset", "Corsair", 189.99, 38, 8, ["Corsair", "Gaming", "RGB", "Wireless"]),
            ("Logitech G Pro X", "Headset", "Logitech", 129.99, 50, 12, ["Logitech", "Gaming", "Professional", "Customizable"]),
            
            # Monitors
            ("Samsung Odyssey G9", "Monitor", "Samsung", 999.99, 20, 5, ["Samsung", "Gaming", "Ultra-wide", "144Hz"]),
            ("LG 27GL850", "Monitor", "LG", 449.99, 45, 10, ["LG", "Gaming", "4K", "Professional"]),
            ("ASUS ROG Swift PG279Q", "Monitor", "ASUS", 699.99, 30, 6, ["ASUS", "Gaming", "144Hz", "Premium"]),
            ("MSI Optix MAG274QRF", "Monitor", "MSI", 399.99, 40, 8, ["MSI", "Gaming", "144Hz", "Budget"]),
            ("Dell UltraSharp U2720Q", "Monitor", "Dell", 549.99, 35, 8, ["Dell", "Professional", "4K", "Ergonomic"]),
            
            # Webcams
            ("Logitech StreamCam", "Webcam", "Logitech", 169.99, 60, 15, ["Logitech", "Streaming", "USB-C", "4K"]),
            ("Razer Kiyo Pro", "Webcam", "Razer", 199.99, 45, 10, ["Razer", "Streaming", "4K", "Premium"]),
            ("HyperX Vision S", "Webcam", "HyperX", 149.99, 50, 12, ["HyperX", "Streaming", "1080p", "Budget"]),
            
            # Microphones
            ("Blue Yeti X", "Microphone", "Blue", 169.99, 55, 12, ["Blue", "Streaming", "Professional", "USB-C"]),
            ("HyperX QuadCast", "Microphone", "HyperX", 139.99, 60, 15, ["HyperX", "Streaming", "RGB", "Budget"]),
            ("Razer Seiren X", "Microphone", "Razer", 99.99, 70, 18, ["Razer", "Streaming", "Compact", "Budget"]),
            
            # Mousepads
            ("SteelSeries QcK", "Mousepad", "SteelSeries", 19.99, 100, 25, ["SteelSeries", "Gaming", "Budget", "Durable"]),
            ("Corsair MM300", "Mousepad", "Corsair", 24.99, 90, 20, ["Corsair", "Gaming", "RGB", "Premium"]),
            ("Razer Goliathus", "Mousepad", "Razer", 29.99, 85, 20, ["Razer", "Gaming", "RGB", "Customizable"]),
            
            # Speakers
            ("Logitech Z623", "Speakers", "Logitech", 129.99, 45, 10, ["Logitech", "Budget", "2.1", "Durable"]),
            ("Razer Nommo Pro", "Speakers", "Razer", 499.99, 25, 5, ["Razer", "Premium", "2.1", "Gaming"]),
            ("Corsair SP2500", "Speakers", "Corsair", 199.99, 35, 8, ["Corsair", "Gaming", "2.1", "RGB"]),
        ]
        
        # Modify specific products for stock scenarios
        # Product 1: Out of stock (Samsung Odyssey G9 - expensive monitor)
        products_data[15] = ("Samsung Odyssey G9", "Monitor", "Samsung", 999.99, 0, 5, ["Samsung", "Gaming", "Ultra-wide", "144Hz"])
        
        # Product 2: Out of stock (Razer BlackWidow V3 Pro - popular keyboard)
        products_data[5] = ("Razer BlackWidow V3 Pro", "Keyboard", "Razer", 229.99, 0, 8, ["Razer", "Gaming", "Wireless", "Mechanical"])
        
        # Product 3: Below low-stock margin (SteelSeries Arctis Pro - stock 3, min_stock 8)
        products_data[12] = ("SteelSeries Arctis Pro", "Headset", "SteelSeries", 199.99, 3, 8, ["SteelSeries", "Gaming", "Premium", "Streaming"])
        
        products = []
        for name, product_type, brand, price, stock, min_stock, tag_names in products_data:
            product = Product(
                name=name,
                type=product_type,
                brand=brand,
                price=price,
                stock_quantity=stock,
                min_stock_level=min_stock
            )
            session.add(product)
            products.append(product)
        
        session.commit()
        
        # Add tags to products
        for product, (name, product_type, brand, price, stock, min_stock, tag_names) in zip(products, products_data):
            for tag_name in tag_names:
                tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
                if tag:
                    product_tag = ProductTag(product_id=product.id, tag_id=tag.id)
                    session.add(product_tag)
        
        session.commit()
        
        # Create users with names reflecting their interests
        users_data = [
            ("John Gaming", ["Gaming", "Razer", "RGB"]),
            ("Sarah Professional", ["Professional", "Dell", "Ergonomic"]),
            ("Mike Streaming", ["Streaming", "HyperX", "USB-C"]),
            ("Emma Wireless", ["Wireless", "Logitech", "Bluetooth"]),
            ("Alex Budget", ["Budget", "MSI", "Compact"]),
            ("Lisa Premium", ["Premium", "Corsair", "4K"]),
            ("Tom Mechanical", ["Mechanical", "SteelSeries", "Customizable"]),
            ("Rachel Silent", ["Silent", "Logitech", "Noise-cancelling"]),
            ("David Ultra-wide", ["Ultra-wide", "Samsung", "144Hz"]),
            ("Jessica Portable", ["Portable", "HP", "Compact"]),
            ("Chris RGB", ["RGB", "Corsair", "Gaming"]),
            ("Maria Ergonomic", ["Ergonomic", "Dell", "Professional"]),
        ]
        
        users = []
        for name, favorite_tag_names in users_data:
            user = User(name=name, is_member=random.choice([True, False]))
            session.add(user)
            users.append(user)
        
        session.commit()
        
        # Add favorite tags to users
        for user, (name, favorite_tag_names) in zip(users, users_data):
            for tag_name in favorite_tag_names:
                tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
                if tag:
                    user_favorite = UserFavoriteTag(user_id=user.id, tag_id=tag.id)
                    session.add(user_favorite)
        
        session.commit()
        
        # Create orders for each user (at least 3 per user)
        order_dates = [
            datetime.now() - timedelta(days=random.randint(1, 365)),
            datetime.now() - timedelta(days=random.randint(1, 365)),
            datetime.now() - timedelta(days=random.randint(1, 365)),
            datetime.now() - timedelta(days=random.randint(1, 365)),
            datetime.now() - timedelta(days=random.randint(1, 365))
        ]
        
        for user in users:
            # Create 3-5 orders per user
            num_orders = random.randint(3, 5)
            for i in range(num_orders):
                order = Order(
                    user_id=user.id,
                    date=order_dates[i] if i < len(order_dates) else datetime.now() - timedelta(days=random.randint(1, 365))
                )
                session.add(order)
                session.commit()
                
                # Add 1-3 products to each order
                num_products = random.randint(1, 3)
                selected_products = random.sample(products, min(num_products, len(products)))
                
                final_price = 0
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    order_product = OrderProduct(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=quantity
                    )
                    session.add(order_product)
                    final_price += product.price * quantity
                
                order.final_price = final_price
                session.commit()
        
        print("Database populated successfully!")
        print(f"Created {len(brands)} brands and {len(categories)} categories")
        print(f"Created {len(products)} products")
        print(f"Created {len(users)} users")
        print("Created orders for all users (3-5 orders each)")
        print("\nStock Status:")
        print("- Samsung Odyssey G9: OUT OF STOCK (0 units)")
        print("- Razer BlackWidow V3 Pro: OUT OF STOCK (0 units)")
        print("- SteelSeries Arctis Pro: LOW STOCK (3 units, min_stock: 8)")

if __name__ == "__main__":
    populate_database() 