from app import app, db, BlightRecommendation

def add_recommendations():
    with app.app_context():
        # First, clear existing recommendations
        BlightRecommendation.query.delete()
        
        # Add your recommendations here
        recommendations = [
            BlightRecommendation(
                disease="Bacterial Leaf Blight",
                cause="Xanthomonas oryzae",
                symptoms="Yellowing and wilting of leaves, water-soaked lesions along leaf edges, progressing to drying.",
                rec_high="Apply copper oxychloride (2 kg/ha) + surfactant; drain excess water.",
                rec_medium="Clip diseased leaf tips; spray copper if streaking spreads.",
                rec_low="Suspected blight. Dry canopy and re-scan after 24 h.",
                preventive_measures="1. Rotate crops to avoid pathogen buildup.<br>2. Use disease-free seeds.<br>3. Control insect vectors (leafhoppers) that spread the disease.<br>4. Avoid overhead irrigation, as water spreads bacteria."
            ),
            BlightRecommendation(
                disease="Sheath Blight",
                cause="Rhizoctonia solani",
                symptoms="Elliptical or oval lesions on leaf sheaths, lesions enlarge and become grayish-white with brown margins, causing lodging.",
                rec_high="Spray carbendazim and reduce canopy humidity via wider spacing.",
                rec_medium="Monitor humid spots; spot-sptray fungicide if streaks enlarge.",
                rec_low="Low certainy. Consider varietal resistance and resample.",
                preventive_measures="1. Rotate with non-host crops (e.g., legumes, vegetables).<br>2. Use resistant rice varieties.<br>3. Maintain good drainage and avoid water stagnation.<br>4. Remove infected plant residues from the field."
            ),
            BlightRecommendation(
                disease="Leaf Scald",
                cause="Microdochium oryzae",
                symptoms="Brown, water-soaked spots that extend into streaks, with a scalded appearance, often seen in high-humidity conditions.",
                rec_high="Apply propiconazole; avoid nitrogen top-dress; improve air flow.",
                rec_medium="Schedule fungicide if lesions reach upper canopy.",
                rec_low="Possible early sheath blight. Scout lower sheaths again in 48 hours.",
                preventive_measures="1. Use disease-resistant rice varieties.<br>2. Avoid excessive irrigation, especially during humid periods.<br>3. Rotate crops to reduce fungal persistence.<br>4. Remove plant debris after harvest."
            ),
            BlightRecommendation(
                disease="Healthy",
                cause="None",
                symptoms="None",
                rec_high="Leaf appears healthy; continue weekly monitoring.",
                rec_medium="Likely healthy. Verify in field.",
                rec_low="Camera glare or shadow; retake image.",
                preventive_measures="None"
            )
        ]
        
        # Add all recommendations
        for recommendation in recommendations:
            db.session.add(recommendation)
        
        # Commit the changes
        db.session.commit()
        print("Blight recommendations added successfully!")

if __name__ == "__main__":
    add_recommendations() 