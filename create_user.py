from app import app, db, User

with app.app_context():
    # Create the database tables if they don't exist
    db.create_all()
    
    # Check if user already exists
    user = User.query.filter_by(username='root').first()
    if not user:
        # Create new user
        user = User(username='root')
        user.set_password('root')
        db.session.add(user)
        db.session.commit()
        print("User 'root' created successfully!")
    else:
        print("User 'root' already exists!") 