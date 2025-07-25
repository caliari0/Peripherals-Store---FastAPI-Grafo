from sqlmodel import Session, select
from app.database import engine
from app.models import (
    User,
    Product,
    Order,
    OrderProduct,
    Tag,
    ProductTag,
)
from datetime import datetime, timedelta
import random


def populate_database():
    with Session(engine) as session:
        # Clear existing data using modern SQLModel approach
        # Delete in correct order to respect foreign key constraints

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
            "Logitech",
            "Razer",
            "Corsair",
            "SteelSeries",
            "HyperX",
            "ASUS",
            "MSI",
            "Gigabyte",
            "Samsung",
            "LG",
            "Dell",
            "HP",
            "Blue",
        ]

        brand_tags = []
        for brand in brands:
            tag = Tag(name=brand)
            session.add(tag)
            brand_tags.append(tag)

        # Create categories (24 categories)
        categories = [
            "Gaming",
            "Wireless",
            "RGB",
            "Mechanical",
            "Silent",
            "Ergonomic",
            "Ultra-wide",
            "4K",
            "144Hz",
            "Bluetooth",
            "USB-C",
            "Thunderbolt",
            "Noise-cancelling",
            "Streaming",
            "Professional",
            "Budget",
            "Premium",
            "Compact",
            "Portable",
            "Durable",
            "Waterproof",
            "Customizable",
            "Multi-device",
            "Low-latency",
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
            (
                "Logitech G Pro X Superlight",
                "Mouse",
                "Logitech",
                149.99,
                50,
                10,
                ["Logitech", "Gaming", "Wireless", "Lightweight"],
            ),
            (
                "Razer DeathAdder V3 Pro",
                "Mouse",
                "Razer",
                159.99,
                45,
                8,
                ["Razer", "Gaming", "Wireless", "Ergonomic"],
            ),
            (
                "Corsair M65 RGB Ultra",
                "Mouse",
                "Corsair",
                89.99,
                60,
                12,
                ["Corsair", "Gaming", "RGB", "Durable"],
            ),
            (
                "SteelSeries Prime Wireless",
                "Mouse",
                "SteelSeries",
                129.99,
                40,
                8,
                ["SteelSeries", "Gaming", "Wireless", "Professional"],
            ),
            (
                "Logitech MX Master 3S",
                "Mouse",
                "Logitech",
                99.99,
                70,
                15,
                ["Logitech", "Professional", "Silent", "Multi-device"],
            ),
            # Keyboards
            (
                "Razer BlackWidow V3 Pro",
                "Keyboard",
                "Razer",
                229.99,
                35,
                8,
                ["Razer", "Gaming", "Wireless", "Mechanical"],
            ),
            (
                "Corsair K100 RGB",
                "Keyboard",
                "Corsair",
                249.99,
                30,
                6,
                ["Corsair", "Gaming", "RGB", "Premium"],
            ),
            (
                "SteelSeries Apex Pro",
                "Keyboard",
                "SteelSeries",
                199.99,
                40,
                8,
                ["SteelSeries", "Gaming", "Customizable", "Professional"],
            ),
            (
                "HyperX Alloy Origins",
                "Keyboard",
                "HyperX",
                89.99,
                55,
                12,
                ["HyperX", "Gaming", "Compact", "Budget"],
            ),
            (
                "Logitech G915 TKL",
                "Keyboard",
                "Logitech",
                179.99,
                45,
                10,
                ["Logitech", "Gaming", "Wireless", "RGB"],
            ),
            # Headsets
            (
                "HyperX Cloud Alpha",
                "Headset",
                "HyperX",
                99.99,
                65,
                15,
                ["HyperX", "Gaming", "Noise-cancelling", "Durable"],
            ),
            (
                "Razer BlackShark V2 Pro",
                "Headset",
                "Razer",
                179.99,
                40,
                8,
                ["Razer", "Gaming", "Wireless", "Noise-cancelling"],
            ),
            (
                "SteelSeries Arctis Pro",
                "Headset",
                "SteelSeries",
                199.99,
                35,
                8,
                ["SteelSeries", "Gaming", "Premium", "Streaming"],
            ),
            (
                "Corsair Virtuoso RGB",
                "Headset",
                "Corsair",
                189.99,
                38,
                8,
                ["Corsair", "Gaming", "RGB", "Wireless"],
            ),
            (
                "Logitech G Pro X",
                "Headset",
                "Logitech",
                129.99,
                50,
                12,
                ["Logitech", "Gaming", "Professional", "Customizable"],
            ),
            # Monitors
            (
                "Samsung Odyssey G9",
                "Monitor",
                "Samsung",
                999.99,
                20,
                5,
                ["Samsung", "Gaming", "Ultra-wide", "144Hz"],
            ),
            (
                "LG 27GL850",
                "Monitor",
                "LG",
                449.99,
                45,
                10,
                ["LG", "Gaming", "4K", "Professional"],
            ),
            (
                "ASUS ROG Swift PG279Q",
                "Monitor",
                "ASUS",
                699.99,
                30,
                6,
                ["ASUS", "Gaming", "144Hz", "Premium"],
            ),
            (
                "MSI Optix MAG274QRF",
                "Monitor",
                "MSI",
                399.99,
                40,
                8,
                ["MSI", "Gaming", "144Hz", "Budget"],
            ),
            (
                "Dell UltraSharp U2720Q",
                "Monitor",
                "Dell",
                549.99,
                35,
                8,
                ["Dell", "Professional", "4K", "Ergonomic"],
            ),
            # Webcams
            (
                "Logitech StreamCam",
                "Webcam",
                "Logitech",
                169.99,
                60,
                15,
                ["Logitech", "Streaming", "USB-C", "4K"],
            ),
            (
                "Razer Kiyo Pro",
                "Webcam",
                "Razer",
                199.99,
                45,
                10,
                ["Razer", "Streaming", "4K", "Premium"],
            ),
            (
                "HyperX Vision S",
                "Webcam",
                "HyperX",
                149.99,
                50,
                12,
                ["HyperX", "Streaming", "1080p", "Budget"],
            ),
            # Microphones
            (
                "Blue Yeti X",
                "Microphone",
                "Blue",
                169.99,
                55,
                12,
                ["Blue", "Streaming", "Professional", "USB-C"],
            ),
            (
                "HyperX QuadCast",
                "Microphone",
                "HyperX",
                139.99,
                60,
                15,
                ["HyperX", "Streaming", "RGB", "Budget"],
            ),
            (
                "Razer Seiren X",
                "Microphone",
                "Razer",
                99.99,
                70,
                18,
                ["Razer", "Streaming", "Compact", "Budget"],
            ),
            # Mousepads
            (
                "SteelSeries QcK",
                "Mousepad",
                "SteelSeries",
                19.99,
                100,
                25,
                ["SteelSeries", "Gaming", "Budget", "Durable"],
            ),
            (
                "Corsair MM300",
                "Mousepad",
                "Corsair",
                24.99,
                90,
                20,
                ["Corsair", "Gaming", "RGB", "Premium"],
            ),
            (
                "Razer Goliathus",
                "Mousepad",
                "Razer",
                29.99,
                85,
                20,
                ["Razer", "Gaming", "RGB", "Customizable"],
            ),
            # Speakers
            (
                "Logitech Z623",
                "Speakers",
                "Logitech",
                129.99,
                45,
                10,
                ["Logitech", "Budget", "2.1", "Durable"],
            ),
            (
                "Razer Nommo Pro",
                "Speakers",
                "Razer",
                499.99,
                25,
                5,
                ["Razer", "Premium", "2.1", "Gaming"],
            ),
            (
                "Corsair SP2500",
                "Speakers",
                "Corsair",
                199.99,
                35,
                8,
                ["Corsair", "Gaming", "2.1", "RGB"],
            ),
            # Additional 40 varied peripherals
            # Additional Mice
            (
                "Logitech G502 HERO",
                "Mouse",
                "Logitech",
                79.99,
                80,
                15,
                ["Logitech", "Gaming", "RGB", "Durable"],
            ),
            (
                "Razer Viper Mini",
                "Mouse",
                "Razer",
                39.99,
                95,
                20,
                ["Razer", "Gaming", "Compact", "Budget"],
            ),
            (
                "Corsair Harpoon RGB",
                "Mouse",
                "Corsair",
                49.99,
                85,
                18,
                ["Corsair", "Gaming", "RGB", "Budget"],
            ),
            (
                "SteelSeries Rival 3",
                "Mouse",
                "SteelSeries",
                29.99,
                100,
                25,
                ["SteelSeries", "Gaming", "Budget", "Compact"],
            ),
            (
                "HyperX Pulsefire Haste",
                "Mouse",
                "HyperX",
                59.99,
                75,
                15,
                ["HyperX", "Gaming", "Lightweight", "Budget"],
            ),
            (
                "ASUS ROG Gladius II",
                "Mouse",
                "ASUS",
                89.99,
                65,
                12,
                ["ASUS", "Gaming", "RGB", "Durable"],
            ),
            (
                "MSI Clutch GM08",
                "Mouse",
                "MSI",
                34.99,
                90,
                20,
                ["MSI", "Gaming", "Budget", "Compact"],
            ),
            (
                "Gigabyte AORUS M2",
                "Mouse",
                "Gigabyte",
                44.99,
                80,
                18,
                ["Gigabyte", "Gaming", "RGB", "Budget"],
            ),
            # Additional Keyboards
            (
                "Logitech G413",
                "Keyboard",
                "Logitech",
                69.99,
                85,
                18,
                ["Logitech", "Gaming", "Mechanical", "Budget"],
            ),
            (
                "Razer Huntsman Mini",
                "Keyboard",
                "Razer",
                119.99,
                60,
                12,
                ["Razer", "Gaming", "Mechanical", "Compact"],
            ),
            (
                "Corsair K70 RGB",
                "Keyboard",
                "Corsair",
                169.99,
                55,
                10,
                ["Corsair", "Gaming", "RGB", "Mechanical"],
            ),
            (
                "SteelSeries Apex 3",
                "Keyboard",
                "SteelSeries",
                49.99,
                90,
                20,
                ["SteelSeries", "Gaming", "Budget", "Silent"],
            ),
            (
                "HyperX Alloy FPS",
                "Keyboard",
                "HyperX",
                79.99,
                75,
                15,
                ["HyperX", "Gaming", "Mechanical", "Compact"],
            ),
            (
                "ASUS ROG Strix Scope",
                "Keyboard",
                "ASUS",
                129.99,
                65,
                12,
                ["ASUS", "Gaming", "RGB", "Mechanical"],
            ),
            (
                "MSI Vigor GK30",
                "Keyboard",
                "MSI",
                39.99,
                95,
                25,
                ["MSI", "Gaming", "Budget", "RGB"],
            ),
            (
                "Gigabyte AORUS K1",
                "Keyboard",
                "Gigabyte",
                54.99,
                80,
                18,
                ["Gigabyte", "Gaming", "RGB", "Budget"],
            ),
            # Additional Headsets
            (
                "Logitech G733",
                "Headset",
                "Logitech",
                149.99,
                55,
                10,
                ["Logitech", "Gaming", "Wireless", "RGB"],
            ),
            (
                "Razer Kraken X",
                "Headset",
                "Razer",
                49.99,
                90,
                20,
                ["Razer", "Gaming", "Lightweight", "Budget"],
            ),
            (
                "Corsair HS60 Pro",
                "Headset",
                "Corsair",
                79.99,
                75,
                15,
                ["Corsair", "Gaming", "Noise-cancelling", "Budget"],
            ),
            (
                "SteelSeries Arctis 1",
                "Headset",
                "SteelSeries",
                59.99,
                85,
                18,
                ["SteelSeries", "Gaming", "Budget", "Portable"],
            ),
            (
                "HyperX Cloud Stinger",
                "Headset",
                "HyperX",
                39.99,
                95,
                25,
                ["HyperX", "Gaming", "Budget", "Lightweight"],
            ),
            (
                "ASUS ROG Delta",
                "Headset",
                "ASUS",
                199.99,
                45,
                8,
                ["ASUS", "Gaming", "Premium", "RGB"],
            ),
            (
                "MSI Immerse GH30",
                "Headset",
                "MSI",
                29.99,
                100,
                25,
                ["MSI", "Gaming", "Budget", "Lightweight"],
            ),
            (
                "Gigabyte AORUS H1",
                "Headset",
                "Gigabyte",
                69.99,
                80,
                18,
                ["Gigabyte", "Gaming", "RGB", "Budget"],
            ),
            # Additional Monitors
            (
                "Samsung CRG9",
                "Monitor",
                "Samsung",
                899.99,
                25,
                5,
                ["Samsung", "Gaming", "Ultra-wide", "120Hz"],
            ),
            (
                "LG 34GN850",
                "Monitor",
                "LG",
                799.99,
                30,
                6,
                ["LG", "Gaming", "Ultra-wide", "144Hz"],
            ),
            (
                "ASUS TUF VG27AQ",
                "Monitor",
                "ASUS",
                429.99,
                50,
                10,
                ["ASUS", "Gaming", "144Hz", "Budget"],
            ),
            (
                "MSI Optix G241",
                "Monitor",
                "MSI",
                199.99,
                70,
                15,
                ["MSI", "Gaming", "144Hz", "Budget"],
            ),
            (
                "Dell S2721DGF",
                "Monitor",
                "Dell",
                399.99,
                55,
                10,
                ["Dell", "Gaming", "144Hz", "Professional"],
            ),
            (
                "HP Omen 27i",
                "Monitor",
                "HP",
                349.99,
                60,
                12,
                ["HP", "Gaming", "144Hz", "Budget"],
            ),
            (
                "Gigabyte G27Q",
                "Monitor",
                "Gigabyte",
                299.99,
                65,
                12,
                ["Gigabyte", "Gaming", "144Hz", "Budget"],
            ),
            # Additional Webcams
            (
                "Logitech C920",
                "Webcam",
                "Logitech",
                89.99,
                85,
                18,
                ["Logitech", "Streaming", "1080p", "Budget"],
            ),
            (
                "Razer Kiyo",
                "Webcam",
                "Razer",
                99.99,
                75,
                15,
                ["Razer", "Streaming", "1080p", "RGB"],
            ),
            (
                "Corsair StreamCam",
                "Webcam",
                "Corsair",
                159.99,
                60,
                12,
                ["Corsair", "Streaming", "1080p", "Premium"],
            ),
            (
                "SteelSeries StreamCam",
                "Webcam",
                "SteelSeries",
                129.99,
                70,
                15,
                ["SteelSeries", "Streaming", "1080p", "Professional"],
            ),
            (
                "ASUS Webcam",
                "Webcam",
                "ASUS",
                79.99,
                80,
                18,
                ["ASUS", "Streaming", "1080p", "Budget"],
            ),
            (
                "MSI Webcam",
                "Webcam",
                "MSI",
                69.99,
                85,
                20,
                ["MSI", "Streaming", "720p", "Budget"],
            ),
            # Additional Microphones
            (
                "Blue Yeti",
                "Microphone",
                "Blue",
                129.99,
                70,
                15,
                ["Blue", "Streaming", "Professional", "USB-C"],
            ),
            (
                "Logitech Blue Sona",
                "Microphone",
                "Logitech",
                399.99,
                30,
                5,
                ["Logitech", "Streaming", "Premium", "Professional"],
            ),
            (
                "Corsair Elgato Wave 3",
                "Microphone",
                "Corsair",
                159.99,
                65,
                12,
                ["Corsair", "Streaming", "Professional", "USB-C"],
            ),
            (
                "SteelSeries Arctis Pro",
                "Microphone",
                "SteelSeries",
                89.99,
                75,
                15,
                ["SteelSeries", "Streaming", "Budget", "Compact"],
            ),
            (
                "ASUS ROG Strix Magnus",
                "Microphone",
                "ASUS",
                119.99,
                60,
                12,
                ["ASUS", "Streaming", "RGB", "Budget"],
            ),
            (
                "MSI Immerse",
                "Microphone",
                "MSI",
                49.99,
                90,
                20,
                ["MSI", "Streaming", "Budget", "Compact"],
            ),
            # Additional Mousepads
            (
                "Logitech G640",
                "Mousepad",
                "Logitech",
                29.99,
                90,
                20,
                ["Logitech", "Gaming", "Budget", "Durable"],
            ),
            (
                "HyperX Fury S",
                "Mousepad",
                "HyperX",
                19.99,
                95,
                25,
                ["HyperX", "Gaming", "Budget", "Durable"],
            ),
            (
                "ASUS ROG Sheath",
                "Mousepad",
                "ASUS",
                39.99,
                80,
                18,
                ["ASUS", "Gaming", "RGB", "Premium"],
            ),
            (
                "MSI Gaming Mousepad",
                "Mousepad",
                "MSI",
                14.99,
                100,
                30,
                ["MSI", "Gaming", "Budget", "Durable"],
            ),
            (
                "Gigabyte AORUS AMP500",
                "Mousepad",
                "Gigabyte",
                44.99,
                75,
                15,
                ["Gigabyte", "Gaming", "RGB", "Premium"],
            ),
            (
                "Dell Precision Mat",
                "Mousepad",
                "Dell",
                24.99,
                85,
                20,
                ["Dell", "Professional", "Budget", "Durable"],
            ),
            # Additional Speakers
            (
                "Logitech Z906",
                "Speakers",
                "Logitech",
                299.99,
                40,
                8,
                ["Logitech", "Premium", "5.1", "Gaming"],
            ),
            (
                "Razer Nommo",
                "Speakers",
                "Razer",
                149.99,
                60,
                12,
                ["Razer", "Gaming", "2.0", "RGB"],
            ),
            (
                "Corsair SP120",
                "Speakers",
                "Corsair",
                79.99,
                75,
                15,
                ["Corsair", "Gaming", "2.0", "Budget"],
            ),
            (
                "SteelSeries Arena 3",
                "Speakers",
                "SteelSeries",
                89.99,
                70,
                15,
                ["SteelSeries", "Gaming", "2.0", "Budget"],
            ),
            (
                "ASUS ROG Strix Magnus",
                "Speakers",
                "ASUS",
                199.99,
                50,
                10,
                ["ASUS", "Gaming", "2.1", "Premium"],
            ),
            (
                "MSI Gaming Speakers",
                "Speakers",
                "MSI",
                59.99,
                80,
                18,
                ["MSI", "Gaming", "2.0", "Budget"],
            ),
            (
                "Gigabyte AORUS GS",
                "Speakers",
                "Gigabyte",
                129.99,
                65,
                12,
                ["Gigabyte", "Gaming", "2.1", "RGB"],
            ),
            (
                "Dell Pro Stereo",
                "Speakers",
                "Dell",
                89.99,
                75,
                15,
                ["Dell", "Professional", "2.0", "Budget"],
            ),
            (
                "HP Pavilion Audio",
                "Speakers",
                "HP",
                69.99,
                80,
                18,
                ["HP", "Budget", "2.0", "Durable"],
            ),
        ]

        # Modify specific products for stock scenarios
        # 7 products out of stock
        out_of_stock_indices = [
            5,
            15,
            25,
            35,
            45,
            55,
            65,
        ]  # Spread across different categories
        for idx in out_of_stock_indices:
            if idx < len(products_data):
                name, product_type, brand, price, _, min_stock, tag_names = (
                    products_data[idx]
                )
                products_data[idx] = (
                    name,
                    product_type,
                    brand,
                    price,
                    0,
                    min_stock,
                    tag_names,
                )

        # 15 products low stock (stock below min_stock_level)
        low_stock_indices = [
            2,
            7,
            12,
            17,
            22,
            27,
            32,
            37,
            42,
            47,
            52,
            57,
            62,
            67,
            72,
        ]  # Spread across different categories
        for idx in low_stock_indices:
            if idx < len(products_data):
                name, product_type, brand, price, _, min_stock, tag_names = (
                    products_data[idx]
                )
                # Set stock to 1-3 units below min_stock_level
                low_stock_amount = max(1, min_stock - random.randint(1, 3))
                products_data[idx] = (
                    name,
                    product_type,
                    brand,
                    price,
                    low_stock_amount,
                    min_stock,
                    tag_names,
                )

        products = []
        for (
            name,
            product_type,
            brand,
            price,
            stock,
            min_stock,
            tag_names,
        ) in products_data:
            product = Product(
                name=name,
                type=product_type,
                brand=brand,
                price=price,
                stock_quantity=stock,
                min_stock_level=min_stock,
            )
            session.add(product)
            products.append(product)

        session.commit()

        # Add tags to products
        for product, (
            name,
            product_type,
            brand,
            price,
            stock,
            min_stock,
            tag_names,
        ) in zip(products, products_data):
            for tag_name in tag_names:
                tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
                if tag:
                    product_tag = ProductTag(product_id=product.id, tag_id=tag.id)
                    session.add(product_tag)

        session.commit()

        # Create users with names reflecting their interests
        users_data = [
            "John Gaming",
            "Sarah Professional",
            "Mike Streaming",
            "Emma Wireless",
            "Alex Budget",
            "Lisa Premium",
            "Tom Mechanical",
            "Rachel Silent",
            "David Ultra-wide",
            "Jessica Portable",
            "Chris RGB",
            "Maria Ergonomic",
            "Kevin Tech",
            "Amanda Creative",
            "Robert Builder",
            "Sophie Designer",
            "Michael Gamer",
        ]

        users = []
        for name in users_data:
            user = User(name=name, is_member=random.choice([True, False]))
            session.add(user)
            users.append(user)

        session.commit()

        session.commit()

        # Create orders for each user (at least 3 per user)
        order_dates = [
            datetime.now() - timedelta(days=random.randint(1, 365)),
            datetime.now() - timedelta(days=random.randint(1, 365)),
            datetime.now() - timedelta(days=random.randint(1, 365)),
            datetime.now() - timedelta(days=random.randint(1, 365)),
            datetime.now() - timedelta(days=random.randint(1, 365)),
        ]

        for user in users:
            # Create 3-8 orders per user
            num_orders = random.randint(3, 8)
            for i in range(num_orders):
                order = Order(
                    user_id=user.id,
                    date=order_dates[i]
                    if i < len(order_dates)
                    else datetime.now() - timedelta(days=random.randint(1, 365)),
                )
                session.add(order)
                session.commit()

                # Add 1-3 products to each order
                num_products = random.randint(1, 3)
                selected_products = random.sample(
                    products, min(num_products, len(products))
                )

                final_price = 0
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    order_product = OrderProduct(
                        order_id=order.id, product_id=product.id, quantity=quantity
                    )
                    session.add(order_product)
                    final_price += product.price * quantity

                order.final_price = final_price
                session.commit()

        print("Database populated successfully!")
        print(f"Created {len(brands)} brands and {len(categories)} categories")
        print(
            f"Created {len(products)} products (30 original + 40 additional = 70 total)"
        )
        print(f"Created {len(users)} users")
        print("Created orders for all users (3-8 orders each)")
        print("\nStock Status:")
        print("- 7 products: OUT OF STOCK (0 units)")
        print("- 15 products: LOW STOCK (below min_stock_level)")
        print("- 48 products: NORMAL STOCK (above min_stock_level)")
        print("\nProduct Distribution:")
        print(
            "- Mice: 13 products (Logitech, Razer, Corsair, SteelSeries, HyperX, ASUS, MSI, Gigabyte)"
        )
        print(
            "- Keyboards: 13 products (Logitech, Razer, Corsair, SteelSeries, HyperX, ASUS, MSI, Gigabyte)"
        )
        print(
            "- Headsets: 13 products (Logitech, Razer, Corsair, SteelSeries, HyperX, ASUS, MSI, Gigabyte)"
        )
        print("- Monitors: 12 products (Samsung, LG, ASUS, MSI, Dell, HP, Gigabyte)")
        print(
            "- Webcams: 8 products (Logitech, Razer, HyperX, Corsair, SteelSeries, ASUS, MSI)"
        )
        print(
            "- Microphones: 8 products (Blue, HyperX, Razer, Logitech, Corsair, SteelSeries, ASUS, MSI)"
        )
        print(
            "- Mousepads: 9 products (SteelSeries, Corsair, Razer, Logitech, HyperX, ASUS, MSI, Gigabyte, Dell)"
        )
        print(
            "- Speakers: 10 products (Logitech, Razer, Corsair, SteelSeries, ASUS, MSI, Gigabyte, Dell, HP)"
        )


if __name__ == "__main__":
    populate_database()
