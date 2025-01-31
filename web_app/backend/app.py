from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.knn.recommender import KNNRecommender

app = Flask(__name__)
CORS(app)

# Initialize the recommender system
recommender = KNNRecommender()
recommender.load_data()
recommender.fit()

@app.route('/api/shows/similar/<int:show_id>', methods=['GET'])
def get_similar_shows(show_id):
    """Get similar shows based on a show ID."""
    try:
        n_recommendations = int(request.args.get('n', 5))
        similar_shows = recommender.get_similar_shows(show_id, n_recommendations)
        return jsonify({
            'success': True,
            'recommendations': similar_shows
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get personalized recommendations based on user ratings."""
    try:
        data = request.get_json()
        if not data or 'ratings' not in data:
            return jsonify({
                'success': False,
                'error': 'No ratings provided'
            }), 400
            
        # Convert ratings to the expected format
        user_ratings = {int(k): float(v) for k, v in data['ratings'].items()}
        n_recommendations = int(data.get('n', 5))
        
        recommendations = recommender.get_recommendations(
            user_ratings,
            n_recommendations
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/shows/search', methods=['GET'])
def search_shows():
    """Search for shows by title."""
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({
                'success': False,
                'error': 'No search query provided'
            }), 400
            
        # Simple search implementation
        matches = recommender.shows_df[
            recommender.shows_df['title'].str.lower().str.contains(query)
        ].to_dict('records')
        
        return jsonify({
            'success': True,
            'shows': matches[:10]  # Limit to 10 results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    # Load environment variables
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    app.run(host=host, port=port, debug=debug) 