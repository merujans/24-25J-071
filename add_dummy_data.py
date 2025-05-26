from app import app, db, RiceBlast, RiceBlight, RiceGrain
from datetime import datetime, timedelta
import random

# Sample data for Rice Blast
blast_classes = ['Healthy', 'Brown Spot', 'Leaf Blast', 'Neck Blast']
blast_dummy_data = [
    {
        'image': 'uploads/blast/sample1.jpg',
        'title': 'Rice Plant Sample 1',
        'datetime': datetime.now() - timedelta(days=5),
        'predicted_class': 'Healthy',
        'predicted_probability': 0.95
    },
    {
        'image': 'uploads/blast/sample2.jpg',
        'title': 'Rice Plant Sample 2',
        'datetime': datetime.now() - timedelta(days=4),
        'predicted_class': 'Brown Spot',
        'predicted_probability': 0.88
    },
    {
        'image': 'uploads/blast/sample3.jpg',
        'title': 'Rice Plant Sample 3',
        'datetime': datetime.now() - timedelta(days=3),
        'predicted_class': 'Leaf Blast',
        'predicted_probability': 0.92
    },
    {
        'image': 'uploads/blast/sample4.jpg',
        'title': 'Rice Plant Sample 4',
        'datetime': datetime.now() - timedelta(days=2),
        'predicted_class': 'Neck Blast',
        'predicted_probability': 0.85
    },
    {
        'image': 'uploads/blast/sample5.jpg',
        'title': 'Rice Plant Sample 5',
        'datetime': datetime.now() - timedelta(days=1),
        'predicted_class': 'Healthy',
        'predicted_probability': 0.91
    }
]

# Sample data for Rice Blight
blight_classes = ['Healthy', 'Bacterial Leaf Blight', 'Sheath Blight', 'Leaf Scald']
blight_dummy_data = [
    {
        'image': 'uploads/blight/sample1.jpg',
        'title': 'Blight Test Sample 1',
        'datetime': datetime.now() - timedelta(days=5),
        'predicted_class': 'Healthy',
        'predicted_probability': 0.94
    },
    {
        'image': 'uploads/blight/sample2.jpg',
        'title': 'Blight Test Sample 2',
        'datetime': datetime.now() - timedelta(days=4),
        'predicted_class': 'Bacterial Leaf Blight',
        'predicted_probability': 0.87
    },
    {
        'image': 'uploads/blight/sample3.jpg',
        'title': 'Blight Test Sample 3',
        'datetime': datetime.now() - timedelta(days=3),
        'predicted_class': 'Sheath Blight',
        'predicted_probability': 0.89
    },
    {
        'image': 'uploads/blight/sample4.jpg',
        'title': 'Blight Test Sample 4',
        'datetime': datetime.now() - timedelta(days=2),
        'predicted_class': 'Leaf Scald',
        'predicted_probability': 0.83
    },
    {
        'image': 'uploads/blight/sample5.jpg',
        'title': 'Blight Test Sample 5',
        'datetime': datetime.now() - timedelta(days=1),
        'predicted_class': 'Bacterial Leaf Blight',
        'predicted_probability': 0.90
    }
]

# Add this to the existing dummy data arrays
grain_classes = ['Normal', 'Impurity', 'Fusarium & Shriveled', 'Sprouted', 'Moldy', 'Broken Grain', 'Infested by Insects', 'Unripe Grain']
grain_dummy_data = [
    {
        'image': 'uploads/grain/sample1.jpg',
        'title': 'Grain Quality Sample 1',
        'datetime': datetime.now() - timedelta(days=5),
        'predicted_class': 'Normal',
        'predicted_probability': 0.94
    },
    {
        'image': 'uploads/grain/sample2.jpg',
        'title': 'Grain Quality Sample 2',
        'datetime': datetime.now() - timedelta(days=4),
        'predicted_class': 'Impurity',
        'predicted_probability': 0.87
    },
    {
        'image': 'uploads/grain/sample3.jpg',
        'title': 'Grain Quality Sample 3',
        'datetime': datetime.now() - timedelta(days=3),
        'predicted_class': 'Fusarium & Shriveled',
        'predicted_probability': 0.89
    },
    {
        'image': 'uploads/grain/sample4.jpg',
        'title': 'Grain Quality Sample 4',
        'datetime': datetime.now() - timedelta(days=2),
        'predicted_class': 'Broken Grain',
        'predicted_probability': 0.92
    },
    {
        'image': 'uploads/grain/sample5.jpg',
        'title': 'Grain Quality Sample 5',
        'datetime': datetime.now() - timedelta(days=1),
        'predicted_class': 'Moldy',
        'predicted_probability': 0.88
    }
]

def add_dummy_data():
    with app.app_context():
        # Clear existing data
        RiceBlast.query.delete()
        RiceBlight.query.delete()
        RiceGrain.query.delete()
        
        # Add Rice Blast dummy data
        for data in blast_dummy_data:
            detection = RiceBlast(
                image=data['image'],
                title=data['title'],
                datetime=data['datetime'],
                predicted_class=data['predicted_class'],
                predicted_probability=data['predicted_probability']
            )
            db.session.add(detection)
        
        # Add Rice Blight dummy data
        for data in blight_dummy_data:
            detection = RiceBlight(
                image=data['image'],
                title=data['title'],
                datetime=data['datetime'],
                predicted_class=data['predicted_class'],
                predicted_probability=data['predicted_probability']
            )
            db.session.add(detection)
        
        # Add Rice Grain dummy data
        for data in grain_dummy_data:
            detection = RiceGrain(
                image=data['image'],
                title=data['title'],
                datetime=data['datetime'],
                predicted_class=data['predicted_class'],
                predicted_probability=data['predicted_probability']
            )
            db.session.add(detection)
        
        # Commit all changes
        db.session.commit()
        print("Dummy data added successfully!")

if __name__ == "__main__":
    add_dummy_data() 