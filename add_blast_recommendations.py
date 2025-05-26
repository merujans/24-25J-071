from app import app, db, BlastRecommendation

def add_recommendations():
    with app.app_context():
        # First, clear existing recommendations
        BlastRecommendation.query.delete()
        
        # Add your recommendations here
        recommendations = [
            BlastRecommendation(
                disease="Brown Spot",
                cause="Bipolaris oryzae",
                symptoms="Small, circular to oval brown lesions on leaves. Spots have a dark brown margin and light brown/gray center. Severe infection leads to leaf drying and plant weakening. Can also affect grains, causing “pecky rice” (discolored grains).",
                rec_high="Spray a copper-based fungicide within 24 h and remove heavily infected leaves.",
                rec_medium="Scout in  48 h; if >10 % of leaves show lesions, apply copper fungicide",
                rec_low="Low-confidence detection. Re-shoot image under daylight or send a lab sample before spraying.",
                preventive_measures="1. Use resistant rice varieties.<br>2. Ensure proper seed treatment with fungicides before sowing.<br>3. Maintain good field sanitation (removing infected plant debris).<br>4. Avoid excessive nitrogen application, which makes plants more vulnerable."
            ),
            BlastRecommendation(
                disease="Leaf Blast",
                cause="Magnaporthe oryzae",
                symptoms="Diamond or spindle-shaped grayish lesions with dark brown margins on leaves. Severe infection leads to leaf drying and plant stunting. Can spread rapidly under humid and warm conditions.",
                rec_high="Apply triazole fungicide immediately and keep a 5 cm flood.",
                rec_medium="Monitor daily; spray triazole if lesions enlarge or reach the collar region.",
                rec_low="Possible early blast. Improve pottasium fertilisation and re-inspect in 3 days.",
                preventive_measures="1. Plant resistant varieties (e.g., IR64, Swarna-Sub1).<br>2. Use clean, disease-free seeds.<br>3. Ensure proper crop spacing for good air circulation.<br>4. Rotate crops to break the disease cycle."
            ),
            BlastRecommendation(
                disease="Neck Blast",
                cause="Magnaporthe oryzae",
                symptoms="Dark brown to black lesions on the neck of the panicle (just below the grain clusters). Infected panicles turn white and fail to produce grains (called “whitehead”). Grain yield is significantly reduced in severe cases.",
                rec_high="Spray triazole + strobilurin at panicle initiation and booting; avoid late nitrogen.",
                rec_medium="High risk. Schedule fungicide at boot stage and maintain shallow flooding.",
                rec_low="Indeterminate. Inspect panicles for grey spindle lesions before treatment.",
                preventive_measures="1. Plant resistant varieties.<br>2. Use disease-free seeds and treat them with fungicides.<br>3. Maintain balanced fertilization (adequate phosphorus and potassium).<br>4. Avoid planting in areas with a history of severe blast outbreaks."
            ),
            BlastRecommendation(
                disease="Healthy",
                cause="None",
                symptoms="None",
                rec_high="No disease signs detected. Keep scouting every 3-5 days.",
                rec_medium="Mostly healthy. Confirm in field and maintain balanced fertiliser.",
                rec_low="Image unclear; retake in better light for confirmation.",
                preventive_measures="None"
            )
        ]
        
        for recommendation in recommendations:
            db.session.add(recommendation)
        
        # Commit the changes
        db.session.commit()
        print("Blast recommendations added successfully!")

if __name__ == "__main__":
    add_recommendations() 
