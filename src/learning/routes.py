from flask import Blueprint, render_template

learning = Blueprint("learning", __name__)

@learning.route("/learning_journey", methods=["GET"])
def index():
    """
    The student would like to see how he is progressing in his learning journey
    """
    return render_template("learning.html")


