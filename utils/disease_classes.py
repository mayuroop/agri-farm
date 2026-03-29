# 38 Plant Disease Classes from the PlantVillage dataset
# Indices match the model output order (alphabetical by class name)

DISEASE_CLASSES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy',
]

# Human-readable names
DISEASE_DISPLAY_NAMES = {
    'Apple___Apple_scab': 'Apple Scab',
    'Apple___Black_rot': 'Apple Black Rot',
    'Apple___Cedar_apple_rust': 'Cedar Apple Rust',
    'Apple___healthy': 'Apple (Healthy)',
    'Blueberry___healthy': 'Blueberry (Healthy)',
    'Cherry_(including_sour)___Powdery_mildew': 'Cherry Powdery Mildew',
    'Cherry_(including_sour)___healthy': 'Cherry (Healthy)',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': 'Corn Gray Leaf Spot',
    'Corn_(maize)___Common_rust_': 'Corn Common Rust',
    'Corn_(maize)___Northern_Leaf_Blight': 'Corn Northern Leaf Blight',
    'Corn_(maize)___healthy': 'Corn (Healthy)',
    'Grape___Black_rot': 'Grape Black Rot',
    'Grape___Esca_(Black_Measles)': 'Grape Esca (Black Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': 'Grape Leaf Blight',
    'Grape___healthy': 'Grape (Healthy)',
    'Orange___Haunglongbing_(Citrus_greening)': 'Citrus Greening (Huanglongbing)',
    'Peach___Bacterial_spot': 'Peach Bacterial Spot',
    'Peach___healthy': 'Peach (Healthy)',
    'Pepper,_bell___Bacterial_spot': 'Bell Pepper Bacterial Spot',
    'Pepper,_bell___healthy': 'Bell Pepper (Healthy)',
    'Potato___Early_blight': 'Potato Early Blight',
    'Potato___Late_blight': 'Potato Late Blight',
    'Potato___healthy': 'Potato (Healthy)',
    'Raspberry___healthy': 'Raspberry (Healthy)',
    'Soybean___healthy': 'Soybean (Healthy)',
    'Squash___Powdery_mildew': 'Squash Powdery Mildew',
    'Strawberry___Leaf_scorch': 'Strawberry Leaf Scorch',
    'Strawberry___healthy': 'Strawberry (Healthy)',
    'Tomato___Bacterial_spot': 'Tomato Bacterial Spot',
    'Tomato___Early_blight': 'Tomato Early Blight',
    'Tomato___Late_blight': 'Tomato Late Blight',
    'Tomato___Leaf_Mold': 'Tomato Leaf Mold',
    'Tomato___Septoria_leaf_spot': 'Tomato Septoria Leaf Spot',
    'Tomato___Spider_mites Two-spotted_spider_mite': 'Tomato Spider Mites',
    'Tomato___Target_Spot': 'Tomato Target Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 'Tomato Yellow Leaf Curl Virus',
    'Tomato___Tomato_mosaic_virus': 'Tomato Mosaic Virus',
    'Tomato___healthy': 'Tomato (Healthy)',
}

