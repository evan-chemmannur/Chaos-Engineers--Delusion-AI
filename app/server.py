"""Flask web server exposing LoveAI features via REST API and web UI."""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, render_template_string, redirect

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.compatibility import CompatibilityAnalyzer
from app.core.image_comparator import ImageComparator
from app.ai.ai_advisor import AIAdvisorService
from app.ai.message_assistant import MessageAssistantService
from app.database.database import db
from app.config import (
    APP_NAME, APP_TAGLINE, COMPATIBILITY_DISCLAIMER, IMAGE_DISCLAIMER,
    GENERAL_DISCLAIMER, DEFAULT_INTERESTS, RELATIONSHIP_STATUSES,
    COMMUNICATION_FREQUENCIES, ADVISOR_GOALS, MESSAGE_TONES
)

app = Flask(__name__, static_folder=str(BASE_DIR / "assets"))

# Serve the main index.html file across all UI routes
@app.route("/")
@app.route("/home")
@app.route("/dashboard")
@app.route("/compatibility")
@app.route("/message")
@app.route("/journey")
@app.route("/milestones")
def index():
    index_path = BASE_DIR / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return render_template_string(content)
    return "LoveAI Server is running. index.html not found.", 404

# Redirect removed feature routes to home
@app.route("/image")
@app.route("/advisor")
def redirect_removed_routes():
    return redirect("/", code=302)

# Serve assets
@app.route("/assets/<path:filename>")
def serve_asset(filename):
    return send_from_directory(BASE_DIR / "assets", filename)

# ----------------- REST API Endpoints ----------------- #

@app.route("/api/config", methods=["GET"])
def get_config():
    """Returns application configuration and selectable options."""
    return jsonify({
        "app_name": APP_NAME,
        "tagline": APP_TAGLINE,
        "disclaimers": {
            "compatibility": COMPATIBILITY_DISCLAIMER,
            "image": IMAGE_DISCLAIMER,
            "general": GENERAL_DISCLAIMER,
        },
        "interests": DEFAULT_INTERESTS,
        "statuses": RELATIONSHIP_STATUSES,
        "frequencies": COMMUNICATION_FREQUENCIES,
        "goals": ADVISOR_GOALS,
        "tones": MESSAGE_TONES,
    })

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Returns current dashboard statistics from SQLite."""
    latest = db.get_latest_compatibility()
    completed, total = db.get_journey_progress()
    return jsonify({
        "latest_compatibility": latest,
        "journey": {
            "completed": completed,
            "total": total,
            "percentage": int((completed / total * 100) if total > 0 else 0)
        }
    })

@app.route("/api/compatibility", methods=["POST"])
def calculate_compatibility():
    """Calculates deterministic compatibility score."""
    data = request.get_json() or {}
    name1 = data.get("name1", "")
    name2 = data.get("name2", "")
    interests = data.get("interests", [])
    
    success, err, result = CompatibilityAnalyzer.analyze(name1, name2, interests)
    if not success:
        return jsonify({"success": False, "error": err}), 400
        
    if "score" in data and isinstance(data["score"], (int, float)):
        result["combined_score"] = max(0, min(100, int(data["score"])))
        
    db.save_compatibility_result(
        name1=result["name1"],
        name2=result["name2"],
        name_score=result["name_score"],
        interest_score=result["interest_score"],
        combined_score=result["combined_score"]
    )
    return jsonify({"success": True, "result": result})

@app.route("/api/image-similarity", methods=["POST"])
def compare_images_endpoint():
    """Receives two uploaded images and runs OpenCV visual similarity analysis."""
    if "image1" not in request.files or "image2" not in request.files:
        return jsonify({"success": False, "error": "Both 'image1' and 'image2' files are required."}), 400
        
    file1 = request.files["image1"]
    file2 = request.files["image2"]
    
    upload_dir = BASE_DIR / "temp_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    path1 = str(upload_dir / f"upload_1_{file1.filename}")
    path2 = str(upload_dir / f"upload_2_{file2.filename}")
    
    try:
        file1.save(path1)
        file2.save(path2)
        
        success, err, result = ImageComparator.compare_images(path1, path2)
        if not success:
            return jsonify({"success": False, "error": err}), 400
            
        return jsonify({"success": True, "result": result})
    finally:
        # Cleanup uploaded files
        for p in [path1, path2]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

@app.route("/api/advisor", methods=["POST"])
def get_advisor_roadmap():
    """Generates personalized roadmap for relationship scenario."""
    data = request.get_json() or {}
    status = data.get("relationship_status", "Classmate")
    freq = data.get("communication_freq", "Sometimes")
    interests = data.get("interests", [])
    goal = data.get("goal", "Ask them to hang out")
    situation = data.get("situation", "")
    
    success, msg, result = AIAdvisorService.generate_roadmap(
        relationship_status=status,
        communication_freq=freq,
        interests=interests,
        goal=goal,
        situation=situation
    )
    if not success:
        return jsonify({"success": False, "error": msg}), 400
        
    return jsonify({"success": True, "result": result})

@app.route("/api/message/analyze", methods=["POST"])
def analyze_message_endpoint():
    """Analyzes tone, pressure, clarity, and naturalness of a message."""
    data = request.get_json() or {}
    message = data.get("message", "")
    if not message.strip():
        return jsonify({"success": False, "error": "Message cannot be empty."}), 400
        
    success, msg, result = MessageAssistantService.analyze_message(message)
    return jsonify({"success": success, "result": result})

@app.route("/api/message/improve", methods=["POST"])
def improve_message_endpoint():
    """Generates alternative variations for message."""
    data = request.get_json() or {}
    message = data.get("message", "")
    tone = data.get("tone", "Casual")
    if not message.strip():
        return jsonify({"success": False, "error": "Message cannot be empty."}), 400
        
    success, msg, result = MessageAssistantService.improve_message(message, tone)
    return jsonify({"success": success, "result": result})

@app.route("/api/milestones", methods=["GET", "POST"])
def milestones_endpoint():
    """Fetches all milestones or adds a new milestone."""
    if request.method == "GET":
        items = db.get_all_milestones()
        return jsonify({"success": True, "milestones": items})
    else:
        data = request.get_json() or {}
        title = data.get("title", "").strip()
        if not title:
            return jsonify({"success": False, "error": "Milestone title required."}), 400
        mid = db.add_milestone(
            title=title,
            description=data.get("description", ""),
            event_date=data.get("event_date", ""),
            notes=data.get("notes", ""),
            completed=data.get("completed", 0)
        )
        return jsonify({"success": True, "id": mid})

@app.route("/api/milestones/<int:milestone_id>/toggle", methods=["POST"])
def toggle_milestone_endpoint(milestone_id):
    """Toggles completion status of a milestone."""
    success = db.toggle_milestone(milestone_id)
    return jsonify({"success": success})

@app.route("/api/milestones/<int:milestone_id>", methods=["DELETE"])
def delete_milestone_endpoint(milestone_id):
    """Deletes milestone."""
    success = db.delete_milestone(milestone_id)
    return jsonify({"success": success})

def run_server(port=5000, host="127.0.0.1"):
    print("==================================================")
    print("LoveAI Web Server is running!")
    print(f"Open in your browser: http://{host}:{port}")
    print("==================================================")
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    run_server()