# Treatment and prevention information per disease
DISEASE_INFO = {
    'Apple___Apple_scab': {
        'severity': 'Medium',
        'treatment': [
            'Apply fungicides containing captan, myclobutanil, or mancozeb',
            'Begin spraying at bud break and repeat every 7-10 days during wet weather',
            'Remove and destroy fallen infected leaves to reduce spore sources',
        ],
        'prevention': [
            'Plant scab-resistant apple varieties',
            'Ensure good air circulation by proper pruning',
            'Avoid overhead irrigation',
        ],
    },
    'Apple___Black_rot': {
        'severity': 'High',
        'treatment': [
            'Prune out cankers and dead wood at least 8 inches below visible infection',
            'Apply fungicides (captan, thiophanate-methyl) during growing season',
            'Remove mummified fruit from trees and ground',
        ],
        'prevention': [
            'Maintain orchard sanitation by removing dead wood',
            'Avoid wounding trees during pruning',
            'Apply dormant copper sprays before bud break',
        ],
    },
    'Apple___Cedar_apple_rust': {
        'severity': 'Medium',
        'treatment': [
            'Apply fungicides (myclobutanil, propiconazole) at pink bud stage',
            'Continue sprays every 7-10 days through petal fall',
            'Remove galls from nearby juniper/cedar trees if possible',
        ],
        'prevention': [
            'Plant rust-resistant apple varieties',
            'Remove eastern red cedars within 1-2 miles if feasible',
            'Apply preventative fungicide sprays in spring',
        ],
    },
    'Apple___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': [
            'Continue regular monitoring for early disease signs',
            'Maintain balanced fertilization',
            'Ensure proper irrigation and drainage',
        ],
    },
    'Blueberry___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Monitor soil pH (4.5-5.5)', 'Regular pruning for air circulation'],
    },
    'Cherry_(including_sour)___Powdery_mildew': {
        'severity': 'Medium',
        'treatment': [
            'Apply sulfur-based or potassium bicarbonate fungicides',
            'Use systemic fungicides (myclobutanil, trifloxystrobin) for severe infections',
            'Remove heavily infected shoots',
        ],
        'prevention': [
            'Plant in full sun with good air circulation',
            'Avoid excess nitrogen fertilization',
            'Apply preventative sulfur sprays in spring',
        ],
    },
    'Cherry_(including_sour)___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Regular pruning', 'Balanced fertilization', 'Monitor for pests'],
    },
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': {
        'severity': 'High',
        'treatment': [
            'Apply fungicides (strobilurins, triazoles) at first sign of disease',
            'Treat at VT/R1 growth stage for best economic return',
            'Use foliar fungicides if disease pressure is high',
        ],
        'prevention': [
            'Plant resistant hybrids',
            'Rotate crops (avoid corn after corn)',
            'Till residue to reduce inoculum',
        ],
    },
    'Corn_(maize)___Common_rust_': {
        'severity': 'Medium',
        'treatment': [
            'Apply fungicides (propiconazole, azoxystrobin) if rust is severe before tasseling',
            'Treat early when pustules first appear on upper leaf surface',
        ],
        'prevention': [
            'Plant rust-resistant corn hybrids',
            'Monitor fields regularly during growing season',
            'Early planting to avoid peak rust-spore periods',
        ],
    },
    'Corn_(maize)___Northern_Leaf_Blight': {
        'severity': 'High',
        'treatment': [
            'Apply foliar fungicides (azoxystrobin, propiconazole) at first sign',
            'Focus treatment on upper canopy to protect ears',
        ],
        'prevention': [
            'Use resistant hybrids',
            'Crop rotation and residue management',
            'Avoid fields with history of northern leaf blight',
        ],
    },
    'Corn_(maize)___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Regular scouting', 'Balanced NPK fertilization', 'Proper plant spacing'],
    },
    'Grape___Black_rot': {
        'severity': 'High',
        'treatment': [
            'Apply fungicides (myclobutanil, mancozeb) starting at bud break',
            'Continue every 10-14 days through véraison',
            'Remove and destroy all mummified berries and infected leaves',
        ],
        'prevention': [
            'Ensure good air circulation through pruning and trellising',
            'Remove mummified fruit in winter',
            'Apply dormant lime-sulfur sprays',
        ],
    },
    'Grape___Esca_(Black_Measles)': {
        'severity': 'High',
        'treatment': [
            'No effective chemical control once established',
            'Prune out infected wood well below visible symptoms',
            'Protect pruning wounds with wound sealants',
        ],
        'prevention': [
            'Use certified disease-free planting material',
            'Avoid large pruning cuts',
            'Apply wound protectants after pruning',
        ],
    },
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': {
        'severity': 'Medium',
        'treatment': [
            'Apply copper-based or mancozeb fungicides',
            'Remove and destroy infected leaves',
        ],
        'prevention': ['Ensure good air circulation', 'Avoid overhead irrigation'],
    },
    'Grape___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Regular canopy management', 'Balanced vine nutrition'],
    },
    'Orange___Haunglongbing_(Citrus_greening)': {
        'severity': 'Critical',
        'treatment': [
            'No cure exists — remove and destroy infected trees',
            'Apply thermotherapy (hot water treatment on young trees) as experimental option',
            'Control Asian citrus psyllid vector with insecticides (imidacloprid, thiamethoxam)',
        ],
        'prevention': [
            'Plant certified disease-free nursery stock',
            'Control psyllid populations with systemic insecticides',
            'Inspect new trees thoroughly before planting',
        ],
    },
    'Peach___Bacterial_spot': {
        'severity': 'High',
        'treatment': [
            'Apply copper-based bactericides starting at shuck split',
            'Continue sprays every 5-7 days during wet weather',
            'Prune out heavily infected shoots',
        ],
        'prevention': [
            'Plant resistant peach varieties',
            'Avoid overhead irrigation',
            'Plant in well-ventilated locations',
        ],
    },
    'Peach___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Annual dormant copper sprays', 'Proper thinning for good air circulation'],
    },
    'Pepper,_bell___Bacterial_spot': {
        'severity': 'High',
        'treatment': [
            'Apply copper-based bactericides weekly',
            'Remove and destroy severely infected plants',
            'Avoid working in wet fields to prevent spread',
        ],
        'prevention': [
            'Use disease-free certified seed',
            'Rotate with non-solanaceous crops for 2-3 years',
            'Avoid overhead irrigation',
        ],
    },
    'Pepper,_bell___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Monitor for aphids (virus vectors)', 'Proper spacing for air flow'],
    },
    'Potato___Early_blight': {
        'severity': 'Medium',
        'treatment': [
            'Apply fungicides (chlorothalonil, mancozeb, azoxystrobin) at first sign',
            'Repeat every 7-14 days depending on disease pressure',
            'Remove lower infected leaves',
        ],
        'prevention': [
            'Plant certified disease-free seed potatoes',
            'Rotate crops for 2-3 years',
            'Maintain adequate soil fertility (especially potassium)',
        ],
    },
    'Potato___Late_blight': {
        'severity': 'Critical',
        'treatment': [
            'Apply fungicides (cymoxanil, mancozeb, chlorothalonil) immediately',
            'Spray every 5-7 days in wet conditions',
            'Destroy infected plants and do not compost them',
        ],
        'prevention': [
            'Plant resistant varieties (e.g., Sarpo Mira)',
            'Use certified disease-free seed potatoes',
            'Avoid overhead irrigation and ensure good drainage',
        ],
    },
    'Potato___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Hill plants to protect tubers', 'Rotate crops yearly'],
    },
    'Raspberry___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Annual cane renovation', 'Monitor for cane blight'],
    },
    'Soybean___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Monitor for aphids and spider mites', 'Rotate with corn'],
    },
    'Squash___Powdery_mildew': {
        'severity': 'Medium',
        'treatment': [
            'Apply potassium bicarbonate, neem oil, or sulfur fungicides',
            'Use systemic fungicides (myclobutanil) for severe infections',
        ],
        'prevention': [
            'Plant mildew-resistant varieties',
            'Space plants for good air circulation',
            'Avoid late-evening watering',
        ],
    },
    'Strawberry___Leaf_scorch': {
        'severity': 'Medium',
        'treatment': [
            'Apply fungicides (captan, myclobutanil) at early sign of disease',
            'Remove heavily infected older leaves',
        ],
        'prevention': [
            'Plant disease-resistant varieties',
            'Avoid overhead irrigation',
            'Maintain good plant spacing',
        ],
    },
    'Strawberry___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Annual renovation after harvest', 'Monitor for spider mites'],
    },
    'Tomato___Bacterial_spot': {
        'severity': 'High',
        'treatment': [
            'Apply copper-based bactericides preventatively',
            'Avoid working in wet fields',
            'Remove heavily infected plant material',
        ],
        'prevention': [
            'Use disease-free certified seed or transplants',
            'Rotate crops for 2+ years',
            'Avoid overhead irrigation',
        ],
    },
    'Tomato___Early_blight': {
        'severity': 'Medium',
        'treatment': [
            'Apply fungicides (chlorothalonil, mancozeb, copper) at first sign',
            'Remove lower infected leaves to reduce spread',
            'Continue spraying on 7-10 day intervals',
        ],
        'prevention': [
            'Rotate crops with non-solanaceous plants',
            'Mulch to prevent soil splash',
            'Maintain adequate plant spacing',
        ],
    },
    'Tomato___Late_blight': {
        'severity': 'Critical',
        'treatment': [
            'Apply fungicides (cymoxanil+mancozeb, chlorothalonil) immediately at first sign',
            'Spray every 5-7 days in cool wet weather',
            'Remove and bag infected plant debris — do not compost',
        ],
        'prevention': [
            'Plant resistant varieties',
            'Avoid overhead watering',
            'Ensure good air circulation',
        ],
    },
    'Tomato___Leaf_Mold': {
        'severity': 'Medium',
        'treatment': [
            'Improve greenhouse ventilation to lower humidity',
            'Apply fungicides (copper, chlorothalonil, mancozeb)',
            'Remove infected leaves',
        ],
        'prevention': [
            'Maintain humidity below 85%',
            'Space plants adequately',
            'Use resistant varieties',
        ],
    },
    'Tomato___Septoria_leaf_spot': {
        'severity': 'High',
        'treatment': [
            'Apply fungicides (chlorothalonil, mancozeb, copper) weekly',
            'Remove lower infected leaves promptly',
            'Avoid wetting foliage when watering',
        ],
        'prevention': [
            'Crop rotation (3-year minimum with non-solanaceous crops)',
            'Mulch soil surface to reduce spore splash',
            'Remove plant debris at end of season',
        ],
    },
    'Tomato___Spider_mites Two-spotted_spider_mite': {
        'severity': 'High',
        'treatment': [
            'Apply miticides (abamectin, spiromesifen) or insecticidal soap',
            'Spray undersides of leaves where mites colonize',
            'Introduce predatory mites (Phytoseiidae) for biological control',
        ],
        'prevention': [
            'Monitor regularly especially in hot dry weather',
            'Maintain adequate soil moisture',
            'Avoid broad-spectrum pesticides that kill natural enemies',
        ],
    },
    'Tomato___Target_Spot': {
        'severity': 'Medium',
        'treatment': [
            'Apply fungicides (azoxystrobin, chlorothalonil) at first sign',
            'Remove infected leaves and destroy',
        ],
        'prevention': [
            'Ensure good air circulation in crop canopy',
            'Avoid excessive nitrogen fertilization',
            'Rotate crops with non-solanaceous plants',
        ],
    },
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
        'severity': 'Critical',
        'treatment': [
            'No cure — remove and destroy infected plants immediately',
            'Control whitefly vector with insecticides (imidacloprid, thiamethoxam)',
            'Use reflective mulches to repel whiteflies',
        ],
        'prevention': [
            'Plant virus-resistant tomato varieties',
            'Use insect-proof screens in greenhouse production',
            'Control whitefly populations proactively',
        ],
    },
    'Tomato___Tomato_mosaic_virus': {
        'severity': 'High',
        'treatment': [
            'No cure — remove and destroy infected plants',
            'Disinfect tools with 10% bleach solution',
            'Wash hands thoroughly after handling infected plants',
        ],
        'prevention': [
            'Use TMV-resistant tomato varieties',
            'Do not smoke near plants (tobacco can carry virus)',
            'Use certified disease-free seed',
        ],
    },
    'Tomato___healthy': {
        'severity': 'None',
        'treatment': ['No treatment needed — plant appears healthy!'],
        'prevention': ['Regular monitoring', 'Balanced fertilization', 'Consistent watering'],
    },
}
